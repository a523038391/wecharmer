# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/20 上午11:28
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : test_api_firstleg.py
# @Project : wecharmer
import json
import random
import string
from datetime import datetime

import allure
import pytest

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.containerbill import ContainerBill
from lib.firstleg.loadingadvice import LoadingAdvice
from lib.firstleg.printpickingbill import Printpickingbill
from lib.firstleg.scanpacking import ScanPacking
from lib.firstleg.shipmentbill import ShipmentBill
from lib.firstleg.stockupbill import StockupBill
from lib.login import Login
from conf.dataconfig import item,shop,warehouse,operateDivision,employee


class TestApiFirstLeg:

    def setup_class(self):

        self.cookies_wc = Login.loginWecharmer()
        self.skucode = item["李朋测试品-凳子-绿色-S"]["skucode"]
        self.shopId=shop["LIPENG"]["id"]
        self.warehouseId=warehouse["李朋自营仓"]["id"]
        self.warehouseName=warehouse["李朋自营仓"]["warehouseName"]
        self.targetWarehouseId=warehouse["西邮WPLA5海外仓"]["id"]
        self.operateDivisionId=operateDivision["运营青蛙椅事业部"]["id"]
        self.platformEnName=shop["LIPENG"]["platformEnName"]
        self.pickerId=employee["李朋"]["id"]
        self.pickerName=employee["李朋"]["realName"]
        self.fbaShipmentCode="FBA16K8TWW9P"
        self.targetWarehouseId2 = warehouse["FBA流水测试"]["id"]
        self.operateDivisionId2 = operateDivision["运营欧洲事业部"]["id"]
        self.shopId2 = shop["SERWALL_US"]["id"]
        self.skucode2 = item["女士西装0125-浅灰-XS"]["skucode"]
        self.skuid2 = item["女士西装0125-浅灰-XS"]["id"]





    def teardown_class(self):
        pass

    def setup_method(self):
        random_number = ''.join(random.choices(string.digits, k=10))

        # 获取当前日期和时间
        now = datetime.now()
        self.formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        self.billNo = "lipeng-api-" + self.formatted_date


    def teardown_method(self):
        pass

    @allure.feature("创建备货单")
    def test_create_stockupbill(self):
        stockupbilldata=StockupBill().create_stockupbill_link(self.cookies_wc,self.skucode,self.shopId, self.warehouseId, self.targetWarehouseId, self.operateDivisionId, self.platformEnName)

        url = f"{waveecharmer_Host}/api/stockupbill/page?stockUpBillStatuses=1,2,3,5,6&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&stockUpBillCodes=%22{stockupbilldata["sourceCode"]}%22&pageIndex=1&pageSize=10"
        #查询备货单
        stockupbill_resp=StockupBill().query_stockupbill(url,self.cookies_wc)
        stockUpBillCode=json.loads(stockupbill_resp.text)["result"]["items"][0]["stockUpBillCode"]
        assert stockupbilldata["sourceCode"]== stockUpBillCode

    @allure.story("头程链路")
    @allure.title("备货单-打印装箱-装柜通知-装柜列表")
    def test_stockupbill_link(self):
        #创建备货单
        stockupbilldata = StockupBill().create_stockupbill_link(self.cookies_wc, self.skucode, self.shopId,
                                                                self.warehouseId, self.targetWarehouseId,
                                                                self.operateDivisionId, self.platformEnName)
        #打印备货单
        Printpickingbill().print_link(self.cookies_wc,2,stockupbilldata["stockUpBillId"],stockupbilldata["sourceCode"],self.pickerId, self.pickerName)
        #装箱
        ScanPacking().scanpacking_link(self.cookies_wc,2,stockupbilldata["stockUpBillId"],stockupbilldata["sourceCode"],self.skucode)

        #装柜通知
        LoadingAdvice().loadingadvice_link(self.cookies_wc,self.billNo,502,self.warehouseId,self.warehouseName,stockupbilldata["stockUpBillId"],stockupbilldata["sourceCode"])

        #装柜列表
        containerbilldata=ContainerBill().create_containerbill_link(self.cookies_wc,stockupbilldata["sourceCode"],502,self.pickerId,self.pickerName,self.billNo)

        # 断言
        containerbill_resp = ContainerBill().get_containerbill(self.cookies_wc, self.billNo)
        containerBillCode = json.loads(containerbill_resp.text)["result"]["items"][0]["containerBillCode"]
        assert containerbilldata["containerBillCode"] == containerBillCode

    @allure.title("发货单-打印装箱-装柜通知-装柜列表")
    def test_shipmentbill_link(self):
        #创建发货单
        shipmentbilldata=ShipmentBill().fba_shipmentbill_link(self.cookies_wc, self.fbaShipmentCode, self.warehouseId,
                                                                 self.targetWarehouseId2,self.operateDivisionId2, self.shopId2,self.skucode2,self.skuid2)

        # 打印发货单
        Printpickingbill().print_link(self.cookies_wc, 1, shipmentbilldata["shipmentbillid"],
                                      shipmentbilldata["shipmentBillCode"], self.pickerId, self.pickerName)

        # 装箱
        ScanPacking().scanpacking_link(self.cookies_wc, 1, shipmentbilldata["shipmentbillid"],
                                       shipmentbilldata["shipmentBillCode"], self.skucode2)

        # 装柜通知
        LoadingAdvice().loadingadvice_link(self.cookies_wc, self.billNo, 505, self.warehouseId, self.warehouseName,
                                           shipmentbilldata["shipmentbillid"], shipmentbilldata["shipmentBillCode"])

        # 装柜列表
        containerbilldata=ContainerBill().create_containerbill_link(self.cookies_wc, shipmentbilldata["shipmentBillCode"], 505, self.pickerId,
                                                  self.pickerName, self.billNo)


        #断言
        containerbill_resp=ContainerBill().get_containerbill(self.cookies_wc,self.billNo)
        containerBillCode=json.loads(containerbill_resp.text)["result"]["items"][0]["containerBillCode"]
        assert containerbilldata["containerBillCode"] == containerBillCode

if __name__ == '__main__':
    #pytest.main(['-vs', 'test_api_firstleg.py',"test_stockupbill_link"])
    pytest.main(['-vs','test_api_firstleg.py::TestApiFirstLeg::test_stockupbill_link'])