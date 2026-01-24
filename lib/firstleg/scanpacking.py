# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/19 下午6:59
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : scanpacking.py
# @Project : wecharmer
import json

import requests

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.printpickingbill import Printpickingbill
from lib.login import Login
from util import httpUtil


class ScanPacking:
    def __init__(self):
        pass

    def scan_billcode(self, cookies, sourceCode):
        """
        扫描单号并茨取单据信息
        :param sourceCode:来源单据code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/scan/billcode/{sourceCode}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("扫描单号并茨取单据信息resp-----------\n" + resp.text)
        return resp

    def scan_all_productcode(self, cookies, sourceType, sourceId, sourceCode):
        """
        获取所有产品的装箱信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/scan/productcode/all?sourceType={sourceType}&sourceId={sourceId}&sourceCode={sourceCode}"
        resp = requests.get(url=url, headers=cookies)
        print("获取所有产品的装箱信息resp-----------\n" + resp.text)
        return resp

    def scan_productcode(self, cookies, sourceType, sourceId, sourceCode, skucode):
        """
        扫描产品并获取装箱信息
        :param sourceCode:来源单据code
        :param sourceType:来源单据类型
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/scan/productcode?sourceType={sourceType}&sourceId={sourceId}&sourceCode={sourceCode}&productCode={skucode}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("扫描产品并获取装箱信息resp-----------\n" + resp.text)
        return resp

    def packing_scanpacking_v1(self, cookies, payload):
        """
        按件装箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/packing"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按件装箱resp-----------\n" + resp.text)
        return resp

    def packing_scanpacking(self, cookies, sourceType, sourceId, sourceCode, skucode):
        """
        按件装箱
        :param sourceCode:来源单据code
        :param sourceType:来源单据类型
        :return:
        """

        # 扫描产品并获取装箱信息
        scan_productcode_resp = ScanPacking().scan_productcode(cookies, sourceType, sourceId, sourceCode, skucode)
        skudata = json.loads(scan_productcode_resp.text)["result"]
        print(skudata)
        dict = {"packingQuantity": 10, "remainingQuantityCpu": 0, "transQtyValid": False}
        skudata.update(dict
                       )
        url = f"{waveecharmer_Host}/api/scanpacking/packing"

        payload = {
            "billCode": sourceCode,
            "boxId": 1,
            "totalWeightWithBox": 500,
            "detailList": [
                skudata

            ]
        }
        print(payload)
        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("装箱resp-----------\n" + resp.text)
        return resp

    def submit_scanpacking(self, cookies, sourceType, sourceId, sourceCode):
        """
        提交装箱审核
        :param sourceType:来源单类型
        :param sourceId:来源单id
        :param sourceCode:来源单code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/all/submit"
        payload = {
            "sourceType": sourceType,
            "sourceId": sourceId,
            "sourceCode": sourceCode
        }
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("提交装箱审核resp-----------\n" + resp.text)
        return resp

    def process_scanpacking(self, cookies, sourceType, sourceId, sourceCode):
        """
        装箱审核
        :param sourceType:来源单类型
        :param sourceId:来源单id
        :param sourceCode:来源单code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/process"
        payload = {
            "sourceType": sourceType,
            "sourceId": sourceId,
            "sourceCode": sourceCode,
            "auditStatus": True,
            "failReason": ""
        }
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("装箱审核resp-----------\n" + resp.text)
        return resp

    def scanpacking_packingbybox(self, cookies, payload):
        """
        按箱装箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/packingByBox"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按箱装箱resp-----------\n" + resp.text)
        return resp

    def scanpacking_link(self, cookies, sourceType, sourceId, sourceCode, skucode):
        try:
            # 扫描单号并茨取单据信息
            ScanPacking().scan_billcode(cookies, sourceCode)
            # 装箱
            ScanPacking().packing_scanpacking(cookies, sourceType, sourceId, sourceCode, skucode)
            # 提交装箱审核
            ScanPacking().submit_scanpacking(cookies, sourceType, sourceId, sourceCode)
            # 装箱审核
            ScanPacking().process_scanpacking(cookies, sourceType, sourceId, sourceCode)

        except Exception as e:
            print("装箱出错", e)

    def shipmentbill_scanpacking_link(self, cookies, sourceType, warehouseId, targetWarehouseId, operateDivisionId,
                                      shopId, purchaserId, purchaserName, product_code, quantity, fbaShipmentCode,supplierId,companyId):
        # 创建发货单-按箱-打印
        shipmentbilldata = Printpickingbill().shipmentbill_box_print(cookies, sourceType, warehouseId,
                                                                     targetWarehouseId, operateDivisionId,
                                                                     shopId, purchaserId, purchaserName, product_code,
                                                                     quantity, fbaShipmentCode,supplierId,companyId)

        # 扫描单号并茨取单据信息
        scan_billcode_resp = ScanPacking().scan_billcode(cookies, shipmentbilldata["shipmentBillCode"])
        scan_billcode_result = json.loads(scan_billcode_resp.text)["result"]

        # 装箱

        for item in scan_billcode_result["packingStockList"]:
            packingbybox_payload = {
                "sourceType": sourceType,
                "sourceId": shipmentbilldata["shipmentbillid"],
                "sourceCode": shipmentbilldata["shipmentBillCode"],
                "packingStockModel": item
            }
            ScanPacking().scanpacking_packingbybox(cookies, packingbybox_payload)

        # 提交审核
        ScanPacking().submit_scanpacking(cookies, sourceType, shipmentbilldata["shipmentbillid"],
                                         shipmentbilldata["shipmentBillCode"])
        # 装箱审核
        ScanPacking().process_scanpacking(cookies, sourceType, shipmentbilldata["shipmentbillid"],
                                          shipmentbilldata["shipmentBillCode"])

        return shipmentbilldata


    #已排柜备货单拣货装箱
    def arrangecontainer_stockupbill_scanpacking_box_link(self, cookies, sourceType, stockUpBillId,sourceCode,

                                         purchaserId, purchaserName):

        # 打印
        Printpickingbill().print_link(cookies, sourceType, stockUpBillId,
                                      sourceCode, purchaserId, purchaserName)

        # 扫描单号并茨取单据信息
        scan_billcode_resp = ScanPacking().scan_billcode(cookies, sourceCode)
        scan_billcode_result = json.loads(scan_billcode_resp.text)["result"]

        # 装箱

        for item in scan_billcode_result["packingStockList"]:
            packingbybox_payload = {
                "sourceType": sourceType,
                "sourceId": stockUpBillId,
                "sourceCode": sourceCode,
                "packingStockModel": item
            }
            ScanPacking().scanpacking_packingbybox(cookies, packingbybox_payload)

        # 提交装箱审核
        ScanPacking().submit_scanpacking(cookies, sourceType, stockUpBillId,
                                         sourceCode)

        # 装箱审核
        ScanPacking().process_scanpacking(cookies, sourceType, stockUpBillId,
                                          sourceCode)





    def stockupbill_scanpacking_box_link(self, cookies, sourceType, shopId, warehouseId, targetWarehouseId,
                                     operateDivisionId,
                                     purchaserId, purchaserName, product_code,quantity):

        # 创建备货单-按箱-打印
        stockupbilldata=Printpickingbill().stockupbill_box_print(cookies, sourceType, shopId, warehouseId, targetWarehouseId,
                                     operateDivisionId,
                                     purchaserId, purchaserName, product_code,quantity)

        # 扫描单号并茨取单据信息
        scan_billcode_resp = ScanPacking().scan_billcode(cookies, stockupbilldata["sourceCode"])
        scan_billcode_result = json.loads(scan_billcode_resp.text)["result"]

        # 装箱

        for item in scan_billcode_result["packingStockList"]:
            packingbybox_payload = {
                "sourceType": sourceType,
                "sourceId": stockupbilldata["stockUpBillId"],
                "sourceCode": stockupbilldata["sourceCode"],
                "packingStockModel": item
            }
            ScanPacking().scanpacking_packingbybox(cookies, packingbybox_payload)

        # 提交装箱审核
        ScanPacking().submit_scanpacking(cookies, sourceType, stockupbilldata["stockUpBillId"],
                                                                  stockupbilldata["sourceCode"])

        # 装箱审核
        ScanPacking().process_scanpacking(cookies, sourceType, stockupbilldata["stockUpBillId"],
                                                                  stockupbilldata["sourceCode"])

        return stockupbilldata



    def stockupbill_scanpacking_link(self, cookies, sourceType, shopId, warehouseId, targetWarehouseId,
                                     operateDivisionId,
                                     purchaserId, purchaserName, product_code):

        # 创建备货单-按件-打印
        stockupbilldata = Printpickingbill().stockupbill_print(cookies, sourceType, shopId, warehouseId,
                                                               targetWarehouseId, operateDivisionId,
                                                               purchaserId, purchaserName, product_code)

        # 获取所有产品装箱信息
        all_productcode_resp = ScanPacking().scan_all_productcode(cookies, sourceType, stockupbilldata["stockUpBillId"],
                                                                  stockupbilldata["sourceCode"])
        all_productcode_result = json.loads(all_productcode_resp.text)["result"]

        # 装箱
        detailList = []
        for item in all_productcode_result:
            detailList_dict = {
                "skuImgUrl": item["skuImgUrl"],
                "thirdImageUrl": None,
                "useImageSource": item["useImageSource"],
                "skuId": item["skuId"],
                "skuCode": item["skuCode"],
                "oldSkuCode": item["oldSkuCode"],
                "skuName": item["skuName"],
                "fnSkuCode": None,
                "packingQuantity": item["remainingQuantity"],
                "remainingQuantity": item["remainingQuantity"],
                "grossWeight": item["grossWeight"],
                "remainingQuantityCpu": 0,
                "transQtyValid": False
            }
            detailList.append(detailList_dict)
        packing_scanpacking_payload = {
            "billCode": stockupbilldata["sourceCode"],
            "boxId": 1,
            "totalWeightWithBox": 20,
            "detailList": detailList
        }
        ScanPacking().packing_scanpacking_v1(cookies, packing_scanpacking_payload)

        # 提交装箱审核
        ScanPacking().submit_scanpacking(cookies, sourceType, stockupbilldata["stockUpBillId"],
                                                                  stockupbilldata["sourceCode"])

        # 装箱审核
        ScanPacking().process_scanpacking(cookies, sourceType, stockupbilldata["stockUpBillId"],
                                                                  stockupbilldata["sourceCode"])

        return stockupbilldata


    def shipmentbill_scanpacking_a_link(self,cookies,sourceType, warehouseId, targetWarehouseId, operateDivisionId,
                                  shopId, purchaserId,purchaserName, product_code, fbaShipmentCode):


        # 创建发货单-按件-打印
        shipmentbilldata=Printpickingbill().shipmentbill_print(cookies,sourceType, warehouseId, targetWarehouseId, operateDivisionId,
                                  shopId, purchaserId,purchaserName, product_code, fbaShipmentCode)

        # 获取所有产品装箱信息
        all_productcode_resp = ScanPacking().scan_all_productcode(cookies, sourceType, shipmentbilldata["shipmentbillid"],
                                                                  shipmentbilldata["shipmentBillCode"])
        all_productcode_result = json.loads(all_productcode_resp.text)["result"]

        # 装箱
        detailList = []
        for item in all_productcode_result:
            detailList_dict = {
                "skuImgUrl": item["skuImgUrl"],
                "thirdImageUrl": None,
                "useImageSource": item["useImageSource"],
                "skuId": item["skuId"],
                "skuCode": item["skuCode"],
                "oldSkuCode": item["oldSkuCode"],
                "skuName": item["skuName"],
                "fnSkuCode": None,
                "packingQuantity": item["remainingQuantity"],
                "remainingQuantity": item["remainingQuantity"],
                "grossWeight": item["grossWeight"],
                "remainingQuantityCpu": 0,
                "transQtyValid": False
            }
            detailList.append(detailList_dict)
        packing_scanpacking_payload = {
            "billCode": shipmentbilldata["shipmentBillCode"],
            "boxId": 1,
            "totalWeightWithBox": 20,
            "detailList": detailList
        }
        ScanPacking().packing_scanpacking_v1(cookies, packing_scanpacking_payload)

        # 提交装箱审核
        ScanPacking().submit_scanpacking(cookies, sourceType, shipmentbilldata["shipmentbillid"],
                                                                  shipmentbilldata["shipmentBillCode"])

        # 装箱审核
        ScanPacking().process_scanpacking(cookies, sourceType, shipmentbilldata["shipmentbillid"],
                                                                  shipmentbilldata["shipmentBillCode"])

        return shipmentbilldata

if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # ScanPacking().scan_billcode(cookies, "BH24061900005")
    # ScanPacking().packing_scanpacking(cookies, 1, "724", "BH24061900004", "LIPENG456-B-P")
    #发货单按箱装箱-审核
    ScanPacking().shipmentbill_scanpacking_link(cookies, 1, 128, 135, 5, 162, 303, "李朋",
                                                     "A5-181", 3, "FBA16M9J26TK")
    #备货单按件装箱-审核
    #ScanPacking().stockupbill_scanpacking_link(cookies,2,161,177,11,5,303,"李朋","A5-181")


    #备货单按箱装箱-审核
    #ScanPacking().stockupbill_scanpacking_box_link(cookies,2,161,177,11,5,303,"李朋","A5-181",3)


    #备货单按件装箱-审核
    #ScanPacking().shipmentbill_scanpacking_a_link(cookies, 1, 150, 135, 5, 162, 303, "李朋",
    #                                            "A5-181", "FBA16M9J26TK")