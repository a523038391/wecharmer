# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2025/2/18 上午9:55
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : waitcontainerbill.py
# @Project : wecharmer
import json
import math
import time
from datetime import datetime, timedelta

import requests

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.stock_inspection import Inspection
from lib.login import Login
from lib.productandmaterial.product import Product
from lib.purchase.purchaseorder import PurchaseOrder
from lib.storage.stock import Stock
from lib.supplier.supplier import Supplier


class WaitContainerBill:
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

    def create_waitcontainerbill(self, cookies, payload):
        """
        创建待排柜
        :return:
        """
        url = f"{waveecharmer_Host}/api/waitcontainerbill/wait/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建待排柜resp-----------\n" + resp.text)
        return resp


    def get_waitcontainerbill_page(self, cookies, payload):
        """
        分页查询待排柜
        :return:
        """
        url = f"{waveecharmer_Host}/api/waitcontainerbill/wait/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("分页查询待排柜resp-----------\n" + resp.text)
        return resp


    def get_waitcontainerbill_items(self, cookies, waitcontainerids):
        """
        根据待排柜Id获取明细集合
        :return:
        """
        url = f"{waveecharmer_Host}/api/waitcontainerbill/wait/items?ids={waitcontainerids}"
        resp = requests.get(url=url, headers=cookies)
        print("根据待排柜Id获取明细集合resp-----------\n" + resp.text)
        return resp

    def create_waitcontainerbill_manual(self, cookies, payload):
        """
        选仓
        :return:
        """
        url = f"{waveecharmer_Host}/api/waitcontainerbill/manual/select/single"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("选仓resp-----------\n" + resp.text)
        return resp

    def create_waitContainer_entity_link(self, cookies, shopId, warehouseId_entity, operateDivisionId, purchaserId,
                                         targetWarehouseId,
                                         product_code, quantity):
        """
        创建待排柜链路-实体仓
        :param targetWarehouseSettingId:预计发往区域
        :param targetWarehouseType:仓库类型
        :param transportationTypeId:运输方式
        :param positionSelection:选仓
        :param isNeedFnSku:是否需要箱贴
        :param warehouseType:仓库类型
        :param overseasWarehouseListingMethod:按箱 按件
        """

        # 创建采购单按箱上架
        Stock().purchase_order_box_link(cookies, shopId, warehouseId_entity, operateDivisionId, purchaserId,
                                        product_code)

        # 获取装箱库存明细平铺箱贴聚合数据分页

        packingstock_spread_page_resp = Stock().get_packingstock_spread_page(cookies, shopId, operateDivisionId,warehouseId_entity,
                                                                             product_code)
        packingstock_spread_page_result = json.loads(packingstock_spread_page_resp.text)["result"]



        #创建待排柜

        count = 1
        items=[]
        sku=[]

        for item in packingstock_spread_page_result["items"]:
            if int(item["boxStickerNo"][-1]) > 1 and int(item["availableStockQuantity"]) / int(
                    item["boxStickerNo"][-1]) > quantity and item["skuCode"] not in sku:
                sam=int(item["availableStockQuantity"]) / int(
                    item["boxStickerNo"][-1])



                print("次数"+str(sam))

                items_dict = {
                    "oneBoxLoadQuantity": item["boxStickerNo"][-1],
                    "inventoryAvailableQuantity": int(item["availableStockQuantity"]),
                    "boxQuantity": quantity,
                    "boxLength": item["cartonLong"],
                    "boxWidth": item["cartonWidth"],
                    "boxHeight": item["cartonHeight"],
                    "ctnVolume": item["totalCtnVolume"],
                    "ctnGrossWeight": item["totalGrossWeight"],
                    "ctnNetWeight": 0,
                    "packageSticker": item["skuCode"]+"--"+str(int(item["boxStickerNo"][-1])),
                    "productSticker": item["fnSku"],
                    "sellerSku": item["sellerSkuCode"],
                    "waitContainerQuantity": int(item["boxStickerNo"][-1])*quantity,
                    "totalVolumeWithBox": float(item["totalCtnVolume"])*quantity,
                    "totalGrossWithBox": float(item["totalCtnVolume"])*quantity
                }
                items_dict.update(item)
                items.append(items_dict)
                sku.append(item["skuCode"])

                count += 1
                if count == 5:
                    break
            else:
                continue




        booking_payload = {
            "waitContainerBillCode": None,
            "operateDivisionId": operateDivisionId,
            "operateDivisionName": "运营青蛙椅事业部",
            "targetWarehouseSettingId": 1,
            "expectedDeliveryDate": self.formatted_date,
            "expectedWarehouseDate": self.formatted_date_eta,
            "targetWarehouseId": None,
            "targetWarehouseName": None,
            "targetWarehouseType": 2,
            "transportationTypeId": 2,
            "positionSelection": 0,
            "transportationTypeName": "海运",
            "inStorageType": 3,
            "isQuickReturn": False,
            "developType": None,
            "shopId": shopId,
            "shopAccount": "LIPENG",
            "operaterId": purchaserId,
            "operaterName": "李朋",
            "isNeedFnSku": "true",
            "warehouseId": warehouseId_entity,
            "warehouseType": 1,
            "warehouseName": "李朋自营仓",
            "overseasWarehouseListingMethod": 1,
            "remark": None,
            "deliveryDayAddition": 0,
            "targetWarehouseSettingName": "美东",
            "details": items
        }

        waitContainer_resp = WaitContainerBill().create_waitcontainerbill(cookies, booking_payload)
        waitContainer_result = json.loads(waitContainer_resp.text)["result"]

        # 选仓

        manual_payload = {
            "warehouseId": targetWarehouseId,
            "id": waitContainer_result
        }
        WaitContainerBill().create_waitcontainerbill_manual(cookies, manual_payload)
        time.sleep(5)

        return waitContainer_result


    def create_waitContainer_supplier_fba_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                           product_code):
        """
        创建待排柜链路-供应商仓-平台仓
        :param targetWarehouseSettingId:预计发往区域
        :param targetWarehouseType:仓库类型
        :param transportationTypeId:运输方式
        :param positionSelection:选仓
        :param isNeedFnSku:是否需要箱贴
        :param warehouseType:仓库类型
        :param overseasWarehouseListingMethod:按箱 按件
        """


        inspection_data = Inspection().inspection_purchaseorder_report(cookies, shopId, warehouseId, operateDivisionId,
                                                                       purchaserId, product_code)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder().get_purchaseorder_details(cookies,
                                                                               inspection_data["purchaseorderid"])
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

        # 根据采购单id查询库存


        supplierinventory_resp = Supplier().get_supplierinventory_page1(cookies, 3, shopId,
                                                                        warehouseId, skuDetailDimensionDetails[0][
                                                                            "purchaseOrderCode"])
        supplierinventory_result = json.loads(supplierinventory_resp.text)["result"]["items"]
        print(supplierinventory_result)

        items = []

        for skuDetail in supplierinventory_result:
            # 查询产品对外关系分页
            sellersku_payload = {
                "shopIds": [
                    shopId
                ],
                "skuCodes": [
                    skuDetail["skuCode"]
                ],
                "isMatch": True,
                "pageSize": 100,
                "pageIndex": 1,
                "isEmptyFnSku": False,
                "operateDivisionId": operateDivisionId
            }

            sellersku_resp = Product().sellersku_page(cookies, sellersku_payload)
            sellersku_result = json.loads(sellersku_resp.text)["result"]["items"][0]

            items_dict = {
                "boxLength": skuDetail["boxGauge"]["ctnLongX"],
                "boxWidth": skuDetail["boxGauge"]["ctnLongY"],
                "boxHeight": skuDetail["boxGauge"]["ctnLongZ"],
                "ctnVolume": skuDetail["boxGauge"]["ctnVolume"],
                "ctnGrossWeight": skuDetail["boxGauge"]["ctnNetWeight"],
                "ctnNetWeight": skuDetail["boxGauge"]["ctnGrossWeight"],
                "oneBoxLoadQuantity": int(skuDetail["boxGauge"]["ctnQuantity"]),
                "boxQuantity": int(
                    int(skuDetail["inventoryAvailableQuantity"]) / int(skuDetail["boxGauge"]["ctnQuantity"])),
                "productCode": skuDetail["skuCode"],
                "packageSticker": None,
                "productSticker": sellersku_result["fnSku"],
                "sellerSku": sellersku_result["code"],
                "waitContainerQuantity": int(skuDetail["inventoryAvailableQuantity"]),
                "totalVolumeWithBox": float(
                    float(skuDetail["boxGauge"]["ctnVolume"]) * int(skuDetail["inventoryAvailableQuantity"]) / int(
                        skuDetail["boxGauge"]["ctnQuantity"])),
                "totalGrossWithBox": float(skuDetail["boxGauge"]["ctnGrossWeight"]) * int(
                    skuDetail["inventoryAvailableQuantity"]) / int(skuDetail["boxGauge"]["ctnQuantity"])
            }
            items_dict.update(skuDetail)
            print(items_dict)

            items.append(items_dict)

        # 创建待排柜单
        booking_payload = {
            "waitContainerBillCode": None,
            "operateDivisionId": operateDivisionId,
            "operateDivisionName": "运营青蛙椅事业部",
            "targetWarehouseSettingId": 2,
            "expectedDeliveryDate": self.formatted_date,
            "expectedWarehouseDate": self.formatted_date_eta,
            "targetWarehouseId": None,
            "targetWarehouseName": None,
            "targetWarehouseType": 3,
            "transportationTypeId": 18,
            "positionSelection": 0,
            "transportationTypeName": "第三方普船整柜",
            "inStorageType": None,
            "isQuickReturn": False,
            "developType": None,
            "shopId": shopId,
            "shopAccount": "LIPENG_US",
            "operaterId": purchaserId,
            "operaterName": "李朋",
            "isNeedFnSku": "true",
            "warehouseId": warehouseId,
            "warehouseType": 5,
            "warehouseName": "恒丰仓库",
            "remark": "备注一下吧",
            "deliveryDayAddition": 0,
            "targetWarehouseSettingName": "美西",
            "details": items
        }

        waitContainer_resp = WaitContainerBill().create_waitcontainerbill(cookies, booking_payload)
        waitContainer_result = json.loads(waitContainer_resp.text)["result"]

        return waitContainer_result






    def create_waitContainer_supplier_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                           targetWarehouseId,
                                           product_code):
        """
        创建待排柜链路-供应商仓-海外仓
        :param targetWarehouseSettingId:预计发往区域
        :param targetWarehouseType:仓库类型
        :param transportationTypeId:运输方式
        :param positionSelection:选仓
        :param isNeedFnSku:是否需要箱贴
        :param warehouseType:仓库类型
        :param overseasWarehouseListingMethod:按箱 按件
        """

        inspection_data = Inspection().inspection_purchaseorder_report(cookies, shopId, warehouseId, operateDivisionId,
                                                                       purchaserId, product_code)

        time.sleep(2)

        # 获取采购单明细
        purchaseOrderDetailId_resp = PurchaseOrder().get_purchaseorder_details(cookies,
                                                                               inspection_data["purchaseorderid"])
        skuDetailDimensionDetails = json.loads(purchaseOrderDetailId_resp.text)["result"]["skuDetailDimensionDetails"]

        # 根据采购单id查询库存


        print("ces1")

        supplierinventory_resp = Supplier().get_supplierinventory_page1(cookies, 3, shopId,
                                                                        warehouseId, skuDetailDimensionDetails[0][
                                                                            "purchaseOrderCode"])
        supplierinventory_result = json.loads(supplierinventory_resp.text)["result"]["items"]
        print(supplierinventory_result)

        items = []

        for skuDetail in supplierinventory_result:
            # 查询产品对外关系分页
            sellersku_payload = {
                "shopIds": [
                    shopId
                ],
                "skuCodes": [
                    skuDetail["skuCode"]
                ],
                "isMatch": True,
                "pageSize": 100,
                "pageIndex": 1,
                "isEmptyFnSku": False,
                "operateDivisionId": operateDivisionId
            }

            sellersku_resp = Product().sellersku_page(cookies, sellersku_payload)
            sellersku_result = json.loads(sellersku_resp.text)["result"]["items"][0]

            items_dict = {
                "boxLength": skuDetail["boxGauge"]["ctnLongX"],
                "boxWidth": skuDetail["boxGauge"]["ctnLongY"],
                "boxHeight": skuDetail["boxGauge"]["ctnLongZ"],
                "ctnVolume": skuDetail["boxGauge"]["ctnVolume"],
                "ctnGrossWeight": skuDetail["boxGauge"]["ctnNetWeight"],
                "ctnNetWeight": skuDetail["boxGauge"]["ctnGrossWeight"],
                "oneBoxLoadQuantity": int(skuDetail["boxGauge"]["ctnQuantity"]),
                "boxQuantity": int(
                    int(skuDetail["inventoryAvailableQuantity"]) / int(skuDetail["boxGauge"]["ctnQuantity"])),
                "productCode": skuDetail["skuCode"],
                "packageSticker": sellersku_result["fnSku"] + "--" + str(int(skuDetail["boxGauge"]["ctnQuantity"])),
                "productSticker": sellersku_result["fnSku"],
                "sellerSku": sellersku_result["code"],
                "waitContainerQuantity": int(skuDetail["inventoryAvailableQuantity"]),
                "totalVolumeWithBox": float(
                    float(skuDetail["boxGauge"]["ctnVolume"]) * int(skuDetail["inventoryAvailableQuantity"]) / int(
                        skuDetail["boxGauge"]["ctnQuantity"])),
                "totalGrossWithBox": float(skuDetail["boxGauge"]["ctnGrossWeight"]) * int(
                    skuDetail["inventoryAvailableQuantity"]) / int(skuDetail["boxGauge"]["ctnQuantity"])
            }
            items_dict.update(skuDetail)
            print(items_dict)

            items.append(items_dict)

        # 创建待排柜单
        booking_payload = {
            "waitContainerBillCode": None,
            "operateDivisionId": operateDivisionId,
            "operateDivisionName": "运营青蛙椅事业部",
            "targetWarehouseSettingId": 2,
            "expectedDeliveryDate": self.formatted_date,
            "expectedWarehouseDate": self.formatted_date_eta,
            "targetWarehouseId": None,
            "targetWarehouseName": None,
            "targetWarehouseType": 2,
            "transportationTypeId": 18,
            "positionSelection": 0,
            "transportationTypeName": "第三方普船整柜",
            "inStorageType": 3,
            "isQuickReturn": False,
            "developType": None,
            "shopId": shopId,
            "shopAccount": "LIPENG",
            "operaterId": purchaserId,
            "operaterName": "李朋",
            "isNeedFnSku": "true",
            "warehouseId": warehouseId,
            "warehouseType": 5,
            "warehouseName": "恒丰仓库",
            "overseasWarehouseListingMethod": 1,
            "remark": "备注一下吧",
            "deliveryDayAddition": 0,
            "targetWarehouseSettingName": "美西",
            "details": items
        }

        waitContainer_resp = WaitContainerBill().create_waitcontainerbill(cookies, booking_payload)
        waitContainer_result = json.loads(waitContainer_resp.text)["result"]

        # 选仓

        manual_payload = {
            "warehouseId": targetWarehouseId,
            "id": waitContainer_result
        }
        WaitContainerBill().create_waitcontainerbill_manual(cookies, manual_payload)

        return waitContainer_result


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    # 海外仓创建待排柜
   #WaitContainerBill().create_waitContainer_supplier_link(cookies, 161, 15, 5, 303, 189, "A5-181")

    # 平台仓创建待排柜
    WaitContainerBill().create_waitContainer_supplier_fba_link(cookies, 162, 15, 5, 303, "A5-181")

    #WaitContainerBill().create_waitContainer_entity_link(cookies,161,150,5,303,189,"A5-181",3)
