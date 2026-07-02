# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/12 下午1:56
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stockupbill.py
# @Project : wecharmer
import json

import requests

from conf.baseconfig import waveecharmer_Host
from datetime import datetime, timedelta

from lib.login import Login
from lib.productandmaterial.product import Product
from lib.storage.stock import Stock
from util import httpUtil


class StockupBill:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        # 如果你只需要年月日，不需要时间部分，可以将其格式化为字符串
        self.formatted_date = new_date.strftime('%Y-%m-%d')

    def query_stockupbill(self, url, cookies):
        """
        查询备货单
        :return:
        """
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("查询备货单resp-----------\n" + resp.text)
        return resp

    def create_stockupbill_v1(self, cookies, payload):
        """
        创建备货单
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建备货单resp-----------\n" + resp.text)
        return resp

    def create_stockupbill_detail_v1(self, cookies, payload):
        """
        创建备货单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建备货单明细resp-----------\n" + resp.text)
        return resp

    def create_stockupbill(self, cookies, shopId, warehouseId, targetWarehouseId, operateDivisionId, platformEnName):
        """
        创建备货单主表信息
        :param shopId:商品id
        :param warehouseId:出发仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部id
        :param platformEnName:平台名称
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/create"
        payload = {
            "stockUpBillCode": "",
            "sendOutGoodsType": 1,
            "shopId": shopId,
            "isFNSKU": False,
            "warehouseId": warehouseId,
            "targetWarehouseId": targetWarehouseId,
            "expectedDeliveryTime": self.formatted_date,
            "platformName": "抖音",
            "shippingAddress": "2311 York Rd",
            "attachmentDetail": [],
            "remark": "",
            "operateDivisionId": operateDivisionId,
            "platformEnName": platformEnName
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("创建备货单主表信息resp-----------\n" + resp.text)
        return resp

    def create_stockupbill_detail(self, cookies, stockUpBillId, skuId, skuImageUrl, thirdImageUrl, useImageSource,
                                  skuCode, skuName, sellerSkuCode):
        """
        创建备货单SKU详细信息
        :param skuId:商品id
        :param skuImageUrl:图片
        :param thirdImageUrl:三方图片
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/create"
        payload = {
            "stockUpBillId": stockUpBillId,
            "stockUpBillDetail": [
                {
                    "skuId": skuId,
                    "plannedShipmentQuantity": 10,
                    "skuImageUrl": skuImageUrl,
                    "thirdImageUrl": thirdImageUrl,
                    "useImageSource": useImageSource,
                    "skuCode": skuCode,
                    "oldSkuCode": "",
                    "skuName": skuName,
                    "sellerSkuCode": sellerSkuCode
                }
            ]
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("创建备货单SKU详细信息resp-----------\n" + resp.text)
        return resp

    def update_share_stockupbill_v1(self, cookies, payload):
        """
        备货单分配库存按件
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/share/update"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("备货单分配库存按件resp-----------\n" + resp.text)
        return resp

    def update_share_stockupbill_box(self, cookies, payload):
        """
        分配库存按箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/box/share/update"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("分配库存按箱resp-----------\n" + resp.text)
        return resp

    def update_share_stockupbill(self, cookies, stockUpBillId, id, skuId, plannedShipmentQuantity):
        """
        备货单分配库存按件
        :param stockUpBillId:备货单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/share/update"
        print(url)
        payload = {
            "id": stockUpBillId,
            "items": [
                {
                    "id": id,
                    "skuId": skuId,
                    "plannedShipmentQuantity": plannedShipmentQuantity,
                    "warehouseLocationIds": []
                }
            ]
        }
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("备货单分配库存按件resp-----------\n" + resp.text)
        return resp

    def get_stockupbill_detail(self, cookies, stockUpBillId):
        """
        通过备货单id获取详情信息
        :param stockUpBillId:备货单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/{stockUpBillId}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("通过备货单id获取详情信息resp-----------\n" + resp.text)
        return resp

    def get_stockupbill_detailbysku(self, cookies, stockUpBillId):
        """
        通过备货单id获取商品详情信息
        :param stockUpBillId:备货单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detailbysku/{stockUpBillId}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("通过备货单id获取商品详情信息resp-----------\n" + resp.text)
        return resp

    def create_stockupbill_link(self, cookies, skucode, shopId, warehouseId, targetWarehouseId, operateDivisionId,
                                platformEnName):
        try:
            # 获取商品信息
            item_resp = Product().query_skulist(cookies, skucode)
            skuId = json.loads(item_resp.text)["result"]["items"][0]["id"]
            skuImageUrl = json.loads(item_resp.text)["result"]["items"][0]["imageUrl"]
            thirdImageUrl = json.loads(item_resp.text)["result"]["items"][0]["thirdImageUrl"]
            useImageSource = json.loads(item_resp.text)["result"]["items"][0]["useImageSource"]
            skuCode = json.loads(item_resp.text)["result"]["items"][0]["code"]
            skuName = json.loads(item_resp.text)["result"]["items"][0]["cnName"]
            sellerSkuCode = json.loads(item_resp.text)["result"]["items"][0]["code"]

            # 创建备货单主表信息
            stockupbill_resp = StockupBill().create_stockupbill(cookies, shopId, warehouseId, targetWarehouseId,
                                                                operateDivisionId, platformEnName)
            stockUpBillId = json.loads(stockupbill_resp.text)["result"]
            # 创建备货单SKU详细信息
            StockupBill().create_stockupbill_detail(cookies, stockUpBillId, skuId, skuImageUrl, thirdImageUrl,
                                                    useImageSource, skuCode, skuName, sellerSkuCode)

            # 通过备货单id获取商品详情信息
            stockupbill_detailbysku_resp = StockupBill().get_stockupbill_detailbysku(cookies, stockUpBillId)
            stockupbill_detailbysku_result = json.loads(stockupbill_detailbysku_resp.text)["result"]

            # 备货单分配库存按件
            StockupBill().update_share_stockupbill(cookies, stockUpBillId, stockupbill_detailbysku_result[0]["id"],
                                                   stockupbill_detailbysku_result[0]["skuId"],
                                                   stockupbill_detailbysku_result[0]["plannedShipmentQuantity"])

            # 通过备货单id获取详情信息
            stockupbill_detail_resp = StockupBill().get_stockupbill_detail(cookies, stockUpBillId)
            sourceCode = json.loads(stockupbill_detail_resp.text)["result"]["stockUpBillCode"]
            print(sourceCode)

        except Exception as e:
            print("创建备货单出错", e)
            stockUpBillId = None
            sourceCode = None

        stockupbilldata = {"skucode": skucode, "stockUpBillId": int(stockUpBillId), "sourceCode": sourceCode}
        print(stockupbilldata)
        return stockupbilldata

    def create_stockupbill_box_link(self, cookies, shopId, warehouseId, targetWarehouseId, operateDivisionId,
                                    purchaserId, product_code, quantity):
        """
        创建备货单链路-按箱
        :param shopId:商品id
        :param warehouseId:出发仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部id
        :param platformEnName:平台名称
        :param shipmentType:0 按件 1按箱
        :return:
        """

        # 创建采购单按箱上架
        Stock().purchase_order_box_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId, product_code)

        # 创建备货单
        stockupbill_payload = {
            "stockUpBillCode": "",
            "sendOutGoodsType": 1,
            "shopId": shopId,
            "isFNSKU": False,
            "warehouseId": warehouseId,
            "targetWarehouseId": targetWarehouseId,
            "expectedDeliveryTime": self.formatted_date,
            "platformName": "抖音",
            "shippingAddress": "617 E Sunkist St",
            "attachmentDetail": [],
            "remark": "",
            "operateDivisionId": operateDivisionId,
            "shipmentType": 1,
            "stockUpType": 1,
            "operaterId": purchaserId,
            "platformEnName": "Tiktok"
        }

        stockupbill_resp = StockupBill().create_stockupbill_v1(cookies, stockupbill_payload)
        stockUpBillId = json.loads(stockupbill_resp.text)["result"]

        # 获取装箱库存明细平铺箱贴聚合数据分页

        packingstock_spread_page_resp = Stock().get_packingstock_spread_page(cookies, shopId, operateDivisionId,warehouseId,
                                                                             product_code)
        packingstock_spread_page_result = json.loads(packingstock_spread_page_resp.text)["result"]
        stockUpBillDetail = []
        boxes = []
        skuid = []
        allocate_items = []
        count = 1

        for item in packingstock_spread_page_result["items"]:
            if int(item["boxStickerNo"][-1]) <= int(item["availableStockQuantity"]) and item["skuId"] not in skuid:
                stockUpBillDetail_dict = {
                    "skuId": item["skuId"],
                    "plannedShipmentQuantity": quantity * int(item["boxStickerNo"][-1]),
                    "skuImageUrl": item["skuImageUrl"],
                    "thirdImageUrl": item["thirdImageUrl"],
                    "useImageSource": item["useImageSource"],
                    "skuCode": item["skuCode"],
                    "oldSkuCode": item["oldSkuCode"],
                    "asinCode": None,
                    "fnSku": None,
                    "lisitingTitle": None
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
                stockUpBillDetail.append(stockUpBillDetail_dict)
                boxes.append(boxes_dict)
                allocate_items.append(allocate_dict)
                count += 1
                if count == 5:
                    break
            else:
                continue
        print(stockUpBillDetail)

        # 创建备货单明细
        stockupbill_detail_payload = {
            "stockUpBillId": stockUpBillId,
            "stockUpBillDetail": stockUpBillDetail,
            "boxes": boxes
        }
        StockupBill().create_stockupbill_detail_v1(cookies, stockupbill_detail_payload)

        # 分配库存

        stockupbill_allocate_payload = {
            "id": stockUpBillId,
            "items": allocate_items
        }
        StockupBill().update_share_stockupbill_box(cookies,stockupbill_allocate_payload)

        # 通过备货单id获取详情信息
        stockupbill_detail_resp = StockupBill().get_stockupbill_detail(cookies, stockUpBillId)
        sourceCode = json.loads(stockupbill_detail_resp.text)["result"]["stockUpBillCode"]
        stockupbilldata = {"stockUpBillId": int(stockUpBillId), "sourceCode": sourceCode}

        return stockupbilldata


    def create_stockupbill_link_v1(self, cookies, shopId, warehouseId, targetWarehouseId, operateDivisionId,
                                   purchaserId, product_code,supplierId,companyId):
        """
        创建备货单链路-按件
        :param shopId:商品id
        :param warehouseId:出发仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部id
        :param platformEnName:平台名称
        :return:
        """
        # 创建采购单按件上架
        Stock().purchase_order_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId, product_code,supplierId,companyId)

        # 创建备货单
        stockupbill_payload = {
            "stockUpBillCode": "",
            "sendOutGoodsType": 1,
            "shopId": shopId,
            "isFNSKU": False,
            "warehouseId": warehouseId,
            "targetWarehouseId": targetWarehouseId,
            "expectedDeliveryTime": self.formatted_date,
            "platformName": "抖音",
            "shippingAddress": "2311 York Rd",
            "attachmentDetail": [],
            "remark": "备注一下",
            "operateDivisionId": operateDivisionId,
            "stockUpType": 1,
            "operaterId":purchaserId,
            "platformEnName": "Tiktok"
        }

        stockupbill_resp = StockupBill().create_stockupbill_v1(cookies, stockupbill_payload)
        stockUpBillId = json.loads(stockupbill_resp.text)["result"]

        # 查询sku信息
        items_payload = {
            "entityInfoType": 1,
            "status": [
                2,
                3
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "cNName": "",
            "sPUCode": product_code,
            "pageIndex": 1,
            "pageSize": 100
        }
        query_skulist_resp = Product().query_skulist_v1(cookies, items_payload)
        query_skulist_result = json.loads(query_skulist_resp.text)["result"]
        print(query_skulist_result["items"])

        # 创建备货单明细
        stockUpBillDetail = []

        for item in query_skulist_result["items"]:
            # 查询批次库存
            url = f"{waveecharmer_Host}/api/stock/batchstocks/groupByShop-OperateDivision-StockType?skuIds={item['id']}&shopIds={shopId}&warehouseIds={warehouseId}&goodOrDefectives=1&operateDivisionIds={operateDivisionId}&stockTypes=1"
            batchstocks_resp = Stock().get_batchstocks(url, cookies)
            batchstocks_result = json.loads(batchstocks_resp.text)["result"]
            stockUpBillDetail_dict = {
                "skuId": item["id"],
                "plannedShipmentQuantity": batchstocks_result[0]["availableStockQuantity"],
                "skuImageUrl": item["imageUrl"],
                "thirdImageUrl": None,
                "useImageSource": item["useImageSource"],
                "skuCode": item["code"],
                "oldSkuCode": item["oldCode"],
                "skuName": item["cnName"],
                "sellerSkuCode": item["code"]
            }
            update_share_dict = {
                "id": 3391,
                "skuId": item["id"],
                "plannedShipmentQuantity": batchstocks_result[0]["availableStockQuantity"],
                "warehouseLocationIds": []
            }

            stockUpBillDetail.append(stockUpBillDetail_dict)

        stockupbill_detail_payload = {
            "stockUpBillId": stockUpBillId,
            "stockUpBillDetail": stockUpBillDetail
        }

        StockupBill().create_stockupbill_detail_v1(cookies, stockupbill_detail_payload)

        # 通过备货单id获取商品详情信息
        stockupbill_detailbysku_resp = StockupBill().get_stockupbill_detailbysku(cookies, stockUpBillId)
        stockupbill_detailbysku_result = json.loads(stockupbill_detailbysku_resp.text)["result"]
        print(stockupbill_detailbysku_result)

        # 分配库存
        update_share_items = []
        for item in stockupbill_detailbysku_result:
            update_share_dict = {
                "id": item["id"],
                "skuId": item["skuId"],
                "plannedShipmentQuantity": item["plannedShipmentQuantity"],
                "warehouseLocationIds": []
            }
            update_share_items.append(update_share_dict)

        print(update_share_items)

        update_share_stockupbill_payload = {
            "id": stockUpBillId,
            "items": update_share_items
        }
        StockupBill().update_share_stockupbill_v1(cookies, update_share_stockupbill_payload)

        # 通过备货单id获取详情信息
        stockupbill_detail_resp = StockupBill().get_stockupbill_detail(cookies, stockUpBillId)
        sourceCode = json.loads(stockupbill_detail_resp.text)["result"]["stockUpBillCode"]
        stockupbilldata = {"stockUpBillId": int(stockUpBillId), "sourceCode": sourceCode}

        return stockupbilldata


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # StockupBill().create_stockupbill_link(cookies, "LIPENG456-B-P", 161, 150, 11, 5, "Tiktok")
    # StockupBill().create_stockupbill(cookies, 161, 150, 11, 5, "Tiktok")

    # 按件创建备货单
    #StockupBill().create_stockupbill_link_v1(cookies, 161, 150, 11, 5, 303, "A5-181")


    #按箱创建备货单
    StockupBill().create_stockupbill_box_link(cookies, 161, 150, 11, 5, 303, "A5-181",3)


