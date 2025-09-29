# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2025/9/26 上午10:34
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : order_api.py
# @Project : wecharmer
import requests

from conf.baseconfig import waveecharmer_emc_Host


class Oreder_Api:
    def __init__(self):
        pass


    def create_salesorder(self, cookies, payload):
        """
        创建销售订单
        :return:
        """
        url = f"{waveecharmer_emc_Host}/api/salesorder/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建销售订单resp-----------\n" + resp.text)
        return resp

    def get_salesorder(self, cookies, salesorderid):
        """
        获取销售订单
        :return:
        """
        url = f"{waveecharmer_emc_Host}/api/salesorder/get/{salesorderid}"
        resp = requests.get(url=url, headers=cookies)
        print("获取销售订单resp-----------\n" + resp.text)
        return resp


    def create_confirmdeliverytime(self, cookies, payload):
        """
        确认答复交期
        :return:
        """
        url = f"{waveecharmer_emc_Host}/api/salesorder/confirmdeliverytime"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("确认答复交期resp-----------\n" + resp.text)
        return resp