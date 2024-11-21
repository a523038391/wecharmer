# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/14 下午2:46
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : dboperation.py
# @Project : wecharmer
from util.dataUtil import dataUtil
import time


class DbOperation:
    def __init__(self):
        pass

    def insert_into_order(self):
        AmazonOrderId = "Lipeng323-6996235-" + dataUtil.random_string(6)
        AmazonOrderData = f'{{"OrderItems":[{{"ASIN":"B0CCNSB2Q8","SellerSKU":"4INHX-MF-Q","OrderItemId":"100041395414601","Title":"MASVIS Queen Size Dual Layer 4 Inch Memory Foam Mattress Topper, 2 Inch Gel Memory Foam and 2 Inch Cooling Pillow Top Mattress Pad Cover for Back Pain, Medium Support","QuantityOrdered":1,"QuantityShipped":0,"ProductInfo":{{"NumberOfItems":1}},"IsGift":false,"IsTransparency":false,"BuyerInfo":{{}}}}],"OrderStatus":"Pending","FulfillmentChannel":"AFN","PaymentMethod":"Other","OrderType":"StandardOrder","AmazonOrderId":"{AmazonOrderId}","SellerOrderId":"{AmazonOrderId}","PurchaseDate":"2024-05-13T10:25:23Z","LastUpdateDate":"2024-05-13T10:25:33Z","SalesChannel":"Amazon.com","ShipServiceLevel":"Expedited","NumberOfItemsShipped":0,"NumberOfItemsUnshipped":1,"PaymentMethodDetails":["Standard"],"MarketplaceId":"ATVPDKIKX0DER","ShipmentServiceLevelCategory":"Expedited","EarliestShipDate":"2024-05-13T13:20:00Z","LatestShipDate":"2024-05-13T13:20:00Z","IsBusinessOrder":false,"IsPrime":false,"IsPremiumOrder":false,"IsGlobalExpressEnabled":false,"IsReplacementOrder":false,"IsSoldByAB":false,"IsISPU":false,"IsAccessPointOrder":false,"BuyerInfo":{{}},"HasRegulatedItems":false}}'
        sql = f"INSERT INTO amazonorder VALUES (NULL,'{AmazonOrderId}','{AmazonOrderData}','162','QICHEN_US_US','US','United States of America','7','亚马逊','Amazon','YA','0','0','李朋测试123','2024-04-03 07:56:11.621136','2024-04-03 08:00:01.346219','1','1','1','管理员','管理员','0',NULL,NULL,'1','2','2024-03-30 01:27:31.000000','1','2024-03-25 00:36:46.000000','李朋批量插入数据需删除','2','获取订单详情成功','0')"
        print(sql)
        dataUtil.update_data(sql)


if __name__ == '__main__':
    for i in range(10):

        DbOperation().insert_into_order()
        time.sleep(0.1)
        print(i)

