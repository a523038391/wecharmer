# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/20 下午3:33
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : loadingadvice.py
# @Project : wecharmer
import json
import time
from datetime import datetime, timedelta

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from util import httpUtil


class LoadingAdvice:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        # 如果你只需要年月日，不需要时间部分，可以将其格式化为字符串
        self.formatted_date = new_date.strftime('%Y-%m-%d')

    def create_loadingadvice(self,cookies,billOfLadingCode,sourceBillCategory,warehouseId,warehouseName,sourceBillId):
        """
        创建装柜通知
        :param billOfLadingCode:提单号
        :param warehouseId:出发仓
        :param sourceBillId:来源单据id
        :param loadingAdviceType:装柜方式
        :param sourceBillCategory:来源单据类型
        :param containerId:货柜类型
        :return:
        """
        url = f"{waveecharmer_Host}/api/loadingadvice"
        payload = {
            "id": 0,
            "loadingAdviceBillCode": "",
            "billOfLadingCode": billOfLadingCode,
            "loadingAdviceType": 1,
            "sourceBillCategory": sourceBillCategory,
            "expectLoadingTime": self.formatted_date,
            "containerId": 4,
            "volume": 3375,
            "loadWeight": 150,
            "remark": "",
            "address": "",
            "driverContactPerson": "",
            "driverTel": "",
            "warehouseName": warehouseName,
            "warehouseId": warehouseId,
            "attachmentDetails": [],
            "containerNo": "",
            "leadSealingNumber": "",
            "carNumer": "",
            "loadingAdviceBillDetails": [
                {
                    "sourceBillId": sourceBillId
                }
            ]
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("创建备货单主表信息resp-----------\n" + resp.text)
        return resp

    def query_loadingadvice(self, url, cookies):
        """
        查询装柜通知
        :return:
        """
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("查询装柜通知resp-----------\n" + resp.text)
        return resp

    def confirmshipment_loadingadvice(self, cookies,loadingadviceid):
        """
        确认发货
        :param loadingadviceid:装柜通知单id
        :return:
        """
        url = f"{waveecharmer_Host}/api/loadingadvice/confirmshipment/{loadingadviceid}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("确认发货resp-----------\n" + resp.text)
        return resp

    def loadingadvice_link(self,cookies,billOfLadingCode,sourceBillCategory,warehouseId,warehouseName,sourceBillId,sourceBillCode):
        #创建装柜通知
        LoadingAdvice().create_loadingadvice(cookies,billOfLadingCode,sourceBillCategory,warehouseId,warehouseName,sourceBillId)
        #查询装柜通知
        url = f"{waveecharmer_Host}/api/loadingadvice/page?loadingAdviceBillStatuses=1,2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&sourceBillCode={sourceBillCode}&billOfLadingCode=&pageIndex=1&pageSize=10"
        LoadingAdvice_tesp =LoadingAdvice().query_loadingadvice( url, cookies)
        loadingadviceid=json.loads(LoadingAdvice_tesp.text)["result"]["items"][0]["id"]

        time.sleep(2)

        #确认发货
        LoadingAdvice().confirmshipment_loadingadvice(cookies,loadingadviceid)





if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    LoadingAdvice().loadingadvice_link(cookies,"3242222",507,"150","李朋自营仓",1158,"DC24082800026")
