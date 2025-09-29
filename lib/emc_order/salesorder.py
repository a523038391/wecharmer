# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2025/9/26 上午10:45
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : salesorder.py
# @Project : wecharmer
import json
import random
import time
from datetime import datetime, timedelta

from interface.emc_order.order_api import Oreder_Api
from lib.login import Login


class Salesorder:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=30)

        # 将时间差加到当前日期上
        new_date = now + three_days

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")

        self.random_number = ''.join(str(random.randint(0, 9)) for _ in range(10))

    def create_salesorder_link(self, cookies):
        """
        创建销售订单链路
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

        # 创建订舱单
        salesorder_payload = {
            "salesOrderCode": "lipeng" + self.random_number,
            "contractNo": "lipeng" + self.random_number,
            "clientId": 7,
            "expectedDeliveryDate": self.formatted_date,
            "remark": None,
            "items": [
                {
                    "productCode": "KPBL002",
                    "quantity": 100
                },
                {
                    "productCode": "KPBL001",
                    "quantity": 200
                }
            ]
        }

        salesorder_resp = Oreder_Api().create_salesorder(cookies, salesorder_payload)
        salesorderid = json.loads(salesorder_resp.text)["result"]

        # 获取销售订单详情
        get_salesorder = Oreder_Api().get_salesorder(cookies, salesorderid)
        get_salesorder_result=json.loads(get_salesorder.text)["result"]

        items = []

        for item in get_salesorder_result["items"]:
            # 查询产品对外关系分页
            tems_dict = {
                    "id":item["id"],
                    "deliveryTime": get_salesorder_result["expectedDeliveryDate"]
                }

            items.append(tems_dict)


        # 确认答复交期
        confirmdeliverytime_payload = {
            "salesOrderId": salesorderid,
            "items": items
        }

        confirmdeliverytime_resp=Oreder_Api().create_confirmdeliverytime(cookies,confirmdeliverytime_payload)


if __name__ == '__main__':
    cookies = Login.loginWecharmer_emc()
    Salesorder().create_salesorder_link(cookies)
