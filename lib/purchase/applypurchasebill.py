# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/8/23 下午2:12
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : applypurchasebill.py
# @Project : wecharmer
import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from datetime import datetime, timedelta

from lib.productandmaterial.product import Product


class ApplyPurchaseBill:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=90)
        three_days_old = timedelta(days=3)
        three_days_future = timedelta(days=180)

        # 将时间差加到当前日期上
        new_date = now + three_days
        old_date = now + three_days_old
        future_date = now + three_days_future
        self.formatted_date_old = old_date.strftime("%Y-%m-%d %H:%M:%S")

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")
        self.formatted_date_future = future_date.strftime("%Y-%m-%d %H:%M:%S")

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

    def get_applypurchasebill_detail_all(self, cookies, applypurchasebillid):
        """
        获取某个申购单所有明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebill/{applypurchasebillid}/detail/all"
        resp = requests.get(url=url, headers=cookies)
        print("获取某个申购单所有明细resp-----------\n" + resp.text)
        return resp


    def get_applypurchasebill(self, cookies, applypurchasebillid):
        """
        获取某个申购单详情
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebill/{applypurchasebillid}"
        resp = requests.get(url=url, headers=cookies)
        print("获取某个申购单详情resp-----------\n" + resp.text)
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

    def create_stock_applypurchasebill_link(self, cookies, shopId, operateDivisionId, purchaserId,
                                            purchasername, product_code):
        """
        创建备货申购单链路
        :param applyPurchaseType:申购方式
        :param developType:定做 现货
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param expectedShipmentAddr:地区i
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """

        # 查询商品信息
        product_list_payload = {
            "entityInfoType": 1,
            "sorts": [
                {
                    "field": "code",
                    "order": "asc"
                }
            ],
            "code": product_code,
            "pageIndex": 1,
            "pageSize": 100
        }
        product_resp = Product().query_spulist(cookies, product_list_payload)
        product_result = json.loads(product_resp.text)["result"]["items"][0]["skus"]

        # 创建备货申购单
        applypurchasebill_payload = {
            "shopId": shopId,
            "applyPurchaseType": 1,
            "operateDivisionId": operateDivisionId,
            "remark": "测试",
            "developType": 1,
            "operaterId": purchaserId,
            "operaterName": purchasername,
            "purchaseBusinessType": 1,
            "attachments": []
        }
        print(applypurchasebill_payload)
        applypurchasebill_resp = ApplyPurchaseBill().create_applypurchasebill(cookies, applypurchasebill_payload)
        applypurchasebillid = json.loads(applypurchasebill_resp.text)["result"]["id"]

        # 创建申购单明细
        purchaseBillDetails = []
        quantity = 0
        for item in product_result:
            quantity += 1000
            purchaseBillDetails_dict = {
                "productId": item["productId"],
                "skuId": item["id"],
                "quantity": quantity,
                "expectedArrivalTime": self.formatted_date
            }
            purchaseBillDetails.append(purchaseBillDetails_dict)

        applypurchasebill_details_payload = {
            "applyPurchaseBillId": applypurchasebillid,
            "purchaseBillDetails": purchaseBillDetails
        }

        ApplyPurchaseBill().create_applypurchasebill_details(cookies, applypurchasebill_details_payload)

        # 送审
        payload = {}
        ApplyPurchaseBill().applypurchasebill_review(applypurchasebillid, cookies, payload)

        return applypurchasebillid

    def create_shipment_applypurchasebill_link(self, cookies, shopId,
                                               operateDivisionId, purchaserId,
                                               purchasername, applypurchasebillid):
        """
        创建出运申购单链路
        :param applyPurchaseType:申购方式
        :param developType:定做 现货
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param expectedShipmentAddr:地区i
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """


        applypurchasebill_payload = {
            "shopId": shopId,
            "applyPurchaseType": 1,
            "operateDivisionId": operateDivisionId,
            "remark": "",
            "expectedArrivalTime": self.formatted_date,
            "expectedPutOnSaleTime": self.formatted_date_future,
            "developType": 1,
            "purchaseBusinessType": 2,
            "bhApplyPurchaseBillId": applypurchasebillid,
            "expectedShipmentAddr": 1,
            "isQuickReturn": False,
            "operaterId": purchaserId,
            "operaterName": purchasername,
            "attachments": []
        }

        applypurchasebill_resp = ApplyPurchaseBill().create_applypurchasebill(cookies, applypurchasebill_payload)
        shipment_applypurchasebillid = json.loads(applypurchasebill_resp.text)["result"]["id"]

        # 获取备货单明细
        get_applypurchasebill_resp = ApplyPurchaseBill().get_applypurchasebill_detail_all(cookies, applypurchasebillid)
        get_applypurchasebill_result = json.loads(get_applypurchasebill_resp.text)["result"]

        # 创建申购单明细
        purchaseBillDetails = []
        quantity = 0
        for item in get_applypurchasebill_result["skuAndMonthYearDetailDimensionDetails"]:
            quantity += 100
            purchaseBillDetails_dict = {
                "productId": item["productId"],
                "skuId": item["skuId"],
                "quantity": quantity
            }
            purchaseBillDetails.append(purchaseBillDetails_dict)

        applypurchasebill_details_payload = {
            "applyPurchaseBillId": shipment_applypurchasebillid,
            "purchaseBillDetails": purchaseBillDetails
        }

        ApplyPurchaseBill().create_applypurchasebill_details(cookies, applypurchasebill_details_payload)

        # 送审
        payload = {}
        ApplyPurchaseBill().applypurchasebill_review(shipment_applypurchasebillid, cookies, payload)
        return shipment_applypurchasebillid
    def create_applypurchasebill_link(self, cookies, shopId, operateDivisionId, operaterId,product_code):

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

        # 查询商品信息
        product_list_payload = {
            "entityInfoType": 1,
            "sorts": [
                {
                    "field": "code",
                    "order": "asc"
                }
            ],
            "code": product_code,
            "pageIndex": 1,
            "pageSize": 100
        }
        product_resp = Product().query_spulist(cookies, product_list_payload)
        product_result = json.loads(product_resp.text)["result"]["items"][0]["skus"]

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
            "operaterId": operaterId,
            "operaterName": "李朋",
            "attachments": [],
            "warehouseType": 2,
            "transportationTypeId": 18,
            "transportationTypeName": None,
            "stockInType": None
        }
        print(applypurchasebill_payload)
        applypurchasebill_resp = ApplyPurchaseBill().create_applypurchasebill(cookies, applypurchasebill_payload)
        applypurchasebillid = json.loads(applypurchasebill_resp.text)["result"]["id"]

        # 创建申购单明细
        purchaseBillDetails = []
        quantity = 0
        for item in product_result:
            quantity += 100
            purchaseBillDetails_dict = {
                "productId": item["productId"],
                "skuId": item["id"],
                "quantity": quantity
            }
            purchaseBillDetails.append(purchaseBillDetails_dict)

        applypurchasebill_details_payload = {
            "applyPurchaseBillId": applypurchasebillid,
            "purchaseBillDetails": purchaseBillDetails
        }

        ApplyPurchaseBill().create_applypurchasebill_details(cookies, applypurchasebill_details_payload)


        # 送审
        payload = {}
        ApplyPurchaseBill().applypurchasebill_review(applypurchasebillid, cookies, payload)

        return applypurchasebillid


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    # 创建常规申购单
    ApplyPurchaseBill().create_applypurchasebill_link(cookies, 161, 5 ,303,"A5-181")

    # 创建备货申购单
    #ApplyPurchaseBill().create_stock_applypurchasebill_link(cookies, 161, 5,303,"李朋","A5-181")

    # 创建出运申购单
    #ApplyPurchaseBill().create_shipment_applypurchasebill_link(cookies, 161, 5, 303, "李朋", "A5-181")
