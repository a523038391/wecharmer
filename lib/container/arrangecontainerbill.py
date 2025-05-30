# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2025/2/28 下午1:46
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : arrangecontainerbill.py
# @Project : wecharmer

import json
import math
import time
from datetime import datetime, timedelta
import random

import requests

from conf.baseconfig import waveecharmer_Host
from lib.container.waitcontainerbill import WaitContainerBill
from lib.firstleg.stock_inspection import Inspection
from lib.login import Login
from lib.productandmaterial.product import Product
from lib.purchase.purchaseorder import PurchaseOrder
from lib.storage.stock import Stock
from lib.supplier.supplier import Supplier


class ArrangeContainerBill:
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

        self.random_number = ''.join(str(random.randint(0, 9)) for _ in range(10))

    def create_arrangecontainerbill(self, cookies, payload):
        """
        创建已排柜
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建已排柜resp-----------\n" + resp.text)
        return resp

    def create_shipmentorstockupbill_arrangecontainerbill(self, cookies, payload):
        """
        生成备货单
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/createshipmentorstockupbill"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("生成备货单resp-----------\n" + resp.text)
        return resp

    def page_arrangecontainerbill(self, cookies, payload):
        """
        分页查询已排柜单
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("分页查询已排柜单resp-----------\n" + resp.text)
        return resp

    def submit_arrangecontainerbill(self, cookies, payload):
        """
        提交已排柜
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/submit"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("提交已排柜resp-----------\n" + resp.text)
        return resp

    def push_thirdwarehouse_arrangecontainerbill(self, cookies, payload):
        """
        推送三方仓已排柜
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/thirdwarehouse/push"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("推送三方仓已排柜resp-----------\n" + resp.text)
        return resp

    def confirmallocate_arrangecontainerbill(self, cookies, payload):
        """
        海外仓补充货件
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/confirmallocate"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("海外仓补充货件resp-----------\n" + resp.text)
        return resp

    def get_transitwarehousedelivery(self, cookies, id):
        """
        获取中转仓发货管理
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/gettransitwarehousedelivery/{id}"
        resp = requests.get(url=url, headers=cookies)
        print("获取中转仓发货管理resp-----------\n" + resp.text)
        return resp

    def get_alreadycontainer_items(self, cookies, id):
        """
        获取已排柜明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/arrangecontainer/alreadycontainer/items/bybillids?billIds={id}"
        resp = requests.get(url=url, headers=cookies)
        print("获取已排柜明细resp-----------\n" + resp.text)
        return resp






    def create_arrangecontainer_link(self, cookies, shopId, warehouseId, warehouseId_entity, operateDivisionId,
                                     purchaserId,
                                     targetWarehouseId,
                                     product_code, quantity):
        """
        创建已排柜链路-海外仓
        :param containerId:货柜id
        :param targetWarehouseType:仓库类型
        :param transportationTypeId:运输方式
        :param destinationAreaId:发往区域id
        :param isNeedFnSku:是否需要箱贴
        :param warehouseType:仓库类型
        :param overseasWarehouseListingMethod:按箱 按件
        """

        # 创建待排柜-供应商仓

        waitContainerid1 = WaitContainerBill().create_waitContainer_supplier_link(cookies, shopId, warehouseId,
                                                                                  operateDivisionId, purchaserId,
                                                                                  targetWarehouseId,
                                                                                  product_code)

        # 创建待排柜-国内仓
        waitContainerid2 = WaitContainerBill().create_waitContainer_entity_link(cookies, shopId, warehouseId_entity,
                                                                                operateDivisionId, purchaserId,
                                                                                targetWarehouseId,
                                                                                product_code, quantity)

        # 查询待排柜明细

        waitContainer_items_resp1 = WaitContainerBill().get_waitcontainerbill_items(cookies,
                                                                                    waitContainerid1)
        waitContainer_items_result1 = json.loads(waitContainer_items_resp1.text)["result"]
        print(waitContainer_items_result1)

        # 分页查询待排柜
        waitContainer_page_payload1 = {
            "waitContainerBillStatuses": [
                2,
                3
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "isFuzzyQuery": "false",
            "waitContainerBillCodes": [
                waitContainer_items_result1[0][
                    "waitContainerBillCode"]
            ],
            "pageIndex": 1,
            "pageSize": 10
        }
        waitContainer_page_resp1 = WaitContainerBill().get_waitcontainerbill_page(cookies,
                                                                                  waitContainer_page_payload1)

        print("等待----")
        print(waitContainer_page_resp1.text)
        waitContainer_page_result1 = json.loads(waitContainer_page_resp1.text)["result"]["items"][0]

        alreadyContainerBillItems = []
        for item in waitContainer_items_result1:
            items_dict = {
                "cpuQuantity": item["waitContainerQuantity"],
                "waitContainerBillItemId": item["id"],
                "spuCode": item["productCode"],
                "deliveryWarehouseName": waitContainer_page_result1["warehouseName"],
                "deliveryWarehouseId": waitContainer_page_result1["warehouseId"],
                "isFnSku": waitContainer_page_result1["isNeedFnSku"],
                "expectedArrivalDate": waitContainer_page_result1["expectedWarehouseDate"],
                "quantity": item["waitContainerQuantity"]
            }
            items_dict.update(waitContainer_page_result1)
            items_dict.update(item)
            alreadyContainerBillItems.append(items_dict)

        # 查询待排柜明细

        waitContainer_items_resp2 = WaitContainerBill().get_waitcontainerbill_items(cookies,
                                                                                    waitContainerid2)
        waitContainer_items_result2 = json.loads(waitContainer_items_resp2.text)["result"]
        print(waitContainer_items_result2)

        # 分页查询待排柜
        waitContainer_page_payload2 = {
            "waitContainerBillStatuses": [
                2,
                3
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "isFuzzyQuery": "false",
            "waitContainerBillCodes": [
                waitContainer_items_result2[0][
                    "waitContainerBillCode"]
            ],
            "pageIndex": 1,
            "pageSize": 10
        }

        waitContainer_page_resp2 = WaitContainerBill().get_waitcontainerbill_page(cookies, waitContainer_page_payload2
                                                                                  )
        waitContainer_page_result2 = json.loads(waitContainer_page_resp2.text)["result"]["items"][0]

        for item in waitContainer_items_result2:
            items_dict = {
                "createdByName": "李朋",
                "createdTime": "2025-02-28T09:11:04.012161+00:00",
                "skuTypeQuantity": 4,
                "expectedContainerTotalQuantity": 1000,
                "alreadyContainerTotalQuantity": 0,
                "cpuQuantity": item["waitContainerQuantity"],
                "waitContainerBillItemId": item["id"],
                "spuCode": item["productCode"],
                "deliveryWarehouseName": waitContainer_page_result2["warehouseName"],
                "deliveryWarehouseId": waitContainer_page_result2["warehouseId"],
                "isFnSku": waitContainer_page_result2["isNeedFnSku"],
                "expectedArrivalDate": waitContainer_page_result2["expectedWarehouseDate"],
                "quantity": item["waitContainerQuantity"]
            }
            items_dict.update(waitContainer_page_result2)
            items_dict.update(item)
            alreadyContainerBillItems.append(items_dict)

        print(alreadyContainerBillItems)

        # 创建已排柜
        arrangecontainer_payload = {
            "alreadyContainerBillCode": None,
            "containerId": 4,
            "containerName": "40H货柜",
            "volume": 76.047645,
            "loadWeight": 19000,
            "expectedGoodsReadyDate": self.formatted_date,
            "targetWarehouseType": 2,
            "targetWarehouseId": targetWarehouseId,
            "targetWarehouseName": "美西LA01仓",
            "destinationAreaId": 3,
            "destinationAreaName": "欧洲",
            "transportationTypeId": 2,
            "transportationTypeName": "海运",
            "remark": "备注1111",
            "submit": False,
            "alreadyContainerBillItems": alreadyContainerBillItems

        }

        arrangecontainerbill_resp = ArrangeContainerBill().create_arrangecontainerbill(cookies,
                                                                                       arrangecontainer_payload)
        arrangecontainerbill_result = json.loads(arrangecontainerbill_resp.text)["result"]

        # 分页查询已排柜单
        page_payload = {
            "status": [
                1,
                2,
                3,
                4,
                5
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "alreadyContainerBillCodes": [
                arrangecontainerbill_result["alreadyContainerBillCode"]
            ],
            "pageIndex": 1,
            "pageSize": 10
        }

        page_resp = ArrangeContainerBill().page_arrangecontainerbill(cookies, page_payload)
        page_result = json.loads(page_resp.text)["result"]["items"][0]

        # 提交

        submit_payload = {
            "id": page_result["id"],
            "status": 2
        }

        ArrangeContainerBill().submit_arrangecontainerbill(cookies, submit_payload)

        # 推送三方仓

        push_payload = {
            "id": page_result["id"],
            "shipCompanyCode": ""
        }

        push_resp = ArrangeContainerBill().push_thirdwarehouse_arrangecontainerbill(cookies, push_payload)
        push_result = json.loads(push_resp.text)

        if push_result["status"] != 200 and push_result["code"] != "Success":
            # 补充货件
            confirmallocate_payload = {
                "id": page_result["id"],
                "stockInBillCode": "lipeng" + self.random_number
            }
            ArrangeContainerBill().confirmallocate_arrangecontainerbill(cookies, confirmallocate_payload)

        # 获取中转仓发货管理

        gettransitwarehousedelivery_resp = ArrangeContainerBill().get_transitwarehousedelivery(cookies,
                                                                                               page_result["id"])
        gettransitwarehousedelivery_result = json.loads(gettransitwarehousedelivery_resp.text)["result"][0]

        # 生成备货单
        createshipmentorstockupbill_payload = {
            "id": page_result["id"],
            "shipmentCode": gettransitwarehousedelivery_result["shipmentCode"],
            "deliveryWarehouseId": gettransitwarehousedelivery_result["deliveryWarehouseId"],
            "isFnSku": gettransitwarehousedelivery_result["isFnSku"]
        }
        reateshipmentorstockupbill_resp = ArrangeContainerBill().create_shipmentorstockupbill_arrangecontainerbill(
            cookies, createshipmentorstockupbill_payload)
        reateshipmentorstockupbill_result = json.loads(reateshipmentorstockupbill_resp.text)["result"]

        arrangecontainer_data = {"id": page_result["id"],
                                 "arrangecontainercode":arrangecontainerbill_result["alreadyContainerBillCode"],
                                 "stockUpBillId": reateshipmentorstockupbill_result["generateBillId"],
                                 "sourceCode": reateshipmentorstockupbill_result["generateBillCode"],
                                 "sourceType": reateshipmentorstockupbill_result["generateType"]
                                 }

        return arrangecontainer_data


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    ArrangeContainerBill().create_arrangecontainer_link(cookies, 161, 15, 150, 5, 303, 189, "A5-181", 3)
