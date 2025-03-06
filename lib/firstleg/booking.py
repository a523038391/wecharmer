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
from lib.firstleg.shipmentbill import ShipmentBill
from lib.firstleg.stock_inspection import Inspection
from lib.login import Login
from datetime import datetime, timedelta

from lib.productandmaterial.product import Product
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

    def create_from_fba_booking(self, cookies, payload):
        """
        创建订舱单-来源预定舱
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/byprepare"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建订舱单-来源预定舱resp-----------\n" + resp.text)
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

    def get_booking_details(self, cookies, bookingid):
        """
        获取订舱单详情
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/details?ids={bookingid}"
        resp = requests.get(url=url, headers=cookies)
        print("获取订舱单详情resp-----------\n" + resp.text)
        return resp

    def page_booking(self, cookies, bookingcode):
        """
        获取订舱单列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/page?status=3,4,8&isLoadingAdviceBillCode=false&isEmptyBookingContainerCode=true&sorts=%7B%22field%22:%22containerNo%22,%22order%22:%22desc%22%7D,%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&code={bookingcode}&pageIndex=1&pageSize=10"
        resp = requests.get(url=url, headers=cookies)
        print("获取订舱单列表resp-----------\n" + resp.text)
        return resp

    def get_booking_allocatefba(self, cookies, bookingid, fbaShipmentCode):
        """
        分配计算FBA
        :return:
        """
        url = f"{waveecharmer_Host}/api/booking/allocatefba/{bookingid}?fbaCodes=%22{fbaShipmentCode}%22"
        resp = requests.get(url=url, headers=cookies)
        print("分配计算FBAresp-----------\n" + resp.text)
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

    def create_fba_booking_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                purchasername, product_code, fbaShipmentCode):
        """
        创建预订舱链路
        :param isLCL:是否拼柜
        :param cargoReadyDay:货号日期
        :param containerId:货柜id
        :param purchaseOrderId:采购单id
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :param purchaseBusinessType:备货 出运 常规
        :param locationType :  目的仓类型
        :return:
        """

        # 创建出运采购单返回id
        purchaseOrderIds = PurchaseOrder().create_shipment_purchaseorder_link(cookies, shopId, warehouseId,
                                                                             operateDivisionId, purchaserId,
                                                                             purchasername, product_code)

        time.sleep(2)
        fba_bookingids = []
        for purchaseOrderId in purchaseOrderIds:


            # 获取采购单明细
            purchaseOrderDetailId_resp = PurchaseOrder().get_purchaseorder_details(cookies, purchaseOrderId)
            skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

            # 根据id获取sku明细

            items = []
            bookingQuantity = 100
            for skuDetail in skuDetailDimensionDetails:
                # 根据id获取sku明细
                query_sku_byids_resp = Product().query_sku_byids(cookies, skuDetail["skuId"])
                result = json.loads(query_sku_byids_resp.text)["result"][0]["suppliers"][0]
                result["isChoose"] = True

                skuDetail["bookingQuantity"] = bookingQuantity
                items_dict = {
                    "cpuQuantity": bookingQuantity * 1.05,
                    "operateDivisionName": "运营青蛙椅事业部",
                    "warehouseId": warehouseId,
                    "purchaseOrderDetailId": skuDetail["id"],
                    "allowBooking": True,
                    "shopAccount": "LIPENG",
                    "warehouseName": "恒丰仓库",
                    "supplierName": "供应商名",
                    "supplierId": 6,
                    "isAllowNegative": True,
                    "supplierList": [result],
                    "ctnGrossWeight": 6,
                    "ctnNetWeight": 6,
                    "ctnQuantity": 5,
                    "ctnLongX": 7,
                    "ctnLongY": 7,
                    "ctnLongZ": 7,
                    "ctnVolume": 0.0003,
                    "packageQuantity": bookingQuantity / 5,
                    "grossWeight": 6,
                    "productWeight": "600.00",
                    "ctnGrossWeightAll": "120.00",
                    "ctnLongXYZ": "0.0060"
                }

                skuDetail.update(items_dict)
                print(skuDetail)
                items.append(skuDetail)
                bookingQuantity += 100

            print(items)

            # 创建订舱单
            booking_payload = {
                "code": "",
                "cargoReadyDay": self.formatted_date,
                "isLCL": None,
                "containerId": None,
                "volume": None,
                "loadWeight": None,
                "warehouseName": "恒丰仓库",
                "attachments": [],
                "remark": "",
                "isPrepare": True,
                "items": items
            }

            booking_resp = Booking().create_booking(cookies, booking_payload)
            fba_bookingid = json.loads(booking_resp.text)["result"]
            print(fba_bookingid)

            # 提交订舱单
            Booking().booking_submit(fba_bookingid, cookies)

            # 分配计算FBA
            booking_allocatefba_resp = Booking().get_booking_allocatefba(cookies, fba_bookingid, fbaShipmentCode)
            booking_allocatefba_result = json.loads(booking_allocatefba_resp.text)["result"]
            fnSkuAndSkus = []
            for item in booking_allocatefba_result[0]["items"]:
                fnSkuAndSku_dict = {
                    "fnSku": item["fnSku"],
                    "skuId": item["skuId"]
                }
                fnSkuAndSkus.append(fnSkuAndSku_dict)

            # 根据FnSku和Sku获取货件明细
            fnsku_sk_payload = {
                "fnSkuAndSkus": fnSkuAndSkus
            }
            fnsku_sku_resp = ShipmentBill().fnsku_sku_shipmentbill(cookies, booking_allocatefba_result[0]["id"],
                                                                   fnsku_sk_payload)
            fnsku_sku_result = json.loads(fnsku_sku_resp.text)["result"]

            # 补充发货信息
            fbaItems = []
            for item, fnsku in zip(booking_allocatefba_result[0]["items"], fnsku_sku_result):
                fbaItem_dict = {
                    "fbaShipmentItemId": fnsku["id"],
                    "bookingBillItemId": item["bookingBillItemId"],
                    "allocateQuantity": item['bookingQuantity']
                }
                fbaItems.append(fbaItem_dict)
            repairshipping_payload = {
                "id": fba_bookingid,
                "locationType": 1,
                "isFnSku": True,
                "isFilled": False,
                "eta": self.formatted_date_eta,
                "sendOutGoodsType": None,
                "isLCL": "false",
                "containerId": None,
                "warehouseName": "恒丰仓库",
                "attachments": [],
                "remark": "",
                "overseaItems": [],
                "fbaItems": [
                    {
                        "bookItems": fbaItems,
                        "productStickerAttachments": [
                            {
                                "name": "货件4_加水印.pdf",
                                "url": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1730788219978_def86e39_24110528754.pdf",

                            }
                        ],
                        "packageStickerAttachments": [
                            {
                                "name": "货件4_加水印.pdf",
                                "url": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1730788219978_def86e39_24110528754.pdf",

                            }
                        ],
                        "fbaId": booking_allocatefba_result[0]["id"]
                    }
                ]
            }

            Booking().repairshipping_booking(cookies, repairshipping_payload)

            # 审核单据
            reviewshipping_payload = {
                "id": fba_bookingid,
                "isOld": False
            }
            Booking().reviewshipping_booking(cookies, reviewshipping_payload)

            fba_bookingids.append(fba_bookingid)

        return fba_bookingids

    def create_booking_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, targetWarehouseId,
                            product_code):
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
        #purchaseOrderId = PurchaseOrder().create_purchaseorder_link(cookies, shopId, warehouseId, operateDivisionId,
        #                                                            purchaserId, product_code)

        inspection_data=Inspection().inspection_purchaseorder_report(cookies, shopId, warehouseId, operateDivisionId,
                                        purchaserId, product_code)

        time.sleep(2)
        #Inspection()
        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder().get_purchaseorder_details(cookies, inspection_data["purchaseorderid"])
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

        # 根据id获取sku明细

        items = []
        bookingQuantity = 100
        for skuDetail in skuDetailDimensionDetails:
            # 根据id获取sku明细
            query_sku_byids_resp = Product().query_sku_byids(cookies, skuDetail["skuId"])
            result = json.loads(query_sku_byids_resp.text)["result"][0]["suppliers"][0]
            result["isChoose"] = True

            skuDetail["bookingQuantity"] = bookingQuantity
            items_dict = {
                "cpuQuantity": bookingQuantity * 1.05,
                "operateDivisionName": "运营青蛙椅事业部",
                "warehouseId": warehouseId,
                "purchaseOrderDetailId": skuDetail["id"],
                "allowBooking": True,
                "shopAccount": "LIPENG",
                "warehouseName": "恒丰仓库",
                "supplierName": "供应商名",
                "supplierId": 6,
                "isAllowNegative": True,
                "supplierList": [result],
                "ctnGrossWeight": 6,
                "ctnNetWeight": 6,
                "ctnQuantity": 5,
                "ctnLongX": 7,
                "ctnLongY": 7,
                "ctnLongZ": 7,
                "ctnVolume": 0.0003,
                "packageQuantity": bookingQuantity / 5,
                "grossWeight": 6,
                "productWeight": "600.00",
                "ctnGrossWeightAll": "120.00",
                "ctnLongXYZ": "0.0060"
            }

            skuDetail.update(items_dict)
            print(skuDetail)
            items.append(skuDetail)
            bookingQuantity += 100

        print(items)

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
            "items": items
        }

        booking_resp = Booking().create_booking(cookies, booking_payload)
        bookingid = json.loads(booking_resp.text)["result"]
        print(bookingid)

        # 提交订舱单
        Booking().booking_submit(bookingid, cookies)

        # 获取订舱单
        Booking_Detail_resp = Booking().get_booking(cookies, bookingid)
        result = json.loads(Booking_Detail_resp.text)["result"]
        overseaItems = []
        for overseaItem in result["items"]:
            overseaItem_dict = {
                "id": 0,
                "bookingBillItemId": overseaItem["id"],
                "allocateQuantity": overseaItem["quantity"],
                "allocatePackageQuantity": overseaItem["quantity"] / overseaItem["ctnQuantity"],
                "shippingShopId": shopId,
                "shippingOperateDivisionId": operateDivisionId,
                "locationWarehouseId": targetWarehouseId,
                "packageSticker": "",
                "productSticker": overseaItem["skuCode"]
            }
            overseaItems.append(overseaItem_dict)

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
            "overseaItems": overseaItems,
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

    def create_booking_from_fba_link(self,cookies,bookingid):
        """
        创建订舱单链路-来源预定舱
        :param isLCL:是否拼柜
        :param cargoReadyDay:货号日期
        :param containerId:货柜id
        :param purchaseOrderId:采购单id
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """

        #获取预定舱详情
        get_detail_resp=Booking().get_booking_details(cookies,bookingid)
        get_detail_result=json.loads(get_detail_resp.text)["result"]

        items=[]
        for item,fbaAllocateItem in zip(get_detail_result[0]["items"],get_detail_result[0]["fbaAllocateItems"]):
            item_dict={
                    "sourceBookingBillId": item["bookingBillId"],
                    "sourceBookingBillItemId": item["id"],
                    "sourceFBAAllocateItemId": fbaAllocateItem["id"],
                    "sourceQuantity": item["surplusAllocateQuantity"],
                    "sourcePackageQuantity": item["surplusAllocatePackageQuantity"]
                }
            items.append(item_dict)


        #创建订舱单-来源预定舱
        byprepare_payload = {
            "containerId": 4,
            "isLCL": False,
            "remark": None,
            "cargoReadyDay": self.formatted_date_eta,
            "attachments": [],
            "updateItems": [],
            "items": items
        }

        from_fba_booking_resp=Booking().create_from_fba_booking(cookies,byprepare_payload)
        bookingid_from_fba=json.loads(from_fba_booking_resp.text)["result"]
        # 提交订舱单
        Booking().booking_submit(bookingid_from_fba, cookies)

        # 审核单据
        reviewshipping_payload = {
            "id": bookingid_from_fba
        }
        Booking().reviewshipping_booking(cookies, reviewshipping_payload)

        return bookingid_from_fba







if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # 创建订舱单
    Booking().create_booking_link(cookies, 161, 15, 5, 303, 180, "A5-181")

    # 创建预定舱
    #Booking().create_fba_booking_link(cookies, 161, 15, 5, 303, "李朋", "A5-181", "FBA16M9J26TK")
