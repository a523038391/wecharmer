# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/6 下午3:02
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : main.py
# @Project : wecharmer
import os
import time

import pytest

if __name__ == '__main__':
    #os.system('allure generate ./temp/my_allure_results -o ./report --clean')
    #pytest.main(['-vs',"testcase/test_freightower.py" ,'--html', './report/5256785252.html'])
    #pytest.main(['-vs', "testcase",'--alluredir=./temp/my_allure_results'])

    #os.system('allure generate ./temp/my_allure_results -o ./report --clean')
    #os.system("allure serve ./report")
    pytest.main(['-vs', '--html','./report/5256785252.html'])
    os.system('allure generate ./temp/my_allure_results -o ./allure-report --clean')
