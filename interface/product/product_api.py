# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 15:31
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : product_api.py
# @Project : wecharmer
from ftplib import parse150

import requests

from conf.baseconfig import waveecharmer_Host

class Product_Api:
    def __init__(self):
        pass

    def query_skulist_v1(self, cookies, payload):
        """
        查询sku信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/sku/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("查询sku信息resp-----------\n" + resp.text)
        return resp