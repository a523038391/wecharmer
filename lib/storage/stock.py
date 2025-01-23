# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/12 下午1:20
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stock.py
# @Project : wecharmer
import json
import random
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from lib.productandmaterial.product import Product
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
        url = f"{waveecharmer_Host}/api/stockinbill/sku-dimension-detail?id={purchase_order_id}&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=100"
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

    def stockinbill_packing_box(self, cookies, payload):
        """
        入库单装箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbill/packing-box"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("入库单装箱resp-----------\n" + resp.text)
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

    def create_putonshelfbill_box(self, cookies, payload):
        """
        按箱上架
        :return:
        """
        url = f"{waveecharmer_Host}/api/putonshelfbill/box"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按箱上架resp-----------\n" + resp.text)
        return resp

    def get_packingstock_page(self, cookies, purchase_order_code):
        """
        获取装箱库存分页列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/packingstock/page?sourceBillCode={purchase_order_code}&isOnShelves=false&isOther=true&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=100"
        resp = requests.get(url=url, headers=cookies)
        print("获取装箱库存分页列表resp-----------\n" + resp.text)
        return resp

    def get_packingstock_spread_page(self, cookies,shopId,operateDivisionId, product_code):
        """
        获取装箱库存明细平铺箱贴聚合数据分页
        :return:
        """
        url = f"{waveecharmer_Host}/api/packingstock/spread/page?shopIds={shopId}&operateDivisionId={operateDivisionId}&isGetSpread=true&isIncludeSellerSku=true&isHideZero=true&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&productCode={product_code}&pageIndex=1&pageSize=100"
        resp = requests.get(url=url, headers=cookies)
        print("获取装箱库存明细平铺箱贴聚合数据分页resp-----------\n" + resp.text)
        return resp

    def purchase_order_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, product_code):
        """
        创建采购单入库按sku上架链路
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
                                                                    purchaserId, product_code)

        # 根据采购单id查询详细
        get_purchaseorder_resp = PurchaseOrder().get_purchaseorder(cookies, purchaseorderid)
        get_purchaseorder_result = json.loads(get_purchaseorder_resp.text)["result"]

        # 创建采购入库单
        items=[]

        for item in get_purchaseorder_result["skuDetailDimensionDetails"]:

            items_dict={
                    "skuId": item["skuId"],
                    "stockInQuantity": item["quantity"],
                    "productType": 1,
                    "tests": []
                }
            items.append(items_dict)
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
            "items": items
        }

        purchase_order_resp = Stock().create_purchase_order(cookies, purchase_order_payload)
        purchase_order_id = json.loads(purchase_order_resp.text)["result"]["id"]
        print(purchase_order_id)

        # 送审
        Stock().purchase_order_review(cookies, purchase_order_id)

        # 获取入库单详情
        dimension_detail_resp = Stock().get_sku_dimension_detail(cookies, purchase_order_id)
        dimension_detail_result = json.loads(dimension_detail_resp.text)["result"]

        # 分页获取库位
        warehouse_location_resp = Stock().get_warehouse_location(cookies, warehouseId)
        warehouse_location_result = json.loads(warehouse_location_resp.text)["result"]

        # 按sku上架
        items=[]

        for item in dimension_detail_result:

            items_dict={
                    "skuId": item["skuId"],
                    "productType": 1,
                    "locations": [
                        {
                            "warehouseLocationId": warehouse_location_result["items"][0]["id"],
                            "quantity": item["notShelfQuantity"]
                        }
                    ]
                }
            items.append(items_dict)
        putonshelfbill_sku_payload = {
            "stockInBillId": purchase_order_id,
            "items": items
        }
        Stock().create_putonshelfbill_sku(cookies, putonshelfbill_sku_payload)

    def purchase_order_box_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, product_code):
        """
        创建采购单入库按箱上架链路
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
                                                                    purchaserId, product_code)

        # 根据采购单id查询详细
        get_purchaseorder_resp = PurchaseOrder().get_purchaseorder(cookies, purchaseorderid)
        get_purchaseorder_result = json.loads(get_purchaseorder_resp.text)["result"]

        # 创建唯一码
        skus = []

        for item in get_purchaseorder_result["skuDetailDimensionDetails"]:
            skus_dict = {
                    "skuId": item["skuId"],
                    "id": item["skuId"],
                    "skuCode": item["skuCode"],
                    "printQuantity": 10
                }
            skus.append(skus_dict)
        serialnumber_payload = {
            "purchaseOrderId": purchaseorderid,
            "skus": skus
        }
        serialnumber_resp = Product().create_serialnumberc(cookies, serialnumber_payload)
        serialnumber_result = json.loads(serialnumber_resp.text)["result"]

        # 创建采购入库单
        items=[]

        for item in get_purchaseorder_result["skuDetailDimensionDetails"]:

            items_dict={
                    "skuId": item["skuId"],
                    "stockInQuantity": item["quantity"],
                    "productType": 1,
                    "tests": []
                }
            items.append(items_dict)
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
            "items": items
        }

        purchase_order_resp = Stock().create_purchase_order(cookies, purchase_order_payload)
        purchase_order_id = json.loads(purchase_order_resp.text)["result"]["id"]
        purchase_order_code = json.loads(purchase_order_resp.text)["result"]["code"]
        print(purchase_order_id)

        # 送审
        Stock().purchase_order_review(cookies, purchase_order_id)

        # 强制等待
        time.sleep(2)

        # 扫描装箱
        count = 0
        while count < 10:
            for content in get_purchaseorder_result["skuDetailDimensionDetails"]:
                packing_box_payload = {
                    "id": purchase_order_id,
                    "boxStandardId": 1,
                    "totalWeightWithBoxActual": 12,
                    "boxItems": [
                        {
                            "skuId": content["skuId"],
                            "quantity": random.randint(1, 9)
                        }
                    ]
                }
                Stock().stockinbill_packing_box(cookies, packing_box_payload)
            print("这是第 {} 次循环".format(count + 1))
            count += 1

        # 分页获取库位
        warehouse_location_resp = Stock().get_warehouse_location(cookies, warehouseId)
        warehouse_location_result = json.loads(warehouse_location_resp.text)["result"]

        # 分页获取入库单装箱库存
        packingstock_page_resp = Stock().get_packingstock_page(cookies, purchase_order_code)
        packingstock_page_result = json.loads(packingstock_page_resp.text)["result"]["items"]
        boxes = []
        for item in packingstock_page_result:
            new_dict = {
                "packingStockId": item["id"],
                "warehouseLocationId": warehouse_location_result["items"][0]["id"],
                "warehouseLocationCode": warehouse_location_result["items"][0]["warehouseLocationCode"]
            }
            boxes.append(new_dict)

        print(boxes)

        # 按箱上架
        putonshelfbill_box_payload = {
            "stockInBillId": purchase_order_id,
            "boxes": boxes
        }

        Stock().create_putonshelfbill_box(cookies, putonshelfbill_box_payload)


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    #Stock().purchase_order_link(cookies, 161, 150, 5, 303, "A5-181")
    # Stock().get_batchstocks(cookies,5452,161,150)
    Stock().purchase_order_box_link(cookies, 161, 1, 5, 303, "A5-181")
