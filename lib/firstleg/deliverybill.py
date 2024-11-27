# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/20 下午5:11
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : deliverybill.py
# @Project : wecharmer
import json

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.inspection import Inspection
from lib.firstleg.loadingadvice import LoadingAdvice
from lib.firstleg.stockupbill import StockupBill
from lib.login import Login
from util import httpUtil


class DeliveryBill:
    def __init__(self):
        pass


    def query_deliverybill(self,url,cookies):
        """
        查询出库单
        :return:
        """
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("查询出库单resp-----------\n" + resp.text)
        return resp



    def booking_deliverybill_link(self,cookies,billOfLadingCode,sourceBillCategory,shopId, warehouseId,warehouseName, operateDivisionId, purchaserId,purchasername, targetWarehouseId,sourceBillType):
        """
        创建订舱单发货全链路
        :param isLCL:是否拼柜
        :param cargoReadyDay:货号日期
        :param containerId:货柜id
        :param purchaseOrderId:采购单id
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """
        #创建订舱单-验货完成
        booking_data=Inspection().create_inspection_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId, targetWarehouseId)

        LoadingAdvice().loadingadvice_link(cookies,billOfLadingCode,sourceBillCategory,warehouseId,warehouseName,booking_data["bookingid"],booking_data["bookingcode"])

        #根据订舱单号查询备货单
        url = f"{waveecharmer_Host}/api/stockupbill/page?stockUpBillStatuses=1,2,3,5,6&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&bookingBillCode={booking_data['bookingcode']}&pageIndex=1&pageSize=10"
        sourceCode_resp=StockupBill().query_stockupbill(cookies,url)
        sourceCode=json.loads(sourceCode_resp.text)["result"]["items"][0]["stockUpBillCode"]




if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    DeliveryBill().booking_deliverybill_link(cookies,533535,507, 161, 15,"恒丰仓库", 5, 303, "李朋",12,502)