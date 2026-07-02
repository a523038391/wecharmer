# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/4/20 上午10:38
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : applypurchasebill_api.py
# @Project : wecharmer

import requests

from conf.baseconfig import waveecharmer_Host
class  ApplyPurchaseBill_Api:
    def __init__(self):
        pass


    def create_applypurchasebillv2(self, cookies, payload):
        """
        创建申购单v2
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebillv2/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建申购单v2resp-----------\n" + resp.text)
        return resp

    def applypurchasebillv2_review(self, cookies, payload):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebillv2/toreview"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("送审resp-----------\n" + resp.text)
        return resp


    def page_applypurchasebillv2(self, cookies, payload):
        """
        分页查询申购单v2
        :return:
        """
        url = f"{waveecharmer_Host}/api/applypurchasebillv2/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("分页查询申购单v2resp-----------\n" + resp.text)
        return resp