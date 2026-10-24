# -*- coding: utf-8 -*-
import json

import requests

from conf.baseconfig import waveecharmer_Host


class SupplierInventoryv2_Api:
    def page_supplierinventory(self, cookies, payload):
        """按采购单号及仓库等条件分页查询供应商库存明细。"""
        url = f"{waveecharmer_Host}/api/supplierinventory/page"
        # GET 集合参数的每个元素按 JSON 编码，字符串需保留双引号。
        # 与旧库存查询 purchaseOrderCodes=%22采购单号%22 的传法一致。
        params = {}
        for key, value in payload.items():
            if isinstance(value, (list, tuple)):
                params[key] = [json.dumps(item, ensure_ascii=False) for item in value]
            elif isinstance(value, bool):
                params[key] = json.dumps(value)
            else:
                params[key] = value
        resp = requests.get(url=url, headers=cookies, params=params, timeout=30)
        print("查询供应商库存明细resp-----------\n" + resp.text)
        return resp
