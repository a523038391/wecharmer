# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 17:12
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : scanpackingv2.py
# @Project : wecharmer
import json
import  time
import requests

from conf.baseconfig import waveecharmer_Host
from interface.firstleg.Printpickingbill_api import Printpickingbill_Api
from lib.firstleg.printpickingbillv2 import Printpickingbill
from lib.login import Login
from datetime import datetime, timedelta
from util import httpUtil


class ScanPacking:
    def __init__(self):
        pass


    def stockupbill_scanpacking_box_link(self, cookies,shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId,quantity):

        # 创建备货单-按箱-打印
        stockupbilldata=Printpickingbill().stockupbill_box_print(cookies, shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId,quantity)

        # 扫描单号并茨取单据信息
        scan_billcode_resp = Printpickingbill_Api().scan_billcode(cookies, stockupbilldata["sourceCode"])
        scan_billcode_result = json.loads(scan_billcode_resp.text)["result"]

        # 装箱

        for item in scan_billcode_result["packingStockList"]:
            packingbybox_payload = {
                "sourceType": 2,
                "sourceId": stockupbilldata["stockUpBillId"],
                "sourceCode": stockupbilldata["sourceCode"],
                "packingStockModel": item
            }
            Printpickingbill_Api().scanpacking_packingbybox(cookies, packingbybox_payload)

        # 提交装箱审核
        payload_submit = {
            "sourceType": 2,
            "sourceId": stockupbilldata["stockUpBillId"],
            "sourceCode": stockupbilldata["sourceCode"]
        }
        Printpickingbill_Api().submit_scanpacking(cookies, payload_submit)

        # 装箱审核
        payload_process = {
            "sourceType": 2,
            "sourceId": stockupbilldata["stockUpBillId"],
            "sourceCode":  stockupbilldata["sourceCode"],
            "auditStatus": True,
            "failReason": ""
        }
        Printpickingbill_Api().process_scanpacking(cookies, payload_process)

        return stockupbilldata



    def stockupbill_scanpacking_link(self, cookies,shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId):

        # 创建备货单-按件-打印
        stockupbilldata = Printpickingbill().stockupbill_print(cookies,shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId)

        # 获取所有产品装箱信息
        all_productcode_resp = Printpickingbill_Api().scan_all_productcode(cookies, 2, stockupbilldata["stockUpBillId"],
                                                                  stockupbilldata["sourceCode"])
        all_productcode_result = json.loads(all_productcode_resp.text)["result"]

        # 装箱
        detailList = []
        for item in all_productcode_result:
            detailList_dict = {
                "skuImgUrl": item["skuImgUrl"],
                "thirdImageUrl": None,
                "useImageSource": item["useImageSource"],
                "skuId": item["skuId"],
                "skuCode": item["skuCode"],
                "oldSkuCode": item["oldSkuCode"],
                "skuName": item["skuName"],
                "fnSkuCode": None,
                "packingQuantity": item["remainingQuantity"],
                "remainingQuantity": item["remainingQuantity"],
                "grossWeight": item["grossWeight"],
                "remainingQuantityCpu": 0,
                "transQtyValid": False
            }
            detailList.append(detailList_dict)
        packing_scanpacking_payload = {
            "billCode": stockupbilldata["sourceCode"],
            "boxId": 1,
            "totalWeightWithBox": 20,
            "detailList": detailList
        }
        Printpickingbill_Api().packing_scanpacking_v1(cookies, packing_scanpacking_payload)


        # 提交装箱审核
        payload_submit = {
            "sourceType": 2,
            "sourceId": stockupbilldata["stockUpBillId"],
            "sourceCode": stockupbilldata["sourceCode"]
        }
        Printpickingbill_Api().submit_scanpacking(cookies, payload_submit)

        # 装箱审核
        payload_process = {
            "sourceType": 2,
            "sourceId": stockupbilldata["stockUpBillId"],
            "sourceCode": stockupbilldata["sourceCode"],
            "auditStatus": True,
            "failReason": ""
        }
        Printpickingbill_Api().process_scanpacking(cookies, payload_process)

        return stockupbilldata


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    #备货单按箱装箱-审核
    #ScanPacking().stockupbill_scanpacking_box_link(cookies, 161,"LIPENG", 150,350, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
    #                                      30,1)

    #备货单按件装箱-审核
    ScanPacking().stockupbill_scanpacking_link(cookies, 161,"LIPENG", 150,350, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
                                          30)