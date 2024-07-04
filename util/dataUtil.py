# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/14 下午12:35
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : dataUtil.py
# @Project : wecharmer
import random
import string

from conf.baseconfig import db


class dataUtil:


    @classmethod
    def random_string(cls, length):
        characters=string.ascii_letters+string.digits
        return ''.join(random.choice(characters) for i in range(length))


    # 创建数据库连接
    @classmethod
    def getConn(cls):
        import pymysql

        return pymysql.connect(host=db["server"],
                               port=3306,
                               user=db["uid"],
                               password=db["pwd"],
                               database=db["database"],
                               charset='utf8')

    # 查询数据
    @classmethod
    def query_all(cls, sql):
        conn = dataUtil.getConn()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            results = cur.fetchall()
            for row in results:
                print(row)
        except Exception as a:
            results = None
        finally:
            cur.close()
            conn.close()
        return results

    # 增删改操作
    @classmethod
    def update_data(cls, sql):
        print(sql)
        flag = False
        conn = dataUtil.getConn()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            flag = True
            print(flag)
        finally:
            cur.close()
            conn.close()
            return flag


if __name__ == '__main__':
    AmazonOrderData = '{"OrderItems":[{"ASIN":"B0CCNSB2Q8","SellerSKU":"4INHX-MF-Q","OrderItemId":"100041395414601","Title":"MASVIS Queen Size Dual Layer 4 Inch Memory Foam Mattress Topper, 2 Inch Gel Memory Foam and 2 Inch Cooling Pillow Top Mattress Pad Cover for Back Pain, Medium Support","QuantityOrdered":1,"QuantityShipped":0,"ProductInfo":{"NumberOfItems":1},"IsGift":false,"IsTransparency":false,"BuyerInfo":{}}],"OrderStatus":"Pending","FulfillmentChannel":"AFN","PaymentMethod":"Other","OrderType":"StandardOrder","AmazonOrderId":"113-6996235-0223445","SellerOrderId":"113-6996235-0223445","PurchaseDate":"2024-05-13T10:25:23Z","LastUpdateDate":"2024-05-13T10:25:33Z","SalesChannel":"Amazon.com","ShipServiceLevel":"Expedited","NumberOfItemsShipped":0,"NumberOfItemsUnshipped":1,"PaymentMethodDetails":["Standard"],"MarketplaceId":"ATVPDKIKX0DER","ShipmentServiceLevelCategory":"Expedited","EarliestShipDate":"2024-05-13T13:20:00Z","LatestShipDate":"2024-05-13T13:20:00Z","IsBusinessOrder":false,"IsPrime":false,"IsPremiumOrder":false,"IsGlobalExpressEnabled":false,"IsReplacementOrder":false,"IsSoldByAB":false,"IsISPU":false,"IsAccessPointOrder":false,"BuyerInfo":{},"HasRegulatedItems":false}'
    sql = f"INSERT INTO amazonorder VALUES (NULL,'113-6996235-0223445','{AmazonOrderData}','44','KUMAN_US','US','United States of America','7','亚马逊','Amazon','YA',NULL,'0','李朋测试123','2024-04-03 07:56:11.621136','2024-04-03 08:00:01.346219','1','1','1','管理员','管理员','0',NULL,NULL,'1','2','2024-03-30 01:27:31.000000','1','2024-03-25 00:36:46.000000','李朋批量插入数据需删除','2','获取订单详情成功','0')"

#   dataUtil().query_all(sql)
#   dataUtil().update_data(sql)
