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
import random

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
        self.year = now.strftime('%Y')
        self.month = now.strftime('%m')

        self.random_number = ''.join(str(random.randint(0, 9)) for _ in range(10))

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

    def create_containerbill(self, cookies, sourceBillType, vouchingClerkId, vouchingClerkName,
                             deliveryBillIds):
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
            "containerNo": "lipeng" + self.random_number,
            "storageNo": "",
            "ladingNo": "lipeng" + self.random_number,
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
            "deliveryBillIds": deliveryBillIds
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

    def create_declarationdiscount(self, cookies, payload):
        """
        生成折扣
        :return:
        """
        url = f"{waveecharmer_Host}/api/firstleginfrastructure/declarationdiscount"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("生成折扣resp-----------\n" + resp.text)
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

    def create_conservancy_declaration(self, cookies, containerBillid, payload):
        """
        填写报关单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/{containerBillid}/conservancy-declaration-no"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("填写报关单号resp-----------\n" + resp.text)
        return resp

    def get_conservancy_declaration(self, cookies, containerBillid):
        """
        获取报关单号
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/{containerBillid}/conservancy-declaration-no"
        resp = requests.get(url=url, headers=cookies)
        print("获取报关单号resp-----------\n" + resp.text)
        return resp

    def conservancy_clearance_batch(self, cookies, containerBillid, payload):
        """
        清关维护
        :return:
        """
        url = f"{waveecharmer_Host}/api/containerbill/{containerBillid}/conservancy-clearance-batch"
        resp = requests.post(url=url, headers=cookies, json=payload)
        print("清关维护resp-----------\n" + resp.text)
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

    def create_containerbill_link(self, cookies, sourceCodes, sourceBillType, vouchingClerkId, vouchingClerkName,
                                  customsDeclarationSubId
                                  ):


        # 查询出货单
        deliveryBillIds=[]
        for sourceCode in sourceCodes:

            url = f"{waveecharmer_Host}/api/deliverybill/page?deliveryBillStates=1,2,3,4&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&sourceCodes=%22{sourceCode}%22&pageIndex=1&pageSize=10"
            DeliveryBill_resp = DeliveryBill().query_deliverybill(url, cookies)
            deliveryBillId = json.loads(DeliveryBill_resp.text)['result']["items"][0]["id"]
            print(deliveryBillId)

            deliveryBillIds.append(deliveryBillId)



        # 创建货柜列表
        ContainerBill_resp = ContainerBill().create_containerbill(cookies, sourceBillType, vouchingClerkId,
                                                                  vouchingClerkName, deliveryBillIds)
        containerBillCode = json.loads(ContainerBill_resp.text)['result']["containerBillCode"]
        containerBillid = json.loads(ContainerBill_resp.text)['result']['id']

        containerBill_data = {"containerBillCode": containerBillCode, "containerBillid": containerBillid}

        # 查询生成报关合同维度
        declaration_contract_resp = ContainerBill().get_declaration_contract(cookies,
                                                                             containerBill_data["containerBillid"])
        declaration_contract_result = json.loads(declaration_contract_resp.text)["result"]

        # 生成报关合同
        declaration_contract_payload = {
            "containerBillId": containerBill_data["containerBillid"],
            "dimensionType": 2,
            "getGenerateContractDimensionDto": {
                "companyAndSupplierList": [
                    {
                        "isOriginalCurrencyComputeDeclarePrice": True,
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
                        "contractGroupTag": 1,
                        "declarationCurrency": "CNY",
                        "preDeclarationCurrency": "CNY"
                    }
                ]
            }
        }

        print(declaration_contract_payload)

        declaration_contract_resp = ContainerBill().create_declaration_contract(cookies, declaration_contract_payload)
        declaration_contract_result = json.loads(declaration_contract_resp.text)

        if declaration_contract_result["errorMessage"]!= None:

            declarationdiscount_payload = {
                "year": self.year,
                "month": self.month,
                "companyId": customsDeclarationSubId,
                "discount": 0.5
            }
            ContainerBill().create_declarationdiscount(cookies,declarationdiscount_payload)
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

        # 获取报告单号
        conservancy_result = ContainerBill().get_conservancy_declaration(cookies, containerBill_data["containerBillid"])
        declarationContractId = json.loads(conservancy_result.text)["result"][0]["id"]

        # 填写报关单号
        conservancy_payload = [
            {
                "declarationNo": "lipeng" + self.random_number,
                "declarationContractId": declarationContractId
            }
        ]
        ContainerBill().create_conservancy_declaration(cookies, containerBill_data["containerBillid"],
                                                       conservancy_payload)

        # 清关维护
        conservancy_payload = {
            "currency": "CNY",
            "amount": 99,
            "clearanceApportionmentMethod": 1
        }
        ContainerBill().conservancy_clearance_batch(cookies, containerBill_data["containerBillid"], conservancy_payload)

        # 保存暂估费用
        estimated_batch_payload = [
            {
                "costType": 3,
                "amount": 4,
                "currency": "CNY",
                "toCnyAmount": 4,
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            }
        ]
        ContainerBill().create_conservancy_estimated_batch(cookies, containerBill_data["containerBillid"],
                                                           estimated_batch_payload)
        # 保存结算费用
        settlement_batch_payload = [
            {
                "costType": 1,
                "amount": 77,
                "currency": "CNY",
                "toCnyAmount": 77,
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            },
            {
                "costType": 2,
                "amount": 77,
                "currency": "CNY",
                "toCnyAmount": 77,
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            },
            {
                "costType": 3,
                "amount": 77,
                "currency": "USD",
                "toCnyRate": 7.1135,
                "toCnyAmount": "547.7395",
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            },
            {
                "costType": 4,
                "amount": 77,
                "currency": "USD",
                "toCnyRate": 7.1135,
                "toCnyAmount": "547.7395",
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            },
            {
                "costType": 5,
                "amount": 77,
                "currency": "CNY",
                "toCnyAmount": 77,
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            },
            {
                "costType": 6,
                "amount": 77,
                "currency": "CNY",
                "toCnyAmount": 77,
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            },
            {
                "costType": 7,
                "amount": 77,
                "currency": "CNY",
                "toCnyAmount": 77,
                "settlementAgent": 3,
                "settlementAgentId": 2,
                "apportionmentMethod": 2,
                "reconciliationStatus": 1,
                "settlementAgentName": "货代名称"
            }
        ]
        ContainerBill().create_conservancy_settlement_batch(cookies, containerBill_data["containerBillid"],
                                                            settlement_batch_payload)
        return containerBill_data

    def stockupbill_containerBill_link(self, cookies, sourceBillCategory, sourceType, shopId, warehouseId,
                                       warehouseName, operateDivisionId, purchaserId, purchaserName, targetWarehouseId,
                                       sourceBillType, customsDeclarationSubId, product_code,supplierId,companyId):
        """
        创建备货单发货全链路
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
        # 备货单按件发货-装柜
        stockupbilldata = LoadingAdvice().stockupbill_loadingadvice_link(cookies, sourceBillCategory, sourceType,
                                                                         shopId, warehouseId, warehouseName,
                                                                         targetWarehouseId,
                                                                         operateDivisionId,
                                                                         purchaserId, purchaserName, product_code,supplierId,companyId)

        # 创建货柜列表
        sourceCodes=[stockupbilldata["sourceCode"]]
        containerBill_data = ContainerBill().create_containerbill_link(cookies, sourceCodes,
                                                                       sourceBillType, purchaserId,
                                                                       purchaserName, customsDeclarationSubId)

        return containerBill_data

    def shipmentbill_containerBill_link(self, cookies, sourceBillCategory, sourceType, shopId, warehouseId,
                                        warehouseName, operateDivisionId, purchaserId, purchaserName, targetWarehouseId,
                                        sourceBillType, customsDeclarationSubId, product_code, quantity,
                                        fbaShipmentCode,supplierId,companyId):
        """
        创建发货单发货全链路
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
        # 发货单按箱发货-装柜
        shipmentbilldata = LoadingAdvice().shipmentbill_loadingadvice_link(cookies, sourceBillCategory, sourceType,
                                                                           warehouseId, warehouseName,
                                                                           targetWarehouseId, operateDivisionId,
                                                                           shopId, purchaserId, purchaserName,
                                                                           product_code, quantity, fbaShipmentCode,supplierId,companyId)

        # 创建货柜列表
        containerBill_data = ContainerBill().create_containerbill_link(cookies, shipmentbilldata["shipmentBillCode"],
                                                                       sourceBillType, purchaserId,
                                                                       purchaserName, customsDeclarationSubId)

        return containerBill_data

    def booking_deliverybill_link(self, cookies, sourceBillCategory, shopId, warehouseId,
                                  warehouseName, operateDivisionId, purchaserId, purchasername, targetWarehouseId,
                                  sourceBillType, customsDeclarationSubId, product_code):
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
                                                           targetWarehouseId, product_code)
        # 装柜

        LoadingAdvice().loadingadvice_link(cookies, sourceBillCategory, warehouseId, warehouseName,
                                           booking_data["bookingid"], booking_data["bookingcode"])
        # 根据订舱单号查询备货单
        url = f"{waveecharmer_Host}/api/stockupbill/page?stockUpBillStatuses=1,2,3,5,6&sorts=%7B%22field%22:%22id%22,%22order%22:%22desc%22%7D&bookingBillCode={booking_data['bookingcode']}&pageIndex=1&pageSize=10"
        sourceCode_resp = StockupBill().query_stockupbill(url, cookies)
        sourceCode = json.loads(sourceCode_resp.text)["result"]["items"][0]["stockUpBillCode"]
        sourceCodes=[sourceCode]

        # 创建货柜列表
        #containerBill_data = ContainerBill().create_containerbill_link(cookies, sourceCodes, sourceBillType, purchaserId,
        #                                                               purchasername, customsDeclarationSubId
        #                                                               )
        #return containerBill_data


if __name__ == '__main__':
    cookies = Login.loginWecharmer()
    # ContainerBill().get_containerbill(cookies, "EGLV143470577152")
    # ContainerBill().create_containerbill_link(cookies,"BH24062000052",502,303,"李朋","3453353534")
    #count = 0
    #while count < 1:
    #    ContainerBill().booking_deliverybill_link(cookies, 507, 161, 15, "恒丰仓库", 5, 303, "李朋", 189, 502, 3,
    #                                              "A5-181")
    #    print("这是第 {} 次循环".format(count + 1))
    #    count += 1

    # 订舱单-装柜列表
    # ContainerBill().booking_deliverybill_link(cookies, 507, 161, 15, "恒丰仓库", 5, 303, "李朋", 12, 502, 3, "A5-181")

    # 备货单-按件-货柜列表
    count = 0
    while count < 200:
        ContainerBill().stockupbill_containerBill_link(cookies, 502, 2, 161, 150, "李朋自营仓", 5, 303, "李朋", 11, 502, 3,
                                                        "A5-181",6,2)
        print("这是第 {} 次循环".format(count + 1))
        count += 1
    # 发货单-按箱-货柜列表
    #ContainerBill().shipmentbill_containerBill_link(cookies,505,1,162, 150, "李朋自营仓",5, 303, "李朋",135,505,3,"A5-181",3, "FBA16M9J26TK",6,2)
