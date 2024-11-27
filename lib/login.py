# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/13 下午2:16
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : login.py
# @Project : wecharmer


import json
from conf.baseconfig import userName, passWord, waveecharmer_Host, freightower_Host, f_userName, f_passWord
from util import httpUtil


class Login:
    @classmethod
    def loginWecharmer(cls):
        """
        登录微诚ERP获取鉴权信息
        :param userName 账号
        :param passWord 密码
        :return:
        """
        url = f"{waveecharmer_Host}/api/account/login"
        payload = {
            "tenantName": "Wecharmer.Hero",
            "account": userName,
            "password": passWord
        }

        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, "")

        if json.loads(resp.text)["code"] == 'Success':
            cookies = {"Authorization": json.loads(resp.text)["result"]}
            print("cookies:", cookies)
            return cookies

        else:
            print(f"登录失败，账号{userName}密码：{passWord}")

    @classmethod
    def loginFreightower(cls):
        """
        登录飞驼获取鉴权信息
        :param f_userName 账号
        :param f_passWord 密码
        :return:
        """
        url = f"{freightower_Host}/auth/api/token"

        payload = {
            "clientId": f_userName,
            "secret": f_passWord
        }
        resp = httpUtil.HttpUtil.make_http_request(url, "post", payload, "")


        if json.loads(resp.text)["message"] == '成功':
            cookies = {"Authorization": f"Bearer {json.loads(resp.text)['data']['access_token']}"}
            print("获取cookies:\n", cookies)
            return cookies

        else:
            print(f"登录失败，账号{f_userName}密码：{f_passWord}")


if __name__ == '__main__':
    Login().loginWecharmer()
    #Login().loginFreightower()
