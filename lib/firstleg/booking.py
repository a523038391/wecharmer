# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/8/27 上午11:12
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : booking.py
# @Project : wecharmer

import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from datetime import datetime, timedelta

from lib.purchase.purchaseorder import PurchaseOrder


class Booking:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)
        three_days_eta = timedelta(days=90)

        # 将时间差加到当前日期上
        new_date = now + three_days
        new_date_eta = now + three_days_eta

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")
        self.formatted_date_eta = new_date_eta.strftime("%Y-%m-%d %H:%M:%S")

    def create_booking(self, cookies, payload):
        """
        创建订舱单
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建订舱单resp-----------\n" + resp.text)
        return resp

    def booking_submit(self, bookingid, cookies):
        """
        提交
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/submit/{bookingid}"
        resp = requests.put(url=url, headers=cookies)
        print("提交resp-----------\n" + resp.text)
        return resp

    def get_booking(self, cookies, bookingid):
        """
        获取订舱单
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/{bookingid}"
        resp = requests.get(url=url, headers=cookies)
        print("获取订舱单resp-----------\n" + resp.text)
        return resp

    def page_booking(self, cookies, bookingcode):
        """
        获取订舱单列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/page?status=4&isLoadingAdviceBillCode=false&isEmptyBookingContainerCode=true&sorts=%7B%22field%22:%22containerNo%22,%22order%22:%22desc%22%7D,%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&code={bookingcode}&pageIndex=1&pageSize=10"
        resp = requests.get(url=url, headers=cookies)
        print("获取订舱单列表resp-----------\n" + resp.text)
        return resp

    def repairshipping_booking(self, cookies, payload):
        """
        补充发货信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/repairshipping"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("补充发货信息resp-----------\n" + resp.text)
        return resp

    def reviewshipping_booking(self, cookies, payload):
        """
        审核发货信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/reviewshipping"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("审核resp-----------\n" + resp.text)
        return resp

    def get_bysupplier(self, cookies, bookingid):
        """
        获取订舱单分页根据供应商
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/page/bysupplier?bookingBillId={bookingid}"
        resp = requests.get(url=url, headers=cookies)
        print("获取订舱单分页根据供应商resp-----------\n" + resp.text)
        return resp

    def create_booking_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, targetWarehouseId,product_code):
        """
        创建订舱单链路
        :param isLCL:是否拼柜
        :param cargoReadyDay:货号日期
        :param containerId:货柜id
        :param purchaseOrderId:采购单id
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """

        # 创建采购单返回id
        purchaseOrderId = PurchaseOrder().create_purchaseorder_link(cookies, shopId, warehouseId, operateDivisionId,
                                                                    purchaserId,product_code)

        time.sleep(2)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder().get_purchaseorder_details(cookies, purchaseOrderId)
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

        # 创建订舱单
        booking_payload = {
            "code": "",
            "cargoReadyDay": "2024-09-28",
            "isLCL": "false",
            "containerId": 4,
            "volume": 3375,
            "loadWeight": 150,
            "warehouseName": "恒丰仓库",
            "attachments": [],
            "remark": "",
            "isPrepare": False,
            "items": [
                {
                    "id": skuDetailDimensionDetails[0]["id"],
                    "purchaseOrderId": skuDetailDimensionDetails[0]["purchaseOrderId"],
                    "purchaseOrderCode": skuDetailDimensionDetails[0]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 54840,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-181",
                    "productName": "常山仓蜡笔小新A5-181",
                    "skuCode": "A5-181-A-F",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725604863983_a405e9c1_24090600259.JPG",
                    "thirdImageUrl": None,
                    "useImageSource": 2,
                    "skuName": "常山仓蜡笔小新-黄色-J",
                    "tranSku": None,
                    "taxRate": 0.04,
                    "maxQuantity": 105,
                    "putOnQuantity": 0,
                    "inventoryAvailableQuantity": 0,
                    "bookingQuantity": 18,
                    "exchangeRate": 1,
                    "companyCurrencyType": "CNY",
                    "purchaseOrderDetailDimension": 1,
                    "applyPurchaseBillId": 4208,
                    "bhApplyPurchaseBillId": None,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-09-06T06:57:13.019773+00:00",
                    "skuId": 49532,
                    "quantity": 100,
                    "suite": 6,
                    "overflowRate": 0.05,
                    "unitPrice": 6,
                    "remark": None,
                    "expectedArrivalTime": None,
                    "cpuQuantity": 105,
                    "operateDivisionName": "运营青蛙椅事业部",
                    "warehouseId": 15,
                    "purchaseOrderDetailId": skuDetailDimensionDetails[0]["id"],
                    "allowBooking": True,
                    "shopAccount": "LIPENG",
                    "warehouseName": "恒丰仓库",
                    "supplierName": "供应商名",
                    "supplierId": 6,
                    "isAllowNegative": True,
                    "supplierList": [
                        {
                            "id": 12499,
                            "skuId": 49532,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 6,
                            "default": True,
                            "link": "",
                            "ctnLongX": 6,
                            "ctnLongY": 6,
                            "ctnLongZ": 6,
                            "ctnQuantity": 6,
                            "ctnNetWeight": 6,
                            "ctnGrossWeight": 6,
                            "ctnVolume": 0.0002,
                            "isChoose": True
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 17,
                    "grossWeight": 6,
                    "productWeight": "612.00",
                    "ctnGrossWeightAll": "102.00",
                    "ctnLongXYZ": "0.0034"
                },
                {
                    "id": skuDetailDimensionDetails[1]["id"],
                    "purchaseOrderId": skuDetailDimensionDetails[1]["purchaseOrderId"],
                    "purchaseOrderCode": skuDetailDimensionDetails[1]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 54840,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-181",
                    "productName": "常山仓蜡笔小新A5-181",
                    "skuCode": "A5-181-A-L",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725604863983_a405e9c1_24090600259.JPG",
                    "thirdImageUrl": True,
                    "useImageSource": 2,
                    "skuName": "常山仓蜡笔小新-黄色-P",
                    "tranSku": True,
                    "taxRate": 0.04,
                    "maxQuantity": 212,
                    "putOnQuantity": 0,
                    "inventoryAvailableQuantity": 0,
                    "bookingQuantity": 24,
                    "exchangeRate": 1,
                    "companyCurrencyType": "CNY",
                    "purchaseOrderDetailDimension": 1,
                    "applyPurchaseBillId": 4208,
                    "bhApplyPurchaseBillId": True,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-09-06T06:57:13.019775+00:00",
                    "skuId": 49533,
                    "quantity": 200,
                    "suite": 6,
                    "overflowRate": 0.06,
                    "unitPrice": 6,
                    "remark": True,
                    "expectedArrivalTime": True,
                    "cpuQuantity": 212,
                    "operateDivisionName": "运营青蛙椅事业部",
                    "warehouseId": 15,
                    "purchaseOrderDetailId": skuDetailDimensionDetails[1]["id"],
                    "shopAccount": "LIPENG",
                    "warehouseName": "恒丰仓库",
                    "supplierName": "供应商名",
                    "supplierId": 6,
                    "isAllowNegative": True,
                    "supplierList": [
                        {
                            "id": 12500,
                            "skuId": 49533,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 6,
                            "default": True,
                            "link": "",
                            "ctnLongX": 6,
                            "ctnLongY": 6,
                            "ctnLongZ": 6,
                            "ctnQuantity": 6,
                            "ctnNetWeight": 6,
                            "ctnGrossWeight": 6,
                            "ctnVolume": 0.0002,
                            "isChoose": True
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 35,
                    "grossWeight": 6,
                    "productWeight": "1260.00",
                    "ctnGrossWeightAll": "210.00",
                    "ctnLongXYZ": "0.0070"
                },
                {
                    "id": skuDetailDimensionDetails[2]["id"],
                    "purchaseOrderId": skuDetailDimensionDetails[2]["purchaseOrderId"],
                    "purchaseOrderCode": skuDetailDimensionDetails[2]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 54840,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-181",
                    "productName": "常山仓蜡笔小新A5-181",
                    "skuCode": "A5-181-B-F",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725604866221_4f633db4_24090600260.JPG",
                    "thirdImageUrl": None,
                    "useImageSource": 2,
                    "skuName": "常山仓蜡笔小新-绿色-J",
                    "tranSku": None,
                    "taxRate": 0.04,
                    "maxQuantity": 318,
                    "putOnQuantity": 0,
                    "inventoryAvailableQuantity": 0,
                    "bookingQuantity": 30,
                    "exchangeRate": 1,
                    "companyCurrencyType": "CNY",
                    "purchaseOrderDetailDimension": 1,
                    "applyPurchaseBillId": 4208,
                    "bhApplyPurchaseBillId": None,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-09-06T06:57:13.019775+00:00",
                    "skuId": 49534,
                    "quantity": 300,
                    "suite": 6,
                    "overflowRate": 0.06,
                    "unitPrice": 6,
                    "remark": None,
                    "expectedArrivalTime": None,
                    "cpuQuantity": 318,
                    "operateDivisionName": "运营青蛙椅事业部",
                    "warehouseId": 15,
                    "purchaseOrderDetailId": skuDetailDimensionDetails[2]["id"],
                    "shopAccount": "LIPENG",
                    "warehouseName": "恒丰仓库",
                    "supplierName": "供应商名",
                    "supplierId": 6,
                    "isAllowNegative": True,
                    "supplierList": [
                        {
                            "id": 12501,
                            "skuId": 49534,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 6,
                            "default": True,
                            "link": "",
                            "ctnLongX": 6,
                            "ctnLongY": 6,
                            "ctnLongZ": 6,
                            "ctnQuantity": 6,
                            "ctnNetWeight": 6,
                            "ctnGrossWeight": 6,
                            "ctnVolume": 0.0002,
                            "isChoose": True
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 53,
                    "grossWeight": 6,
                    "productWeight": "1908.00",
                    "ctnGrossWeightAll": "318.00",
                    "ctnLongXYZ": "0.0106"
                },
                {
                    "id": skuDetailDimensionDetails[3]["id"],
                    "purchaseOrderId": skuDetailDimensionDetails[3]["purchaseOrderId"],
                    "purchaseOrderCode": skuDetailDimensionDetails[3]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 54840,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-181",
                    "productName": "常山仓蜡笔小新A5-181",
                    "skuCode": "A5-181-B-L",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725604866221_4f633db4_24090600260.JPG",
                    "thirdImageUrl": None,
                    "useImageSource": 2,
                    "skuName": "常山仓蜡笔小新-绿色-P",
                    "tranSku": None,
                    "taxRate": 0.04,
                    "maxQuantity": 424,
                    "putOnQuantity": 0,
                    "inventoryAvailableQuantity": 0,
                    "bookingQuantity": 36,
                    "exchangeRate": 1,
                    "companyCurrencyType": "CNY",
                    "purchaseOrderDetailDimension": 1,
                    "applyPurchaseBillId": 4208,
                    "bhApplyPurchaseBillId": None,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-09-06T06:57:13.019776+00:00",
                    "skuId": 49535,
                    "quantity": 400,
                    "suite": 6,
                    "overflowRate": 0.06,
                    "unitPrice": 6,
                    "remark": None,
                    "expectedArrivalTime": None,
                    "cpuQuantity": 424,
                    "operateDivisionName": "运营青蛙椅事业部",
                    "warehouseId": 15,
                    "purchaseOrderDetailId": skuDetailDimensionDetails[3]["id"],
                    "shopAccount": "LIPENG",
                    "warehouseName": "恒丰仓库",
                    "supplierName": "供应商名",
                    "supplierId": 6,
                    "isAllowNegative": True,
                    "supplierList": [
                        {
                            "id": 12502,
                            "skuId": 49535,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 6,
                            "default": True,
                            "link": "",
                            "ctnLongX": 6,
                            "ctnLongY": 6,
                            "ctnLongZ": 6,
                            "ctnQuantity": 6,
                            "ctnNetWeight": 6,
                            "ctnGrossWeight": 6,
                            "ctnVolume": 0.0002,
                            "isChoose": True
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 70,
                    "grossWeight": 6,
                    "productWeight": "2520.00",
                    "ctnGrossWeightAll": "420.00",
                    "ctnLongXYZ": "0.0140"
                }
            ]
        }

        booking_resp = Booking().create_booking(cookies, booking_payload)
        bookingid = json.loads(booking_resp.text)["result"]
        print(bookingid)

        # 提交订舱单
        Booking().booking_submit(bookingid, cookies)

        # 获取订舱单
        Booking_Detail_resp = Booking().get_booking(cookies, bookingid)
        result = json.loads(Booking_Detail_resp.text)["result"]





        # 补充订舱单发货信息
        repairshipping_payload = {
            "id": bookingid,
            "locationType": 2,
            "isFnSku": False,
            "isFilled": False,
            "eta": self.formatted_date_eta,
            "isLCL": "false",
            "cargoReadyDay": self.formatted_date,
            "code": result["code"],
            "containerId": 4,
            "warehouseName": "恒丰仓库",
            "attachments": [],
            "remark": "",
            "overseaItems": [
                {
                    "id": 0,
                    "bookingBillItemId": result["items"][0]["id"],
                    "allocateQuantity": 18,
                    "allocatePackageQuantity": 3,
                    "shippingShopId": shopId,
                    "shippingOperateDivisionId": operateDivisionId,
                    "locationWarehouseId": targetWarehouseId,
                    "packageSticker": "",
                    "productSticker": skuDetailDimensionDetails[0]["skuCode"]
                },
                {
                    "id": 0,
                    "bookingBillItemId": result["items"][1]["id"],
                    "allocateQuantity": 24,
                    "allocatePackageQuantity": 4,
                    "shippingShopId": shopId,
                    "shippingOperateDivisionId": operateDivisionId,
                    "locationWarehouseId": targetWarehouseId,
                    "packageSticker": "",
                    "productSticker": skuDetailDimensionDetails[1]["skuCode"]
                },
                {
                    "id": 0,
                    "bookingBillItemId": result["items"][2]["id"],
                    "allocateQuantity": 30,
                    "allocatePackageQuantity": 5,
                    "shippingShopId": shopId,
                    "shippingOperateDivisionId": operateDivisionId,
                    "locationWarehouseId": targetWarehouseId,
                    "packageSticker": "",
                    "productSticker": skuDetailDimensionDetails[2]["skuCode"]
                },
                {
                    "id": 0,
                    "bookingBillItemId": result["items"][3]["id"],
                    "allocateQuantity": 36,
                    "allocatePackageQuantity": 6,
                    "shippingShopId": shopId,
                    "shippingOperateDivisionId": operateDivisionId,
                    "locationWarehouseId": targetWarehouseId,
                    "packageSticker": "",
                    "productSticker": skuDetailDimensionDetails[3]["skuCode"]
                }
            ],
            "fbaItems": []
        }

        Booking().repairshipping_booking(cookies, repairshipping_payload)

        # 审核单据
        reviewshipping_payload = {
            "id": bookingid,
            "isOld": False
        }
        Booking().reviewshipping_booking(cookies, reviewshipping_payload)

        return bookingid


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    Booking().create_booking_link(cookies, 161, 15, 5, 303, 11,"A5-181")
