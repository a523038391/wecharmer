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

    def repairshipping_booking(self, cookies, payload):
        """
        补充发货信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/repairshipping"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("提交resp-----------\n" + resp.text)
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

    def get_bysupplier(self, cookies,bookingid):
        """
        获取订舱单分页根据供应商
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/page/bysupplier?bookingBillId={bookingid}"
        resp = requests.get(url=url, headers=cookies)
        print("获取订舱单分页根据供应商resp-----------\n" + resp.text)
        return resp



    def create_booking_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, targetWarehouseId):
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
                                                                    purchaserId)

        time.sleep(2)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder().get_purchaseorder_details(cookies, purchaseOrderId)
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

        # 创建订舱单
        booking_payload = {
            "code": "",
            "cargoReadyDay": self.formatted_date,
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
                    "purchaseOrderId": purchaseOrderId,
                    "purchaseOrderCode": skuDetailDimensionDetails[0]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 1138,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-145",
                    "productName": "常山仓蜡笔小新A5-145",
                    "skuCode": "A5-145-A-F",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1721974476180_64754b06_24072600405.png",
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
                    "applyPurchaseBillId": 4002,
                    "bhApplyPurchaseBillId": None,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-08-27T03:02:35.550442+00:00",
                    "skuId": 6355,
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
                            "id": 11527,
                            "skuId": 6355,
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
                        },
                        {
                            "id": 11655,
                            "skuId": 6355,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 44,
                            "default": False,
                            "link": None,
                            "ctnLongX": 44,
                            "ctnLongY": 44,
                            "ctnLongZ": 44,
                            "ctnQuantity": 44,
                            "ctnNetWeight": 44,
                            "ctnGrossWeight": 44,
                            "ctnVolume": 0.085184
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 3,
                    "grossWeight": 6,
                    "productWeight": "108.00",
                    "ctnGrossWeightAll": "18.00",
                    "ctnLongXYZ": "0.0006"
                },
                {
                    "id": skuDetailDimensionDetails[1]["id"],
                    "purchaseOrderId": purchaseOrderId,
                    "purchaseOrderCode": skuDetailDimensionDetails[0]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 1138,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-145",
                    "productName": "常山仓蜡笔小新A5-145",
                    "skuCode": "A5-145-A-L",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1721974476180_64754b06_24072600405.png",
                    "thirdImageUrl": None,
                    "useImageSource": 2,
                    "skuName": "常山仓蜡笔小新-黄色-P",
                    "tranSku": None,
                    "taxRate": 0.04,
                    "maxQuantity": 212,
                    "putOnQuantity": 0,
                    "inventoryAvailableQuantity": 0,
                    "bookingQuantity": 24,
                    "exchangeRate": 1,
                    "companyCurrencyType": "CNY",
                    "purchaseOrderDetailDimension": 1,
                    "applyPurchaseBillId": 4002,
                    "bhApplyPurchaseBillId": None,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-08-27T03:02:35.550444+00:00",
                    "skuId": 6356,
                    "quantity": 200,
                    "suite": 6,
                    "overflowRate": 0.06,
                    "unitPrice": 6,
                    "remark": None,
                    "expectedArrivalTime": None,
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
                            "id": 11528,
                            "skuId": 6356,
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
                        },
                        {
                            "id": 11654,
                            "skuId": 6356,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 44,
                            "default": False,
                            "link": None,
                            "ctnLongX": 44,
                            "ctnLongY": 44,
                            "ctnLongZ": 44,
                            "ctnQuantity": 44,
                            "ctnNetWeight": 44,
                            "ctnGrossWeight": 44,
                            "ctnVolume": 0.085184
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 4,
                    "grossWeight": 6,
                    "productWeight": "144.00",
                    "ctnGrossWeightAll": "24.00",
                    "ctnLongXYZ": "0.0008"
                },
                {
                    "id": skuDetailDimensionDetails[2]["id"],
                    "purchaseOrderId": purchaseOrderId,
                    "purchaseOrderCode": skuDetailDimensionDetails[0]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 1138,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-145",
                    "productName": "常山仓蜡笔小新A5-145",
                    "skuCode": "A5-145-B-F",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1721974479008_8f508747_24072600406.jpg",
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
                    "applyPurchaseBillId": 4002,
                    "bhApplyPurchaseBillId": None,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-08-27T03:02:35.550445+00:00",
                    "skuId": 6357,
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
                            "id": 11529,
                            "skuId": 6357,
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
                        },
                        {
                            "id": 11658,
                            "skuId": 6357,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 44,
                            "default": False,
                            "link": None,
                            "ctnLongX": 44,
                            "ctnLongY": 44,
                            "ctnLongZ": 44,
                            "ctnQuantity": 44,
                            "ctnNetWeight": 44,
                            "ctnGrossWeight": 44,
                            "ctnVolume": 0.085184
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 5,
                    "grossWeight": 6,
                    "productWeight": "180.00",
                    "ctnGrossWeightAll": "30.00",
                    "ctnLongXYZ": "0.0010"
                },
                {
                    "id": skuDetailDimensionDetails[3]["id"],
                    "purchaseOrderId": purchaseOrderId,
                    "purchaseOrderCode": skuDetailDimensionDetails[0]["purchaseOrderCode"],
                    "productCategoryId": 210,
                    "productId": 1138,
                    "productCategoryFullName": "摇摇椅>红色摇摇椅",
                    "productCode": "A5-145",
                    "productName": "常山仓蜡笔小新A5-145",
                    "skuCode": "A5-145-B-L",
                    "oldSkuCode": "",
                    "skuImageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1721974479008_8f508747_24072600406.jpg",
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
                    "applyPurchaseBillId": 4002,
                    "bhApplyPurchaseBillId": None,
                    "stockInQuantity": 0,
                    "retrunedQuantity": 0,
                    "supplierStockInQuantity": 0,
                    "cyPurchasedQuantity": 0,
                    "lastCYPurchaseQuantity": 0,
                    "link": "",
                    "createdBy": 303,
                    "createdByName": "李朋",
                    "createdTime": "2024-08-27T03:02:35.550445+00:00",
                    "skuId": 6358,
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
                            "id": 11530,
                            "skuId": 6358,
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
                        },
                        {
                            "id": 11657,
                            "skuId": 6358,
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "supplierName": "供应商名",
                            "currency": "CNY",
                            "price": 44,
                            "default": False,
                            "link": None,
                            "ctnLongX": 44,
                            "ctnLongY": 44,
                            "ctnLongZ": 44,
                            "ctnQuantity": 44,
                            "ctnNetWeight": 44,
                            "ctnGrossWeight": 44,
                            "ctnVolume": 0.085184
                        }
                    ],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 6,
                    "ctnLongX": 6,
                    "ctnLongY": 6,
                    "ctnLongZ": 6,
                    "ctnVolume": 0.0002,
                    "packageQuantity": 6,
                    "grossWeight": 6,
                    "productWeight": "216.00",
                    "ctnGrossWeightAll": "36.00",
                    "ctnLongXYZ": "0.0012"
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
                    "productSticker": "A5-145-A-F"
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
                    "productSticker": "A5-145-A-L"
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
                    "productSticker": "A5-145-B-F"
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
                    "productSticker": "A5-145-B-L"
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
        Booking().reviewshipping_booking(cookies,reviewshipping_payload )

        return bookingid


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    Booking().create_booking_link(cookies, 161, 15, 5, 303, 11)
