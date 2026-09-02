# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 16:41
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : Printpickingbill_api.py
# @Project : wecharmer
import requests
import  time
from conf.baseconfig import waveecharmer_Host

class Printpickingbill_Api:
    def __init__(self):
        pass


    def assign_picker(self, cookies,payload):
        """
        指派拣货员
        :return:
        """
        url = f"{waveecharmer_Host}/api/printpickingbill/assign/picker"


        resp = requests.post(url=url, headers=cookies, json=payload)
        print("指派拣货员resp-----------\n" + resp.text)
        return resp

    def print_pickingbill(self,cookies,payload):
        """
        打印
        :return:
        """
        url = f"{waveecharmer_Host}/api/printpickingbill/confirm/print"


        resp = requests.put(url=url, headers=cookies, json=payload)
        print("打印resp-----------\n" + resp.text)
        return resp

    def scan_billcode(self, cookies, sourceCode):
        """
        扫描单号并茨取单据信息
        :param sourceCode:来源单据code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/scan/billcode/{sourceCode}"
        resp = requests.get(url=url, headers=cookies)
        print("扫描单号并茨取单据信息resp-----------\n" + resp.text)
        return resp

    def scanpacking_packingbybox(self, cookies, payload):
        """
        按箱装箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/packingByBox"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按箱装箱resp-----------\n" + resp.text)
        return resp

    def submit_scanpacking(self, cookies, payload):
        """
        提交装箱审核
        :param sourceType:来源单类型
        :param sourceId:来源单id
        :param sourceCode:来源单code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/all/submit"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("提交装箱审核resp-----------\n" + resp.text)
        return resp

    def process_scanpacking(self, cookies, payload):
        """
        装箱审核
        :param sourceType:来源单类型
        :param sourceId:来源单id
        :param sourceCode:来源单code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/process"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("装箱审核resp-----------\n" + resp.text)
        return resp


    def scan_all_productcode(self, cookies, sourceType, sourceId, sourceCode):
        """
        获取所有产品的装箱信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/scan/productcode/all?sourceType={sourceType}&sourceId={sourceId}&sourceCode={sourceCode}"
        resp = requests.get(url=url, headers=cookies)
        print("获取所有产品的装箱信息resp-----------\n" + resp.text)
        return resp


    def packing_scanpacking_v1(self, cookies, payload):
        """
        按件装箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/packing"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按件装箱resp-----------\n" + resp.text)
        return resp