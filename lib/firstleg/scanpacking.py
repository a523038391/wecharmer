# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/19 下午6:59
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : scanpacking.py
# @Project : wecharmer
import json

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from util import httpUtil


class ScanPacking:
    def __init__(self):
        pass

    def scan_billcode(self, cookies, sourceCode):
        """
        扫描单号并茨取单据信息
        :param sourceCode:来源单据code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/scan/billcode/{sourceCode}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("扫描单号并茨取单据信息resp-----------\n" + resp.text)

    def scan_productcode(self, cookies, sourceType, sourceId, sourceCode, skucode):
        """
        扫描产品并获取装箱信息
        :param sourceCode:来源单据code
        :param sourceType:来源单据类型
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/scan/productcode?sourceType={sourceType}&sourceId={sourceId}&sourceCode={sourceCode}&productCode={skucode}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("扫描产品并获取装箱信息resp-----------\n" + resp.text)
        return resp

    def packing_scanpacking(self, cookies, sourceType, sourceId, sourceCode, skucode):
        """
        装箱
        :param sourceCode:来源单据code
        :param sourceType:来源单据类型
        :return:
        """

        # 扫描产品并获取装箱信息
        scan_productcode_resp = ScanPacking().scan_productcode(cookies, sourceType, sourceId, sourceCode, skucode)
        skudata = json.loads(scan_productcode_resp.text)["result"]
        print(skudata)
        dict = {"packingQuantity": 10, "remainingQuantityCpu": 0, "transQtyValid": False}
        skudata.update(dict
                       )
        url = f"{waveecharmer_Host}/api/scanpacking/packing"

        payload = {
            "billCode": sourceCode,
            "boxId": 1,
            "totalWeightWithBox": 500,
            "detailList": [
                skudata

            ]
        }
        print(payload)
        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("装箱resp-----------\n" + resp.text)
        return resp

    def submit_scanpacking(self, cookies, sourceType, sourceId, sourceCode):
        """
        提交装箱审核
        :param sourceType:来源单类型
        :param sourceId:来源单id
        :param sourceCode:来源单code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/all/submit"
        payload = {
            "sourceType": sourceType,
            "sourceId": sourceId,
            "sourceCode": sourceCode
        }
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("提交装箱审核resp-----------\n" + resp.text)
        return resp

    def process_scanpacking(self, cookies, sourceType, sourceId, sourceCode):
        """
        装箱审核
        :param sourceType:来源单类型
        :param sourceId:来源单id
        :param sourceCode:来源单code
        :return:
        """
        url = f"{waveecharmer_Host}/api/scanpacking/process"
        payload = {
            "sourceType": sourceType,
            "sourceId": sourceId,
            "sourceCode": sourceCode,
            "auditStatus": True,
            "failReason": ""
        }
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("装箱审核resp-----------\n" + resp.text)
        return resp

    def scanpacking_link(self,cookies,sourceType, sourceId,sourceCode,skucode):
        try:
            #扫描单号并茨取单据信息
            ScanPacking().scan_billcode(cookies,sourceCode)
            #装箱
            ScanPacking().packing_scanpacking(cookies,sourceType, sourceId,sourceCode,skucode)
            #提交装箱审核
            ScanPacking().submit_scanpacking(cookies,sourceType, sourceId,sourceCode)
            #装箱审核
            ScanPacking().process_scanpacking(cookies,sourceType, sourceId,sourceCode)

        except Exception as e:
            print("装箱出错",e)




if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # ScanPacking().scan_billcode(cookies, "BH24061900005")
    ScanPacking().packing_scanpacking(cookies, 2, "724", "BH24061900004", "LIPENG456-B-P")
