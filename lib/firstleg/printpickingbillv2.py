# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 16:30
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : printpickingbillv2.py
# @Project : wecharmer


from conf.baseconfig import waveecharmer_Host
from interface.firstleg.Printpickingbill_api import Printpickingbill_Api
from lib.firstleg.shipmentbill import ShipmentBill
from lib.firstleg.stockupbillv2 import StockupBill
from lib.login import Login
from util import httpUtil


class Printpickingbill:

    def __init__(self):
        pass

    def print_link(self,cookies,sourceType,sourceId,sourceCode,pickerId, pickerName):
        """
        指派拣货员
        :param sourceType:来源单据类型(1=FBA发货单,2=海外仓备货单)
        :param sourceId:来源单据id
        :param sourceCode:来源单据编号
        :param pickerId:拣货员id
        :param pickerName:拣货员名称
        :param printtemplateCode:打印模板code
        :return:
        """

        try:
            #指派拣货员
            payload_assign = {
                "sourceType": sourceType,
                "sourceId": sourceId,
                "sourceCode": sourceCode,
                "pickerId": pickerId,
                "pickerName": pickerName
            }
            Printpickingbill_Api().assign_picker(cookies,payload_assign)

            payload_print = {
                "sourceType": sourceType,
                "sourceId": sourceId,
                "sourceCode": sourceCode,
                "printtemplateCode": "JHD002"
            }

            #打印
            Printpickingbill_Api().print_pickingbill(cookies,payload_print)

        except Exception as e:
            print("打印出错",e)



    def stockupbill_box_print(self,cookies, shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId,quantity):
        #创建备货单按箱
        stockupbilldata=StockupBill().create_stockupbill_box_link(cookies, shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId,quantity)

        # 打印
        Printpickingbill().print_link(cookies, 2, stockupbilldata["stockUpBillId"],
                                      stockupbilldata["sourceCode"], purchaserId, operaterName)

        return stockupbilldata

    def stockupbill_print(self,cookies, shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId):
        #创建备货单按件
        stockupbilldata=StockupBill().create_stockupbill_link(cookies, shopId, shopAccount, warehouseId,targetWarehouseId,
                                                                          operateDivisionId, operaterId, operaterName,
                                                                          purchaserId,
                                                                          product_code, salesPlanDate,
                                                                          expectedShelfDate, supplierId, companyId)
        # 打印
        Printpickingbill().print_link(cookies, 2, stockupbilldata["stockUpBillId"],
                                      stockupbilldata["sourceCode"], purchaserId, operaterName)
        return stockupbilldata


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    #创建备货单按箱-打印
    #Printpickingbill().stockupbill_box_print(cookies, 161,"LIPENG", 150,350, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
    #                                      30,3)

    #创建备货单按件-打印
    Printpickingbill().stockupbill_print(cookies, 161,"LIPENG", 150,350, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
                                          30)