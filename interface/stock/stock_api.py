# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/1 13:54
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : stock_api.py
# @Project : wecharmer

import requests

from conf.baseconfig import waveecharmer_Host
class Stock_Api:

    def __init__(self):
        pass


    def create_purchase_order(self, cookies, payload):
        """
        创建采购入库
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbillv2/purchase-order"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建采购入库resp-----------\n" + resp.text)
        return resp

    def purchase_order_review(self, cookies, purchase_order_id):
        """
        入库单送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbillv2/approve-status/{purchase_order_id}/review"
        resp = requests.put(url=url, headers=cookies)
        print("入库单送审resp-----------\n" + resp.text)
        return resp

    def get_sku_dimension_detail(self, cookies, purchase_order_id):
        """
        获取入库单sku明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbillv2/sku-dimension-detail?id={purchase_order_id}&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=100"
        resp = requests.get(url=url, headers=cookies)
        print("获取入库单sku明细resp-----------\n" + resp.text)
        return resp

    def get_warehouse_location(self, cookies, warehouseId):
        """
        分页获取库位
        :return:
        """
        url = f"{waveecharmer_Host}/api/warehouse/location/page?warehouseId={warehouseId}&goodOrDefective=1&able=1&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=10"
        resp = requests.get(url=url, headers=cookies)
        print("分页获取库位resp-----------\n" + resp.text)
        return resp

    def create_putonshelfbill_sku(self, cookies, payload):
        """
        按sku上架
        :return:
        """
        url = f"{waveecharmer_Host}/api/putonshelfbillv2/sku"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按sku上架resp-----------\n" + resp.text)
        return resp

    def stockinbill_packing_box(self, cookies, payload):
        """
        入库单装箱
        :return:
        """
        url = f"{waveecharmer_Host}/api/stockinbillv2/packing-box"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("入库单装箱resp-----------\n" + resp.text)
        return resp

    def get_packingstock_page(self, cookies, purchase_order_code):
        """
        获取装箱库存分页列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/packingstock/page?sourceBillCode={purchase_order_code}&isOnShelves=false&isOther=true&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&pageIndex=1&pageSize=100"
        resp = requests.get(url=url, headers=cookies)
        print("获取装箱库存分页列表resp-----------\n" + resp.text)
        return resp

    def get_packingstock_spread_page(self, cookies,shopId,operateDivisionId,warehouseId, product_code):
        """
        获取装箱库存明细平铺箱贴聚合数据分页
        :return:
        """
        url = f"{waveecharmer_Host}/api/packingstock/spread/page?shopIds={shopId}&operateDivisionId={operateDivisionId}&warehouseIds={warehouseId}&isGetSpread=true&isIncludeSellerSku=true&isHideZero=true&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&productCode={product_code}&pageIndex=1&pageSize=100"
        resp = requests.get(url=url, headers=cookies)
        print("获取装箱库存明细平铺箱贴聚合数据分页resp-----------\n" + resp.text)
        return resp

    def create_putonshelfbill_box(self, cookies, payload):
        """
        按箱上架
        :return:
        """
        url = f"{waveecharmer_Host}/api/putonshelfbillv2/box"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("按箱上架resp-----------\n" + resp.text)
        return resp

    def get_batchstocks(self, url, cookies):
        resp = requests.get(url=url, headers=cookies)
        print("查询店铺运营事业部库存类型维度的批次库存resp-----------\n" + resp.text)
        return resp