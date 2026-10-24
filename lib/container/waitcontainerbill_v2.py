# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File : waitcontainerbill_v2.py
# @Project : wecharmer
import json
from datetime import datetime

from interface.firstleg.waitcontainerbill_api import WaitContainerBill_Api
from interface.purchase.purchaseorder_api import PurchaseOrder_Api
from interface.supplier.supplier_inventory_v2_api import SupplierInventoryv2_Api
from lib.firstleg.stock_inspectionv2 import Inspectionv2
from lib.login import Login
from lib.productandmaterial.product import Product


class WaitContainerBillv2:
    @staticmethod
    def _get_result(resp, step):
        """检查 HTTP 和业务状态，再提取接口结果。"""
        resp.raise_for_status()
        result = json.loads(resp.text)
        if result.get("status", 200) != 200 or result.get("success") is False:
            raise ValueError(f"{step}失败：{resp.text}")
        return result.get("result")

    def create_waitContainer_supplier_v2_link(self, cookies, shopId, shopAccount, warehouseId,
                                              operateDivisionId, operaterId, operaterName, purchaserId,
                                              product_code, salesPlanDate, expectedShelfDate, supplierId, companyId):
        """创建供应商仓到海外仓的待排柜链路。"""
        return self._create_waitContainer_supplier_v2_link(
            cookies, shopId, shopAccount, warehouseId, operateDivisionId, operaterId, operaterName,
            purchaserId, product_code, salesPlanDate, expectedShelfDate, supplierId, companyId, 2)

    def create_waitContainer_supplier_fba_v2_link(self, cookies, shopId, shopAccount, warehouseId,
                                                 operateDivisionId, operaterId, operaterName, purchaserId,
                                                 product_code, salesPlanDate, expectedShelfDate, supplierId, companyId):
        """创建供应商仓到 FBA 平台仓的待排柜链路，使用 FNSKU。"""
        return self._create_waitContainer_supplier_v2_link(
            cookies, shopId, shopAccount, warehouseId, operateDivisionId, operaterId, operaterName,
            purchaserId, product_code, salesPlanDate, expectedShelfDate, supplierId, companyId, 3)

    def _create_waitContainer_supplier_v2_link(self, cookies, shopId, shopAccount, warehouseId,
                                               operateDivisionId, operaterId, operaterName, purchaserId,
                                               product_code, salesPlanDate, expectedShelfDate, supplierId, companyId,
                                               targetWarehouseType):
        inspection_data = Inspectionv2().inspection_purchaseorder_report(
            cookies, shopId, shopAccount, warehouseId, operateDivisionId, operaterId, operaterName,
            purchaserId, product_code, salesPlanDate, expectedShelfDate, supplierId, companyId)
        booking_payload, data = self._build_waitContainer_supplier_payload(
            cookies, shopId, shopAccount, warehouseId, operateDivisionId, operaterId, operaterName,
            purchaserId, product_code, salesPlanDate, expectedShelfDate, supplierId, companyId,
            targetWarehouseType, inspection_data["purchaseorderid"])
        data["waitContainerBillId"] = self._submit_waitcontainerbill(cookies, booking_payload)
        return data

    def create_waitContainer_supplier_batch_v2_link(self, cookies, params_list, targetWarehouseType=2):
        """
        多组采购/验货全部完成后，合并库存明细创建一张待排柜单并送审。
        :param params_list:验货入参字典列表，每组不包含 cookies
        :param targetWarehouseType:2 海外仓，3 FBA 平台仓
        :return:合并后的待排柜单 ID 和各组采购单数据
        主单仓库、日期等共用字段取第一组，明细保留各组返回的店铺、采购单等数据。
        """
        inspection_items = []
        for params in params_list:
            inspection_data = Inspectionv2().inspection_purchaseorder_report(cookies, **params)
            inspection_items.append((params, inspection_data["purchaseorderid"]))

        # 全部验货完成后再查询库存并组装，期间不重复创建采购数据
        payloads = []
        purchaseorders = []
        for params, purchaseOrderId in inspection_items:
            payload, data = self._build_waitContainer_supplier_payload(
                cookies, **params, targetWarehouseType=targetWarehouseType, purchaseOrderId=purchaseOrderId)
            payloads.append(payload)
            purchaseorders.append(data)
        booking_payload = payloads[0]
        booking_payload["details"] = [item for payload in payloads for item in payload["details"]]
        waitContainerBillId = self._submit_waitcontainerbill(cookies, booking_payload)
        return {"waitContainerBillId": waitContainerBillId, "purchaseOrders": purchaseorders}

    def _submit_waitcontainerbill(self, cookies, booking_payload):
        waitContainer_resp = WaitContainerBill_Api().create_waitcontainerbillv2(cookies, booking_payload)
        waitContainerBillId = self._get_result(waitContainer_resp, "申请排柜")
        approve_resp = WaitContainerBill_Api().waitcontainerbillv2_askapprove(cookies, waitContainerBillId)
        self._get_result(approve_resp, f"待排柜单 {waitContainerBillId} 送审")
        return waitContainerBillId

    def _build_waitContainer_supplier_payload(self, cookies, shopId, shopAccount, warehouseId,
                                               operateDivisionId, operaterId, operaterName, purchaserId,
                                               product_code, salesPlanDate, expectedShelfDate, supplierId, companyId,
                                               targetWarehouseType, purchaseOrderId):
        """使用已有采购单查询库存并组装排柜参数，不创建或提交单据。"""
        expectedWarehouseDate = datetime.fromisoformat(expectedShelfDate).isoformat()

        # 从新采购单查询单号，限定本次申请的数据范围
        purchaseorder_resp = PurchaseOrder_Api().get_purchaseorderv1_details(cookies, purchaseOrderId)
        purchaseorder_result = self._get_result(purchaseorder_resp, "获取采购单明细")
        purchaseorder_items = purchaseorder_result["skuDetailDimensionDetails"]
        purchaseOrderCode = purchaseorder_items[0]["purchaseOrderCode"]

        # 按采购单号分页查询库存，查询结束直接使用返回的数据
        inventory_items = []
        pageIndex = 1
        while True:
            supplierinventory_payload = {
                "purchaseOrderCodes": [purchaseOrderCode],
                "supplierInventoryWarehouse": 3,
                "shopIds": [shopId],
                "operateDivisionIds": [operateDivisionId],
                "supplierIds": [supplierId],
                "warehouseIds": [warehouseId],
                "isContainSpu": True,
                "isHideAvailableZero": True,
                "pageIndex": pageIndex,
                "pageSize": 100
            }
            supplierinventory_resp = SupplierInventoryv2_Api().page_supplierinventory(cookies, supplierinventory_payload)
            supplierinventory_result = self._get_result(supplierinventory_resp, "按采购单号查询库存")
            inventory_page_items = supplierinventory_result["items"]
            inventory_items.extend(inventory_page_items)
            if not supplierinventory_result.get("hasNextPages", len(inventory_page_items) == 100):
                break
            pageIndex += 1

        # 关联申请池 ID，不检查可排柜状态和数量，不等待重查
        items = []
        pageIndex = 1
        while True:
            waitapplycontainer_payload = {
                "purchaseOrderCodes": [purchaseOrderCode],
                "productCode": product_code,
                "shopAccounts": [shopAccount],
                "operateDivisionIds": [operateDivisionId],
                "isShowSelf": False,
                "pageIndex": pageIndex,
                "pageSize": 100,
                "sorts": [{"field": "id", "order": "asc"}]
            }
            waitapplycontainer_resp = WaitContainerBill_Api().page_waitapplycontainer(cookies, waitapplycontainer_payload)
            waitapplycontainer_result = self._get_result(waitapplycontainer_resp, "查询待申请排柜池")
            page_items = waitapplycontainer_result["items"]
            items.extend(page_items)
            if not waitapplycontainer_result.get("hasNextPages", len(page_items) == 100):
                break
            pageIndex += 1
        pool_by_inventory_id = {item["supplierInventoryId"]: item for item in items}

        # 仓库名称、排柜数量、箱规和采购明细使用按采购单号查到的库存数据
        warehouseName = inventory_items[0]["warehouseName"]
        details = []
        # 固定请求参数，明细在下面组装
        booking_payload = {
            "targetWarehouseType": targetWarehouseType,
            "transportationTypeId": 18,
            "transportationTypeName": "第三方普船整柜",
            "inStorageType": None,
            "inStorageTypeName": None,
            "expectedWarehouseDate": expectedWarehouseDate,
            "isNeedFnSku": targetWarehouseType == 3,
            "isCombinationProduct": False, "remark": "",
            "targetWarehouseSettingId": 2,
            "targetWarehouseSettingName": "美西",
            "warehouseId": warehouseId, "warehouseName": warehouseName, "details": details
        }
        if targetWarehouseType == 2:
            booking_payload["inStorageType"] = 11
            booking_payload["inStorageTypeName"] = "Wayfair多渠道"
        for stock in inventory_items:
            item = pool_by_inventory_id[stock["id"]]
            boxGauge = stock["boxGauge"]
            waitContainerQuantity = int(stock["inventoryAvailableQuantity"])
            shippingPort = stock["shippingPorts"][0]

            # 按店铺、事业部和 SKU 查询产品贴
            sellersku_payload = {
                "shopIds": [shopId], "skuCodes": [item["skuCode"]],
                "operateDivisionId": operateDivisionId, "isMatch": True, "isEmptyFnSku": False,
                "pageIndex": 1, "pageSize": 100
            }
            sellersku_resp = Product().sellersku_page(cookies, sellersku_payload)
            sellersku_result = self._get_result(sellersku_resp, "查询产品对外关系")
            sellersku_result = sellersku_result["items"][0]

            items_dict = {
                "waitApplyContainerId": item["id"],
                "waitContainerQuantity": waitContainerQuantity,
                "overseasWarehouseListingMethod": 1,
                "shopId": stock["shopId"], "shopAccount": stock["shopAccount"],
                "operateDivisionId": stock["operateDivisionId"],
                "operateDivisionName": stock["operateDivisionName"],
                "operaterId": stock["operaterId"], "operaterName": stock["operaterName"],
                "supplierId": stock["supplierId"],
                "portId": shippingPort["portId"], "portName": shippingPort["portName"],
                "oneBoxLoadQuantity": int(boxGauge["ctnQuantity"]),
                "boxLength": boxGauge["ctnLongX"], "boxWidth": boxGauge["ctnLongY"], "boxHeight": boxGauge["ctnLongZ"],
                "ctnVolume": boxGauge["ctnVolume"], "ctnGrossWeight": boxGauge["ctnGrossWeight"],
                "ctnNetWeight": boxGauge["ctnNetWeight"],
                "applyPurchaseBillId": stock["applyPurchaseBillId"],
                "applyPurchaseBillCode": stock["applyPurchaseBillCode"],
                "purchaseOrderId": stock["purchaseOrderId"], "purchaseOrderCode": stock["purchaseOrderCode"],
                "purchaseOrderDetailId": stock["purchaseOrderDetailId"],
                "attributeTag": stock["attributeTag"],
                "productId": stock["productId"], "productCode": stock["spuCode"],
                "skuId": stock["skuId"], "skuCode": stock["skuCode"], "skuName": stock["skuName"],
                "packageSticker": None if targetWarehouseType == 3 else stock["skuCode"],
                "productSticker": sellersku_result.get("fnSku") or "",
                "sellerSku": (sellersku_result.get("code") or "") if booking_payload["isNeedFnSku"] else "",
                "countryTwoCharCode": item["countryTwoCharCode"], "salesPlanDate": item["salesPlanDate"],
                "expectedWarehouseDate": item["expectedPutOnSaleTime"],
                "inventoryAvailableQuantity": stock["inventoryAvailableQuantity"],
                "appliedQuantity": item["appliedQuantity"]
            }
            details.append(items_dict)

        return booking_payload, {"purchaseOrderId": purchaseOrderId, "purchaseOrderCode": purchaseOrderCode,
                                 "waitApplyContainerIds": [item["waitApplyContainerId"] for item in details]}


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    # 与验货链路使用同一组入参，排柜固定值直接写在 booking_payload 中。
    # waitcontainer_data = WaitContainerBillv2().create_waitContainer_supplier_v2_link(
    #     cookies, shopId=161, shopAccount="LIPENG", warehouseId=129,
    #     operateDivisionId=5, operaterId=303, operaterName="李朋", purchaserId=303,
    #     product_code="A5-181", salesPlanDate="2026-08", expectedShelfDate="2027-02-20",
    #     supplierId=920, companyId=29)
    # print(waitcontainer_data)

    # FBA 平台仓：需要时改用这个入口，避免一次运行同时创建两套采购链路。
    # waitcontainer_data = WaitContainerBillv2().create_waitContainer_supplier_fba_v2_link(
    #     cookies, shopId=162, shopAccount="LIPENG_US", warehouseId=129,
    #     operateDivisionId=5, operaterId=303, operaterName="李朋", purchaserId=303,
    #     product_code="A5-181", salesPlanDate="2026-08", expectedShelfDate="2027-02-20",
    #     supplierId=920, companyId=29)
    # print(waitcontainer_data)

    # 四组共用的参数
    base_params = {
        "shopId": 161,
        "shopAccount": "LIPENG",
        "warehouseId": 129,
        "operateDivisionId": 5,
        "operaterId": 303,
        "operaterName": "李朋",
        "purchaserId": 303,
        "product_code": "B101-003",
        "salesPlanDate": "2026-08",
        "expectedShelfDate": "2027-02-20"
    }

    # 四组仅供应商和公司主体不同，第三、四组自行填写。
    params_list = [
        {**base_params, "supplierId": 920, "companyId": 29},
        {**base_params, "supplierId": 6, "companyId": 2},
        {**base_params, "supplierId": 112, "companyId": 29},
        {**base_params, "supplierId": 113, "companyId": 30}
    ]


    waitcontainer_data = WaitContainerBillv2().create_waitContainer_supplier_batch_v2_link(
        cookies,
        params_list
    )
    print(waitcontainer_data)
