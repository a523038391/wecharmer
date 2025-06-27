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
from lib.container.arrangecontainerbill import ArrangeContainerBill
from lib.firstleg.booking import Booking
from lib.login import Login
from datetime import datetime, timedelta

from lib.productandmaterial.product import Product
from lib.purchase.purchaseorder import PurchaseOrder
from lib.supplier.supplier import Supplier


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

    def get_inspection_list(self, cookies, url):
        """
        查询验货单列表
        :return:
        """
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



    def inspection_report(self, cookies, bookingid, purchaserId):
        """
        尾期验货-创建验货申请报告链路
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

        # 获取订舱单明细
        Booking_Detail_resp = Booking().get_booking(cookies, bookingid)
        Booking_Detail_result = json.loads(Booking_Detail_resp.text)["result"]
        bookingcode = Booking_Detail_result["code"]

        # 获取订舱单分页根据供应商
        bysupplier_resp = Booking().get_bysupplier(cookies, bookingid)
        bysupplier_result = json.loads(bysupplier_resp.text)["result"]

        # 创建验货申请
        items = []
        for Detail in Booking_Detail_result["items"]:
            item_dict = {
                "purchaseOrderId": Detail["purchaseOrderId"],
                "skuId": Detail["skuId"]
            }
            items.append(item_dict)

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
            "sourceBillCategory": 507,
            "items": items
        }

        inspection_resp = Inspection().create_inspection(cookies, inspection_payload)
        inspectionid = json.loads(inspection_resp.text)["result"]

        # 提交验货申请
        Inspection().inspection_submit(cookies, inspectionid)

        # 指派验货员
        Inspection().inspection_assign(cookies, inspectionid, purchaserId)

        # 查询验货申请单详情
        inspection_items_resp = Inspection().get_inspection_items(cookies, inspectionid)
        inspection_items_result = json.loads(inspection_items_resp.text)["result"]

        # 查询验货单列表
        url = f"{waveecharmer_Host}/api/inspection/require/page?status=2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&bookingBillCode={bookingcode}&pageIndex=1&pageSize=10"
        print(url)
        inspection_list_resp = Inspection().get_inspection_list(cookies, url)
        inspection_list_result = json.loads(inspection_list_resp.text)["result"]
        # 查询订舱单详情
        get_booking_resp = Booking().get_booking(cookies, bookingid)
        get_booking_result = json.loads(get_booking_resp.text)["result"]

        # 创建验货报告
        requireItemIdObj = {}
        packagedStockItems = []
        boxSizeItems = []
        for item, booking in zip(inspection_items_result, get_booking_result["items"]):
            requireItemIdObj[f"{item['purchaseOrderCode']}-{item['skuCode']}"] = item["id"]
            packagedStockItem_dict = {
                "purchaseOrderId": item["purchaseOrderId"],
                "skuId": item["skuId"],
                "packagedQuantity": item["requireQuantity"]
            }

            boxSizeItem_dict = {
                "requireItemId": item["id"],
                "ctnLongX": booking["ctnLongX"],
                "ctnLongY": booking["ctnLongY"],
                "ctnLongZ": booking["ctnLongZ"],
                "ctnVolume": booking["ctnVolume"],
                "ctnNetWeight": booking["ctnNetWeight"],
                "totalCtnVolume": booking["totalCtnVolume"],
                "ctnGrossWeight": booking["ctnGrossWeight"],
                "totalCtnGrossWeight": booking["totalCtnGrossWeight"],
                "totalGrossWeight": booking["totalGrossWeight"]
            }
            packagedStockItems.append(packagedStockItem_dict)
            boxSizeItems.append(boxSizeItem_dict)

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
            "requireItemIdObj": requireItemIdObj,
            "item": {
                "inspectionWay": 1,
                "qualifiedQuantity": None,
                "defectQuantity": None
            },
            "packagedStockItems": packagedStockItems,
            "boxSizeItems": boxSizeItems
        }
        inspection_report_resp = Inspection().create_inspection_report(cookies, inspection_report_payload)
        inspection_report_id = json.loads(inspection_report_resp.text)["result"]

        # 送审
        Inspection().inspection_askapprove(cookies, inspection_report_id)

        booking_data = {"bookingid": bookingid, "bookingcode": bookingcode}
        time.sleep(15)

        return booking_data

    def create_inspection_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, targetWarehouseId,
                               product_code):

        # 创建订舱通知返回id
        bookingid = Booking().create_booking_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                                  targetWarehouseId, product_code)

        # 生成验货报告

        booking_data = Inspection().inspection_report(cookies, bookingid, purchaserId)

        return booking_data

    def create_fba_inspection_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                   purchasername, product_code, fbaShipmentCode):

        # 创建预定舱返回id

        bookingids = Booking().create_fba_booking_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                                       purchasername, product_code, fbaShipmentCode)

        # 生成验货吧报告
        booking_data = Inspection().inspection_report(cookies, bookingids[0], purchaserId)

        return booking_data

    def create_fba_inspection_booking_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                           purchasername, product_code, fbaShipmentCode):

        # 预定舱-生成验货报告
        booking_data = Inspection().create_fba_inspection_link(cookies, shopId, warehouseId, operateDivisionId,
                                                               purchaserId,
                                                               purchasername, product_code, fbaShipmentCode)

        # 预定舱-生成订舱通知
        bookingid_from_fba = Booking().create_booking_from_fba_link(cookies, booking_data["bookingid"])

        return bookingid_from_fba

    def create_arrangecontainer_inspection_link(self,cookies,arrangecontainerid,purchaserId):

        # 获取订舱单明细
        alreadycontainer_Detail_resp = ArrangeContainerBill().get_alreadycontainer_items(cookies, arrangecontainerid)
        alreadycontainer_Detail_result = json.loads(alreadycontainer_Detail_resp.text)["result"]

        # 创建验货申请
        items = []
        supplierId=""
        bookingBillCode=""

        for Detail in alreadycontainer_Detail_result:

            if Detail["deliveryWarehouseType"]==5:
                item_dict = {
                    "purchaseOrderId": Detail["purchaseOrderId"],
                    "skuId": Detail["skuId"]
                }
                supplierId=Detail["supplierId"]
                bookingBillCode=Detail["alreadyContainerBillCode"]

                items.append(item_dict)
            else:
                continue

        inspection_payload = {
            "code": "",
            "name": "",
            "requireType": 1,
            "bookingBillId": arrangecontainerid,
            "requireDate": self.formatted_date,
            "supplierId": supplierId,
            "remark": "",
            "bookingBillCode": bookingBillCode,
            "attachments": [],
            "sourceBillCategory": 607,
            "items": items
        }

        inspection_resp = Inspection().create_inspection(cookies, inspection_payload)
        inspectionid = json.loads(inspection_resp.text)["result"]

        # 提交验货申请
        Inspection().inspection_submit(cookies, inspectionid)

        # 指派验货员
        Inspection().inspection_assign(cookies, inspectionid, purchaserId)

        # 查询验货申请单详情
        inspection_items_resp = Inspection().get_inspection_items(cookies, inspectionid)
        inspection_items_result = json.loads(inspection_items_resp.text)["result"]

        # 查询验货单列表
        url = f"{waveecharmer_Host}/api/inspection/require/page?status=2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&bookingBillCode={bookingBillCode}&pageIndex=1&pageSize=10"
        print(url)
        inspection_list_resp = Inspection().get_inspection_list(cookies, url)
        inspection_list_result = json.loads(inspection_list_resp.text)["result"]


        # 创建验货报告
        requireItemIdObj = {}
        packagedStockItems = []
        boxSizeItems = []
        for item, booking in zip(inspection_items_result, alreadycontainer_Detail_result):

            if booking["deliveryWarehouseType"] == 5:
                requireItemIdObj[f"{item['purchaseOrderCode']}-{item['skuCode']}"] = item["id"]
                packagedStockItem_dict = {
                    "purchaseOrderId": item["purchaseOrderId"],
                    "skuId": item["skuId"],
                    "packagedQuantity": item["requireQuantity"]
                }

                boxSizeItem_dict = {
                    "requireItemId": item["id"],
                    "ctnLongX": booking["boxLength"],
                    "ctnLongY": booking["boxWidth"],
                    "ctnLongZ": booking["boxHeight"],
                    "ctnVolume": booking["ctnVolume"],
                    "ctnNetWeight": booking["ctnNetWeight"],
                    "totalCtnVolume": booking["totalVolumeWithBox"],
                    "ctnGrossWeight": booking["ctnGrossWeight"],
                    "totalCtnGrossWeight": booking["totalGrossWithBox"],
                    "totalGrossWeight": booking["totalGrossWithBox"]
                }
                packagedStockItems.append(packagedStockItem_dict)
                boxSizeItems.append(boxSizeItem_dict)


            else:
                continue

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
            "requireItemIdObj": requireItemIdObj,
            "item": {
                "inspectionWay": 1,
                "qualifiedQuantity": None,
                "defectQuantity": None
            },
            "packagedStockItems": packagedStockItems,
            "boxSizeItems": boxSizeItems
        }
        inspection_report_resp = Inspection().create_inspection_report(cookies, inspection_report_payload)
        inspection_report_id = json.loads(inspection_report_resp.text)["result"]

        # 送审
        Inspection().inspection_askapprove(cookies, inspection_report_id)

        time.sleep(15)






if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    # 备货验货
    #Inspection().inspection_purchaseorder_report(cookies, 161, 15, 5, 303, "A5-181")

    # 订舱单尾期验货
    Inspection().create_inspection_link(cookies, 161, 15, 5, 303, 12, "A5-181")
    # 预定舱尾期验货
    # Inspection().create_fba_inspection_link(cookies, 161, 15, 5, 303, "李朋", "A5-181","FBA16M9J26TK")

    # 预定舱生成订舱通知
    # Inspection().create_fba_inspection_booking_link(cookies, 161, 15, 5, 303, "李朋", "A5-181","FBA16M9J26TK")
