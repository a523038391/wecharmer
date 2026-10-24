# -*- coding: utf-8 -*-
import requests

from conf.baseconfig import waveecharmer_Host


class WaitContainerBill_Api:
    def page_waitapplycontainer(self, cookies, payload):
        """分页查询待申请排柜池。"""
        url = f"{waveecharmer_Host}/api/waitapplycontainer/page"
        resp = requests.post(url=url, headers=cookies, json=payload, timeout=30)
        print("分页查询待申请排柜池resp-----------\n" + resp.text)
        return resp

    def create_waitcontainerbillv2(self, cookies, payload):
        """从申请池创建待排柜单，支持多条采购明细。"""
        url = f"{waveecharmer_Host}/api/waitcontainerbillv2/createv2"
        resp = requests.post(url=url, headers=cookies, json=payload, timeout=30)
        print("申请排柜resp-----------\n" + resp.text)
        return resp

    def waitcontainerbillv2_askapprove(self, cookies, waitContainerBillId):
        """新版待排柜送审。"""
        url = f"{waveecharmer_Host}/api/waitcontainerbillv2/ask-approval"
        resp = requests.put(url=url, headers=cookies, params={"id": waitContainerBillId}, timeout=30)
        print("新版待排柜送审resp-----------\n" + resp.text)
        return resp
