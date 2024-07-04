# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/12 上午11:59
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : product.py
# @Project : wecharmer
from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from util import httpUtil


class Product:
    def __init__(self):
        pass

    def query_skulist(self,cookies,skucode):
        url = f"{waveecharmer_Host}/api/product/sku/page"
        payload = {
            "entityInfoType": 1,
            "status": [
                2,
                3
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "codes": [
                skucode
            ],
            "pageIndex": 1,
            "pageSize": 10
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("根据sku编码查询sku信息resp-----------\n" + resp.text)
        return resp



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    Product().query_skulist(cookies,"LIPENG456-B-P")