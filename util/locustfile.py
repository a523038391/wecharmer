# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/4/14 下午4:39
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : locustfile.py.py
# @Project : wecharmer
from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 3)  # 每个用户请求间隔 1~3 秒

    @task(3)  # 权重为3，更频繁执行
    def get_list(self):
        self.client.get("/api/items")

    @task(1)  # 权重为1
    def create_item(self):
        payload = {"name": "test", "price": 10.5}
        self.client.post("/api/items", json=payload)