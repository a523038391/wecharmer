# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/10/9 下午3:45
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : demo.py
# @Project : wecharmer
import time
import uuid


import json

import pandas as pd
import requests
import hashlib
import random
import time
from urllib.parse import quote

# 有道翻译API的URL和你的APP_KEY与APP_SECRET
YOUDAO_URL = "https://openapi.youdao.com/api"
APP_KEY = "212b0a5a74f2a7e5"
APP_SECRET = "3MSzbZBgHEbluiEurhC9XGxR7KJL5luH"


def youdao_translate(text, to_lang="es"):
    """
    使用有道翻译API进行翻译
    """
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    sign = APP_KEY +text + salt + curtime + APP_SECRET
    sign = hashlib.sha256(sign.encode('utf-8')).hexdigest()
    signType="v3"

    url = f"{YOUDAO_URL}?appKey={APP_KEY}&q={quote(text)}&from=zh-CHS&to={to_lang}&salt={salt}&sign={sign}&curtime={curtime}&signType={signType}"
    #url1=f"{YOUDAO_URL}?appKey={APP_KEY}&q={quote(text)}&from=zh-CHS&to={to_lang}&salt={salt}&sign={sign}&curtime={curtime}&signType={signType}"
    print(url)
    response = requests.get(url)
    if json.loads(response.text)["errorCode"] == "0":
        result=json.loads(response.text)["translation"][0]
        print(result)
        return result

    return ""



# 读取Excel文件
file_name = '导出多语言数据2024112010522524112000052.xlsx'
df = pd.read_excel(file_name)

# 确保'Text'列是字符串类型
df['Text'] = df['Text'].astype(str)

# 遍历DataFrame中的每一行
for index, row in df.iterrows():
    # 检查'Code'列是否有文本
    for index, row in df.iterrows():
        # 检查'Code'列是否有文本
        if pd.notna(row['Code']):
            # 翻译文本
            translated_text = youdao_translate(str(row['Code']))

            if translated_text:  # 如果翻译成功
                df.at[index, 'Text'] = translated_text
                # 将当前DataFrame状态保存到Excel文件
                df.to_excel(file_name, index=False)
                time.sleep(2)
                print(f"Translated and saved row {index + 1}")



print("翻译完成并保存到原文件")

