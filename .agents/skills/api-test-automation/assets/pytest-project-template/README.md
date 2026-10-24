# pytest 接口自动化测试项目

基于 pytest + requests 的接口自动化测试框架，由「接口自动化」skill 生成。

## 环境准备

```bash
pip install -r requirements.txt
```

## 配置

修改 `config.ini`：

- `[api] base_url`：被测服务地址
- `[auth] token`：固定 token（留空则读取环境变量 `AUTH_TOKEN`）

## 运行

```bash
# 运行全部用例
pytest

# 运行指定文件 / 指定用例
pytest test_cases/test_user_api.py
pytest test_cases/test_user_api.py::TestCreateUser::test_create_user_success
```

## 目录结构

```
├── conftest.py            # 全局 fixture：base_url、token、http_client
├── config.ini             # 环境配置
├── utils/
│   ├── http_client.py     # requests 封装（token 头、超时、日志）
│   ├── assertions.py      # assert_ok / assert_fail 通用断言
│   └── cleanup.py         # 后置清理注册器
└── test_cases/            # 按接口模块组织的测试用例
```

## 编写用例规范

- 正常场景：`data = assert_ok(resp, business_code=0)` 后断言具体 data
- 异常场景：`assert_fail(resp, status_code=400, business_code=10001, message_keyword="...")`
- 创建数据：用 yield fixture 或 `CleanupRegistry` 后置清理
- 详细规范见 skill 的 `references/codegen-rules.md`
