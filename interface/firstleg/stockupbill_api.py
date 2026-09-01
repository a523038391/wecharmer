# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 15:12
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stockupbill_api.py
# @Project : wecharmer
import requests

from conf.baseconfig import waveecharmer_Host

class Stockupbill_Api:
    def __init__(self):
        pass

    def create_stockupbill(self, cookies, payload):
        """
        创建备货单
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建备货单resp-----------\n" + resp.text)
        return resp

    def create_stockupbill_detail(self, cookies, payload):
        """
        创建备货单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建备货单明细resp-----------\n" + resp.text)
        return resp

    def get_stockupbill_detailbysku(self, cookies, stockUpBillId):
        """
        通过备货单id获取商品详情信息
        :param stockUpBillId:备货单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detailbysku/{stockUpBillId}"
        payload = {}
        resp = requests.get(url=url, headers=cookies)
        print("通过备货单id获取商品详情信息resp-----------\n" + resp.text)
        return resp

    def update_share_stockupbill_v1(self, cookies, payload):
        """
        备货单分配库存按件
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/share/update"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("备货单分配库存按件resp-----------\n" + resp.text)
        return resp



    def get_stockupbill_detail(self, cookies, stockUpBillId):
        """
        通过备货单id获取详情信息
        :param stockUpBillId:备货单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/{stockUpBillId}"
        payload = {}
        resp = requests.get(url=url, headers=cookies)
        print("通过备货单id获取详情信息resp-----------\n" + resp.text)
        return resp

    def update_share_stockupbill_box(self, cookies, payload):
        """
        分配库存按箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/box/share/update"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("分配库存按箱resp-----------\n" + resp.text)
        return resp