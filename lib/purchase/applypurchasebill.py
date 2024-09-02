# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/8/23 下午2:12
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : applypurchasebill.py
# @Project : wecharmer
import json

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from datetime import datetime, timedelta


class ApplyPurchaseBill:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=90)

        # 将时间差加到当前日期上
        new_date = now + three_days
        self.formatted_date_old = now.strftime("%Y-%m-%d %H:%M:%S")

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")

    def create_applypurchasebill(self, cookies, payload):
        """
        创建申购单
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebill"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建申购单resp-----------\n" + resp.text)
        return resp

    def create_applypurchasebill_details(self, cookies, payload):
        """
        创建申购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebill/details"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建申购单明细resp-----------\n" + resp.text)
        return resp



    def applypurchasebill_review(self, applypurchasebillid, cookies, payload):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebill/approvestatus/{applypurchasebillid}/review"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("送审resp-----------\n" + resp.text)
        return resp

    def create_applypurchasebill_link(self, cookies, shopId, operateDivisionId):
        """
        创建常规申购单链路
        :param applyPurchaseType:申购方式
        :param developType:定做 现货
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param expectedShipmentAddr:地区i
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """
        # 创建常规申购单
        applypurchasebill_payload = {
            "shopId": shopId,
            "applyPurchaseType": 1,
            "operateDivisionId": operateDivisionId,
            "remark": "",
            "expectedArrivalTime": self.formatted_date_old,
            "expectedPutOnSaleTime": self.formatted_date,
            "developType": 2,
            "sampleUsageIds": [],
            "purchaseBusinessType": 3,
            "expectedShipmentAddr": 1,
            "isQuickReturn": False,
            "attachments": []
        }
        print(applypurchasebill_payload)
        applypurchasebill_resp = ApplyPurchaseBill().create_applypurchasebill(cookies, applypurchasebill_payload)
        applypurchasebillid = json.loads(applypurchasebill_resp.text)["result"]["id"]

        # 创建申购单明细
        applypurchasebill_details_payload = {
            "applyPurchaseBillId": applypurchasebillid,
            "purchaseBillDetails": [
                {
                    "productId": 1138,
                    "skuId": 6355,
                    "quantity": 100
                },
                {
                    "productId": 1138,
                    "skuId": 6356,
                    "quantity": 200
                },
                {
                    "productId": 1138,
                    "skuId": 6357,
                    "quantity": 300
                },
                {
                    "productId": 1138,
                    "skuId": 6358,
                    "quantity": 400
                }
            ]
        }

        ApplyPurchaseBill().create_applypurchasebill_details(cookies, applypurchasebill_details_payload)

        #送审
        payload={}
        ApplyPurchaseBill().applypurchasebill_review(applypurchasebillid, cookies, payload)

        return applypurchasebillid




if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    ApplyPurchaseBill().create_applypurchasebill_link(cookies, 161, 5)
