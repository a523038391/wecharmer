# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/20 上午11:25
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : containerbill.py
# @Project : wecharmer
import json
from datetime import datetime

import requests

from conf.baseconfig import waveecharmer_Host
from lib.firstleg.deliverybill import DeliveryBill
from lib.firstleg.inspection import Inspection
from lib.firstleg.loadingadvice import LoadingAdvice
from lib.firstleg.stockupbill import StockupBill
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

    def create_containerbill(self, cookies, sourceBillType, vouchingClerkId, vouchingClerkName, ladingNo,
                             deliveryBillId):
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

    def create_declaration_contract(self, cookies, payload):
        """
        生成报关合同
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/declaration-contract/create"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("生成报关合同resp-----------\n" + resp.text)
        return resp

    def get_declaration_contract(self, cookies, containerBillid):
        """
        查询生成报关合同维度
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/declaration-contract/generate-dimension?containerBillId={containerBillid}"
        resp = requests.get(url=url, headers=cookies)
        print("查询生成报关合同维度resp-----------\n" + resp.text)
        return resp

    def get_conservancy_export_date(self, cookies, containerBillid):
        """
        获取出口日期
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/{containerBillid}/conservancy-export-date"
        resp = requests.get(url=url, headers=cookies)
        print("获取出口日期resp-----------\n" + resp.text)
        return resp

    def create_conservancy_export_date(self, cookies, containerBillid, payload):
        """
        生成出口日期
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/{containerBillid}/conservancy-export-date"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("生成出口日期resp-----------\n" + resp.text)
        return resp

    def create_conservancy_estimated_batch(self, cookies, containerBillid, payload):
        """
        保存暂估费用
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/{containerBillid}/conservancy-estimated-batch"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("保存暂估费用resp-----------\n" + resp.text)
        return resp

    def create_conservancy_settlement_batch(self, cookies, containerBillid, payload):
        """
        保存结算费用
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/{containerBillid}/conservancy-settlement-batch"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("保存结算费用resp-----------\n" + resp.text)
        return resp

    def create_containerbill_link(self, cookies, sourceCode, sourceBillType, vouchingClerkId, vouchingClerkName,
                                  ladingNo):
        # 查询出货单
        url = f"{waveecharmer_Host}/api/deliverybill/page?deliveryBillStates=1,2,3,4&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&sourceCodes=%22{sourceCode}%22&pageIndex=1&pageSize=10"
        DeliveryBill_resp = DeliveryBill().query_deliverybill(url, cookies)
        deliveryBillId = json.loads(DeliveryBill_resp.text)['result']["items"][0]["id"]

        # 创建货柜列表
        ContainerBill_resp = ContainerBill().create_containerbill(cookies, sourceBillType, vouchingClerkId,
                                                                  vouchingClerkName, ladingNo, deliveryBillId)
        containerBillCode = json.loads(ContainerBill_resp.text)['result']["containerBillCode"]
        containerBillid = json.loads(ContainerBill_resp.text)['result']['id']
        containerBill_data = {"containerBillCode": containerBillCode, "containerBillid": containerBillid}
        return containerBill_data

    def booking_deliverybill_link(self, cookies, billOfLadingCode, sourceBillCategory, shopId, warehouseId,
                                  warehouseName, operateDivisionId, purchaserId, purchasername, targetWarehouseId,
                                  sourceBillType, customsDeclarationSubId):
        """
        创建订舱单发货全链路
        :param isLCL:是否拼柜
        :param cargoReadyDay:货号日期
        :param containerId:货柜id
        :param purchaseOrderId:采购单id
        :param supplierAccountId:供应商账户id
        :param purchaseBusinessType:备货 出运 常规
        :param purchaseBusinessType:备货 出运 常规
        :param dimensionType: 生成报关合同类型
        :param customsDeclarationSubId: 报关主体
        :return:
        """
        # 创建订舱单-验货完成
        booking_data = Inspection().create_inspection_link(cookies, shopId, warehouseId, operateDivisionId, purchaserId,
                                                           targetWarehouseId)

        LoadingAdvice().loadingadvice_link(cookies, billOfLadingCode, sourceBillCategory, warehouseId, warehouseName,
                                           booking_data["bookingid"], booking_data["bookingcode"])

        # 根据订舱单号查询备货单
        url = f"{waveecharmer_Host}/api/stockupbill/page?stockUpBillStatuses=1,2,3,5,6&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&bookingBillCode={booking_data["bookingcode"]}&pageIndex=1&pageSize=10"
        sourceCode_resp = StockupBill().query_stockupbill(url, cookies)
        sourceCode = json.loads(sourceCode_resp.text)["result"]["items"][0]["stockUpBillCode"]

        # 创建货柜列表
        containerBill_data = ContainerBill().create_containerbill_link(cookies, sourceCode, sourceBillType, purchaserId,
                                                                       purchasername,
                                                                       billOfLadingCode)

        # 查询生成报关合同维度
        declaration_contract_resp = ContainerBill().get_declaration_contract(cookies,
                                                                             containerBill_data["containerBillid"])
        declaration_contract_result = json.loads(declaration_contract_resp.text)["result"]

        # 生成报关合同
        declaration_contract_payload = {
            "containerBillId": containerBill_data["containerBillid"],
            "currency": "USD",
            "isPurchaseOrderUnitPrice": False,
            "dimensionType": 2,
            "getGenerateContractDimensionDto": {
                "companyAndSupplierList": [
                    {
                        "supplierId": declaration_contract_result["companyAndSupplierList"][0]["supplierId"],
                        "supplierName": declaration_contract_result["companyAndSupplierList"][0]["supplierName"],
                        "companyId": declaration_contract_result["companyAndSupplierList"][0]["companyId"],
                        "companyName": declaration_contract_result["companyAndSupplierList"][0]["companyName"],
                        "overseasReceiverId": declaration_contract_result["companyAndSupplierList"][0][
                            "overseasReceiverId"],
                        "overseasReceiver": declaration_contract_result["companyAndSupplierList"][0][
                            "overseasReceiver"],
                        "customsDeclarationSubId": customsDeclarationSubId,
                        "customsDeclarationSubName": "浙江微诚",
                        "contractGroupTag": 1
                    }
                ]
            }
        }

        ContainerBill().create_declaration_contract(cookies, declaration_contract_payload)

        # 获取出口日期
        export_date_resp = ContainerBill().get_conservancy_export_date(cookies, containerBill_data["containerBillid"])
        export_date_result = json.loads(export_date_resp.text)["result"]

        # 生成出口日期
        export_date_payload = [
            {
                "id": export_date_result[0]["id"],
                "contractNo": export_date_result[0]["contractNo"],
                "declarationNo": None,
                "overseasReceiver": "测试",
                "companyId": None,
                "companyName": "",
                "targetWarehouseId": 0,
                "targetWarehouseName": "",
                "exportDate": self.formatted_date,
                "declarationContractId": export_date_result[0]["id"]
            }
        ]

        ContainerBill().create_conservancy_export_date(cookies, containerBill_data["containerBillid"],
                                                       export_date_payload)

        # 保存暂估费用
        estimated_batch_payload = [
            {
                "costType": 1,
                "amount": 6,
                "currency": "CNY",
                "toCnyAmount": 6,
                "settlementAgentId": 4,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1
            }
        ]
        ContainerBill().create_conservancy_estimated_batch(cookies, containerBill_data["containerBillid"],
                                                           estimated_batch_payload)
        # 保存结算费用
        settlement_batch_payload = [
            {
                "costType": 1,
                "amount": 6,
                "currency": "CNY",
                "toCnyRate": 1,
                "toCnyAmount": 6,
                "settlementAgent": 1,
                "settlementAgentId": 4,
                "settlementAgentName": "挂车队",
                "apportionmentMethod": 2,
                "isEffective": True
            }
        ]
        ContainerBill().create_conservancy_settlement_batch(cookies, containerBill_data["containerBillid"],settlement_batch_payload)


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # ContainerBill().get_containerbill(cookies, "EGLV143470577152")
    # ContainerBill().create_containerbill_link(cookies,"BH24062000052",502,303,"李朋","3453353534")
    ContainerBill().booking_deliverybill_link(cookies, 533535, 507, 161, 15, "恒丰仓库", 5, 303, "李朋", 12, 502, 3)
