# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/5/27 下午2:15
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : task_api.py
# @Project : wecharmer
import requests

from conf.baseconfig import waveecharmer_Host


class Task_Api:
    def __init__(self):

        pass

    def create_waitapplycontainer(self, cookies, payload):
        """
        生成待申请排柜池数据
        :return:
        """
        url = f"{waveecharmer_Host}/api/waitapplycontainer/generate-data/job"
        resp = requests.post(url=url, headers=cookies,json=payload)
        print("生成待申请排柜池数据resp-----------\n" + resp.text)
        return resp


    def out_execution(self, cookies, payload):
        """
        执行所有申请排柜规则，更新待申请排柜池的是否可排柜
        :return:
        """
        url = f"{waveecharmer_Host}/api/waitapplycontainer/execution-rules/job"
        resp = requests.post(url=url, headers=cookies,json=payload)
        print("执行所有申请排柜规则，更新待申请排柜池的是否可排柜resp-----------\n" + resp.text)
        return resp





