---
name: api-test-automation
description: 根据接口文档（API 文档）与接口测试用例，生成可直接运行的 Python + pytest + requests 接口自动化测试脚本。当用户要求「生成自动化测试脚本 / pytest 脚本 / 接口自动化用例 / 测试代码 / 接口测试」，并提供了接口文档或接口测试用例（或两者之一）时使用。生成的脚本支持 base_url 配置、token 请求头、正常/异常场景断言、创建数据的后置清理，结构清晰可直接放入项目运行。
agent_created: true
---

# 接口自动化（API Test Automation）

## Overview

将接口文档 + 接口测试用例转换为一个完整、可运行的 pytest + requests 测试项目。本项目以「生成代码」为核心交付物：在用户指定的目录下产出符合规范的项目结构，用户可直接运行或改造。

## 触发时机

- 用户粘贴接口文档（接口路径、请求方法、参数、响应结构、错误码）
- 用户粘贴接口测试用例（正常场景、异常场景、边界值）
- 用户要求「生成 pytest 自动化测试脚本 / 接口自动化测试代码」
- 用户仅提供接口文档，要求自动推导测试用例并生成脚本

## 工作流

### Step 1: 解析输入

从接口文档与测试用例中提取以下信息：

- **base_url**：文档中的服务地址（如 `http://10.0.0.1:8080`）；未提供时保留模板中的占位并提示用户补充
- **认证方式**：token 的获取途径（固定 token / 登录接口返回 / 请求头位置，如 `Authorization: Bearer` 或自定义头 `X-Token`）
- **接口清单**：方法（GET/POST/PUT/PATCH/DELETE）+ 路径 + 请求参数（必填/选填/类型/校验规则）+ 响应结构（status_code、业务 code、data、message 字段名）
- **错误码表**：业务错误码及其含义，用于异常场景断言
- **用例清单**：逐条拆分正常场景、异常场景、边界值场景，标注每条的断言点

若用户只给了测试用例而未给接口文档，以用例中的请求信息为准；两者冲突时以接口文档为准，并在交付说明中标注差异。

### Step 2: 规划生成内容

按接口模块组织测试文件（一个接口/一个模块一个 `test_*.py`），列出：

- 基础骨架文件（从模板复制）：`conftest.py`、`pytest.ini`、`config.ini`、`requirements.txt`、`utils/` 下的封装
- 每个接口模块对应的 `test_cases/test_<module>_api.py`
- 若文档提供登录接口：为 conftest 增加自动获取 token 的 fixture
- 需要删除模板中与本次无关的示例文件

### Step 3: 生成基础骨架

从 `assets/pytest-project-template/` 复制模板到目标目录，然后按文档信息修改：

1. `config.ini`：写入真实的 `base_url`、`timeout`
2. `conftest.py`：
   - 保留 `base_url`、`http_client` fixture
   - 若 token 来自登录接口，增加 `token` fixture（登录 → 提取 token → 传给 http_client）；若为固定 token，指导用户写入 config.ini 或环境变量 `AUTH_TOKEN`
   - token 请求头位置按文档调整（默认 `Authorization: Bearer <token>`）
3. `utils/http_client.py`：若响应字段名不同（如 code 字段叫 `code`、message 叫 `msg`），无需改封装，在断言中按实际字段处理
4. 删除 `test_cases/test_user_api.py` 示例（除非本次目标就是用户接口）

### 结构与技术选型适配（在 Step 3/4 之前判断）

用户可能提出自定义目录结构或技术变体，以用户要求为准，但核心规范不变：

- 常见变体：`config.yaml`/`yaml` 数据驱动、`common/` 公共层、`testcases/` 目录、Allure 报告、pytest 参数化（`@pytest.mark.parametrize` 从 yaml 加载数据）
- 无论结构如何，保持：配置驱动（无硬编码 URL/token）、统一请求封装、断言三要素、创建数据后置清理
- 数据驱动时：yaml 中每个用例含 `case_id`（作参数化 id）、`title`（作 Allure 标题）、请求参数、`expect`（status_code/code/message_keyword/data_checks）、可选 `cleanup`
- 支持 Allure 时：`pytest.ini` 加 `--alluredir=reports/allure-results`；用例加 `@allure.feature/story/title` 装饰器（参数化动态标题用 `@allure.title("{case[title]}")`）；环境信息通过写入 `allure-results/environment.properties` 展示（**不要用 `allure.environment()`，该 API 不存在**）

### Step 4: 生成测试用例代码

在 `test_cases/` 下为每个接口模块生成 `test_<module>_api.py`。**严格遵循 `references/codegen-rules.md` 中的生成规范**，要点：

- 每个接口一个 `Test<接口名>` 类，每条用例一个 `test_` 方法
- 正常场景：使用 `assert_ok()` 断言 HTTP 状态码、业务 code、data 内容
- 异常场景：使用 `assert_fail()` 断言 HTTP 状态码、业务错误码、错误信息关键词
- 创建类数据：用 `yield` fixture 或 `CleanupRegistry` 注册后置清理
- 测试数据生成：名称/邮箱等字段追加时间戳或随机后缀，避免重复冲突
- 每条用例方法写 docstring 说明验证点，与测试用例编号对应（如 `用例编号: TC-001`）

### Step 5: 自检

生成完成后逐项检查：

1. 所有 `.py` 文件通过语法检查（运行 `python -m py_compile` 遍历生成目录）
2. 每个测试方法至少含一个断言
3. 正常场景覆盖 status_code + 业务 code + data
4. 异常场景覆盖错误码 + 错误信息
5. 所有创建数据的用例都有清理逻辑
6. 无硬编码 URL（一律走 `http_client` + `base_url`）
7. 无硬编码 token（一律走 config/env）

发现不合规项立即修复后再交付。

### Step 6: 交付

向用户说明：

- 生成的项目路径与目录结构
- 环境准备与运行方式（`pip install -r requirements.txt`、`pytest -v`）
- config.ini 中需要用户补充的配置（base_url、token）
- 与接口文档存在差异或未覆盖的用例

## 资源

### references/codegen-rules.md（必须加载）

生成代码时的完整规范：项目结构、命名、断言写法、清理策略、常见响应结构适配、易错点。**在 Step 3/4 生成代码前必须读取并遵循。**

### assets/pytest-project-template/（必须复制）

可直接复用的 pytest 项目模板，包含：

- `config.ini` — base_url / token / timeout 配置
- `conftest.py` — base_url、http_client fixture，token 注入
- `utils/http_client.py` — requests 封装（token 头、超时、日志）
- `utils/assertions.py` — `assert_ok` / `assert_fail` 通用断言
- `utils/cleanup.py` — 后置清理注册器
- `test_cases/test_user_api.py` — 完整示例（正常/异常/清理）
- `pytest.ini`、`requirements.txt`、`README.md`

复制整个 `pytest-project-template` 目录后按 Step 3/4 修改，而非逐文件重写。
