# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/20 下午5:11
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : deliverybill.py
# @Project : wecharmer
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