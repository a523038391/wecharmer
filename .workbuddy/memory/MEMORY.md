# wecharmer 项目记忆

## 项目概述
微诚ERP(Wecharmer)接口自动化测试框架，作者 lipeng(李朋)。
覆盖跨境电商头程物流全链路：采购→订舱→验货→备货→装箱→装柜→发货。
同时对接飞驼(Freightower)海运物流跟踪平台。

## 架构分层
- main.py: pytest入口 + allure报告，pytest.ini配置 -vs/失败重跑2次/alluredir
- testcase/: 3个测试文件(test_api_firstleg / test_freightower / test_ui_firstleg)
- lib/: 业务逻辑核心，头程8子模块 + 采购/供应商/商品/仓储/货柜/飞驼/登录
- util/: HttpUtil(HTTP封装) / dataUtil(DB工具pymysql) / asyncio_aiohttp(异步压测) / locustfile(Locust)
- conf/: baseconfig(域名/账号/DB/Jenkins/钉钉) / dataconfig(测试数据:SKU/仓库/店铺/事业部/员工/供应商)
- message/: send_dingding(钉钉机器人+Jenkins报告推送)

## 核心设计模式
lib/下每个业务模块封装两层：
- 单步操作方法：如 create_stockupbill, query_stockupbill
- _link全链路方法：如 create_stockupbill_link，串联多步骤完整流程
测试用例调用_link方法即可跑通整条链路。

## 关键文件
- lib/login.py: 三系统登录(ERP/EMC/飞驼)，返回 {"Authorization": token} header
- lib/firstleg/inspection.py: 验货全链路编排(最核心的_link方法)
- lib/firstleg/booking.py: 订舱单链路(含FBA预定舱分支)
- lib/firstleg/stockupbill.py: 备货单链路(按件/按箱两种)
- lib/freightower.py: 飞驼海运物流跟踪(船公司匹配/海运跟踪/码头订阅/海关跟踪)

## 已知问题
- interface/层6个文件基本是空壳，未完成从lib/分离接口定义
- HTTP调用不统一：inspection.py/stockupbill.py等部分方法直接import requests绕过HttpUtil封装
- 敏感信息(密码/DB凭据/钉钉token)硬编码在baseconfig.py
