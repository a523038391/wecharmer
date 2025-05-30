# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/12/16 下午2:44
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : supplier.py
# @Project : wecharmer
import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from lib.purchase.purchaseorder import PurchaseOrder


class Supplier:
    def __init__(self):
        pass

    def create_supplierstockin(self, cookies, payload):
        """
        创建工厂入库单
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierstockin/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建工厂入库单resp-----------\n" + resp.text)
        return resp


    def get_supplierstockin_originorderinfo(self, cookies, purchaseorderid,originOrderType):
        """
        获取来源单据的商品明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierstockin/originorderinfo?originOrderId={purchaseorderid}&originOrderType={originOrderType}"
        resp = requests.get(url=url, headers=cookies)
        print("获取来源单据的商品明细resp-----------\n" + resp.text)
        return resp

    def get_supplierinventory_page(self, cookies, purchaseOrderId,supplierInventoryWarehouse):
        """
        获取供应商库存分页列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierinventory/page?purchaseOrderIds={purchaseOrderId}&supplierInventoryWarehouse={supplierInventoryWarehouse}&pageSize=1000"
        resp = requests.get(url=url, headers=cookies)
        print("获取供应商库存分页列表resp-----------\n" + resp.text)
        return resp


    def get_supplierinventory_page1(self, cookies,supplierInventoryWarehouse,shopId,warehouseId,purchaseOrderCode):
        """
        获取供应商库存分页
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierinventory/page?supplierInventoryWarehouse={supplierInventoryWarehouse}&isHideAvailableZero=true&isContainSpu=true&warehouseIds={warehouseId}&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&shopIds={shopId}&purchaseOrderCodes=%22{purchaseOrderCode}%22&pageIndex=1&pageSize=10"
        print(url)
        print(cookies)
        time.sleep(5)
        resp = requests.get(url=url, headers=cookies)

        print("获取供应商库存分页resp-----------\n" + resp.text)
        return resp


    def submit_supplierstockin(self, cookies, id):
        """
        提交工厂入库单
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierstockin/{id}/submit"
        resp = requests.post(url=url, headers=cookies)
        print("提交工厂入库单resp-----------\n" + resp.text)
        return resp

    def supplierstockin_link(self, cookies, shopId, warehouseId, operateDivisionId,
                                                                    purchaserId, product_code):
        """
        创建工厂入库单链路
        :param isSubmit:是否提交
        :param receiptType:单据类型id
        :param warehouseType:虚拟仓类型枚举
        :param originOrderType:入库单类型枚举
        :return:
        """


        # 创建采购单返回id
        purchaseOrderId = PurchaseOrder().create_purchaseorder_link(cookies, shopId, warehouseId, operateDivisionId,
                                                                    purchaserId, product_code)


        time.sleep(15)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder().get_purchaseorder_details(cookies, purchaseOrderId)
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]


        #查询采购单列表
        purchaseOrder_resp=PurchaseOrder().page_purchaseorder(cookies,skuDetailDimensionDetails[0]["purchaseOrderCode"])
        purchaseOrder_items=json.loads(purchaseOrder_resp.text)["result"]["items"]

        #获取来源单据的商品明细
        originorderinfo_resp=Supplier().get_supplierstockin_originorderinfo(cookies,purchaseOrderId,2)
        originorderinfo_result=json.loads(originorderinfo_resp.text)["result"]



        #创建工厂入库单

        itmes=[]

        for itme in originorderinfo_result:
            originorderinfo_dict={
                    "skuId": itme["skuId"],
                    "stockInQuantity": itme["purchaseQuantity"],
                    "purchaseOrderId": itme["purchaseOrderId"],
                    "id": None,
                    "warehouseId":  purchaseOrder_items[0]["warehouseId"],
                    "warehouseName": purchaseOrder_items[0]["warehouseName"]
                }
            itmes.append(originorderinfo_dict)

        supplierstockin_payload = {
            "supplierInOrderCode": "",
            "receiptType": 1001,
            "originOrderType": 2,
            "supplierId": purchaseOrder_items[0]["supplierId"],
            "warehouseType": 1,
            "remarks": "",
            "attachments": [],
            "originOrderId": purchaseOrder_items[0]["id"],
            "originOrderCode": purchaseOrder_items[0]["purchaseOrderCode"],
            "scanCode": "",
            "sourceBillId": purchaseOrder_items[0]["id"],
            "warehouseId": purchaseOrder_items[0]["warehouseId"],
            "warehouseName": purchaseOrder_items[0]["warehouseName"],
            "isSubmit": False,
            "items":
                itmes
        }
        print(supplierstockin_payload)


        supplierstockin_resp=Supplier().create_supplierstockin(cookies, supplierstockin_payload)
        supplierstockin_result=json.loads(supplierstockin_resp.text)["result"]




        #提交
        Supplier().submit_supplierstockin(cookies,supplierstockin_result)

        supplierstockin_data={"purchaseOrderId": purchaseOrderId, "purchaseOrderCode":purchaseOrder_items[0]["purchaseOrderCode"],"supplierId": purchaseOrder_items[0]["supplierId"]}


        return supplierstockin_data





if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    Supplier().supplierstockin_link(cookies, 161, 15, 5, 303,  "A5-181")

