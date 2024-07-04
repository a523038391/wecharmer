# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/19 下午5:34
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : printpickingbill.py
# @Project : wecharmer
from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from util import httpUtil


class Printpickingbill:

    def __init__(self):
        pass

    def assign_picker(self, cookies,sourceType, sourceId, sourceCode, pickerId, pickerName):
        """
        指派拣货员
        :param sourceType:来源单据类型(1=FBA发货单,2=海外仓备货单)
        :param sourceId:来源单据id
        :param sourceCode:来源单据编号
        :param pickerId:拣货员id
        :param pickerName:拣货员名称
        :return:
        """
        url = f"{waveecharmer_Host}/api/printpickingbill/assign/picker"
        payload = {
            "sourceType": sourceType,
            "sourceId": sourceId,
            "sourceCode": sourceCode,
            "pickerId": pickerId,
            "pickerName": pickerName
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("指派拣货员resp-----------\n" + resp.text)
        return resp

    def print_pickingbill(self,cookies,sourceType,sourceId,sourceCode):
        """
        打印
        :param sourceType:来源单据类型(1=FBA发货单,2=海外仓备货单)
        :param sourceId:来源单据id
        :param sourceCode:来源单据编号
        :param printtemplateCode:打印模板code
        :return:
        """
        url = f"{waveecharmer_Host}/api/printpickingbill/confirm/print"
        payload = {
            "sourceType": sourceType,
            "sourceId": sourceId,
            "sourceCode": sourceCode,
            "printtemplateCode": "JHD002"
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("打印resp-----------\n" + resp.text)
        return resp


    def print_link(self,cookies,sourceType,sourceId,sourceCode,pickerId, pickerName):
        try:
            #指派拣货员
            Printpickingbill().assign_picker(cookies,sourceType, sourceId, sourceCode, pickerId, pickerName)

            #打印
            Printpickingbill().print_pickingbill(cookies,sourceType,sourceId,sourceCode)

        except Exception as e:
            print("打印出错",e)



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    #Printpickingbill().assign_picker(cookies, 2,725, "BH24062000032", 303, "李朋")
    #Printpickingbill().print_pickingbill(cookies,2,755,"BH24062000033")
    Printpickingbill().print_link(cookies,2,754,"BH24062000032",303, "李朋")