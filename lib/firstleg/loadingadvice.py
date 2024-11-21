# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/20 下午3:33
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : loadingadvice.py
# @Project : wecharmer
import json
import time
import random
from datetime import datetime, timedelta

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.scanpacking import ScanPacking
from lib.login import Login
from util import httpUtil


class LoadingAdvice:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        # 如果你只需要年月日，不需要时间部分，可以将其格式化为字符串
        self.formatted_date = new_date.strftime('%Y-%m-%d')

        self.random_number = ''.join(str(random.randint(0, 9)) for _ in range(10))

    def create_loadingadvice(self, cookies, sourceBillCategory, warehouseId, warehouseName, sourceBillId):
        """
        创建装柜通知
        :param billOfLadingCode:提单号
        :param warehouseId:出发仓
        :param sourceBillId:来源单据id
        :param loadingAdviceType:装柜方式
        :param sourceBillCategory:来源单据类型
        :param containerId:货柜类型
        :return:
        """
        url = f"{waveecharmer_Host}/api/loadingadvice"
        payload = {
            "id": 0,
            "loadingAdviceBillCode": "",
            "billOfLadingCode": "lipeng" + self.random_number,
            "loadingAdviceType": 1,
            "sourceBillCategory": sourceBillCategory,
            "expectLoadingTime": self.formatted_date,
            "containerId": 4,
            "volume": 3375,
            "loadWeight": 150,
            "remark": "",
            "address": "",
            "driverContactPerson": "",
            "driverTel": "",
            "warehouseName": warehouseName,
            "warehouseId": warehouseId,
            "attachmentDetails": [],
            "containerNo": "",
            "leadSealingNumber": "",
            "carNumer": "",
            "loadingAdviceBillDetails": [
                {
                    "sourceBillId": sourceBillId
                }
            ]
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("创建装柜单信息resp-----------\n" + resp.text)
        return resp

    def query_loadingadvice(self, url, cookies):
        """
        查询装柜通知
        :return:
        """
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("查询装柜通知resp-----------\n" + resp.text)
        return resp

    def confirmshipment_loadingadvice(self, cookies, loadingadviceid):
        """
        确认发货
        :param loadingadviceid:装柜通知单id
        :return:
        """
        url = f"{waveecharmer_Host}/api/loadingadvice/confirmshipment/{loadingadviceid}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("确认发货resp-----------\n" + resp.text)
        return resp

    def loadingadvice_link(self, cookies, sourceBillCategory, warehouseId, warehouseName, sourceBillId, sourceBillCode):
        # 创建装柜通知
        LoadingAdvice().create_loadingadvice(cookies, sourceBillCategory, warehouseId, warehouseName, sourceBillId)
        # 查询装柜通知
        url = f"{waveecharmer_Host}/api/loadingadvice/page?loadingAdviceBillStatuses=1,2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&sourceBillCode={sourceBillCode}&billOfLadingCode=&pageIndex=1&pageSize=10"
        LoadingAdvice_tesp = LoadingAdvice().query_loadingadvice(url, cookies)
        loadingadviceid = json.loads(LoadingAdvice_tesp.text)["result"]["items"][0]["id"]

        time.sleep(2)

        # 确认发货
        LoadingAdvice().confirmshipment_loadingadvice(cookies, loadingadviceid)

    def shipmentbill_loadingadvice_link(self, cookies, sourceBillCategory, sourceType, warehouseId, warehouseName,
                                        targetWarehouseId, operateDivisionId,
                                        shopId, purchaserId, purchaserName, product_code, quantity, fbaShipmentCode):
        # 发货单-按箱-装箱
        shipmentbilldata = ScanPacking().shipmentbill_scanpacking_link(cookies, sourceType, warehouseId,
                                                                       targetWarehouseId, operateDivisionId,
                                                                       shopId, purchaserId, purchaserName, product_code,
                                                                       quantity, fbaShipmentCode)

        # 装柜
        LoadingAdvice().loadingadvice_link(cookies, sourceBillCategory, warehouseId, warehouseName,
                                           shipmentbilldata["shipmentbillid"], shipmentbilldata["shipmentBillCode"])


        return shipmentbilldata
    def stockupbill_loadingadvice_link(self,cookies,sourceBillCategory, sourceType, shopId, warehouseId,warehouseName, targetWarehouseId,
                                     operateDivisionId,
                                     purchaserId, purchaserName, product_code):
        #备货单-按件-装箱
        stockupbilldata= ScanPacking().stockupbill_scanpacking_link(cookies, sourceType, shopId, warehouseId, targetWarehouseId,
                                     operateDivisionId,
                                     purchaserId, purchaserName, product_code)
        # 装柜
        LoadingAdvice().loadingadvice_link(cookies, sourceBillCategory, warehouseId, warehouseName,
                                           stockupbilldata["stockUpBillId"],
                                           stockupbilldata["sourceCode"])

        return stockupbilldata

    def shipmentbill_loadingadvice_a_link(self,cookies,sourceBillCategory,sourceType, warehouseId,warehouseName, targetWarehouseId, operateDivisionId,
                                  shopId, purchaserId,purchaserName, product_code, fbaShipmentCode):


        # 发货单-按件-装箱
        shipmentbilldata=ScanPacking().shipmentbill_scanpacking_a_link(cookies,sourceType, warehouseId, targetWarehouseId, operateDivisionId,
                                  shopId, purchaserId,purchaserName, product_code, fbaShipmentCode)

        # 装柜
        LoadingAdvice().loadingadvice_link(cookies, sourceBillCategory, warehouseId, warehouseName,
                                           shipmentbilldata["shipmentbillid"],
                                           shipmentbilldata["shipmentBillCode"])

        return shipmentbilldata


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # LoadingAdvice().loadingadvice_link(cookies,507,"150","李朋自营仓",1158,"DC24090600036")
    #发货单按箱发货-装柜
    #LoadingAdvice().shipmentbill_loadingadvice_link(cookies, 505, 1, 150, "李朋自营仓", 135, 5, 162, 303, "李朋",
    #                                                "A5-181", 3, "FBA16M9J26TK")
    #备货单按件发货-装柜
    # LoadingAdvice().stockupbill_loadingadvice_link(cookies, 502, 2, 161, 150, "李朋自营仓", 11, 5, 303, "李朋",
    #                                                "A5-181")

    #发货单按件发货-装柜
    LoadingAdvice().shipmentbill_loadingadvice_a_link(cookies, 505, 1, 150, "李朋自营仓", 135, 5, 162, 303, "李朋",
                                                   "A5-181",  "FBA16M9J26TK")
