# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/6/3 下午4:30
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : firstleg_ui.py
# @Project : wecharmer
from conf.baseconfig import waveecharmer_ui
from selenium import webdriver
from lib.login_ui import LoginUi
from selenium.webdriver.common.by import By

import time

class FirstLeg_Ui:
    def __init__(self):
        pass


    def query_containerlist(self,driver,billNo):
        url = f"{waveecharmer_ui}/express/container/list"
        driver.get(url)
        driver.find_element(By.XPATH,"//textarea[@placeholder='提单号']").send_keys(billNo)
        driver.find_element(By.XPATH,"//*[contains(text(),'查 询')]").click()
        time.sleep(2)
        shippingCompanyCode=driver.find_element(By.XPATH, '//tbody[@class="ant-table-tbody"]/tr[2]/td[27]').text
        print(shippingCompanyCode)

        content = driver.find_element(By.XPATH, '//tbody[@class="ant-table-tbody"]/tr[2]/td[26]/a').text
        print(content)
        if content == "进行中" or "已完成" :
            print("判断")
            driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//tbody[@class="ant-table-tbody"]/tr[2]/td[26]/a'))
            #driver.find_element(By.XPATH, '//tbody[@class="ant-table-tbody"]/tr[2]/td[26]/a').click()
            time.sleep(1)

            #进场时间
            enterPortTime=driver.find_element(By.XPATH, "//div[contains(text(),'进场')]/following-sibling::div[1]").text
            print(enterPortTime)

        else:
            enterPortTime=None

        return shippingCompanyCode




if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.maximize_window()
    LoginUi().login(driver)
    #time.sleep(2)

    FirstLeg_Ui().query_containerlist(driver,"EGLV143467030058")
    driver.quit()