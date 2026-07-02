# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/4/20 上午10:43
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : applypurchasebill_v2.py
# @Project : wecharmer


import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from interface.purchase.applypurchasebill_api import ApplyPurchaseBill_Api
from lib.login import Login
from datetime import datetime, timedelta

from lib.productandmaterial.product import Product



class ApplyPurchaseBillv2:
    def __init__(self):
        pass

    def create_applypurchasebillv2_link(self, cookies, shopId,shopAccount, operateDivisionId, operaterId, product_code,salesPlanDate,expectedShelfDate):
        """
        创建常规申购单链路
        :param applyPurchaseType:申购方式
        :param developType:定做 现货
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param expectedShipmentAddr:地区i
        :param purchaseBusinessType:备货 出运 常规
        :param salesPlanDate:销售计划年月
        :param expectedShelfDate:期望上架日期
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

        # 创建申购单明细
        details = []
        quantity = 0
        for item in product_result:
            quantity += 500
            purchaseBillDetails_dict = {
                "spuId": item["productId"],
                "skuId": item["id"],
                "quantity": quantity,
                "operaterId": operaterId,
                "operaterName": "李朋",
                "replenishmentSuggestQuantity": None,
                "shopId": shopId,
                "shopAccount": shopAccount,
                "operateDivisionId": operateDivisionId,
                "operateDivisionName": "运营青蛙椅事业部",
                "countryId": 14,
                "countryTwoCharCode": "US",
                "salesPlanDate": salesPlanDate,
                "expectedShelfDate": expectedShelfDate,
                "applyPurchaseBillType": 1,
                "isUrgent": False,
                "remark": "",
                "packingMethodRemark": "",
                "sampleUsageId": None,
                "sampleUsageName": None,
                "status": 2
            }
            details.append(purchaseBillDetails_dict)

        # 创建常规申购单
        applypurchasebillv2_payload = {

            "details": details,
            "toReview": False
        }
        print(applypurchasebillv2_payload)
        applypurchasebill_resp = ApplyPurchaseBill_Api().create_applypurchasebillv2(cookies, applypurchasebillv2_payload)
        applypurchasebill_result = json.loads(applypurchasebill_resp.text)["result"]

        # 送审
        payload = [applypurchasebill_result["applyPurchaseBillId"]]
        ApplyPurchaseBill_Api().applypurchasebillv2_review(cookies, payload)

        return applypurchasebill_result


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    ApplyPurchaseBillv2().create_applypurchasebillv2_link(cookies, 161,"LIPENG", 2, 217, "V123-109","2026-08","2026-09-30")