# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/10/10 下午2:19
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : demo1.py
# @Project : wecharmer


import pandas as pd
from googletrans import Translator

# 初始化翻译器
translator = Translator()

# 读取Excel文件
file_name = '导出多语言数据20241009153841_24100900101.xlsx'
df = pd.read_excel(file_name)

# 确保'Text'列是字符串类型
df['Text'] = df['Text'].astype(str)

# 定义一个函数来翻译文本
def translate_text(text, dest_lang="en"):
    try:
        # 自动检测语言并翻译到目标语言
        translation = translator.translate(text, dest=dest_lang)
        # 检查翻译结果是否为None
        if translation is not None:
            return translation.text
        else:
            return "Translation failed"
    except Exception as e:
        print(f"Error: {e}")
        return "Translation failed"

# 遍历DataFrame中的每一行
for index, row in df.iterrows():
    # 检查'Code'列是否有文本
    if pd.notna(row['Code']):
        # 翻译文本
        df.at[index, 'Text'] = translate_text(str(row['Code']))

# 将翻译后的DataFrame保存到原Excel文件
df.to_excel(file_name, index=False)

print("翻译完成并保存到原文件")