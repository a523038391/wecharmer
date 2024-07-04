# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/12 下午1:56
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stockupbill.py
# @Project : wecharmer
import json

from conf.baseconfig import waveecharmer_Host
from datetime import datetime, timedelta

from lib.login import Login
from lib.productandmaterial.product import Product
from util import httpUtil


class StockupBill:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)

        # 将时间差加到当前日期上
        new_date = now + three_days

        # 如果你只需要年月日，不需要时间部分，可以将其格式化为字符串
        self.formatted_date = new_date.strftime('%Y-%m-%d')


    def query_stockupbill(self,url,cookies):
        """
        查询备货单
        :return:
        """
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("查询备货单resp-----------\n" + resp.text)
        return resp



    def create_stockupbill(self, cookies, shopId, warehouseId, targetWarehouseId, operateDivisionId, platformEnName):
        """
        创建备货单主表信息
        :param shopId:商品id
        :param warehouseId:出发仓
        :param targetWarehouseId:目的仓
        :param operateDivisionId:运营事业部id
        :param platformEnName:平台名称
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/create"
        payload = {
            "stockUpBillCode": "",
            "sendOutGoodsType": 1,
            "shopId": shopId,
            "isFNSKU": False,
            "warehouseId": warehouseId,
            "targetWarehouseId": targetWarehouseId,
            "expectedDeliveryTime": self.formatted_date,
            "platformName": "抖音",
            "shippingAddress": "2311 York Rd",
            "attachmentDetail": [],
            "remark": "",
            "operateDivisionId": operateDivisionId,
            "platformEnName": platformEnName
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("创建备货单主表信息resp-----------\n" + resp.text)
        return resp






    def create_stockupbill_detail(self,cookies,stockUpBillId,skuId,skuImageUrl,thirdImageUrl,useImageSource,skuCode,skuName,sellerSkuCode):
        """
        创建备货单SKU详细信息
        :param skuId:商品id
        :param skuImageUrl:图片
        :param thirdImageUrl:三方图片
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/create"
        payload = {
            "stockUpBillId": stockUpBillId,
            "stockUpBillDetail": [
                {
                    "skuId": skuId,
                    "plannedShipmentQuantity": 10,
                    "skuImageUrl": skuImageUrl,
                    "thirdImageUrl": thirdImageUrl,
                    "useImageSource": useImageSource,
                    "skuCode": skuCode,
                    "oldSkuCode": "",
                    "skuName": skuName,
                    "sellerSkuCode": sellerSkuCode
                }
            ]
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("创建备货单SKU详细信息resp-----------\n" + resp.text)
        return resp


    def update_share_stockupbill(self,cookies,stockUpBillId):
        """
        备货单分配库存按件
        :param stockUpBillId:备货单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/share/update/{stockUpBillId}"
        print(url)
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "put", payload, cookies)
        print("备货单分配库存按件resp-----------\n" + resp.text)
        return resp


    def get_stockupbill_detail(self,cookies,stockUpBillId):
        """
        通过备货单id获取详情信息
        :param stockUpBillId:备货单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockupbill/detail/{stockUpBillId}"
        payload = {}
        resp = httpUtil.HttpUtil.make_http_request(url, "get", payload, cookies)
        print("通过备货单id获取详情信息resp-----------\n" + resp.text)
        return resp





    def create_stockupbill_link(self,cookies,skucode,shopId, warehouseId, targetWarehouseId, operateDivisionId, platformEnName):
        try:
            #获取商品信息
            item_resp=Product().query_skulist(cookies, skucode)
            skuId=json.loads(item_resp.text)["result"]["items"][0]["id"]
            skuImageUrl=json.loads(item_resp.text)["result"]["items"][0]["imageUrl"]
            thirdImageUrl=json.loads(item_resp.text)["result"]["items"][0]["thirdImageUrl"]
            useImageSource=json.loads(item_resp.text)["result"]["items"][0]["useImageSource"]
            skuCode=json.loads(item_resp.text)["result"]["items"][0]["code"]
            skuName=json.loads(item_resp.text)["result"]["items"][0]["cnName"]
            sellerSkuCode=json.loads(item_resp.text)["result"]["items"][0]["code"]

            #创建备货单主表信息
            stockupbill_resp=StockupBill().create_stockupbill(cookies, shopId, warehouseId, targetWarehouseId, operateDivisionId, platformEnName)
            stockUpBillId=json.loads(stockupbill_resp.text)["result"]
            #创建备货单SKU详细信息
            StockupBill().create_stockupbill_detail(cookies,stockUpBillId,skuId,skuImageUrl,thirdImageUrl,useImageSource,skuCode,skuName,sellerSkuCode)
            #备货单分配库存按件
            StockupBill().update_share_stockupbill(cookies,stockUpBillId)
            #通过备货单id获取详情信息
            stockupbill_detail_resp=StockupBill().get_stockupbill_detail(cookies,stockUpBillId)
            sourceCode=json.loads(stockupbill_detail_resp.text)["result"]["stockUpBillCode"]
            print(sourceCode)

        except Exception as e:
            print("创建备货单出错",e)
            stockUpBillId=None
            sourceCode=None

        stockupbilldata = {"skucode": skucode, "stockUpBillId": int(stockUpBillId), "sourceCode": sourceCode}
        print(stockupbilldata)
        return stockupbilldata







if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    StockupBill().create_stockupbill_link(cookies,"LIPENG456-B-P",161, 150, 11, 5, "Tiktok")
    #StockupBill().create_stockupbill(cookies, 161, 150, 11, 5, "Tiktok")

