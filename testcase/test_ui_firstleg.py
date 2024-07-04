# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/3 下午4:38
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : test_ui_firstleg.py
# @Project : wecharmer
import json

import pytest
from selenium import webdriver

from lib.firstleg_ui import FirstLeg_Ui
from lib.freightower import Freightower
from lib.login_ui import LoginUi
from lib.login import Login


class TestFreightowerui:


    def setup_class(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        self.cookies_ft = Login.loginFreightower()
        self.cookies_wc = Login.loginWecharmer()
        self.billNo = "EGLV143467030058"
        self.portCode = "CNNGB"
        LoginUi().login(self.driver)



    def teardown_class(self):
        self.driver.quit()

    def setup_function(self):
        self.driver.refresh()

    def teardown_function(self):
        pass


    @pytest.mark.smoke
    @pytest.mark.firstleg
    def test_query_containerlist(self):

        ui_data = FirstLeg_Ui().query_containerlist(self.driver, self.billNo)


        freightower_data = Freightower().freightower_link(self.cookies_ft, self.billNo, self.portCode)

        if ui_data== "":
            assert  json.loads(freightower_data)["carrierCode"]== None

        else:

            assert ui_data == json.loads(freightower_data)["carrierCode"]




if __name__ == '__main__':
    #pytest.main(['-vs', 'test_ui_firstleg.py'])
    pytest.main(['-vs', '--html=','../report/5256785252.html'])
    #pytest.main(['-vs', '-k','test_query_containerlist'])