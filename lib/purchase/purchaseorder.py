# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/8/23 下午3:24
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : purchaseorder.py
# @Project : wecharmer


import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from lib.login import Login
from datetime import datetime, timedelta

from lib.productandmaterial.product import Product
from lib.purchase.applypurchasebill import ApplyPurchaseBill


class PurchaseOrder:
    def __init__(self):
        # 获取当前日期和时间
        now = datetime.now()

        # 创建一个时间差，表示3天
        three_days = timedelta(days=3)
        three_days_future = timedelta(days=180)
        three_days_old = timedelta(days=90)

        # 将时间差加到当前日期上
        new_date = now + three_days
        future_date = now + three_days_future
        old_date = now + three_days_old

        self.formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")
        self.formatted_date_future = future_date.strftime("%Y-%m-%d %H:%M:%S")
        self.formatted_date_old = old_date.strftime("%Y-%m-%d %H:%M:%S")

    def get_purchaseorder_details(self, cookies, purchaseorderid):
        """
        根据id获取采购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/details/fullall?purchaseOrderIds={purchaseorderid}"

        resp = requests.get(url=url, headers=cookies)
        print("获取采购单明细resp-----------\n" + resp.text)
        return resp

    def create_purchaseorder(self, cookies, payload):
        """
        创建采购单
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建采购单resp-----------\n" + resp.text)
        return resp

    def create_purchaseorder_details(self, cookies, payload):
        """
        创建采购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/purchaseorderdetails"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("创建采购单明细resp-----------\n" + resp.text)
        return resp

    def purchaseorder_review(self, purchaseorderid, cookies, payload):
        """
        送审
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/approvestatus/{purchaseorderid}/review"
        resp = requests.put(url=url, headers=cookies, json=payload)
        print("送审resp-----------\n" + resp.text)
        return resp

    def get_purchaseorder(self, cookies, purchaseorderid):
        """
        根据id获取采购单明细
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/{purchaseorderid}/detail/all"
        resp = requests.get(url=url, headers=cookies)
        print("获取采购单明细resp-----------\n" + resp.text)
        return resp

    def page_purchaseorder(self, cookies, purchaseordercode):
        """
        查询采购单列表
        :return:
        """
        url = f"{waveecharmer_Host}/api/purchaseorder/page?purchaseSourceTypes=4&purchaseOrderStatuses=2&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&purchaseOrderCode={purchaseordercode}&pageIndex=1&pageSize=10"
        resp = requests.get(url=url, headers=cookies)
        print("查询采购单列表resp-----------\n" + resp.text)
        return resp

    def create_stock_purchaseorder_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                        purchasername, product_code):
        """
        创建备货采购单链路
        :param companyId:财务公司抬头id
        :param supplierId:供应商id
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """

        # 创建备货单返回id
        applypurchasebillid = ApplyPurchaseBill().create_stock_applypurchasebill_link(cookies, shopId,
                                                                                      operateDivisionId, purchaserId,
                                                                                      purchasername, product_code)

        time.sleep(2)

        # 创建备货采购单
        purchaseorder_payload = {
            "companyId": 2,
            "supplierId": 6,
            "warehouseId": warehouseId,
            "purchaseOrderType": 1,
            "purchasePlanBillCode": "",
            "productDevelopType": 1,
            "supplierPaymentMethod": 2,
            "operateDivisionId": operateDivisionId,
            "shopId": shopId,
            "remark": "",
            "logisticsFee": 0,
            "attachments": [],
            "purchaserId": purchaserId,
            "deliveryDate": None,
            "companyCurrencyType": "CNY",
            "exchangeRate": 1,
            "supplierContactPerson": "小常",
            "supplierContactPersonMobile": "17620866231",
            "supplierSettlementMethod": 3,
            "supplierSettlementDay": 20,
            "supplierPrepaidRate": 0.8,
            "purchaseOrderCode": None,
            "purchaseSourceType": 1,
            "applyPurchaseBillId": applypurchasebillid,
            "operaterId": purchaserId,
            "operaterName": purchasername,
            "applyPurchaseBillCode": "BS24110100005",
            "soureBillId": 5324,
            "expectedArrivalTime": None,
            "expectedPutOnSaleTime": None,
            "supplierAccountNumber": "",
            "supplierOpeningBank": "",
            "chargePerson": "小李1",
            "chargePersonMobile": "176201232411",
            "address": "广州"
        }

        for i in range(5):

            purchaseorder_resp = PurchaseOrder().create_purchaseorder(cookies, purchaseorder_payload)
            print("创建备货采购单第" + str(i) + "次")
            print(purchaseorder_resp)
            purchaseorder_result = json.loads(purchaseorder_resp.text)["result"]

            if purchaseorder_result == None:
                continue

            else:

                break
        purchaseorderid = json.loads(purchaseorder_resp.text)["result"]["id"]

        # 获取备货单明细
        get_applypurchasebill_resp = ApplyPurchaseBill().get_applypurchasebill_detail_all(cookies, applypurchasebillid)
        get_applypurchasebill_result = json.loads(get_applypurchasebill_resp.text)["result"]

        # 创建采购单明细
        purchaseOrderDetails = []
        unitPrice = 100
        for item in get_applypurchasebill_result["skuAndMonthYearDetailDimensionDetails"]:
            unitPrice += 50
            purchaseOrderDetails_dict = {
                "skuId": item["skuId"],
                "quantity": item["quantity"],
                "unitPrice": unitPrice,
                "taxRate": 0.04,
                "expectedArrivalTime": item["expectedArrivalTime"],
                "overflowRate": 0
            }
            purchaseOrderDetails.append(purchaseOrderDetails_dict)
        purchaseorder_details_payload = {
            "purchaseOrderId": purchaseorderid,
            "purchaseOrderDetails": purchaseOrderDetails
        }

        for i in range(5):

            purchaseorder_details_resp = PurchaseOrder().create_purchaseorder_details(cookies,
                                                                                      purchaseorder_details_payload)
            purchaseorder_details_result = json.loads(purchaseorder_details_resp.text)["result"]
            print("创建出运采购单明细第" + str(i) + "次")
            if purchaseorder_details_result == None:
                continue

            else:
                break

        # 送审
        payload = {}
        PurchaseOrder().purchaseorder_review(purchaseorderid, cookies, payload)

        return {"purchaseorderid": purchaseorderid, "applypurchasebillid": applypurchasebillid}

    def create_shipment_purchaseorder_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                           purchasername, product_code):
        """
        创建出运采购单链路
        :param companyId:财务公司抬头id
        :param supplierId:供应商id
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """

        # 创建备货采购单
        PurchaseOrderdata = PurchaseOrder().create_stock_purchaseorder_link(cookies, shopId, warehouseId,
                                                                            operateDivisionId, purchaserId,
                                                                            purchasername, product_code)
        purchaseorderids = []
        for i in range(2):
            # 创建出运申购单

            shipment_applypurchasebillid = ApplyPurchaseBill().create_shipment_applypurchasebill_link(cookies, shopId,
                                                                                                      operateDivisionId,
                                                                                                      purchaserId,
                                                                                                      purchasername,
                                                                                                      PurchaseOrderdata[
                                                                                                          "applypurchasebillid"])

            # 获取备货单明细
            get_applypurchasebill_resp = ApplyPurchaseBill().get_applypurchasebill_detail_all(cookies,
                                                                                              shipment_applypurchasebillid)
            get_applypurchasebill_result = json.loads(get_applypurchasebill_resp.text)["result"]
            print("chuyun")

            # 创建出运采购单
            purchaseorder_payload = {
                "companyId": 2,
                "supplierId": 6,
                "warehouseId": warehouseId,
                "purchaseOrderType": 1,
                "productDevelopType": 1,
                "supplierPaymentMethod": 2,
                "operateDivisionId": operateDivisionId,
                "shopId": shopId,
                "remark": "",
                "logisticsFee": 0,
                "attachments": [],
                "purchaserId": purchaserId,
                "deliveryDate": self.formatted_date,
                "planDeliveryDate": None,
                "companyCurrencyType": "CNY",
                "exchangeRate": 1,
                "exchangeRateLimit": None,
                "supplierContactPerson": "小常",
                "supplierContactPersonMobile": "17620866231",
                "supplierSettlementMethod": 3,
                "supplierSettlementDay": 20,
                "supplierPrepaidRate": 0.8,
                "purchaseSourceType": 2,
                "purchaseOrderCode": None,
                "purchasePlanBillId": None,
                "skuSupplierObj": {
                    "49532": 6,
                    "49533": 6,
                    "49534": 6,
                    "49535": 6
                },
                "bhApplyPurchaseBillId": PurchaseOrderdata[
                    "applypurchasebillid"],
                "operaterId": purchaserId,
                "operaterName": purchasername,
                "bhPurchaseBillId": PurchaseOrderdata["purchaseorderid"],
                "bhPurchaseBillCode": "BO24110100016",
                "applyPurchaseBillCode": "QG24110100027",
                "applyPurchaseBillId": shipment_applypurchasebillid,
                "soureBillId": shipment_applypurchasebillid,
                "expectedArrivalTime": self.formatted_date_old,
                "expectedPutOnSaleTime": self.formatted_date_future,
                "supplierAccountNumber": "",
                "supplierOpeningBank": "",
                "chargePerson": "小李1",
                "chargePersonMobile": "176201232411",
                "address": "广州"
            }
            for i in range(5):

                purchaseorder_resp = PurchaseOrder().create_purchaseorder(cookies, purchaseorder_payload)
                print("创建出运采购单第" + str(i) + "次")
                print(purchaseorder_resp)
                purchaseorder_result = json.loads(purchaseorder_resp.text)["result"]

                if purchaseorder_result == None:
                    continue

                else:

                    break
            purchaseorderid = json.loads(purchaseorder_resp.text)["result"]["id"]

            # 创建采购单明细
            purchaseOrderDetails = []
            unitPrice = 100
            for item in get_applypurchasebill_result["skuDetailDimensionDetails"]:
                unitPrice += 50
                purchaseOrderDetails_dict = {
                    "skuId": item["skuId"],
                    "quantity": item["quantity"],
                    "overflowRate": 0.05,
                    "unitPrice": unitPrice,
                    "taxRate": 0.04
                }
                purchaseOrderDetails.append(purchaseOrderDetails_dict)
            purchaseorder_details_payload = {
                "purchaseOrderId": purchaseorderid,
                "purchaseOrderDetails": purchaseOrderDetails
            }
            print(purchaseorder_details_payload)
            for i in range(5):

                purchaseorder_details_resp = PurchaseOrder().create_purchaseorder_details(cookies,
                                                                                          purchaseorder_details_payload)
                purchaseorder_details_result = json.loads(purchaseorder_details_resp.text)["result"]
                print("创建出运采购单明细第" + str(i) + "次")
                if purchaseorder_details_result == None:
                    continue

                else:
                    break

            # 送审
            payload = {}
            PurchaseOrder().purchaseorder_review(purchaseorderid, cookies, payload)
            purchaseorderids.append(purchaseorderid)
        print(purchaseorderids)

        return purchaseorderids

    def create_purchaseorder_link(self, cookies, shopId, warehouseId, operateDivisionId, purchaserId, product_code):
        """
        创建采购单链路
        :param companyId:财务公司抬头id
        :param supplierId:供应商id
        :param operateDivisionId:运营事业部
        :param shopId:店铺
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :return:
        """

        # 创建备货单返回id
        applypurchasebillid = ApplyPurchaseBill().create_applypurchasebill_link(cookies, shopId, operateDivisionId,
                                                                                purchaserId,
                                                                                product_code)

        time.sleep(20)

        #获取申购单详情
        get_applypurchase_resp=ApplyPurchaseBill().get_applypurchasebill(cookies,applypurchasebillid)
        get_applypurchase_result=json.loads(get_applypurchase_resp.text)["result"]

        # 创建采购单
        purchaseorder_payload = {
            "companyId": 31,
            "supplierId": 6,
            "warehouseId": warehouseId,
            "purchaseOrderType": 1,
            "productDevelopType": 2,
            "supplierPaymentMethod": 2,
            "operateDivisionId": operateDivisionId,
            "shopId": shopId,
            "remark": "",
            "logisticsFee": 0,
            "attachments": [],
            "purchaserId": purchaserId,
            "deliveryDate": self.formatted_date,
            "planDeliveryDate": None,
            "companyCurrencyType": "CNY",
            "exchangeRate": 1,
            "supplierContactPerson": "小常",
            "supplierContactPersonMobile": "17620866231",
            "supplierSettlementMethod": 3,
            "supplierSettlementDay": 20,
            "supplierPrepaidRate": 0.8,
            "purchaseSourceType": 4,
            "purchaseOrderCode": None,
            "purchasePlanBillId": None,
            "skuSupplierObj": {
                "6355": 6,
                "6356": 6,
                "6357": 6,
                "6358": 6
            },
            "bhApplyPurchaseBillId": None,
            "operaterId": purchaserId,
            "operaterName": "李朋",
            "applyPurchaseBillCode": "QG24082300017",
            "applyPurchaseBillId": applypurchasebillid,
            "soureBillId": applypurchasebillid,
            "expectedArrivalTime": get_applypurchase_result["expectedArrivalTime"],
            "expectedPutOnSaleTime": get_applypurchase_result["expectedPutOnSaleTime"],
            "supplierAccountNumber": "3308110120100011538",
            "supplierOpeningBank": "广州银行",
            "chargePerson": "小飞",
            "chargePersonMobile": "17620865451",
            "address": "Detail Address",
            "developDivisionId": get_applypurchase_result["developDivisionId"],
            "productGroupId": get_applypurchase_result["productGroupId"],
            "developDivisionName": get_applypurchase_result["developDivisionName"],
            "productGroupName": get_applypurchase_result["productGroupName"]
        }

        for i in range(5):

            purchaseorder_resp = PurchaseOrder().create_purchaseorder(cookies, purchaseorder_payload)
            print("创建常规采购单第" + str(i) + "次")
            print(purchaseorder_resp)
            purchaseorder_result = json.loads(purchaseorder_resp.text)["result"]

            if purchaseorder_result == None:
                continue

            else:

                break
        purchaseorderid = json.loads(purchaseorder_resp.text)["result"]["id"]

        # 查询商品信息
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
            "pageSize": 100
        }
        product_resp = Product().query_spulist(cookies, product_list_payload)
        product_result = json.loads(product_resp.text)["result"]["items"][0]["skus"]

        # 获取备货单明细
        get_applypurchasebill_resp = ApplyPurchaseBill().get_applypurchasebill_detail_all(cookies, applypurchasebillid)
        get_applypurchasebill_result = json.loads(get_applypurchasebill_resp.text)["result"]

        # 创建采购单明细
        purchaseOrderDetails = []
        unitPrice = 100
        for item in get_applypurchasebill_result["skuDetailDimensionDetails"]:
            unitPrice += 50
            purchaseOrderDetails_dict = {
                "skuId": item["skuId"],
                "quantity": item["quantity"],
                "overflowRate": 0.05,
                "unitPrice": unitPrice,
                "taxRate": 0.04
            }
            purchaseOrderDetails.append(purchaseOrderDetails_dict)
        purchaseorder_details_payload = {
            "purchaseOrderId": purchaseorderid,
            "purchaseOrderDetails": purchaseOrderDetails
        }

        for i in range(5):

            purchaseorder_details_resp = PurchaseOrder().create_purchaseorder_details(cookies,
                                                                                      purchaseorder_details_payload)
            purchaseorder_details_result = json.loads(purchaseorder_details_resp.text)["result"]
            print("创建常规采购单明细第" + str(i) + "次")
            if purchaseorder_details_result == None:
                continue

            else:
                break

        # 送审
        payload = {}
        PurchaseOrder().purchaseorder_review(purchaseorderid, cookies, payload)
        time.sleep(2)


        return purchaseorderid


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # 创建常规采购单
    PurchaseOrder().create_purchaseorder_link(cookies, 161, 15, 5, 303, "A5-181")

    # 创建备货采购单
    # PurchaseOrder().create_stock_purchaseorder_link(cookies, 161, 15, 5, 303, "李朋", "A5-181")

    # 创建出运采购单
    # PurchaseOrder().create_shipment_purchaseorder_link(cookies, 161, 15, 5, 303, "李朋", "A5-181")
