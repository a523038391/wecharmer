# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/5/23 下午5:42
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : login_ui.py
# @Project : wecharmer
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


import option
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By



from conf.baseconfig import waveecharmer_ui,userName,passWord
global driver

class LoginUi:

    def login(self,driver):
        url = f"{waveecharmer_ui}/user/login"
        driver.get(url)
        #driver.implicitly_wait(5)
        #time.sleep(2)
        print(driver.find_element(By.XPATH, '//*[@id="formLogin"]/div[1]/div/div/div/span').is_displayed())
        driver.find_element(By.XPATH, '//*[@id="formLogin"]/div[1]/div/div/div/span/input').send_keys(userName)
        driver.find_element(By.XPATH, '//*[@id="formLogin"]/div[2]/div/div/div/span/input').send_keys(passWord)
        driver.find_element(By.XPATH,"//*[contains(text(),'登')]").click()
        #time.sleep(3)
        WebDriverWait(driver, timeout=10).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'欢迎使用微诚ERP系统')]")))





if __name__ == '__main__':
    driver = webdriver.Edge()  # 启动Edge浏览器

    LoginUi().login(driver)


















