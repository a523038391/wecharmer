# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 15:09
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stockupbillv2.py
# @Project : wecharmer
import json

import requests

from conf.baseconfig import waveecharmer_Host
from datetime import datetime, timedelta

from interface.firstleg.stockupbill_api import Stockupbill_Api
from interface.product.product_api import Product_Api
from interface.stock.stock_api import Stock_Api
from lib.login import Login
from lib.productandmaterial.product import Product
from lib.storage.stock import Stock
from lib.storage.stock_v2 import Stockv2
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


    def create_stockupbill_link(self, cookies, shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId):
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
        Stockv2().purchase_order_link(cookies, shopId, shopAccount, warehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId)

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

        stockupbill_resp = Stockupbill_Api().create_stockupbill(cookies, stockupbill_payload)
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
        query_skulist_resp = Product_Api().query_skulist_v1(cookies, items_payload)
        query_skulist_result = json.loads(query_skulist_resp.text)["result"]
        print(query_skulist_result["items"])

        # 创建备货单明细
        stockUpBillDetail = []

        for item in query_skulist_result["items"]:
            # 查询批次库存
            url = f"{waveecharmer_Host}/api/stock/batchstocks/groupByShop-OperateDivision-StockType?skuIds={item['id']}&shopIds={shopId}&warehouseIds={warehouseId}&goodOrDefectives=1&operateDivisionIds={operateDivisionId}&stockTypes=1"
            batchstocks_resp = Stock_Api().get_batchstocks(url, cookies)
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

            stockUpBillDetail.append(stockUpBillDetail_dict)

        stockupbill_detail_payload = {
            "stockUpBillId": stockUpBillId,
            "stockUpBillDetail": stockUpBillDetail
        }

        Stockupbill_Api().create_stockupbill_detail(cookies, stockupbill_detail_payload)

        # 通过备货单id获取商品详情信息
        stockupbill_detailbysku_resp = Stockupbill_Api().get_stockupbill_detailbysku(cookies, stockUpBillId)
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
        Stockupbill_Api().update_share_stockupbill_v1(cookies, update_share_stockupbill_payload)

        # 通过备货单id获取详情信息
        stockupbill_detail_resp = Stockupbill_Api().get_stockupbill_detail(cookies, stockUpBillId)
        sourceCode = json.loads(stockupbill_detail_resp.text)["result"]["stockUpBillCode"]
        stockupbilldata = {"stockUpBillId": int(stockUpBillId), "sourceCode": sourceCode}

        return stockupbilldata



    def create_stockupbill_box_link(self, cookies, shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId,quantity):
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
        Stockv2().purchase_order_box_link(cookies, shopId, shopAccount, warehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId)

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

        stockupbill_resp = Stockupbill_Api().create_stockupbill(cookies, stockupbill_payload)
        stockUpBillId = json.loads(stockupbill_resp.text)["result"]

        # 获取装箱库存明细平铺箱贴聚合数据分页

        packingstock_spread_page_resp =  Stock_Api().get_packingstock_spread_page(cookies, shopId, operateDivisionId,warehouseId,
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
        Stockupbill_Api().create_stockupbill_detail(cookies, stockupbill_detail_payload)

        # 分配库存

        stockupbill_allocate_payload = {
            "id": stockUpBillId,
            "items": allocate_items
        }
        Stockupbill_Api().update_share_stockupbill_box(cookies,stockupbill_allocate_payload)

        # 通过备货单id获取详情信息
        stockupbill_detail_resp = Stockupbill_Api().get_stockupbill_detail(cookies, stockUpBillId)
        sourceCode = json.loads(stockupbill_detail_resp.text)["result"]["stockUpBillCode"]
        stockupbilldata = {"stockUpBillId": int(stockUpBillId), "sourceCode": sourceCode}

        return stockupbilldata


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    # 按件创建备货单
    #StockupBill().create_stockupbill_link(cookies, 161,"LIPENG", 150,350, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
    #                                              30)

    # 按箱创建备货单
    StockupBill().create_stockupbill_box_link(cookies, 161,"LIPENG", 150,350, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
                                                  30,3)