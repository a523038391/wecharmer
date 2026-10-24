"""新版待排柜离线验证，所有业务接口均替换为模拟响应。"""
import json
import inspect
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import requests

from lib.container.waitcontainerbill_v2 import WaitContainerBillv2
from lib.firstleg.stock_inspectionv2 import Inspectionv2
from interface.supplier.supplier_inventory_v2_api import SupplierInventoryv2_Api


def response(result=None, status=200):
    resp = requests.Response()
    resp.status_code = 200
    resp._content = json.dumps({"status": status, "result": result}).encode()
    return resp


def pool_item(id=101, purchaseOrderDetailId=501, **changes):
    item = {
        "id": id, "supplierInventoryId": id + 600, "purchaseOrderId": 10, "purchaseOrderCode": "PO-10",
        "purchaseOrderDetailId": purchaseOrderDetailId, "supplierId": 920,
        "shopId": 161, "shopAccount": "LIPENG", "operateDivisionId": 5,
        "operateDivisionName": "运营事业部", "operaterId": 303, "operaterName": "李朋",
        "skuId": 1, "skuCode": "SKU-1", "skuName": "测试SKU", "productId": 2,
        "productCode": "A5-181", "portId": 3, "portName": "起运港",
        "oneBoxLoadQuantity": 12, "boxLength": 40, "boxWidth": 30, "boxHeight": 20,
        "ctnVolume": 0.024, "ctnGrossWeight": 10, "ctnNetWeight": 9,
        "applyPurchaseBillId": 20, "applyPurchaseBillCode": "AP-20", "attributeTag": 1,
        "inventoryAvailableQuantity": 120, "appliedQuantity": 0, "isCanContainer": True,
        "countryTwoCharCode": "US", "salesPlanDate": "2026-08-01T00:00:00",
        "expectedPutOnSaleTime": "2027-02-20T00:00:00"
    }
    item.update(changes)
    return item


def inventory_item(id=701, purchaseOrderDetailId=501, **changes):
    item = pool_item(purchaseOrderDetailId=purchaseOrderDetailId)
    item.update({
        "id": id, "warehouseId": 129, "warehouseName": "库存返回的工厂仓", "supplierInventoryWarehouse": 3, "spuCode": "A5-181",
        "boxGauge": {"ctnQuantity": 24, "ctnLongX": 50, "ctnLongY": 35, "ctnLongZ": 25,
                     "ctnVolume": 0.04375, "ctnGrossWeight": 15, "ctnNetWeight": 14},
        "shippingPorts": [{"portId": 3, "portName": "库存起运港"}]
    })
    item.update(changes)
    return item


class WaitContainerBillV2Tests(unittest.TestCase):
    def setUp(self):
        module = "lib.container.waitcontainerbill_v2."
        self.inspection = self.enterContext(patch(module + "Inspectionv2")).return_value.inspection_purchaseorder_report
        self.purchase = self.enterContext(patch(module + "PurchaseOrder_Api")).return_value
        self.api = self.enterContext(patch(module + "WaitContainerBill_Api")).return_value
        self.inventory = self.enterContext(patch(module + "SupplierInventoryv2_Api")).return_value
        self.product = self.enterContext(patch(module + "Product")).return_value
        self.inspection.return_value = {"purchaseorderid": 10}
        self.purchase.get_purchaseorderv1_details.return_value = response({
            "skuDetailDimensionDetails": [{"purchaseOrderCode": "PO-10"}]})
        self.api.page_waitapplycontainer.return_value = response({"items": [pool_item()], "hasNextPages": False})
        self.inventory.page_supplierinventory.return_value = response({"items": [inventory_item()], "hasNextPages": False})
        self.api.create_waitcontainerbillv2.return_value = response(1000)
        self.api.waitcontainerbillv2_askapprove.return_value = response()
        self.product.sellersku_page.return_value = response({
            "items": [{"skuId": 1, "shopId": 161, "operateDivisionId": 5,
                       "fnSku": "FNSKU-1", "code": "SELLER-1"}]})
        self.params = {
            "cookies": {"Authorization": "offline"}, "shopId": 161, "shopAccount": "LIPENG",
            "warehouseId": 129, "operateDivisionId": 5, "operaterId": 303,
            "operaterName": "李朋", "purchaserId": 303, "product_code": "A5-181",
            "salesPlanDate": "2026-08", "expectedShelfDate": "2027-02-20", "supplierId": 920,
            "companyId": 29
        }

    def run_link(self, **changes):
        return WaitContainerBillv2().create_waitContainer_supplier_v2_link(**(self.params | changes))

    def test_purchase_parameters_and_pool_values_reach_application(self):
        result = self.run_link()
        self.inspection.assert_called_once_with(
            self.params["cookies"], 161, "LIPENG", 129, 5, 303, "李朋", 303,
            "A5-181", "2026-08", "2027-02-20", 920, 29)
        payload = self.api.create_waitcontainerbillv2.call_args.args[1]
        item = payload["details"][0]
        self.assertEqual(item["waitApplyContainerId"], 101)
        self.assertEqual(item["purchaseOrderDetailId"], 501)
        self.assertEqual(item["waitContainerQuantity"], 120)
        self.assertEqual(item["oneBoxLoadQuantity"], 24)
        self.assertEqual(item["boxLength"], 50)
        self.assertEqual(item["portName"], "库存起运港")
        self.assertEqual(payload["warehouseName"], "库存返回的工厂仓")
        inventory_payload = self.inventory.page_supplierinventory.call_args.args[1]
        self.assertEqual(inventory_payload["purchaseOrderCodes"], ["PO-10"])
        self.assertEqual(inventory_payload["supplierInventoryWarehouse"], 3)
        self.assertEqual(item["productSticker"], "FNSKU-1")
        self.assertFalse(payload["isNeedFnSku"])
        self.assertEqual(item["packageSticker"], "SKU-1")
        self.assertEqual(item["sellerSku"], "")
        self.assertEqual(result["waitContainerBillId"], 1000)
        self.assertEqual(payload["targetWarehouseType"], 2)
        self.assertEqual(payload["transportationTypeId"], 18)
        self.assertEqual(payload["targetWarehouseSettingId"], 2)
        self.assertEqual(payload["inStorageType"], 11)
        self.assertEqual(payload["inStorageTypeName"], "Wayfair多渠道")
        self.assertNotIn("inStorageType", item)
        self.assertNotIn("inStorageTypeName", item)

    def test_pagination_preserves_same_sku_different_details_and_filters_other_orders(self):
        self.inventory.page_supplierinventory.return_value = response({
            "items": [inventory_item(), inventory_item(702, 502, attributeTag=2)], "hasNextPages": False})
        self.api.page_waitapplycontainer.side_effect = [
            response({"items": [pool_item(), pool_item(999, purchaseOrderId=99)], "hasNextPages": True}),
            response({"items": [pool_item(102, 502, attributeTag=2)], "hasNextPages": False})]
        result = self.run_link()
        self.assertEqual(result["waitApplyContainerIds"], [101, 102])
        payload = self.api.create_waitcontainerbillv2.call_args.args[1]
        self.assertEqual([item["waitContainerQuantity"] for item in payload["details"]], [120, 120])
        self.assertTrue(all("inStorageType" not in item for item in payload["details"]))
        self.api.waitcontainerbillv2_askapprove.assert_called_once_with(self.params["cookies"], 1000)




    def test_business_failure_does_not_submit_approval(self):
        self.api.create_waitcontainerbillv2.return_value = response(None, status=1000)
        with self.assertRaisesRegex(ValueError, "申请排柜失败"):
            self.run_link()
        self.api.waitcontainerbillv2_askapprove.assert_not_called()

    def test_quantity_uses_inventory_instead_of_pool_quantity(self):
        self.inventory.page_supplierinventory.return_value = response({
            "items": [inventory_item(inventoryAvailableQuantity=96.0)], "hasNextPages": False})
        self.run_link()
        payload = self.api.create_waitcontainerbillv2.call_args.args[1]
        self.assertEqual(payload["details"][0]["waitContainerQuantity"], 96)
        self.assertIs(type(payload["details"][0]["waitContainerQuantity"]), int)

    def test_inventory_pagination(self):
        self.inventory.page_supplierinventory.side_effect = [
            response({"items": [], "hasNextPages": True}),
            response({"items": [inventory_item()], "hasNextPages": False})]
        self.run_link()
        self.assertEqual(self.inventory.page_supplierinventory.call_count, 2)
        self.assertEqual(self.inventory.page_supplierinventory.call_args.args[1]["pageIndex"], 2)
        self.assertEqual(len(self.api.create_waitcontainerbillv2.call_args.args[1]["details"]), 1)





    def test_signature_matches_inspection_chain(self):
        actual = inspect.signature(WaitContainerBillv2.create_waitContainer_supplier_v2_link)
        expected = inspect.signature(Inspectionv2.inspection_purchaseorder_report)
        self.assertEqual(actual, expected)

    def test_creation_is_followed_by_approval_with_returned_bill_id(self):
        self.run_link()
        self.api.create_waitcontainerbillv2.assert_called_once()
        self.api.waitcontainerbillv2_askapprove.assert_called_once_with(self.params["cookies"], 1000)
        calls = [item[0] for item in self.api.method_calls]
        self.assertLess(calls.index("create_waitcontainerbillv2"), calls.index("waitcontainerbillv2_askapprove"))

    def test_approval_failure_is_reported(self):
        self.api.waitcontainerbillv2_askapprove.return_value = response(None, status=1002)
        with self.assertRaisesRegex(ValueError, "待排柜单 1000 送审失败"):
            self.run_link()

    def test_fba_uses_requested_shop_and_fnsku(self):
        self.inventory.page_supplierinventory.return_value = response({"items": [inventory_item(
            shopId=162, shopAccount="LIPENG_US")], "hasNextPages": False})
        self.api.page_waitapplycontainer.return_value = response({"items": [pool_item(
            shopId=162, shopAccount="LIPENG_US")], "hasNextPages": False})
        WaitContainerBillv2().create_waitContainer_supplier_fba_v2_link(
            **(self.params | {"shopId": 162, "shopAccount": "LIPENG_US"}))
        payload = self.api.create_waitcontainerbillv2.call_args.args[1]
        self.assertEqual(payload["targetWarehouseType"], 3)
        self.assertTrue(payload["isNeedFnSku"])
        self.assertIsNone(payload["inStorageType"])
        self.assertIsNone(payload["inStorageTypeName"])
        item = payload["details"][0]
        self.assertEqual(item["shopId"], 162)
        self.assertEqual(item["shopAccount"], "LIPENG_US")
        self.assertIsNone(item["packageSticker"])
        self.assertEqual(item["productSticker"], "FNSKU-1")
        self.assertEqual(item["sellerSku"], "SELLER-1")
        self.assertEqual(self.inspection.call_args.args[1:3], (162, "LIPENG_US"))
        self.assertEqual(self.product.sellersku_page.call_args.args[1]["shopIds"], [162])
        self.api.waitcontainerbillv2_askapprove.assert_called_once_with(self.params["cookies"], 1000)

    def test_four_inspections_finish_before_one_combined_creation(self):
        params = {key: value for key, value in self.params.items() if key != "cookies"}
        params_list = [params | {"product_code": f"PRODUCT-{index}"} for index in range(4)]
        self.inspection.side_effect = [{"purchaseorderid": index} for index in range(10, 14)]
        def build_payload(*args, **kwargs):
            self.assertEqual(self.inspection.call_count, 4)
            purchaseOrderId = kwargs["purchaseOrderId"]
            return ({"warehouseId": 129, "details": [{"purchaseOrderId": purchaseOrderId}]},
                    {"purchaseOrderId": purchaseOrderId})
        with patch.object(WaitContainerBillv2, "_build_waitContainer_supplier_payload", side_effect=build_payload) as build:
            result = WaitContainerBillv2().create_waitContainer_supplier_batch_v2_link(
                self.params["cookies"], params_list, targetWarehouseType=3)
        self.assertEqual(build.call_count, 4)
        for call in build.call_args_list:
            self.assertEqual(call.kwargs["targetWarehouseType"], 3)
        self.api.create_waitcontainerbillv2.assert_called_once()
        payload = self.api.create_waitcontainerbillv2.call_args.args[1]
        self.assertEqual([item["purchaseOrderId"] for item in payload["details"]], [10, 11, 12, 13])
        self.api.waitcontainerbillv2_askapprove.assert_called_once_with(self.params["cookies"], 1000)
        self.assertEqual(len(result["purchaseOrders"]), 4)

    def test_batch_inspection_failure_does_not_create_waitcontainerbill(self):
        params = {key: value for key, value in self.params.items() if key != "cookies"}
        self.inspection.side_effect = [{"purchaseorderid": 10}, ValueError("验货失败")]
        with self.assertRaisesRegex(ValueError, "验货失败"):
            WaitContainerBillv2().create_waitContainer_supplier_batch_v2_link(self.params["cookies"], [params] * 4)
        self.inventory.page_supplierinventory.assert_not_called()
        self.api.create_waitcontainerbillv2.assert_not_called()

    def test_rule_flag_does_not_block_submission_or_trigger_requery(self):
        self.api.page_waitapplycontainer.return_value = response({
            "items": [pool_item(isCanContainer=False, reason="服务端规则原因")], "hasNextPages": False})
        self.run_link()
        self.api.create_waitcontainerbillv2.assert_called_once()
        self.inventory.page_supplierinventory.assert_called_once()
        self.api.page_waitapplycontainer.assert_called_once()

    def test_pool_quantity_does_not_override_inventory_quantity(self):
        self.api.page_waitapplycontainer.return_value = response({
            "items": [pool_item(inventoryAvailableQuantity=1)], "hasNextPages": False})
        self.run_link()
        payload = self.api.create_waitcontainerbillv2.call_args.args[1]
        self.assertEqual(payload["details"][0]["waitContainerQuantity"], 120)
        self.api.page_waitapplycontainer.assert_called_once()

    def test_uses_inventory_fields_without_comparing_pool_metadata(self):
        self.api.page_waitapplycontainer.return_value = response({
            "items": [pool_item(purchaseOrderDetailId=999, attributeTag=2)], "hasNextPages": False})
        self.run_link()
        payload = self.api.create_waitcontainerbillv2.call_args.args[1]
        self.assertEqual(payload["details"][0]["purchaseOrderDetailId"], 501)
        self.assertEqual(payload["details"][0]["attributeTag"], 1)


class SupplierInventoryQueryTests(unittest.TestCase):
    def prepare_query(self, payload):
        with patch("interface.supplier.supplier_inventory_v2_api.requests.get", return_value=response()) as get:
            SupplierInventoryv2_Api().page_supplierinventory({}, payload)
        kwargs = get.call_args.kwargs
        request = requests.Request("GET", kwargs["url"], params=kwargs["params"]).prepare()
        return parse_qs(urlsplit(request.url).query)

    def test_purchase_codes_are_json_strings_in_actual_query(self):
        codes = ["PO-20261022-1", 'PO-中文 & "特殊值"']
        query = self.prepare_query({"purchaseOrderCodes": codes})
        self.assertEqual([json.loads(value) for value in query["purchaseOrderCodes"]], codes)
        self.assertEqual(query["purchaseOrderCodes"][0], '"PO-20261022-1"')

    def test_numeric_arrays_and_boolean_filters(self):
        query = self.prepare_query({"shopIds": [161, 162], "warehouseIds": [129],
                                    "isHideAvailableZero": True, "isContainSpu": False, "pageIndex": 2})
        self.assertEqual(query["shopIds"], ["161", "162"])
        self.assertEqual(query["warehouseIds"], ["129"])
        self.assertEqual(query["isHideAvailableZero"], ["true"])
        self.assertEqual(query["isContainSpu"], ["false"])
        self.assertEqual(query["pageIndex"], ["2"])

    def test_encoding_preserves_input_payload(self):
        payload = {"purchaseOrderCodes": ["PO-1"], "isContainSpu": True}
        self.prepare_query(payload)
        self.assertEqual(payload, {"purchaseOrderCodes": ["PO-1"], "isContainSpu": True})


if __name__ == "__main__":
    unittest.main()
