# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/4/21 下午3:08
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : purchaseorder_api.py
# @Project : wecharmer


import requests

from conf.baseconfig import waveecharmer_Host
class  PurchaseOrder_Api:
    def __init__(self):
        pass

    def create_purchaseorderv1(self, cookies, payload):
        """
        创建采购单v1
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorderv1/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建采购单v2resp-----------\n" + resp.text)
        return resp

    def get_purchaseorderv1_details(self, cookies, purchaseorderv1id):
        """
        根据id获取采购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorderv1/details/fullall?purchaseOrderIds={purchaseorderv1id}"

        resp = requests.get(url=url, headers=cookies)
        print("获取采购单明细resp-----------\n" + resp.text)
        return resp

    def get_purchaseorder_groups(self, cookies, purchaseorderv1id):
        """
        根据id获取采购单明细分组
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorderv1/{purchaseorderv1id}/detail-groups"
        resp = requests.get(url=url, headers=cookies)
        print("获取采购单明细分组resp-----------\n" + resp.text)
        return resp


    def purchaseorderv1_review(self, purchaseorderv1id, cookies, payload):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorderv1/{purchaseorderv1id}/approve-status-review"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("送审resp-----------\n" + resp.text)
        return resp

    def page_purchaseorderv1(self, cookies, payload):
        """
        查询采购单列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorderv1/page"
        resp = requests.post(url=url, headers=cookies,json=payload)
        print("查询采购单列表resp-----------\n" + resp.text)
        return resp


    def purchaseorderv1_quantity(self, cookies, payload):
        """
        采购单跟新交货数量
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorderv1/sync-delivered-quantity/by-flow-step"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("采购单跟新交货数量resp-----------\n" + resp.text)
        return resp