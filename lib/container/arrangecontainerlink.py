# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2025/3/4 下午3:04
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : arrangecontainerlink.py
# @Project : wecharmer

import json
import math
import time
from datetime import datetime, timedelta
import random

import requests

from conf.baseconfig import waveecharmer_Host
from lib.container.arrangecontainerbill import ArrangeContainerBill
from lib.container.waitcontainerbill import WaitContainerBill
from lib.firstleg.inspection import Inspection
from lib.firstleg.loadingadvice import LoadingAdvice
from lib.firstleg.scanpacking import ScanPacking
from lib.login import Login

class ArrangeContainerLink:
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



    #海外仓创建已排柜-验货
    def arrangecontainer_inspection_oversea_link(self, cookies,sourceBillCategory, shopId, warehouseId,warehouseName, warehouseId_entity, operateDivisionId,
                                     purchaserId,purchaserName,
                                     targetWarehouseId,
                                     product_code, quantity):

        #创建已排柜
        arrangecontainer_data=ArrangeContainerBill().create_arrangecontainer_link( cookies, shopId, warehouseId, warehouseId_entity, operateDivisionId,
                                     purchaserId,
                                     targetWarehouseId,
                                     product_code, quantity)

        #创建验货申请报告
        Inspection().create_arrangecontainer_inspection_link(cookies,arrangecontainer_data["id"],purchaserId)


        #备货单-拣货装箱
        ScanPacking().arrangecontainer_stockupbill_scanpacking_box_link(cookies, arrangecontainer_data["sourceType"], arrangecontainer_data["stockUpBillId"],arrangecontainer_data["sourceCode"],

                                         purchaserId, purchaserName)


        #装柜通知

        LoadingAdvice().arrangecontainer_loadingadvice_link(cookies, sourceBillCategory, warehouseId, warehouseName,
                                           arrangecontainer_data["id"], arrangecontainer_data["arrangecontainercode"])


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    ArrangeContainerLink().arrangecontainer_inspection_oversea_link(cookies,"607" ,161, 15,"恒丰仓库" ,150, 5, 303, "李朋",189, "A5-181", 3)
