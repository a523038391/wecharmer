# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/19 下午2:07
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : send_dingding.py
# @Project : wecharmer


import os
import requests
# 导入jenkins文件的包
from jenkins import Jenkins


class JenkinsContest:
    def __init__(self):
        # jenkins的IP地址
        self.jenkins_url = "http://127.0.0.1:8080/"

        # 登录jenkins
        self.server = Jenkins(self.jenkins_url, username='lipeng', password='Aa123456!')

    def Send_DingTalk(self):
        # 选择你的jenkins项目名称的地址,这段代码加上jenkins的url就会进入你的ApiTest项目
        job_name = "job/web自动化测试"
        # 发消息的地址
        job_url = self.server.get_info(job_name)["url"]
        # 获取最新的构建任务名称，用于拼接后续allure地址
        job_last_number = self.server.get_info(job_name)["lastBuild"]["number"]

        # 测试报告allure地址
        report_url = job_url + str(job_last_number) + "/allure"
        print(report_url)
        content = {}
        file_path = os.path.dirname(os.getcwd()) + "/allure-report/export/prometheusData.txt"
        print(file_path)
        f = open(file_path, "r", encoding="utf-8")
        for line in f.readlines():
            launch_name = line.strip("\n").split()[0]
            num = line.strip("\n").split()[1]
            # 把分割出来的数据组装成键值对 update是一个方法用于组装字典的
            content.update({launch_name: num})
        f.close()
        passed_num = content["launch_status_passed"]  # 通过数量
        failed_num = content["launch_status_failed"]  # 失败数量
        broken_num = content["launch_status_broken"]  # 阻塞数量
        skipped_num = content["launch_status_skipped"]  # 跳过数量
        case_num = content["launch_retries_run"]  # 总数量
        print(content)

        """
        钉钉消息发送，通过webhook发送消息
        """
        content = {
            "msgtype": "text",
            "text": {
                "content": "自动化测试报告结果: \n运行总数" + case_num
                           + "\n通过数量: " + passed_num
                           + "\n失败数量: " + failed_num
                           + "\n阻塞数量: " + broken_num
                           + "\n跳过数量: " + skipped_num
                           + "\n构建地址: " + job_url
                           + "\n报告地址: " + report_url
            }
        }
        webhook = "https://oapi.dingtalk.com/robot/send?access_token=26b4b5963ab1d629ba3ed9efd8ff8362806003f01b1570e80e2b86597355f212"
        requests.post(url=webhook, json=content, verify=False)


if __name__ == '__main__':
   JenkinsContest().Send_DingTalk()