# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/8/27 下午4:36
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : inspection.py
# @Project : wecharmer
import json
import math
import time
from datetime import datetime, timedelta

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
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

    def inspection_purchaseorder_report(self, cookies, shopId, warehouseId, operateDivisionId,
                                        purchaserId, product_code,supplierId,companyId):
        """
        备货验货-创建验货申请报告链路
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

        # 创建采购单工厂入库
        supplierstockin_data = Supplier().supplierstockin_link(cookies, shopId, warehouseId, operateDivisionId,
                                                               purchaserId, product_code,supplierId,companyId)

        # 获取某个采购单的所有明细，根据采购单ds(头程订舱用)
        purchaseorder_details = PurchaseOrder().get_purchaseorder_details(cookies,
                                                                          supplierstockin_data["purchaseOrderId"])

        # 获取供应商库存分页列表
        supplierinventory_page_resp = Supplier().get_supplierinventory_page(cookies,
                                                                            supplierstockin_data["purchaseOrderId"], 1)
        supplierinventory_page_result = json.loads(supplierinventory_page_resp.text)["result"]

        items = []

        for item in supplierinventory_page_result["items"]:
            # 查询产品对外关系分页
            sellersku_payload = {
                "shopIds": [
                    shopId
                ],
                "skuCodes": [
                    item["skuCode"]
                ],
                "isMatch": True,
                "pageSize": 100,
                "pageIndex": 1,
                "isEmptyFnSku": False,
                "operateDivisionId": operateDivisionId
            }

            sellersku_resp = Product().sellersku_page(cookies, sellersku_payload)
            sellersku_result = json.loads(sellersku_resp.text)["result"]
            query_sku_resp=Product().query_sku_byids(cookies,item["skuId"])
            query_sku_result=json.loads(query_sku_resp.text)["result"][0]


            if sellersku_result["items"] == [] :
                supplierinventory_dict = {
                    "purchaseOrderId": item["purchaseOrderId"],
                    "skuId": item["skuId"],
                    "requireQuantity": item["inventoryQuantity"],
                    "productSticker":None,
                    "ctnQuantity": query_sku_result["suppliers"][0]["ctnQuantity"],
                    "packageQuantity": math.floor(
                        item["inventoryQuantity"] / query_sku_result["suppliers"][0]["ctnQuantity"]),
                    "warehouseId": warehouseId,
                    "ctnLongX": query_sku_result["suppliers"][0]["ctnLongX"],
                    "ctnLongY": query_sku_result["suppliers"][0]["ctnLongY"],
                    "ctnLongZ": query_sku_result["suppliers"][0]["ctnLongZ"],
                    "ctnVolume": query_sku_result["suppliers"][0]["ctnVolume"],
                    "ctnGrossWeight": query_sku_result["suppliers"][0]["ctnGrossWeight"],
                    "ctnNetWeight": query_sku_result["suppliers"][0]["ctnNetWeight"],
                    "supplierId": query_sku_result["suppliers"][0]["supplierId"],
                    "supplierName": query_sku_result["suppliers"][0]["supplierName"]
                }
            else:

                supplierinventory_dict = {
                    "purchaseOrderId": item["purchaseOrderId"],
                    "skuId": item["skuId"],
                    "skuCode": item["skuCode"],
                    "requireQuantity": item["inventoryQuantity"],
                    "productSticker": sellersku_result["items"][0]["fnSku"],
                     "ctnQuantity": query_sku_result["suppliers"][0]["ctnQuantity"],
                    "packageQuantity": math.floor(item["inventoryQuantity"]/query_sku_result["suppliers"][0]["ctnQuantity"]),
                    "warehouseId": warehouseId,
                    "ctnLongX": query_sku_result["suppliers"][0]["ctnLongX"],
                    "ctnLongY": query_sku_result["suppliers"][0]["ctnLongY"],
                    "ctnLongZ": query_sku_result["suppliers"][0]["ctnLongZ"],
                    "ctnVolume": query_sku_result["suppliers"][0]["ctnVolume"],
                    "ctnGrossWeight": query_sku_result["suppliers"][0]["ctnGrossWeight"],
                    "ctnNetWeight": query_sku_result["suppliers"][0]["ctnNetWeight"],
                    "supplierId": query_sku_result["suppliers"][0]["supplierId"],
                    "supplierName": query_sku_result["suppliers"][0]["supplierName"]
                }

            items.append(supplierinventory_dict)

        inspection_payload = {
            "code": "",
            "name": "",
            "requireType": 4,
            "bookingBillId": None,
            "requireDate": self.formatted_date,
            "supplierId": supplierstockin_data["supplierId"],
            "remark": "",
            "bookingBillCode": "",
            "attachments": [],
            "sourceBillCategory": 507,
            "isCheckSku": False,
            "items": items
        }

        inspection_resp = Inspection().create_inspection(cookies, inspection_payload)
        inspectionid = json.loads(inspection_resp.text)["result"]

        # 提交验货申请
        Inspection().inspection_submit(cookies, inspectionid)

        # 指派验货员
        Inspection().inspection_assign(cookies, inspectionid, 303)

        # 查询验货单列表
        url = f"{waveecharmer_Host}/api/inspection/require/page?status=1,2,3,5,6&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&purchaseOrderCode={supplierstockin_data["purchaseOrderCode"]}&pageIndex=1&pageSize=10"
        print(url)

        inspection_list_resp = Inspection().get_inspection_list(cookies, url)
        inspection_list_result = json.loads(inspection_list_resp.text)["result"]

        # 查询验货申请单详情
        inspection_items_resp = Inspection().get_inspection_items(cookies, inspectionid)
        inspection_items_result = json.loads(inspection_items_resp.text)["result"]

        # 创建验货报告
        requireItemIdObj = {}
        goodItemInputs = []

        for item in inspection_items_result:
            requireItemIdObj[f"{item['purchaseOrderCode']}-{item['skuCode']}"] = item["id"]
            goodItemInputs_dict = {
                "purchaseOrderId": item["purchaseOrderId"],
                "skuId": item["skuId"],
                "goodQuantity": item["requireQuantity"],
                "repairedQuantity": 0,
                "defReturnQuantity": None,
                "inspectionRequireItemId": item["id"]
            }

            goodItemInputs.append(goodItemInputs_dict)

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
            "goodItemInputs": goodItemInputs
        }

        inspection_report_resp = Inspection().create_inspection_report(cookies, inspection_report_payload)
        inspection_report_id = json.loads(inspection_report_resp.text)["result"]

        # 送审
        Inspection().inspection_askapprove(cookies, inspection_report_id)

        inspection_data = {"purchaseorderid": supplierstockin_data["purchaseOrderId"]}
        time.sleep(2)

        return inspection_data


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    # 备货验货
    Inspection().inspection_purchaseorder_report(cookies, 161, 15, 2, 303, "A5-181",112,2)



