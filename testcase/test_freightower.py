# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/13 下午5:35
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : test_freightower.py
# @Project : wecharmer
import json
import os
from datetime import datetime

import pytest

from lib.firstleg.containerbill import ContainerBill
from util.dataUtil import dataUtil
from lib.freightower import Freightower
from lib.login import Login


class TestFreightower:

    def setup_class(self):
        self.cookies_ft = Login.loginFreightower()
        self.cookies_wc = Login.loginWecharmer()
        self.billNo = "EGLV143467030058"
        self.portCode = "CNNGB"

    def teardown_class(self):
        pass

    def setup_function(self):
        pass

    def teardown_function(self):
        pass

    @pytest.mark.firstleg
    def test_freightower_link(self):
        #船公司识别，获取编码
        firstleg_resp = ContainerBill().get_containerbill(self.cookies_wc, self.billNo)
        freightower_resp=Freightower().freightower_link(self.cookies_ft,self.billNo,self.portCode)
        shipVoyage = json.loads(firstleg_resp.text)["result"]["items"][0]["shipVoyage"]
        print(shipVoyage.split("/")[0])

        assert json.loads(firstleg_resp.text)["result"]["items"][0]["shippingCompanyCode"] == json.loads(freightower_resp)["carrierCode"]

        assert shipVoyage.split("/")[0] == json.loads(freightower_resp)["vessel"]
        assert shipVoyage.split("/")[1] == json.loads(freightower_resp)["voyage"]
        datetime.now()





if __name__ == '__main__':
    #pytest.main(['-vs', '--reruns=2','test_freightower.py'])
    #pytest.main(['-vs', '--reruns=2', '-k=link'])
    #pytest.main(['-vs','--reruns', '2', '--alluredir','../report/my_allure_results'])
    pytest.main(['-vs', '--html', './5256785252.html'])

    #pytest.main(['-vs',"testcase/test_freightower.py" ,'--html', '../report/5256785252.html'])


    #os.system('allure generate ../temp/my_allure_results -o ../report --clean')





