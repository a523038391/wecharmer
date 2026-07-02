# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/5/27 下午1:14
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : inspection_api.py
# @Project : wecharmer
import requests

from conf.baseconfig import waveecharmer_Host


class Inspection_Api:
    def __init__(self):
        pass

    def create_inspection(self, cookies, payload):
        """
        创建验货申请
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建验货申请resp-----------\n" + resp.text)
        return resp


    def inspection_submit(self, cookies, inspectionid):
        """
        提交
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require/submit/{inspectionid}"
        resp = requests.put(url=url, headers=cookies)
        print("提交resp-----------\n" + resp.text)
        return resp

    def inspection_assign(self, cookies, inspectionid, purchaserId):
        """
        指派验货员
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require/assign/{inspectionid}/{purchaserId}"
        resp = requests.put(url=url, headers=cookies)
        print("指派验货员resp-----------\n" + resp.text)
        return resp

    def get_inspection_items(self, cookies, inspectionid):
        """
        查询验货单详情
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/require/items/{inspectionid}"
        resp = requests.get(url=url, headers=cookies)
        print("查询验货单详情resp-----------\n" + resp.text)
        return resp

    def get_inspection_list(self, cookies, url):
        """
        查询验货单列表
        :return:
        """
        resp = requests.get(url=url, headers=cookies)
        print("查询验货单列表resp-----------\n" + resp.text)
        return resp

    def create_inspection_report(self, cookies, payload):
        """
        创建验货报告
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/report"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建验货报告resp-----------\n" + resp.text)
        return resp

    def inspection_askapprove(self, cookies, inspection_report_id):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/inspection/report/askapprove/{inspection_report_id}"
        resp = requests.put(url=url, headers=cookies)
        print("送审resp-----------\n" + resp.text)
        return resp
