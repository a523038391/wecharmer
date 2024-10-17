# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/9/14 上午10:21
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : bookingcontainer.py
# @Project : wecharmer


import json
import random
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.booking import Booking
from lib.login import Login
from datetime import datetime, timedelta


class BookingContainer:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")
        self.random_number = ''.join(str(random.randint(0, 9)) for _ in range(10))

    def create_bookingcontainer(self, cookies, payload):
        """
        创建订柜单
        :return:
        """
        url = f"{waveecharmer_Host}/api/bookingcontainer/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建订柜单resp-----------\n" + resp.text)
        return resp

    def page_bookingcontainer(self, cookies, payload):
        """
        获取订柜单列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/bookingcontainer/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("获取订柜单列表resp-----------\n" + resp.text)
        return resp

    def page_inquiry(self, cookies, payload):
        """
        获取询价单列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/inquiry/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("获取询价单列表resp-----------\n" + resp.text)
        return resp

    def create_inquiry(self, cookies, payload):
        """
        创建询价单
        :return:
        """
        url = f"{waveecharmer_Host}/api/inquiry/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建询价单resp-----------\n" + resp.text)
        return resp


    def inquiry_review(self, id, cookies):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/inquiry/ask-approval?id={id}"
        resp = requests.put(url=url, headers=cookies)
        print("送审resp-----------\n" + resp.text)
        return resp

    def create_bookingcontainer_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                     targetWarehouseId, product_code, billCategory):
        """
        创建订柜单链路
        :param billCategory:单据类型
        :param locationWarehouseId:目的仓id
        :param shippingMethodId:发货方式
        :param bookingBerthMethod:订舱方式
        :param isNeedInquiry:是否询价
        :param loadingContainerMethod:装柜方式
        :return:
        """

        # 创建订舱通知返回id
        bookingid = Booking().create_booking_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                                  targetWarehouseId, product_code)

        # 获取订舱单
        Booking_Detail_resp = Booking().get_booking(cookies, bookingid)
        result = json.loads(Booking_Detail_resp.text)["result"]

        # 查询订舱通知列表
        page_Booking_resp = Booking().page_booking(cookies, result['code'])
        page_Booking_result = json.loads(page_Booking_resp.text)["result"]

        # 创建顶柜单
        bookingcontainer_payload = {
            "billCategory": 507,
            "locationWarehouseId": targetWarehouseId,
            "locationWarehouseName": "ZH-LA01-HIGO[纵横美西1号仓HIGO仓]",
            "bookingBerthMethod": 1,
            "shippingMethodId": 4,
            "isNeedInquiry": "是",
            "loadingContainerMethod": 1,
            "containerId": 5,
            "containerName": "测试",
            "containerVolume": 1,
            "containerLoadWeight": 1,
            "cutoffOrdersTime": self.formatted_date,
            "ladingNo": "lipeng" + self.random_number,
            "sailingDate": self.formatted_date,
            "remark": "备注一下",
            "boxTotalVolume": None,
            "boxTotalWeight": None,
            "productTotalWeight": None,
            "vouchingClerkId": purchaserId,
            "vouchingClerkName": "李朋",
            "detailList": [
                {
                    "sourceBillId": bookingid,
                    "sourceBillCode": result['code'],
                    "deliveryDate": page_Booking_result['items'][0]['deliveryDate'],
                    "boxQuantity": int(page_Booking_result['items'][0]['totalPackageQuantity']),
                    "boxTotalVolume": page_Booking_result['items'][0]['totalCtnVolume'],
                    "boxTotalWeight": page_Booking_result['items'][0]['totalCtnGrossWeight'],
                    "productTotalWeight": page_Booking_result['items'][0]['totalGrossWeight'],
                    "cargoReadyDay": page_Booking_result['items'][0]['cargoReadyDay'],
                }
            ]
        }
        print(bookingcontainer_payload)
        BookingContainer().create_bookingcontainer(cookies, bookingcontainer_payload)

        # 根据来源单据查询货柜单
        page_bookingcontaine_payload = {
            "statusList": [
                1
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "sourceBillCodes": [
                result['code']
            ],
            "pageIndex": 1,
            "pageSize": 10
        }
        page_bookingcontainer_resp = BookingContainer().page_bookingcontainer(cookies, page_bookingcontaine_payload)
        page_bookingcontainer = json.loads(page_bookingcontainer_resp.text)["result"]

        # 创建询价单
        inquiry_payload = {
            "remark": "",
            "quoteAttachmentName": None,
            "quoteAttachmentUrl": None,
            "bookingContainerBillId": page_bookingcontainer["items"][0]["id"],
            "bookingContainerBillCode": page_bookingcontainer["items"][0]["bookingContainerCode"],
            "quoteInfoList": [
                {
                    "freightForwardingName": "环美",
                    "freightForwardingId": 3,
                    "isFullyInclusive": 1,
                    "shippingCompanyName": "长荣",
                    "shippingCompanyId": 14,
                    "effectiveDay": 99,
                    "shipName": "COSCO ITALY 069E",
                    "etd": self.formatted_date,
                    "remark": "备注一些",
                    "feesList": [
                        {
                            "quoteInfoFeesType": 1,
                            "currencyCode": "USD",
                            "amount": 99,
                            "exchangeRate": 7.1027
                        },
                        {
                            "quoteInfoFeesType": 2,
                            "currencyCode": "USD",
                            "amount": 99,
                            "exchangeRate": 7.1027
                        },
                        {
                            "quoteInfoFeesType": 3,
                            "currencyCode": "USD",
                            "amount": 99,
                            "exchangeRate": 7.1027
                        },
                        {
                            "quoteInfoFeesType": 4,
                            "currencyCode": "USD",
                            "amount": 99,
                            "exchangeRate": 7.1027
                        },
                        {
                            "quoteInfoFeesType": 5,
                            "currencyCode": "USD",
                            "amount": 99,
                            "exchangeRate": 7.1027
                        }
                    ],
                    "isDefault": True,
                    "quoteAttachmentUrl": None,
                    "quoteAttachmentName": None
                }
            ],
            "inquiryAttachmentList": [],
            "inquiryBillCode": "",
            "isSaveAndAudit": False
        }

        BookingContainer().create_inquiry(cookies, inquiry_payload)

        # 查询询价单
        page_inquiry_payload = {
            "statusList": [
                1,
                2,
                3,
                4
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "isFuzzyQuery": "false",
            "bookingContainerBillCode": page_bookingcontainer["items"][0]["bookingContainerCode"],
            "pageIndex": 1,
            "pageSize": 10
        }
        page_inquiry_resp = BookingContainer().page_inquiry(cookies, page_inquiry_payload)
        page_inquiry_result = json.loads(page_inquiry_resp.text)["result"]

        # 送审
        BookingContainer().inquiry_review(page_inquiry_result["items"][0]["id"],cookies)



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    BookingContainer().create_bookingcontainer_link(cookies, 161, 15, 5, 303, 12, "A5-181", 507)
