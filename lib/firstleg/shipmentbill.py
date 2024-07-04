# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/7/3 下午3:13
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : shipmentbill.py
# @Project : wecharmer
import json
from wsgiref import headers

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from datetime import datetime, timedelta

from lib.storage.stock import Stock


class ShipmentBill:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")

    def query_fbashipmentinfo_page(self, url, cookies):
        """
        查询货件列表
        :return:
        """

        resp = requests.get(url=url, headers=cookies)
        print("查询货件列表resp-----------\n" + resp.text)
        return resp

    def get_fbashipmentinfo_details(self, url, cookies):
        """
        查询货件明细
        :return:
        """
        resp = requests.get(url=url, headers=cookies)
        print("查询货件明细resp-----------\n" + resp.text)
        return resp

    def create_fab_shipmentbill(self, cookies, payload):
        """
        创建fab发货单
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/fba"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建发货单resp-----------\n" + resp.text)
        return resp

    def create_fab_shipmentbill_item(self, shipmentbillid, cookies, payload):
        """
        创建fab发货单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/shipmentbill/{shipmentbillid}/fba/item"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建fab发货单明细resp-----------\n" + resp.text)
        return resp


    def shipmentbill_allocate(self,shipmentbillid, cookies, payload):
        url = f"{waveecharmer_Host}/api/shipmentbill/{shipmentbillid}/allocate"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("分配库存resp-----------\n" + resp.text)
        return resp




    def fba_shipmentbill_link(self, cookies, fbaShipmentCode, warehouseId, targetWarehouseId, operateDivisionId, shopId,
                              skucode, skuIds):
        """
        创建发货单链路
        :param sendOutGoodsType:仓库中转类型
        :param warehouseId:发货仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param shipmentBillStatus:发货单状态
        :param shipmentType:按箱 按件
        :return:
        """
        try:
            # 根据货件号查询货件列表
            fbashipmentinfo_url = f"{waveecharmer_Host}/api/fbashipmentinfo/page?shipmentStatus=1,2,3,6,7,8,9,10,11&isEmptyReferenceId=false&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&fbaShipmentCode={fbaShipmentCode}&pageIndex=1&pageSize=10"
            fbashipmentinfo_resp = ShipmentBill().query_fbashipmentinfo_page(fbashipmentinfo_url, cookies)
            sourceShipmentInfoId = json.loads(fbashipmentinfo_resp.text)["result"]["items"][0]["id"]

            # 创建发货单
            shipmentbill_payload = {
                "remark": "",
                "shipmentBillCode": None,
                "sendOutGoodsType": 1,
                "expectedDeliveryTime": self.formatted_date,
                "sourceShipmentInfoId": sourceShipmentInfoId,
                "warehouseId": warehouseId,
                "shipmentBillStatus": 11,
                "targetWarehouseId": targetWarehouseId,
                "shopId": shopId,
                "shippingAddress": "1111111111111111",
                "attachments": [],
                "productShipmentType": None,
                "sourceShipmentInfoCode": None,
                "operateDivisionId": operateDivisionId,
                "shipmentType": 0
            }
            print(shipmentbill_payload)
            shipmentbill_resp = ShipmentBill().create_fab_shipmentbill(cookies, shipmentbill_payload)
            shipmentbillid = json.loads(shipmentbill_resp.text)["result"]["id"]
            shipmentBillCode=json.loads(shipmentbill_resp.text)["result"]["shipmentBillCode"]

            # 查询货件明细
            fbashipmentinfo_details_url = f"{waveecharmer_Host}/api/fbashipmentinfo/{sourceShipmentInfoId}/details/page?operateDivisionIds=2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&skuCodes=%22{skucode}%22&pageIndex=1&pageSize=10"
            fbashipmentinfo_item_resp=ShipmentBill().get_fbashipmentinfo_details(fbashipmentinfo_details_url,cookies)
            fnSku= json.loads(fbashipmentinfo_item_resp.text)["result"]["items"][0]["fnSku"]
            sellerSku=json.loads(fbashipmentinfo_item_resp.text)["result"]["items"][0]["sellerSku"]
            # 查询库存信息
            get_batchstocks_url = f"{waveecharmer_Host}/api/stock/batchstocks/groupByShop-OperateDivision-StockType?goodOrDefectives=1&skuIds={skuIds}&shopIds={shopId}&warehouseIds={warehouseId}&operateDivisionIds=2&stockTypes=1&pageSize=10000"
            Stock().get_batchstocks(get_batchstocks_url,cookies)

            # 创建fab发货单明细

            shipmentbill_item_payload = {
                "items": [
                    {
                        "sellerSku": sellerSku,
                        "fnSku": fnSku,
                        "skuId": skuIds,
                        "plannedShipmentQuantity": 10
                    }
                ],
                "thirdPartyWarehouseReferences": [],
                "boxes": []
            }
            ShipmentBill().create_fab_shipmentbill_item(shipmentbillid, cookies, shipmentbill_item_payload)

            #分配库存
            shipmentbill_allocate_payload={}
            ShipmentBill().shipmentbill_allocate(shipmentbillid, cookies,shipmentbill_allocate_payload)

        except Exception as e:
            print("创建发货单出错",e)
            shipmentbillid=None
            shipmentBillCode=None

        shipmentbilldata = {"skucode": skucode, "shipmentbillid": int(shipmentbillid), "shipmentBillCode": shipmentBillCode}

        return shipmentbilldata



if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    ShipmentBill().fba_shipmentbill_link(cookies, "FBA16K8TWW9P", 150, 135, 2, 122, "B-XF2-00A-D-9-0125-QGR-XS",1002)
