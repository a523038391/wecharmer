# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/8/23 下午3:24
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : purchaseorder.py
# @Project : wecharmer


import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from datetime import datetime, timedelta

from lib.purchase.applypurchasebill import ApplyPurchaseBill


class PurchaseOrder:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")


    def get_purchaseorder_details(self,cookies,purchaseorderid):
        """
        根据id获取采购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/details/fullall?purchaseOrderIds={purchaseorderid}"
        resp = requests.get(url=url, headers=cookies)
        print("获取采购单明细resp-----------\n" + resp.text)
        return resp


    def create_purchaseorder(self, cookies, payload):
        """
        创建采购单
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建采购单resp-----------\n" + resp.text)
        return resp

    def create_purchaseorder_details(self, cookies, payload):
        """
        创建采购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/purchaseorderdetails"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建采购单明细resp-----------\n" + resp.text)
        return resp



    def purchaseorder_review(self, purchaseorderid, cookies, payload):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/approvestatus/{purchaseorderid}/review"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("送审resp-----------\n" + resp.text)
        return resp


    def get_purchaseorder(self,cookies, purchaseorderid):
        """
        根据id获取采购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/{purchaseorderid}/detail/all"
        resp = requests.get(url=url, headers=cookies)
        print("获取采购单明细resp-----------\n" + resp.text)
        return resp


    def create_purchaseorder_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId):
        """
        创建采购单链路
        :param companyId:财务公司抬头id
        :param supplierId:供应商id
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """

        # 创建备货单返回id
        applypurchasebillid = ApplyPurchaseBill().create_applypurchasebill_link(cookies, shopId, operateDivisionId)

        time.sleep(2)

        # 创建采购单
        purchaseorder_payload = {
            "companyId": 2,
            "supplierId": 6,
            "warehouseId": warehouseId,
            "purchaseOrderType": 1,
            "productDevelopType": 2,
            "supplierPaymentMethod": 2,
            "operateDivisionId": operateDivisionId,
            "shopId": shopId,
            "remark": "",
            "logisticsFee": 0,
            "attachments": [],
            "purchaserId": purchaserId,
            "deliveryDate": self.formatted_date,
            "planDeliveryDate": None,
            "companyCurrencyType": "CNY",
            "exchangeRate": 1,
            "supplierContactPerson": "小常",
            "supplierContactPersonMobile": "17620866231",
            "supplierSettlementMethod": 1,
            "supplierSettlementDay": 20,
            "supplierPrepaidRate": 0.8,
            "purchaseSourceType": 4,
            "purchaseOrderCode": None,
            "purchasePlanBillId": None,
            "skuSupplierObj": {
                "6355": 6,
                "6356": 6,
                "6357": 6,
                "6358": 6
            },
            "bhApplyPurchaseBillId": None,
            "applyPurchaseBillCode": "QG24082300017",
            "applyPurchaseBillId": applypurchasebillid,
            "soureBillId": 3973,
            "expectedArrivalTime": "2024-08-23T07:20:13+00:00",
            "expectedPutOnSaleTime": "2024-11-21T07:20:13+00:00",
            "supplierAccountNumber": "",
            "supplierOpeningBank": "",
            "chargePerson": "小飞",
            "chargePersonMobile": "17620865451",
            "address": "Detail Address"
        }
        purchaseorder_resp = PurchaseOrder().create_purchaseorder(cookies, purchaseorder_payload)
        print(purchaseorder_resp)
        purchaseorderid = json.loads(purchaseorder_resp.text)["result"]["id"]

        # 创建采购单明细
        purchaseorder_details_payload = {
            "purchaseOrderId": purchaseorderid,
            "purchaseOrderDetails": [
                {
                    "skuId": 6355,
                    "quantity": 100,
                    "overflowRate": 0.05,
                    "unitPrice": 6,
                    "taxRate": 0.04
                },
                {
                    "skuId": 6356,
                    "quantity": 200,
                    "overflowRate": 0.06,
                    "unitPrice": 6,
                    "taxRate": 0.04
                },
                {
                    "skuId": 6357,
                    "quantity": 300,
                    "overflowRate": 0.06,
                    "unitPrice": 6,
                    "taxRate": 0.04
                },
                {
                    "skuId": 6358,
                    "quantity": 400,
                    "overflowRate": 0.06,
                    "unitPrice": 6,
                    "taxRate": 0.04
                }
            ]
        }
        PurchaseOrder().create_purchaseorder_details(cookies, purchaseorder_details_payload)

        #送审
        payload = {}
        PurchaseOrder().purchaseorder_review(purchaseorderid,cookies,payload)

        return purchaseorderid



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    PurchaseOrder().create_purchaseorder_link(cookies, 161, 15, 5, 303)
