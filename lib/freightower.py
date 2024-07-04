# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/13 下午4:29
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : freightower.py
# @Project : wecharmer
import json

from conf.baseconfig import freightower_Host
from lib import login
from lib.login import Login
from util import httpUtil


class Freightower:

    def __init__(self):
        pass

    def container_match(self, cookies, billNo):
        """
        船公司匹配
        :param billNo:提单号
        :return:
        """

        url = f"{freightower_Host}/container/match"

        payload = {
            "businessNumber": billNo
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("船公司匹配resp-----------\n" + resp.text)
        return resp

    def query_transportation(self, cookies, billNo, carrierCode):
        """
        查询海运综合信息
        :param billNo:提单号
        :param carrierCode:船公司代码
        :return:
        """
        url = f"{freightower_Host}/application/v1/query"
        payload = {
            "billNo": billNo,
            "containerNo": "",
            "carrierCode": carrierCode,
            "portCode": "",
            "isExport": "",
            "businessNo": ""
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("海运综合跟踪resp-----------\n" + resp.text)
        return resp

    def port_subscribe(self, cookies, billNo, portCode):
        """
        码头综合订阅
        :param billNo:提单号
        :param portCode:港口编码
        :return:
        """
        url = f"{freightower_Host}/terminal/port/event/subscribe"
        payload = {
            "businessNumber": billNo,
            "portCode": portCode,
            "ieid": "E"
        }
        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("码头综合订阅resp-----------\n" + resp.text)
        return resp

    def get_port_subscribe(self, cookies, subscriptionId):
        """
        码头综合跟踪查询
        :param subscriptionId:订阅号
        :return:
        """
        url = f"{freightower_Host}/terminal/port/event/shipment?subscriptionId={subscriptionId}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("码头综合跟踪查询resp-----------\n" + resp.text)
        return resp

    def get_cn_customs(self, cookies, billNo):
        """
        中国海关跟踪查询
        :param billNo:提单号
        :return:
        """
        url = f"{freightower_Host}/terminal/cn/customs/getBlnoDeclare?blno={billNo}&ieid=E"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("中国海关跟踪查询resp-----------\n" + resp.text)
        return resp

    def freightower_link(self, cookies, billNo, portCode):
        # 查询船公司
        match_resp = Freightower().container_match(cookies, billNo)
        if json.loads(match_resp.text)["statusCode"] == 20000:
            # 船公司编码
            carrierCode = json.loads(match_resp.text)["data"]["matchCarrierCode"][0]
            print("船公司编码------\n" + carrierCode)

        else:
            carrierCode = None
            print(match_resp.text)

        # 海运综合跟踪
        transportation_resp = Freightower().query_transportation(cookies, billNo, carrierCode)
        if json.loads(transportation_resp.text)["statusCode"] == 20000:
            # 航名
            vessel = json.loads(transportation_resp.text)["data"]["result"]["firstVessel"]["vessel"]
            # 航次
            voyage = json.loads(transportation_resp.text)["data"]["result"]["firstVessel"]["voyage"]
            # 订单状态
            statuscategory = json.loads(transportation_resp.text)["data"]["result"]["statusCategory"]

            places=json.loads(transportation_resp.text)["data"]["result"]["places"]
            for rom in places:
                if rom["type"] == 2:
                    # 预计出港时间
                    receipt_etd=rom["etd"]
                    #实际开船日期
                    receipt_atd=rom["atd"]
                    if receipt_atd== None :
                        receipt_atd=rom["atd_ais"]

                elif rom["type"] == 4:
                    # 预计到港时间
                    delivery_eta=rom["eta"]

                    # 实际到港时间
                    delivery_ata=rom["ata"]
                    if delivery_ata == None :
                        delivery_ata=rom["atb_ais"]
                        if delivery_ata == None :
                            delivery_ata=rom["ata_ais"]
            # 预计出港时间
            #receipt_etd = json.loads(transportation_resp.text)["data"]["result"]["receipt"]["etd"]
            # 实际出港时间
            #receipt_atd = json.loads(transportation_resp.text)["data"]["result"]["receipt"]["atd"]
            # 预计到港时间
            #delivery_eta = json.loads(transportation_resp.text)["data"]["result"]["delivery"]["eta"]
            # 实际到港时间
            #delivery_ata = json.loads(transportation_resp.text)["data"]["result"]["delivery"]["ata"]
            print(
                f"船名/航次:{vessel}/{voyage}\n订单状态：{statuscategory}\n预计出港时间：{receipt_etd}\n实际出港时间：{receipt_atd}\n预计到港时间：{delivery_eta}\n实际到港时间：{delivery_ata}")
        else:

            vessel = None
            voyage = None
            statuscategory = None
            receipt_etd = None
            receipt_atd = None
            delivery_eta = None
            delivery_ata = None
            print(transportation_resp.text)

        # 码头综合订阅
        port_subscribe_resp = Freightower().port_subscribe(cookies, billNo, portCode)
        if json.loads(port_subscribe_resp.text)["statusCode"] == 20000:
            subscribe_data = json.loads(port_subscribe_resp.text)["data"]
            print("码头综合订阅id：" + subscribe_data)

        else:
            subscribe_data = None
            print(port_subscribe_resp.text)

        # 码头综合查询
        get_port_subscribe_resp = Freightower().get_port_subscribe(cookies, subscribe_data)
        # print(json.loads(get_port_subscribe_resp.text)["statusCode"])
        if json.loads(get_port_subscribe_resp.text)["statusCode"] == 20000:
            # 物流跟踪
            try:
                print(get_port_subscribe_resp.text)
                transportEvents = json.loads(get_port_subscribe_resp.text)["data"]["shipment"]["transportEvents"]

                print(transportEvents)
                for rom in transportEvents:
                    if rom["eventClassifier"] == "EST" and rom["transportCall"]["facilityCategory"] == "BRTH" and rom[
                        "transportEventCategory"] == "ARRI":
                        estimatedArrivalTime = rom["eventTime"]
                        print(f"预计抵港时间：{estimatedArrivalTime}")

                    elif rom["eventClassifier"] == "EST" and rom["transportCall"]["facilityCategory"] == "BRTH" and rom[
                        "transportEventCategory"] == "DEPA":
                        estimatedDepartureTime = rom["eventTime"]
                        print(f"计划离港时间：{estimatedDepartureTime}")

                    elif rom["eventClassifier"] == "ACT" and rom["transportCall"]["facilityCategory"] == "POTE" and rom[
                        "transportEventCategory"] == "CYOP":
                        startLoadingTime = rom["eventTime"]
                        print(f"进箱开始时间：{startLoadingTime}")

                    elif rom["eventClassifier"] == "ACT" and rom["transportCall"]["facilityCategory"] == "POTE" and rom[
                        "transportEventCategory"] == "CYCL":
                        endLoadingTime = rom["eventTime"]
                        print(f"进箱截至时间：{endLoadingTime}")

                    elif rom["eventClassifier"] == "ACT" and rom["transportCall"]["facilityCategory"] == "POTE" and rom[
                        "transportEventCategory"] == "SICT":
                        cutoffOrdersTime = rom["eventTime"]
                        print(f"截单时间：{cutoffOrdersTime}")

                    elif rom["eventClassifier"] == "ACT" and rom["transportCall"]["facilityCategory"] == "POTE" and rom[
                        "transportEventCategory"] == "CUCT":
                        cutoffCustomsClearanceTime = rom["eventTime"]
                        print(f"截关时间：{cutoffCustomsClearanceTime}")

                    elif rom["eventClassifier"] == "ACT" and rom["transportCall"]["facilityCategory"] == "BRTH" and rom[
                        "transportEventCategory"] == "ARRI":
                        actualArrivalTime = rom["eventTime"]
                        print(f"实际靠港时间：{actualArrivalTime}")

                    elif rom["eventClassifier"] == "ACT" and rom["transportCall"]["facilityCategory"] == "BRTH" and rom[
                        "transportEventCategory"] == "DEPA":
                        actualDepartureTime = rom["eventTime"]
                        print(f"实际离港时间：{actualDepartureTime}")

            except Exception as e:
                estimatedArrivalTime = None
                estimatedDepartureTime = None
                startLoadingTime = None
                endLoadingTime = None
                cutoffOrdersTime = None
                cutoffCustomsClearanceTime = None
                actualArrivalTime = None
                actualDepartureTime = None
                print("发生异常：", e)

        else:
            estimatedArrivalTime = None
            estimatedDepartureTime = None
            startLoadingTime = None
            endLoadingTime = None
            cutoffOrdersTime = None
            cutoffCustomsClearanceTime = None
            actualArrivalTime = None
            actualDepartureTime = None
            print(get_port_subscribe_resp.text)

        try:
            customs_resp = Freightower().get_cn_customs(cookies, billNo)
            if json.loads(customs_resp.text)["statusCode"] == 20000:

                # 预配仓单时间
                status = json.loads(customs_resp.text)["data"]["data"]["status"]
                print(status)

                for rom in status:
                    if rom["statuscd"] == "BLR":
                        preparingShippingTime = rom["noticedate"]
                        print(f"预配单时间：{preparingShippingTime}")
                        break

            else:
                preparingShippingTime = None
                print(customs_resp.text)
        except Exception as e:
            preparingShippingTime = None
            print("发生异常：", e)

        freightower_data = {"carrierCode": carrierCode,
                            "vessel": vessel,
                            "voyage": voyage,
                            "statuscategory": statuscategory,
                            "receipt_atd":receipt_atd,
                            "receipt_etd": receipt_etd,
                            "delivery_eta":delivery_eta,
                            "delivery_ata":delivery_ata,
                            "preparingShippingTime": preparingShippingTime}
        freightower_json = json.dumps(freightower_data)

        print(freightower_json)
        return freightower_json


if __name__ == '__main__':
    cookies = Login.loginFreightower()
    # Freightower().container_match(cookies,"EGLV143470577152")
    Freightower().freightower_link(cookies, "278723706", "CNNGB")
    # Freightower().get_port_subscribe(cookies,342478679633305600)

