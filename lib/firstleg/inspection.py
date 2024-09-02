# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/8/27 下午4:36
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : inspection.py
# @Project : wecharmer
import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.booking import Booking
from lib.login import Login
from datetime import datetime, timedelta


class Inspection:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")

    def create_inspection(self, cookies, payload):
        """
        创建验货申请
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建验货申请resp-----------\n" + resp.text)
        return resp

    def inspection_submit(self, cookies, inspectionid):
        """
        提交
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require/submit/{inspectionid}"
        resp = requests.put(url=url, headers=cookies)
        print("提交resp-----------\n" + resp.text)
        return resp

    def inspection_assign(self, cookies, inspectionid, purchaserId):
        """
        指派验货员
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require/assign/{inspectionid}/{purchaserId}"
        resp = requests.put(url=url, headers=cookies)
        print("指派验货员resp-----------\n" + resp.text)
        return resp


    def get_inspection_items(self, cookies, inspectionid):
        """
        查询验货单详情
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require/items/{inspectionid}"
        resp = requests.get(url=url, headers=cookies)
        print("查询验货单详情resp-----------\n" + resp.text)
        return resp



    def get_inspection_list(self, cookies, bookingcode):
        """
        查询验货单列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require/page?status=2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&bookingBillCode={bookingcode}&pageIndex=1&pageSize=10"
        resp = requests.get(url=url, headers=cookies)
        print("查询验货单列表resp-----------\n" + resp.text)
        return resp


    def create_inspection_report(self, cookies, payload):
        """
        创建验货报告
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/report"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建验货报告resp-----------\n" + resp.text)
        return resp

    def inspection_askapprove(self, cookies, inspection_report_id):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/report/askapprove/{inspection_report_id}"
        resp = requests.put(url=url, headers=cookies)
        print("送审resp-----------\n" + resp.text)
        return resp




    def create_inspection_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, targetWarehouseId):
        """
        创建验货申请链路
        :param requireType:收货类型
        :param requireDate:验货日期
        :param containerId:货柜id
        :param purchaseOrderId:采购单id
        :param supplierAccountId:供应商账户id
        :param supplierId:供应商id
        :param conclusion:合格 不合格
        :param inspectionWay:免检
        :return:
        """
        # 创建订舱通知返回id
        bookingid = Booking().create_booking_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                                  targetWarehouseId)

        # 获取订舱单明细
        Booking_Detail_resp = Booking().get_booking(cookies, bookingid)
        Booking_Detail_result = json.loads(Booking_Detail_resp.text)["result"]
        bookingcode=Booking_Detail_result["code"]

        # 获取订舱单分页根据供应商
        bysupplier_resp = Booking().get_bysupplier(cookies, bookingid)
        bysupplier_result = json.loads(bysupplier_resp.text)["result"]

        # 创建验货申请
        inspection_payload = {
            "code": "",
            "name": "",
            "requireType": 1,
            "bookingBillId": bookingid,
            "requireDate": self.formatted_date,
            "supplierId": bysupplier_result[0]["supplierId"],
            "remark": "",
            "bookingBillCode": Booking_Detail_result["code"],
            "attachments": [],
            "sourceType": 2,
            "items": [
                {
                    "purchaseOrderId": Booking_Detail_result["items"][0]["purchaseOrderId"],
                    "skuId": 6355
                },
                {
                    "purchaseOrderId": Booking_Detail_result["items"][0]["purchaseOrderId"],
                    "skuId": 6356
                },
                {
                    "purchaseOrderId": Booking_Detail_result["items"][0]["purchaseOrderId"],
                    "skuId": 6357
                },
                {
                    "purchaseOrderId": Booking_Detail_result["items"][0]["purchaseOrderId"],
                    "skuId": 6358
                }
            ]
        }

        inspection_resp = Inspection().create_inspection(cookies, inspection_payload)
        inspectionid = json.loads(inspection_resp.text)["result"]

        # 提交验货申请
        Inspection().inspection_submit(cookies, inspectionid)

        # 指派验货员
        Inspection().inspection_assign(cookies, inspectionid, purchaserId)

        #查询验货申请单详情
        inspection_items_resp = Inspection().get_inspection_items(cookies, inspectionid)
        inspection_items_result=json.loads(inspection_items_resp.text)["result"]

        #查询验货单列表
        inspection_list_resp=Inspection().get_inspection_list(cookies, bookingcode)
        inspection_list_result=json.loads(inspection_list_resp.text)["result"]


        # 创建验货报告
        inspection_report_payload = {
            "code": "",
            "supplierName": inspection_list_result["items"][0]["supplierName"],
            "supplierId": inspection_list_result["items"][0]["supplierId"],
            "inspectorName": inspection_list_result["items"][0]["inspectorName"],
            "requireType": inspection_list_result["items"][0]["requireType"],
            "bookingBillCode": inspection_list_result["items"][0]["bookingBillCode"],
            "selectCode": inspection_list_result["items"][0]["code"],
            "reportDate": self.formatted_date,
            "requireId": inspection_list_result["items"][0]["id"],
            "conclusion": 1,
            "remark": None,
            "attachments": [],
            "requireItemIdObj": {
                f"{inspection_items_result[0]["purchaseOrderCode"]}-{inspection_items_result[0]["skuCode"]}": inspection_items_result[0]["id"],
                f"{inspection_items_result[1]["purchaseOrderCode"]}-{inspection_items_result[1]["skuCode"]}": inspection_items_result[1]["id"],
                f"{inspection_items_result[2]["purchaseOrderCode"]}-{inspection_items_result[2]["skuCode"]}": inspection_items_result[2]["id"],
                f"{inspection_items_result[3]["purchaseOrderCode"]}-{inspection_items_result[3]["skuCode"]}": inspection_items_result[3]["id"]
            },
            "item": {
                "inspectionWay": 1,
                "qualifiedQuantity": None,
                "defectQuantity": None
            },
            "packagedStockItems": [
                {
                    "purchaseOrderId": inspection_items_result[0]["purchaseOrderId"],
                    "skuId": inspection_items_result[0]["skuId"],
                    "packagedQuantity": 18
                },
                {
                    "purchaseOrderId": inspection_items_result[1]["purchaseOrderId"],
                    "skuId": inspection_items_result[1]["skuId"],
                    "packagedQuantity": 24
                },
                {
                    "purchaseOrderId": inspection_items_result[2]["purchaseOrderId"],
                    "skuId": inspection_items_result[2]["skuId"],
                    "packagedQuantity": 30
                },
                {
                    "purchaseOrderId": inspection_items_result[3]["purchaseOrderId"],
                    "skuId": inspection_items_result[3]["skuId"],
                    "packagedQuantity": 36
                }
            ],
            "boxSizeItems": [
                {
                    "requireItemId": inspection_items_result[0]["id"],
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "ctnNetWeight": 6,
                    "totalCtnVolume": 0.0006,
                    "ctnGrossWeight": 6,
                    "totalCtnGrossWeight": 18,
                    "totalGrossWeight": 108
                },
                {
                    "requireItemId": inspection_items_result[1]["id"],
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "ctnNetWeight": 6,
                    "totalCtnVolume": 0.0008,
                    "ctnGrossWeight": 6,
                    "totalCtnGrossWeight": 24,
                    "totalGrossWeight": 144
                },
                {
                    "requireItemId": inspection_items_result[2]["id"],
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "ctnNetWeight": 6,
                    "totalCtnVolume": 0.001,
                    "ctnGrossWeight": 6,
                    "totalCtnGrossWeight": 30,
                    "totalGrossWeight": 180
                },
                {
                    "requireItemId": inspection_items_result[3]["id"],
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "ctnNetWeight": 6,
                    "totalCtnVolume": 0.0012,
                    "ctnGrossWeight": 6,
                    "totalCtnGrossWeight": 36,
                    "totalGrossWeight": 216
                }
            ]
        }
        inspection_report_resp =  Inspection().create_inspection_report(cookies,inspection_report_payload)
        inspection_report_id=json.loads(inspection_report_resp.text)["result"]

        #送审
        Inspection().inspection_askapprove(cookies,inspection_report_id)

        booking_data={"bookingid":bookingid,"bookingcode":bookingcode}

        return booking_data


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    Inspection().create_inspection_link(cookies, 161, 15, 5, 303, 12)
