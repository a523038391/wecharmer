# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/13 下午2:37
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : httpUtil.py
# @Project : wecharmer
import requests



class HttpUtil:
    @classmethod
    def make_http_request(cls,url,method,payload,cookies):
        methods = {
            "get" : requests.get,
            "post" : requests.post,
            "put" : requests.put,
            "delete" : requests.delete
        }

        try:
            request_func= methods[method]

            response = request_func(url,json=payload,headers=cookies)

            response.raise_for_status()

            return response

        except KeyError:
            raise ValueError({f"不支持的http方法：{method}"})
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(response.text)

        except requests.exceptions.RequestException as err:
            print(f"Other error occurred: {err}")
