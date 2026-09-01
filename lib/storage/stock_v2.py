# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 13:58
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stock_v2.py
# @Project : wecharmer
import json
import random
import time

import requests

from conf.baseconfig import waveecharmer_Host
from interface.stock import stock_api
from lib.login import Login
from lib.productandmaterial.product import Product
from lib.purchase.purchaseorder import PurchaseOrder

from interface.purchase.purchaseorder_api import PurchaseOrder_Api
from lib.purchase.purchaseorder_v2 import PurchaseOrderv2
from interface.stock.stock_api import Stock_Api
from lib.storage import stock


class Stockv2:
    def __init__(self):
        pass

    def purchase_order_link(self, cookies, shopId, shopAccount, warehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId):
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
        purchaseorderv1id = PurchaseOrderv2().create_purchaseorderv2_link(cookies, shopId, shopAccount, warehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId)
        time.sleep(2)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder_Api().get_purchaseorder_groups(cookies, purchaseorderv1id)
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]

        # 创建采购入库单
        items = []

        for item in skuDetailDimensionDetails:
            items_dict = {
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
            "purchaseOrderId": purchaseorderv1id,
            "warehouseName": "工厂虚拟仓",
            "purchaseOrderCode": skuDetailDimensionDetails[0]["purchaseOrderCode"],
            "remark": "",
            "sourceBillId": purchaseorderv1id,
            "code": "",
            "isSpeedScan": False,
            "productType": 1,
            "attachments": [],
            "items": items
        }

        purchase_order_resp = Stock_Api().create_purchase_order(cookies, purchase_order_payload)
        purchase_order_id = json.loads(purchase_order_resp.text)["result"]["id"]

        # 送审
        Stock_Api().purchase_order_review(cookies, purchase_order_id)

        # 获取入库单详情
        dimension_detail_resp =Stock_Api().get_sku_dimension_detail(cookies, purchase_order_id)
        dimension_detail_result = json.loads(dimension_detail_resp.text)["result"]

        # 分页获取库位
        warehouse_location_resp = Stock_Api().get_warehouse_location(cookies, warehouseId)
        warehouse_location_result = json.loads(warehouse_location_resp.text)["result"]

        # 按sku上架
        items = []

        for item in dimension_detail_result:
            items_dict = {
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
        Stock_Api().create_putonshelfbill_sku(cookies, putonshelfbill_sku_payload)


    def purchase_order_box_link(self, cookies, shopId, shopAccount, warehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId):
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
        purchaseorderv1id = PurchaseOrderv2().create_purchaseorderv2_link(cookies, shopId, shopAccount, warehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId)
        time.sleep(2)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder_Api().get_purchaseorder_groups(cookies, purchaseorderv1id)
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]

        # 创建采购入库单
        items = []

        for item in skuDetailDimensionDetails:
            items_dict = {
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
            "purchaseOrderId": purchaseorderv1id,
            "warehouseName": "工厂虚拟仓",
            "purchaseOrderCode": skuDetailDimensionDetails[0]["purchaseOrderCode"],
            "remark": "",
            "sourceBillId": purchaseorderv1id,
            "code": "",
            "isSpeedScan": False,
            "productType": 1,
            "attachments": [],
            "items": items
        }

        purchase_order_resp = Stock_Api().create_purchase_order(cookies, purchase_order_payload)
        purchase_order_id = json.loads(purchase_order_resp.text)["result"]["id"]
        purchase_order_code = json.loads(purchase_order_resp.text)["result"]["code"]


        # 送审
        Stock_Api().purchase_order_review(cookies, purchase_order_id)

        # 强制等待
        time.sleep(1)

        # 扫描装箱
        count = 0
        while count < 10:
            for content in skuDetailDimensionDetails:
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
                Stock_Api().stockinbill_packing_box(cookies, packing_box_payload)
            print("这是第 {} 次循环".format(count + 1))
            count += 1

        # 分页获取库位
        warehouse_location_resp = Stock_Api().get_warehouse_location(cookies, warehouseId)
        warehouse_location_result = json.loads(warehouse_location_resp.text)["result"]

        # 分页获取入库单装箱库存
        packingstock_page_resp = Stock_Api().get_packingstock_page(cookies, purchase_order_code)
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

        Stock_Api().create_putonshelfbill_box(cookies, putonshelfbill_box_payload)



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    #按件入库上架
    #Stockv2().purchase_order_link(cookies, 161,"LIPENG", 129, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
    #                                              30)
    #按箱入库上架
    Stockv2().purchase_order_box_link(cookies, 161,"LIPENG", 150, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
                                                  30)

