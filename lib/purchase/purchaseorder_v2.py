# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/4/20 上午10:44
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : purchaseorder_v2.py
# @Project : wecharmer


import json
import time

import requests

from conf.baseconfig import waveecharmer_Host
from interface.purchase.applypurchasebill_api import ApplyPurchaseBill_Api
from interface.purchase.purchaseorder_api import PurchaseOrder_Api
from lib.login import Login
from datetime import datetime, timedelta

from lib.productandmaterial.product import Product
from lib.purchase.applypurchasebill_v2 import ApplyPurchaseBillv2


class PurchaseOrderv2:
    def __init__(self):
        pass

    def create_purchaseorderv2_link(self, cookies, shopId, shopAccount,warehouseId, operateDivisionId, operaterId,operaterName, purchaserId,
                                    product_code, salesPlanDate, expectedShelfDate, supplierId, companyId):
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

        # 创建申购单返回code
        applypurchasebillv2code1 = ApplyPurchaseBillv2().create_applypurchasebillv2_link(cookies, shopId,shopAccount,
                                                                                         operateDivisionId,operaterName, operaterId,
                                                                                         product_code, salesPlanDate,
                                                                                         expectedShelfDate)

        applypurchasebillv2code2 = ApplyPurchaseBillv2().create_applypurchasebillv2_link(cookies, shopId,shopAccount,
                                                                                         operateDivisionId,operaterName, operaterId,
                                                                                         product_code, salesPlanDate,
                                                                                         expectedShelfDate)

        applypurchasebillv2code3 = ApplyPurchaseBillv2().create_applypurchasebillv2_link(cookies, shopId,shopAccount,
                                                                                         operateDivisionId,operaterName, operaterId,
                                                                                         product_code, salesPlanDate,
                                                                                         expectedShelfDate)

        time.sleep(3)

        # 查询申购单v2
        page_applypurchasebillv2 = {
            "approveStatuses": [
                3
            ],
            "applyPurchaseType": 1,
            "applyPurchaseBillStatuses": [
                2,
                3
            ],
            "sorts": [
                {
                    "field": "id",
                    "order": "desc"
                }
            ],
            "applyPurchaseBillCodes": [
                applypurchasebillv2code1["applyPurchaseBillCode"],
                applypurchasebillv2code2["applyPurchaseBillCode"],
                applypurchasebillv2code3["applyPurchaseBillCode"]
            ],
            "pageIndex": 1,
            "pageSize": 100,
            "znd": "t197014"
        }

        page_applypurchasebillv2_resp = ApplyPurchaseBill_Api().page_applypurchasebillv2(cookies,
                                                                                         page_applypurchasebillv2)
        page_applypurchasebillv2_result = json.loads(page_applypurchasebillv2_resp.text)["result"]

        time.sleep(2)

        # 创建采购单明细
        purchaseOrderDetails = []
        unitPrice = 100
        day=0

        for item in page_applypurchasebillv2_result["items"]:
            day+=1
            #unitPrice += 50

            # 解析为 datetime 对象（时区信息会被保留）
            dt = datetime.fromisoformat(item["latestContractDeliveryDate"])

            # 减去一天
            dt_prev = dt - timedelta(days=day)

            # 转换回 ISO 格式字符串（与原始格式一致）
            result = dt_prev.isoformat()
            purchaseOrderDetails_dict = {
                "remainingPurchaseQuantity": item["quantity"],
                "productCategoryFullName": item["categoryName"],
                "productCode": item["spuCode"],
                "applyPurchaseBillDetailId": item["id"],
                "productId": item["spuId"],
                "noTaxPrice": 2.8846,
                "amount": unitPrice * item["quantity"],
                "unitPrice": unitPrice,
                "deliveryDate": result
            }
            purchaseOrderDetails_dict.update(item)
            purchaseOrderDetails.append(purchaseOrderDetails_dict)
        print(purchaseOrderDetails)

        # 创建采购单
        purchaseorderv2_payload = {
            "purchaseOrderCode": "",
            "companyId":companyId,
            "companyCurrencyType": "USD",
            "exchangeRate": 7,
            "exchangeRateLimit": 0,
            "purchaserId": purchaserId,
            "logisticsFee": None,
            "remark": "",
            "supplierId": supplierId,
            "supplierCode": "GYS00007[供应商名（勿动！！！-后面数据均引用该供应商）]",
            "supplierContactPerson": "小常",
            "supplierContactPersonMobile": "17620866231",
            "supplierSettlementMethod": 3,
            "supplierSettlementDay": 30,
            "supplierPrepaidRate": 0.8,
            "developDivisionId": 2,
            "developDivisionName": "开发户外事业部",
            "applyPurchaseType": None,
            "warehouseId": warehouseId,
            "chargePerson": "小李1",
            "chargePersonMobile": "176201232411",
            "address": "广州",
            "purchaseType": 1,
            "isMaterial": False,
            "supplierName": "供应商名（勿动！！！-后面数据均引用该供应商）",
            "supplierPaymentMethod": 2,
            "supplierAccountId": None,
            "warehouseName": "B[恒丰仓库]",
            "details":purchaseOrderDetails
        }
        print(purchaseorderv2_payload)
        purchaseorderv1_details_resp = PurchaseOrder_Api().create_purchaseorderv1(cookies,purchaseorderv2_payload)
        purchaseorderv1id = json.loads(purchaseorderv1_details_resp.text)["result"]

        # 送审
        payload = {}
        PurchaseOrder_Api().purchaseorderv1_review(purchaseorderv1id, cookies, payload)
        time.sleep(2)


        return purchaseorderv1id


if __name__ == '__main__':
    cookies = Login.loginWecharmer()

    # 创建采购单
    PurchaseOrderv2().create_purchaseorderv2_link(cookies, 161,"LIPENG", 129, 5, 303, "李朋", 303,"A5-181", "2026-08", "2026-12-30", 6,
                                                  30)
