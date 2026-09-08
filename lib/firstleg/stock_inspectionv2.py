# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/5/27 上午11:22
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stock_inspectionv2.py
# @Project : wecharmer


import json
import math
import time
from datetime import datetime, timedelta

import requests

from conf.baseconfig import waveecharmer_Host
from interface.firstleg.inspection_api import Inspection_Api
from interface.purchase.purchaseorder_api import PurchaseOrder_Api
from interface.supplier.supplier_api import Supplier_Api
from interface.taskgroup.task_api import Task_Api
from lib.login import Login
from lib.productandmaterial.product import Product
from lib.purchase.purchaseorder import PurchaseOrder
from lib.supplier.supplier import Supplier
from lib.supplier.supplier_v2 import Supplierv2


class Inspectionv2:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")

    def inspection_purchaseorder_report(self, cookies, shopId, shopAccount, warehouseId, operateDivisionId, operaterId,operaterName,
                                        purchaserId,
                                        product_code, salesPlanDate, expectedShelfDate, supplierId, companyId):
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
        supplierstockin_data = Supplierv2().supplierstockinv2_link(cookies, shopId, shopAccount, warehouseId,
                                                                   operateDivisionId, operaterId,operaterName, purchaserId,
                                                                   product_code, salesPlanDate, expectedShelfDate,
                                                                   supplierId, companyId)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder_Api().get_purchaseorderv1_details(cookies, supplierstockin_data[
            "purchaseOrderId"])
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

        # 获取供应商库存
        supplierinventoryv1_payload = {
            "purchaseOrderIds": [
                supplierstockin_data[
                    "purchaseOrderId"]
            ],
            "pageSize": 9999,
            "supplierInventoryWarehouse": 1,
            "znd": 1779851864808
        }

        page_supplierinventoryv1_resp=Supplier_Api().page_supplierinventoryv1(cookies,supplierinventoryv1_payload)
        page_supplierinventoryv1_result=json.loads(page_supplierinventoryv1_resp.text)["result"]

        items = []
        for item in page_supplierinventoryv1_result["items"]:
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
            print(item["skuId"])
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
            "sourceBillCategory": 200,
            "isCheckSku": False,
            "items": items
        }

        inspection_resp = Inspection_Api().create_inspection(cookies, inspection_payload)
        inspectionid = json.loads(inspection_resp.text)["result"]

        # 提交验货申请
        Inspection_Api().inspection_submit(cookies, inspectionid)

        # 指派验货员
        Inspection_Api().inspection_assign(cookies, inspectionid, purchaserId)

        # 查询验货单列表
        url = f"{waveecharmer_Host}/api/inspection/require/page?status=1,2,3,5,6&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&purchaseOrderCode={supplierstockin_data["purchaseOrderCode"]}&pageIndex=1&pageSize=10"
        print(url)

        inspection_list_resp = Inspection_Api().get_inspection_list(cookies, url)
        inspection_list_result = json.loads(inspection_list_resp.text)["result"]

        # 查询验货申请单详情
        inspection_items_resp = Inspection_Api().get_inspection_items(cookies, inspectionid)
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

        inspection_report_resp = Inspection_Api().create_inspection_report(cookies, inspection_report_payload)
        inspection_report_id = json.loads(inspection_report_resp.text)["result"]

        # 送审
        Inspection_Api().inspection_askapprove(cookies, inspection_report_id)

        inspection_data = {"purchaseorderid": supplierstockin_data["purchaseOrderId"]}
        time.sleep(70)

        #采购单更新交货数量
        purchaseorderv1_payload = {}
        PurchaseOrder_Api().purchaseorderv1_quantity(cookies,purchaseorderv1_payload)
        time.sleep(2)

        #生成库存池

        waitapplycontainer_payload={}
        Task_Api().create_waitapplycontainer(cookies,waitapplycontainer_payload)
        time.sleep(2)
        #执行排柜规则

        execution__payload={}
        Task_Api().out_execution(cookies,execution__payload)
        return inspection_data



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    Inspectionv2().inspection_purchaseorder_report(cookies, 162,"LIPENG_US", 129, 5, 303,"李朋", 303, "A5-181", "2026-08", "2026-12-30", 113,
                                                  2)

    #578
    #629
