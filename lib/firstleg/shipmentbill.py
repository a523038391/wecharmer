# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/7/3 下午3:13
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : shipmentbill.py
# @Project : wecharmer
import json
from wsgiref import headers

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from datetime import datetime, timedelta

from lib.storage.stock import Stock


class ShipmentBill:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")

    def query_fbashipmentinfo_page(self, url, cookies):
        """
        查询货件列表
        :return:
        """

        resp = requests.get(url=url, headers=cookies)
        print("查询货件列表resp-----------\n" + resp.text)
        return resp

    def get_fbashipmentinfo_details(self, url, cookies):
        """
        查询货件明细
        :return:
        """
        resp = requests.get(url=url, headers=cookies)
        print("查询货件明细resp-----------\n" + resp.text)
        return resp

    def get_item_stock(self, cookies, shipmentbillid):
        """
        查询发货单商品信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/{shipmentbillid}/item-stock"
        resp = requests.get(url=url, headers=cookies)
        print("查询发货单商品信息resp-----------\n" + resp.text)
        return resp


    def fnsku_sku_shipmentbill(self, cookies,id, payload):
        """
        根据FnSku和Sku获取货件明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/fbashipmentinfo/{id}/details/fnsku-sku"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("根据FnSku和Sku获取货件明细resp-----------\n" + resp.text)
        return resp

    def create_fab_shipmentbill(self, cookies, payload):
        """
        创建fab发货单
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/fba"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建发货单resp-----------\n" + resp.text)
        return resp

    def create_fab_shipmentbill_item(self, shipmentbillid, cookies, payload):
        """
        创建fab发货单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/{shipmentbillid}/fba/item"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建fab发货单明细resp-----------\n" + resp.text)
        return resp

    def shipmentbill_allocate(self, cookies, payload):
        """
        分配库存按件
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/allocate"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("分配库存按件resp-----------\n" + resp.text)
        return resp

    def shipmentbill_allocate_box(self, cookies, payload):
        """
        分配库存按箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/allocate/box"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("分配库存按箱resp-----------\n" + resp.text)
        return resp

    def shipmentbill_related_fba(self, cookies, payload, shipmentbillid):
        """
        关联货件
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/{shipmentbillid}/related-fba"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("关联货件resp-----------\n" + resp.text)
        return resp

    def fba_shipmentbill_link_v1(self,cookies, warehouseId, targetWarehouseId, operateDivisionId,
                                  shopId, purchaserId, product_code,  fbaShipmentCode):
        """
        创建发货单按件链路
        :param sendOutGoodsType:仓库中转类型
        :param warehouseId:发货仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param shipmentBillStatus:发货单状态
        :param shipmentType:按箱 按件
        :return:
        """

        # 创建采购单按件上架
        Stock().purchase_order_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId, product_code)

        # 根据货件号查询货件列表
        fbashipmentinfo_url = f"{waveecharmer_Host}/api/fbashipmentinfo/page?shipmentStatus=1,2,3,6,7,8,9,10,11&isEmptyReferenceId=false&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&fbaShipmentCode={fbaShipmentCode}&pageIndex=1&pageSize=10"
        fbashipmentinfo_resp = ShipmentBill().query_fbashipmentinfo_page(fbashipmentinfo_url, cookies)
        sourceShipmentInfoId = json.loads(fbashipmentinfo_resp.text)["result"]["items"][0]["id"]

        # 创建发货单
        shipmentbill_payload = {
            "remark": "",
            "shipmentBillCode": None,
            "sendOutGoodsType": 1,
            "expectedDeliveryTime": self.formatted_date,
            "sourceShipmentInfoId": sourceShipmentInfoId,
            "warehouseId": warehouseId,
            "shipmentBillStatus": 11,
            "targetWarehouseId": targetWarehouseId,
            "shopId": shopId,
            "shippingAddress": "1111111111111111",
            "attachments": [],
            "productShipmentType": None,
            "sourceShipmentInfoCode": None,
            "operateDivisionId": operateDivisionId,
            "shipmentType": 0,
            "operaterId": purchaserId
        }
        print(shipmentbill_payload)
        shipmentbill_resp = ShipmentBill().create_fab_shipmentbill(cookies, shipmentbill_payload)
        shipmentbillid = json.loads(shipmentbill_resp.text)["result"]["id"]
        shipmentBillCode = json.loads(shipmentbill_resp.text)["result"]["shipmentBillCode"]

        # 查询货件明细
        fbashipmentinfo_details_url = f"{waveecharmer_Host}/api/fbashipmentinfo/{sourceShipmentInfoId}/details/page?operateDivisionIds={operateDivisionId}&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=10"
        fbashipmentinfo_item_resp = ShipmentBill().get_fbashipmentinfo_details(fbashipmentinfo_details_url, cookies)
        bashipmentinfo_item_result= json.loads(fbashipmentinfo_item_resp.text)["result"]["items"]
        items=[]

        for item in bashipmentinfo_item_result:
            # 查询库存信息
            get_batchstocks_url = f"{waveecharmer_Host}/api/stock/batchstocks/groupByShop-OperateDivision-StockType?goodOrDefectives=1&skuIds={item['skuId']}&shopIds={shopId}&warehouseIds={warehouseId}&operateDivisionIds={operateDivisionId}&stockTypes=1&pageSize=10000"
            get_batchstocks_rest=Stock().get_batchstocks(get_batchstocks_url, cookies)
            get_batchstocks_result=json.loads(get_batchstocks_rest.text)["result"][0]
            items_dict={
                    "sellerSku": item["sellerSku"],
                    "fnSku": item["fnSku"],
                    "skuId": item["skuId"],
                    "plannedShipmentQuantity": get_batchstocks_result["availableStockQuantity"]
                }
            items.append(items_dict)


        # 创建fab发货单明细

        shipmentbill_item_payload = {
            "items": items,
            "thirdPartyWarehouseReferences": [],
            "boxes": []
        }
        ShipmentBill().create_fab_shipmentbill_item(shipmentbillid, cookies, shipmentbill_item_payload)

        # 查询发货单商品信息
        shipmentbill_detailbysku_resp = ShipmentBill().get_item_stock(cookies, shipmentbillid)
        shipmentbill_detailbysku_result = json.loads(shipmentbill_detailbysku_resp.text)["result"]

        items=[]

        for item in shipmentbill_detailbysku_result:
            items_dict={
                    "id": item["id"],
                    "skuId": item["skuId"],
                    "plannedShipmentQuantity": item["plannedShipmentQuantity"],
                    "warehouseLocationIds": []
                }

            items.append(items_dict)

        # 分配库存
        shipmentbill_allocate_payload = {
            "id": shipmentbillid,
            "items": items
        }
        ShipmentBill().shipmentbill_allocate(cookies, shipmentbill_allocate_payload)

        shipmentbilldata = { "shipmentbillid": int(shipmentbillid),
                            "shipmentBillCode": shipmentBillCode}

        return shipmentbilldata




    def fba_shipmentbill_link(self, cookies, fbaShipmentCode, warehouseId, targetWarehouseId, operateDivisionId, shopId,
                              skucode, skuIds):
        """
        创建发货单按件链路
        :param sendOutGoodsType:仓库中转类型
        :param warehouseId:发货仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param shipmentBillStatus:发货单状态
        :param shipmentType:按箱 按件
        :return:
        """
        try:
            # 根据货件号查询货件列表
            fbashipmentinfo_url = f"{waveecharmer_Host}/api/fbashipmentinfo/page?shipmentStatus=1,2,3,6,7,8,9,10,11&isEmptyReferenceId=false&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&fbaShipmentCode={fbaShipmentCode}&pageIndex=1&pageSize=10"
            fbashipmentinfo_resp = ShipmentBill().query_fbashipmentinfo_page(fbashipmentinfo_url, cookies)
            sourceShipmentInfoId = json.loads(fbashipmentinfo_resp.text)["result"]["items"][0]["id"]

            # 创建发货单
            shipmentbill_payload = {
                "remark": "",
                "shipmentBillCode": None,
                "sendOutGoodsType": 1,
                "expectedDeliveryTime": self.formatted_date,
                "sourceShipmentInfoId": sourceShipmentInfoId,
                "warehouseId": warehouseId,
                "shipmentBillStatus": 11,
                "targetWarehouseId": targetWarehouseId,
                "shopId": shopId,
                "shippingAddress": "1111111111111111",
                "attachments": [],
                "productShipmentType": None,
                "sourceShipmentInfoCode": None,
                "operateDivisionId": operateDivisionId,
                "shipmentType": 0
            }
            print(shipmentbill_payload)
            shipmentbill_resp = ShipmentBill().create_fab_shipmentbill(cookies, shipmentbill_payload)
            shipmentbillid = json.loads(shipmentbill_resp.text)["result"]["id"]
            shipmentBillCode = json.loads(shipmentbill_resp.text)["result"]["shipmentBillCode"]

            # 查询货件明细
            fbashipmentinfo_details_url = f"{waveecharmer_Host}/api/fbashipmentinfo/{sourceShipmentInfoId}/details/page?operateDivisionIds=2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&skuCodes=%22{skucode}%22&pageIndex=1&pageSize=10"
            fbashipmentinfo_item_resp = ShipmentBill().get_fbashipmentinfo_details(fbashipmentinfo_details_url, cookies)
            fnSku = json.loads(fbashipmentinfo_item_resp.text)["result"]["items"][0]["fnSku"]
            sellerSku = json.loads(fbashipmentinfo_item_resp.text)["result"]["items"][0]["sellerSku"]
            # 查询库存信息
            get_batchstocks_url = f"{waveecharmer_Host}/api/stock/batchstocks/groupByShop-OperateDivision-StockType?goodOrDefectives=1&skuIds={skuIds}&shopIds={shopId}&warehouseIds={warehouseId}&operateDivisionIds=2&stockTypes=1&pageSize=10000"
            Stock().get_batchstocks(get_batchstocks_url, cookies)

            # 创建fab发货单明细

            shipmentbill_item_payload = {
                "items": [
                    {
                        "sellerSku": sellerSku,
                        "fnSku": fnSku,
                        "skuId": skuIds,
                        "plannedShipmentQuantity": 10
                    }
                ],
                "thirdPartyWarehouseReferences": [],
                "boxes": []
            }
            ShipmentBill().create_fab_shipmentbill_item(shipmentbillid, cookies, shipmentbill_item_payload)

            # 查询发货单商品信息
            shipmentbill_detailbysku_resp = ShipmentBill().get_item_stock(cookies, shipmentbillid)
            shipmentbill_detailbysku_result = json.loads(shipmentbill_detailbysku_resp.text)["result"]
            # 分配库存
            shipmentbill_allocate_payload = {
                "id": shipmentbillid,
                "items": [
                    {
                        "id": shipmentbill_detailbysku_result[0]["id"],
                        "skuId": shipmentbill_detailbysku_result[0]["skuId"],
                        "plannedShipmentQuantity": shipmentbill_detailbysku_result[0]["plannedShipmentQuantity"],
                        "warehouseLocationIds": []
                    }
                ]
            }
            ShipmentBill().shipmentbill_allocate(cookies, shipmentbill_allocate_payload)

        except Exception as e:
            print("创建发货单出错", e)
            shipmentbillid = None
            shipmentBillCode = None

        shipmentbilldata = {"skucode": skucode, "shipmentbillid": int(shipmentbillid),
                            "shipmentBillCode": shipmentBillCode}

        return shipmentbilldata

    def fba_shipmentbill_box_link(self, cookies, warehouseId, targetWarehouseId, operateDivisionId,
                                  shopId, purchaserId, product_code, quantity, fbaShipmentCode):
        """
        创建发货单按箱链路
        :param sendOutGoodsType:仓库中转类型
        :param warehouseId:发货仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param shipmentBillStatus:发货单状态
        :param shipmentType:按箱 按件
        :return:
        """
        # 创建采购单按箱上架
        Stock().purchase_order_box_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId, product_code)
        # 创建发货单
        shipmentbill_payload = {
            "remark": "备注一下",
            "shipmentBillCode": None,
            "sendOutGoodsType": 1,
            "expectedDeliveryTime": self.formatted_date,
            "sourceShipmentInfoId": None,
            "warehouseId": warehouseId,
            "shipmentBillStatus": None,
            "targetWarehouseId": targetWarehouseId,
            "shopId": shopId,
            "shippingAddress": "1111111111111111",
            "attachments": [
                {
                    "uid": "vc-upload-1727329678329-5",
                    "lastModified": 1725433747681,
                    "lastModifiedDate": "2024-09-04T07:09:07.681Z",
                    "name": "IMG_1092.JPG",
                    "size": 198249,
                    "type": "image/jpeg",
                    "percent": 0,
                    "originFileObj": {
                        "uid": "vc-upload-1727329678329-5"
                    },
                    "status": "done",
                    "suffix": "JPG",
                    "url": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1727335762087_6f18266b_24092600157.JPG",
                    "attachmentName": "IMG_1092.JPG",
                    "attachmentUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1727335762087_6f18266b_24092600157.JPG"
                }
            ],
            "productShipmentType": None,
            "sourceShipmentInfoCode": None,
            "operateDivisionId": operateDivisionId,
            "shipmentType": 1,
            "operaterId": purchaserId
        }

        shipmentbill_resp = ShipmentBill().create_fab_shipmentbill(cookies, shipmentbill_payload)
        shipmentbillid = json.loads(shipmentbill_resp.text)["result"]["id"]
        shipmentBillCode = json.loads(shipmentbill_resp.text)["result"]["shipmentBillCode"]

        # 获取装箱库存明细平铺箱贴聚合数据分页

        packingstock_spread_page_resp = Stock().get_packingstock_spread_page(cookies, shopId, operateDivisionId,warehouseId,
                                                                             product_code)
        packingstock_spread_page_result = json.loads(packingstock_spread_page_resp.text)["result"]
        items = []
        boxes = []
        skuid = []
        allocate_items = []
        count = 1

        for item in packingstock_spread_page_result["items"]:
            if int(item["boxStickerNo"][-1]) <= int(item["availableStockQuantity"]) and item["skuId"] not in skuid:
                items_dict = {
                    "sellerSku": item["sellerSkuCode"],
                    "fnSku": item["fnSku"],
                    "skuId": item["skuId"],
                    "plannedShipmentQuantity": quantity * int(item["boxStickerNo"][-1])
                }
                boxes_dict = {
                    "boxStickerNo": item["boxStickerNo"],
                    "quantity": quantity
                }

                allocate_dict = {
                    "id": item["id"],
                    "boxStickerNo": item["boxStickerNo"],
                    "skuId": item["skuId"],
                    "plannedShipmentQuantity": quantity * int(item["boxStickerNo"][-1]),
                    "warehouseLocationIds": []
                }
                skuid.append(item["skuId"])
                items.append(items_dict)
                boxes.append(boxes_dict)
                allocate_items.append(allocate_dict)
                count += 1
                if count == 5:
                    break
            else:
                continue
        print(items)

        # 创建fab发货单明细

        shipmentbill_item_payload = {
            "items": items,
            "thirdPartyWarehouseReferences": [],
            "boxes": boxes
        }
        ShipmentBill().create_fab_shipmentbill_item(shipmentbillid, cookies, shipmentbill_item_payload)

        # 分配库存
        shipmentbill_allocate_payload = {
            "id": shipmentbillid,
            "items": allocate_items
        }
        ShipmentBill().shipmentbill_allocate_box(cookies, shipmentbill_allocate_payload)

        # 根据货件号查询货件列表
        fbashipmentinfo_url = f"{waveecharmer_Host}/api/fbashipmentinfo/page?shipmentStatus=1,2,3,6,7,8,9,10,11&isEmptyReferenceId=false&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&fbaShipmentCode={fbaShipmentCode}&pageIndex=1&pageSize=10"
        fbashipmentinfo_resp = ShipmentBill().query_fbashipmentinfo_page(fbashipmentinfo_url, cookies)
        sourceShipmentInfoId = json.loads(fbashipmentinfo_resp.text)["result"]["items"][0]["id"]

        # 关联货件
        related_fba__payload = {
            "isCheckQuantity": True,
            "fbaShipmentInfoId": sourceShipmentInfoId
        }
        ShipmentBill().shipmentbill_related_fba(cookies, related_fba__payload,shipmentbillid)

        shipmentbilldata = {"shipmentbillid": int(shipmentbillid),
                            "shipmentBillCode": shipmentBillCode}
        return shipmentbilldata


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # ShipmentBill().fba_shipmentbill_link(cookies, "FBA16K8TWW9P", 150, 135, 2, 122, "B-XF2-00A-D-9-0125-QGR-XS", 1002)

    #发货单-按箱
    ShipmentBill().fba_shipmentbill_box_link(cookies, 150, 135, 5, 162, 303,
                                            "A5-181", 3, "FBA16M9J26TK")

    #发货单-按件
    #ShipmentBill().fba_shipmentbill_link_v1(cookies, 150, 189, 5, 162, 303,
    #                                         "A5-181",  "FBA16M9J26TK")

