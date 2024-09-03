# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/12 下午1:20
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stock.py
# @Project : wecharmer
import json

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from lib.purchase.purchaseorder import PurchaseOrder
from util import httpUtil


class Stock:
    def __init__(self):
        pass

    def get_batchstocks(self, url, cookies):
        resp = requests.get(url=url, headers=cookies)
        print("查询店铺运营事业部库存类型维度的批次库存resp-----------\n" + resp.text)
        return resp

    def get_warehouse_location(self, cookies, warehouseId):
        """
        分页获取库位
        :return:
        """
        url = f"{waveecharmer_Host}/api/warehouse/location/page?warehouseId={warehouseId}&goodOrDefective=1&able=1&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=10"
        resp = requests.get(url=url, headers=cookies)
        print("分页获取库位resp-----------\n" + resp.text)
        return resp


    def get_sku_dimension_detail(self, cookies, purchase_order_id):
        """
        获取入库单sku明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbill/sku-dimension-detail?id={purchase_order_id}&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=10"
        resp = requests.get(url=url, headers=cookies)
        print("获取入库单sku明细resp-----------\n" + resp.text)
        return resp

    def create_purchase_order(self, cookies, payload):
        """
        创建采购入库
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbill/purchase-order"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建采购入库resp-----------\n" + resp.text)
        return resp

    def purchase_order_review(self, cookies, purchase_order_id):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbill/approve-status/{purchase_order_id}/review"
        resp = requests.put(url=url, headers=cookies)
        print("送审resp-----------\n" + resp.text)
        return resp

    def create_putonshelfbill_sku(self, cookies, payload):
        """
        按sku上架
        :return:
        """
        url = f"{waveecharmer_Host}/api/putonshelfbill/sku"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按sku上架resp-----------\n" + resp.text)
        return resp

    def purchase_order_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId):
        """
        创建采购单入库上架链路
        :param companyId:财务公司抬头id
        :param supplierId:供应商id
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """
        # 创建采购单返回id
        purchaseorderid = PurchaseOrder().create_purchaseorder_link(cookies, shopId, warehouseId, operateDivisionId,
                                                                    purchaserId)

        # 根据采购单id查询详细
        get_purchaseorder_resp = PurchaseOrder().get_purchaseorder(cookies, purchaseorderid)
        get_purchaseorder_result = json.loads(get_purchaseorder_resp.text)["result"]

        # 创建采购入库单
        purchase_order_payload = {
            "fileList": [],
            "sourceType": 1,
            "importType": "采购入库",
            "scanCode": "",
            "purchaseOrderId": purchaseorderid,
            "warehouseName": "恒丰仓库",
            "purchaseOrderCode": get_purchaseorder_result["skuDetailDimensionDetails"][0]["purchaseOrderCode"],
            "remark": "",
            "sourceBillId": purchaseorderid,
            "code": "",
            "isSpeedScan": False,
            "productType": 1,
            "attachments": [],
            "items": [
                {
                    "skuId": get_purchaseorder_result["skuDetailDimensionDetails"][0]["skuId"],
                    "stockInQuantity": 100,
                    "productType": 1,
                    "tests": []
                },
                {
                    "skuId": get_purchaseorder_result["skuDetailDimensionDetails"][1]["skuId"],
                    "stockInQuantity": 200,
                    "productType": 1,
                    "tests": []
                },
                {
                    "skuId": get_purchaseorder_result["skuDetailDimensionDetails"][2]["skuId"],
                    "stockInQuantity": 300,
                    "productType": 1,
                    "tests": []
                },
                {
                    "skuId": get_purchaseorder_result["skuDetailDimensionDetails"][3]["skuId"],
                    "stockInQuantity": 400,
                    "productType": 1,
                    "tests": []
                }
            ]
        }

        purchase_order_resp = Stock().create_purchase_order(cookies, purchase_order_payload)
        purchase_order_id = json.loads(purchase_order_resp.text)["result"]["id"]
        print(purchase_order_id)

        # 送审
        Stock().purchase_order_review(cookies, purchase_order_id)

        #获取入库单详情
        dimension_detail_resp=Stock().get_sku_dimension_detail(cookies, purchase_order_id)
        dimension_detail_result=json.loads(dimension_detail_resp.text)["result"]

        # 分页获取库位
        warehouse_location_resp = Stock().get_warehouse_location(cookies, warehouseId)
        warehouse_location_result = json.loads(warehouse_location_resp.text)["result"]

        # 按sku上架
        putonshelfbill_sku_resp = {
            "stockInBillId": purchase_order_id,
            "items": [
                {
                    "skuId": dimension_detail_result[0]["skuId"],
                    "productType": 1,
                    "locations": [
                        {
                            "warehouseLocationId": warehouse_location_result["items"][0]["id"],
                            "quantity": dimension_detail_result[0]["notShelfQuantity"]
                        }
                    ]
                },
                {
                    "skuId": dimension_detail_result[1]["skuId"],
                    "productType": 1,
                    "locations": [
                        {
                            "warehouseLocationId": warehouse_location_result["items"][0]["id"],
                            "quantity": dimension_detail_result[1]["notShelfQuantity"]
                        }
                    ]
                },
                {
                    "skuId": dimension_detail_result[2]["skuId"],
                    "productType": 1,
                    "locations": [
                        {
                            "warehouseLocationId": warehouse_location_result["items"][0]["id"],
                            "quantity": dimension_detail_result[2]["notShelfQuantity"]
                        }
                    ]
                },
                {
                    "skuId": dimension_detail_result[3]["skuId"],
                    "productType": 1,
                    "locations": [
                        {
                            "warehouseLocationId": warehouse_location_result["items"][0]["id"],
                            "quantity": dimension_detail_result[3]["notShelfQuantity"]
                        }
                    ]
                }
            ]
        }
        Stock().create_putonshelfbill_sku(cookies, putonshelfbill_sku_resp)


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    Stock().purchase_order_link(cookies, 161, 150, 5, 303)
    # Stock().get_batchstocks(cookies,5452,161,150)
