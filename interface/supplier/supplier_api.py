# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/5/27 上午10:07
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : supplier_api.py
# @Project : wecharmer
import requests

from conf.baseconfig import waveecharmer_Host


class Supplier_Api:
    def __init__(self):
        pass


    def get_supplierstockinv1_originorderinfo(self, cookies, purchaseorderv1id,originOrderType):
        """
        获取来源单据的商品明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierstockinv1/originorderinfo?originOrderId={purchaseorderv1id}&originOrderType={originOrderType}"
        resp = requests.get(url=url, headers=cookies)
        print("获取来源单据的商品明细resp-----------\n" + resp.text)
        return resp

    def create_supplierstockinv1(self, cookies, payload):
        """
        创建工厂入库单
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierstockinv1/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建工厂入库单resp-----------\n" + resp.text)
        return resp

    def submit_supplierstockinv1(self, cookies, id):
        """
        提交工厂入库单
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierstockinv1/{id}/submit"
        resp = requests.post(url=url, headers=cookies)
        print("提交工厂入库单resp-----------\n" + resp.text)
        return


    def page_supplierinventoryv1(self, cookies, payload):
        """
        按采购单+SkU聚合分页查询供应商库存
        :return:
        """
        url = f"{waveecharmer_Host}/api/supplierinventoryv1/page/purchase-order-sku"
        resp = requests.post(url=url, headers=cookies,json=payload)
        print("按采购单+SkU聚合分页查询供应商库存resp-----------\n" + resp.text)
        return resp