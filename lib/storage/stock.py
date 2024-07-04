# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/12 下午1:20
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stock.py
# @Project : wecharmer
import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from util import httpUtil


class Stock:
    def __init__(self):
        pass


    def get_batchstocks(self,url,cookies):
        resp = requests.get(url=url, headers=cookies)
        print("查询店铺运营事业部库存类型维度的批次库存resp-----------\n" + resp.text)
        return resp



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    #Stock().get_batchstocks(cookies,5452,161,150)