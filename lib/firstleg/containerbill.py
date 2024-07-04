# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/20 上午11:25
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : containerbill.py
# @Project : wecharmer
import json
from datetime import datetime

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.deliverybill import DeliveryBill
from lib.login import Login
from util import httpUtil


class ContainerBill:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 如果你只需要年月日，不需要时间部分，可以将其格式化为字符串
        self.formatted_date = now.strftime('%Y-%m-%d')

    def get_containerbill(self, cookies, billNo):
        """
        根据提单号查询货柜列表
        :param billNo:提单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/page?containerBillStatus=1,2,3&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&ladingNos=%22{billNo}%22&pageIndex=1&pageSize=10"
        print(url)
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("根据提单号查询货柜列表resp-----------\n" + resp.text)
        return resp

    def create_containerbill(self, cookies,sourceBillType,vouchingClerkId,vouchingClerkName,ladingNo,deliveryBillId):
        """
        创建货柜列表
        :param ladingNo:提单号
        :param sourceBillType:来源单据类型
        :param departurePortId:起运港id
        :param destinationPortId:目的港id
        :param vouchingClerkId:单证员id
        :param vouchingClerkName:单证员名称
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill"
        payload = {
            "remark": "",
            "sourceBillType": sourceBillType,
            "containerBillCode": "",
            "departurePortId": 1,
            "destinationPortId": 8,
            "vouchingClerkId": vouchingClerkId,
            "vouchingClerkName": vouchingClerkName,
            "containerNo": "",
            "storageNo": "",
            "ladingNo": ladingNo,
            "freightForwardingId": None,
            "transportationTypeId": None,
            "shipVoyage": "",
            "estimatedSailingDate": None,
            "estimatedArrivalDate": None,
            "estimatedEntryDate": None,
            "actualLoadingDate": self.formatted_date,
            "actualSailingDate": None,
            "actualArrivalDate": None,
            "actualEntryDate": None,
            "id": 298,
            "status": 1,
            "departurePortName": None,
            "destinationPortName": None,
            "freightForwardingName": None,
            "transportationTypeName": None,
            "promisedArrivalDays": 0,
            "deliveryBillIds": [
                deliveryBillId
            ]
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("创建货柜列表resp-----------\n" + resp.text)
        return resp

    def create_containerbill_link(self,cookies,sourceCode,sourceBillType,vouchingClerkId,vouchingClerkName,ladingNo):
        #查询出货单
        url = f"{waveecharmer_Host}/api/deliverybill/page?deliveryBillStates=1,2,3,4&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&sourceCodes=%22{sourceCode}%22&pageIndex=1&pageSize=10"
        DeliveryBill_resp=DeliveryBill().query_deliverybill(url,cookies)
        deliveryBillId=json.loads(DeliveryBill_resp.text)['result']["items"][0]["id"]

        #创建货柜列表
        ContainerBill_resp=ContainerBill().create_containerbill( cookies,sourceBillType,vouchingClerkId,vouchingClerkName,ladingNo,deliveryBillId)
        containerBillCode=json.loads(ContainerBill_resp.text)['result']["containerBillCode"]
        return containerBillCode

if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    #ContainerBill().get_containerbill(cookies, "EGLV143470577152")
    ContainerBill().create_containerbill_link(cookies,"BH24062000052",502,303,"李朋","3453353534")
