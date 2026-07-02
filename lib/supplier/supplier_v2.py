# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/5/27 上午10:04
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : supplier_v2.py
# @Project : wecharmer

import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from interface.purchase.purchaseorder_api import PurchaseOrder_Api
from interface.supplier.supplier_api import Supplier_Api
from lib.login import Login
from lib.purchase.purchaseorder import PurchaseOrder

from lib.purchase.purchaseorder_v2 import PurchaseOrderv2


class Supplierv2:
    def __init__(self):
        pass

    def supplierstockinv2_link(self, cookies, shopId, shopAccount, warehouseId, operateDivisionId, operaterId,
                               purchaserId,
                               product_code, salesPlanDate, expectedShelfDate, supplierId, companyId):
        """
         创建工厂入库单链路
         :param isSubmit:是否提交
         :param receiptType:单据类型id
         :param warehouseType:虚拟仓类型枚举
         :param originOrderType:入库单类型枚举
         :return:
        """

        # 创建采购单返回id
        purchaseorderv1id = PurchaseOrderv2().create_purchaseorderv2_link(cookies, shopId, shopAccount, warehouseId,
                                                                          operateDivisionId, operaterId, purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId)
        time.sleep(2)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder_Api().get_purchaseorderv1_details(cookies, purchaseorderv1id)
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

        # 查询采购单列表
        page_payload = {
            "purchaseOrderStatuses": [
                2,
                5
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "purchaseOrderCodes": [
                skuDetailDimensionDetails[0]["purchaseOrderCode"]
            ],
            "pageIndex": 1,
            "pageSize": 10,
            "znd": "t564200"
        }
        purchaseOrder_resp = PurchaseOrder_Api().page_purchaseorderv1(cookies,page_payload)
        purchaseOrder_items = json.loads(purchaseOrder_resp.text)["result"]["items"]

        # 获取来源单据的商品明细
        originorderinfo_resp = Supplier_Api().get_supplierstockinv1_originorderinfo(cookies, purchaseorderv1id, 2)
        originorderinfo_result = json.loads(originorderinfo_resp.text)["result"]

        # 创建工厂入库单

        itmes = []

        for itme in originorderinfo_result:
            originorderinfo_dict = {
                "skuId": itme["skuId"],
                "stockInQuantity": itme["purchaseQuantity"],
                "purchaseOrderId": itme["purchaseOrderId"],
                "id": None,
                "warehouseId": purchaseOrder_items[0]["warehouseId"],
                "warehouseName": purchaseOrder_items[0]["warehouseName"]
            }
            itmes.append(originorderinfo_dict)

        supplierstockin_payload = {
            "supplierInOrderCode": "",
            "receiptType": 1001,
            "originOrderType": 2,
            "supplierId": purchaseOrder_items[0]["supplierId"],
            "warehouseType": 1,
            "remarks": "",
            "attachments": [],
            "originOrderId": purchaseOrder_items[0]["id"],
            "originOrderCode": purchaseOrder_items[0]["purchaseOrderCode"],
            "scanCode": "",
            "sourceBillId": purchaseOrder_items[0]["id"],
            "warehouseId": purchaseOrder_items[0]["warehouseId"],
            "warehouseName": purchaseOrder_items[0]["warehouseName"],
            "isSubmit": False,
            "items":
                itmes
        }
        print(supplierstockin_payload)

        supplierstockin_resp = Supplier_Api().create_supplierstockinv1(cookies, supplierstockin_payload)
        supplierstockin_result = json.loads(supplierstockin_resp.text)["result"]

        # 提交
        Supplier_Api().submit_supplierstockinv1(cookies, supplierstockin_result)

        supplierstockin_data = {"purchaseOrderId": purchaseorderv1id,
                                "purchaseOrderCode": purchaseOrder_items[0]["purchaseOrderCode"],
                                "supplierId": purchaseOrder_items[0]["supplierId"]}


        print(supplierstockin_data)
        return supplierstockin_data


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    Supplierv2().supplierstockinv2_link(cookies, 161, "LIPENG", 15, 5, 303, 303, "B101-003", "2026-08", "2026-08-01",
                                        70,
                                        29)
