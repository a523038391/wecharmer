# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/12 上午11:59
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : product.py
# @Project : wecharmer

import json
import random
import time
from datetime import datetime
import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from util import httpUtil


class Product:
    def __init__(self):
        # 生成随机数字
        self.random_number = ''.join(str(random.randint(0, 9)) for _ in range(8))

        # 获取当前日期和时间
        now = datetime.now()

        self.formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

    def query_skulist_v1(self, cookies, payload):
        """
        查询sku信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/sku/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("查询sku信息resp-----------\n" + resp.text)
        return resp

    def product_file(self, cookies, payload):
        """
        上传产品附件
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/file"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("上传产品附件resp-----------\n" + resp.text)
        return resp

    def sellersku_new(self, cookies, payload):
        """
        建立映射
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/sellersku/new"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("建立映射resp-----------\n" + resp.text)
        return resp

    def query_sku_byids(self, cookies, id):
        """
        根据id查询sku信息
        :return:
        """

        url = f"{waveecharmer_Host}/api/product/sku/list/byids?skuIds={id}"
        resp = requests.get(url=url, headers=cookies)
        print("根据id查询sku信息resp-----------\n" + resp.text)
        return resp

    def query_skulist(self, cookies, skucode):
        """
        根据sku编码查询sku信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/sku/page"
        payload = {
            "entityInfoType": 1,
            "status": [
                2,
                3
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "codes": [
                skucode
            ],
            "pageIndex": 1,
            "pageSize": 10
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, cookies)
        print("根据sku编码查询sku信息resp-----------\n" + resp.text)
        return resp

    def query_spulist(self, cookies, payload):
        """
        查询spu列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/page"

        resp = requests.post(url=url, headers=cookies, json=payload)
        print("查询spu列表信息resp-----------\n" + resp.text)
        return resp

    def create_product_base(self, cookies, payload):
        """
        创建产品基本信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/base"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建产品基本信息resp-----------\n" + resp.text)
        return resp

    def sellersku_page(self, cookies, payload):
        """
        产品对外关系分页
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/sellersku/page"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("产品对外关系分页resp-----------\n" + resp.text)
        return resp

    def create_productspec(self, cookies, payload, product_id):
        """
        创建产品规格信息
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/productspec/{product_id}"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建产品规格信息resp-----------\n" + resp.text)
        return resp

    def create_serialnumberc(self, cookies, payload):
        """
        创建产品唯一码
        :return:
        """
        url = f"{waveecharmer_Host}/api/product/serialnumber/bypurchaseorderdetail"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建产品唯一码resp-----------\n" + resp.text)
        return resp

    def create_product_link(self, cookies, developDivisionId, developerId, shopId, operateDivisionId):
        """
        创建产品链路
        :param developDivisionId:开发事业部id
        :param productName:产品名称
        :param categoryId:类目id
        :param unitId:单位id
        :param invoiceArticleId:开票id
        :param entityInfoType:产品类型
        :param priority:优先级
        :param specId:规格名id
        :param specValueId:规格值id
        :param useImageSource:图片来源
        :param status:出售状态
        :param specValueId:规格值id
        :param supplierId:供应商id
        :return:
        """

        # 创建产品基本信息
        product_base_payload = {
            "developDivisionId": developDivisionId,
            "categoryId": 210,
            "productName": "卡皮巴拉" + self.formatted_date,
            "code": "",
            "brevityCode": "kapibala" + self.random_number,
            "unitId": 8,
            "invoiceArticleId": 43,
            "enName": "CHAIR",
            "name": "",
            "developerId": developerId,
            "ingredient": "卡皮巴拉",
            "enIngredient": "卡皮巴拉",
            "craft": "",
            "remark": "",
            "entityInfoType": 1,
            "skus": [],
            "boms": []
        }

        product_base_resp = Product().create_product_base(cookies, product_base_payload)
        product_id = json.loads(product_base_resp.text)["result"]["id"]
        product_code = json.loads(product_base_resp.text)["result"]["code"]

        # 创建产品规格信息
        productspec_payload = {
            "developDivisionId": None,
            "specs": [
                {
                    "priority": 0,
                    "specId": 42,
                    "isImage": True,
                    "id": 0
                },
                {
                    "priority": 1,
                    "specId": 43,
                    "isImage": False,
                    "id": 0
                }
            ],
            "specValues": [
                {
                    "priority": 0,
                    "specId": 42,
                    "specValueId": 99,
                    "imageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725434144788_656f1042_24090400173.JPG",
                    "extend": "",
                    "id": 0
                },
                {
                    "priority": 1,
                    "specId": 42,
                    "specValueId": 100,
                    "imageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725434152470_28dc10d5_24090400175.JPG",
                    "extend": "",
                    "id": 0
                },
                {
                    "priority": 0,
                    "specId": 43,
                    "specValueId": 101,
                    "imageUrl": "",
                    "extend": "",
                    "id": 0
                },
                {
                    "priority": 1,
                    "specId": 43,
                    "specValueId": 102,
                    "imageUrl": "",
                    "extend": "",
                    "id": 0
                }
            ],
            "skus": [
                {
                    "imageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725434144788_656f1042_24090400173.JPG",
                    "useImageSource": 2,
                    "code": product_code + "-A-A-20",
                    "oldCode": "",
                    "cnName": "卡皮巴拉-大小-20cm-" + self.formatted_date,
                    "status": 2,
                    "longX": 55,
                    "longY": 55,
                    "longZ": 55,
                    "netWeight": 55,
                    "grossWeight": 55,
                    "suite": 1,
                    "specs": [
                        {
                            "priority": 0,
                            "specValueId": 99
                        },
                        {
                            "priority": 1,
                            "specValueId": 101
                        }
                    ],
                    "suppliers": [
                        {
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "currency": "CNY",
                            "price": 5,
                            "default": True,
                            "ctnLongX": 55,
                            "ctnLongY": 55,
                            "ctnLongZ": 5,
                            "ctnVolume": "0.0151",
                            "ctnQuantity": 5,
                            "ctnNetWeight": 5,
                            "ctnGrossWeight": 5,
                            "link": ""
                        }
                    ],
                    "specValueIdRule": "99-101",
                    "name": "黄色-XL",
                    "isAdd": True,
                    "specs0": "黄色",
                    "specs1": "XL"
                },
                {
                    "imageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725434144788_656f1042_24090400173.JPG",
                    "useImageSource": 2,
                    "code": product_code + "-A-B-50",
                    "oldCode": "",
                    "cnName": "卡皮巴拉-大小-50cm-" + self.formatted_date,
                    "status": 2,
                    "longX": 55,
                    "longY": 55,
                    "longZ": 55,
                    "netWeight": 55,
                    "grossWeight": 55,
                    "suite": 1,
                    "specs": [
                        {
                            "priority": 0,
                            "specValueId": 99
                        },
                        {
                            "priority": 1,
                            "specValueId": 102
                        }
                    ],
                    "suppliers": [
                        {
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "currency": "CNY",
                            "price": 5,
                            "default": True,
                            "ctnLongX": 55,
                            "ctnLongY": 55,
                            "ctnLongZ": 5,
                            "ctnVolume": "0.0151",
                            "ctnQuantity": 5,
                            "ctnNetWeight": 5,
                            "ctnGrossWeight": 5,
                            "link": ""
                        }
                    ],
                    "specValueIdRule": "99-102",
                    "name": "黄色-L",
                    "isAdd": True,
                    "specs0": "黄色",
                    "specs1": "L"
                },
                {
                    "imageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725434152470_28dc10d5_24090400175.JPG",
                    "useImageSource": 2,
                    "code": product_code + "-B-A-70",
                    "oldCode": "",
                    "cnName": "卡皮巴拉-大小-70cm-" + self.formatted_date,
                    "status": 2,
                    "longX": 55,
                    "longY": 55,
                    "longZ": 55,
                    "netWeight": 55,
                    "grossWeight": 55,
                    "suite": 1,
                    "specs": [
                        {
                            "priority": 0,
                            "specValueId": 100
                        },
                        {
                            "priority": 1,
                            "specValueId": 101
                        }
                    ],
                    "suppliers": [
                        {
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "currency": "CNY",
                            "price": 5,
                            "default": True,
                            "ctnLongX": 55,
                            "ctnLongY": 55,
                            "ctnLongZ": 5,
                            "ctnVolume": "0.0151",
                            "ctnQuantity": 5,
                            "ctnNetWeight": 5,
                            "ctnGrossWeight": 5,
                            "link": ""
                        }
                    ],
                    "specValueIdRule": "100-101",
                    "name": "绿色-XL",
                    "isAdd": True,
                    "specs0": "绿色",
                    "specs1": "XL"
                },
                {
                    "imageUrl": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1725434152470_28dc10d5_24090400175.JPG",
                    "useImageSource": 2,
                    "code": product_code + "-B-B-100",
                    "oldCode": "",
                    "cnName": "卡皮巴拉-大小-100cm-" + self.formatted_date,
                    "status": 2,
                    "longX": 55,
                    "longY": 55,
                    "longZ": 55,
                    "netWeight": 55,
                    "grossWeight": 55,
                    "suite": 1,
                    "specs": [
                        {
                            "priority": 0,
                            "specValueId": 100
                        },
                        {
                            "priority": 1,
                            "specValueId": 102
                        }
                    ],
                    "suppliers": [
                        {
                            "supplierId": 6,
                            "supplierCode": "GYS00007",
                            "currency": "CNY",
                            "price": 5,
                            "default": True,
                            "ctnLongX": 55,
                            "ctnLongY": 55,
                            "ctnLongZ": 5,
                            "ctnVolume": "0.0151",
                            "ctnQuantity": 5,
                            "ctnNetWeight": 5,
                            "ctnGrossWeight": 5,
                            "link": ""
                        }
                    ],
                    "specValueIdRule": "100-102",
                    "name": "绿色-L",
                    "isAdd": True,
                    "specs0": "绿色",
                    "specs1": "L"
                }
            ]
        }

        Product().create_productspec(cookies, productspec_payload, product_id)
        time.sleep(1)

        # 查询sku信息
        product_list_payload = {
            "entityInfoType": 1,
            "sorts": [
                {
                    "field": "code",
                    "order": "asc"
                }
            ],
            "code": product_code,
            "pageIndex": 1,
            "pageSize": 10
        }
        product_resp = Product().query_spulist(cookies, product_list_payload)
        product_result = json.loads(product_resp.text)["result"]["items"][0]["skus"]

        product_data = {"productId": product_id, "productName": "卡皮巴拉" + self.formatted_date,
                        "spuCode": product_code,
                        "sku1": {"id": product_result[0]["id"], "code": product_result[0]["code"],
                                 "cnName": product_result[0]["cnName"]},
                        "sku2": {"id": product_result[1]["id"], "code": product_result[1]["code"],
                                 "cnName": product_result[1]["cnName"]},
                        "sku3": {"id": product_result[2]["id"], "code": product_result[2]["code"],
                                 "cnName": product_result[2]["cnName"]},
                        "sku4": {"id": product_result[3]["id"], "code": product_result[3]["code"],
                                 "cnName": product_result[3]["cnName"]}}

        # 上传产品附件
        file_payload = {
            "attachedId": product_id,
            "files": [
                {
                    "url": "https://wecharmer-erp-test.obs.cn-east-3.myhuaweicloud.com/ProhibitDeletion/1734499501913_f0511a8a_24121800252.xlsx",
                    "name": "导出货柜单_24121302483_20241218.xlsx",
                    "fileTypeId": 10
                }
            ]
        }

        Product().product_file(cookies, file_payload)

        # 创建映射

        product_resp = Product().query_spulist(cookies, product_list_payload)
        product_result = json.loads(product_resp.text)["result"]["items"][0]["skus"]
        print(product_result)

        for sku in product_result:
            sellersku_payload = {
                "shopId": shopId,
                "fnSku": sku["code"],
                "code": sku["code"] + "-seller",
                "brandId": 6,
                "operateDivisionId": operateDivisionId,
                "operaterId": developerId,
                "isMultiple": False,
                "skus": [
                    {
                        "skuId": sku["id"],
                        "amount": 1
                    }
                ]
            }

            Product().sellersku_new(cookies, sellersku_payload)
        print(product_data)

        return product_data

    # 创建映射关系
    def sellersku_link(self, cookies,shopId, developerId, operateDivisionId, product_code):
        # 查询sku信息
        product_list_payload = {
            "entityInfoType": 1,
            "sorts": [
                {
                    "field": "code",
                    "order": "asc"
                }
            ],
            "code": product_code,
            "pageIndex": 1,
            "pageSize": 10
        }

        # 创建映射

        product_resp = Product().query_spulist(cookies, product_list_payload)
        product_result = json.loads(product_resp.text)["result"]["items"][0]["skus"]
        print(product_result)

        for sku in product_result:
            sellersku_payload = {
                "shopId": shopId,
                "fnSku": sku["code"],
                "code": sku["code"] + "-seller",
                "brandId": 6,
                "operateDivisionId": operateDivisionId,
                "operaterId": developerId,
                "isMultiple": False,
                "skus": [
                    {
                        "skuId": sku["id"],
                        "amount": 1
                    }
                ]
            }

            Product().sellersku_new(cookies, sellersku_payload)


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # Product().query_skulist(cookies, "LIPENG456-B-P")
    #Product().create_product_link(cookies, 2, 303,161,5)

    # 创建映射
    Product().sellersku_link(cookies,161,303,5,"S7621-202")
