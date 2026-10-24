# 代码生成规范（Codegen Rules）

生成 pytest + requests 接口自动化测试代码时遵循以下规范。所有规则以「可直接运行、结构清晰、便于改造」为目标。

## 1. 项目结构

```
<目标目录>/
├── conftest.py              # 全局 fixture：base_url、token、http_client
├── pytest.ini               # pytest 配置（testpaths、addopts）
├── requirements.txt         # pytest、requests 依赖
├── config.ini               # base_url / timeout / token 配置
├── utils/
│   ├── __init__.py
│   ├── http_client.py       # requests 封装：token 头、超时、请求日志
│   ├── assertions.py        # assert_ok / assert_fail 通用断言
│   └── cleanup.py           # CleanupRegistry 后置清理注册器
└── test_cases/
    ├── __init__.py
    └── test_<模块>_api.py   # 按接口模块拆分，如 test_user_api.py
```

所有请求一律通过 `http_client` fixture 发起（它持有 base_url 与 token），**禁止在用例中硬编码 URL 或 token**。

## 2. 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 测试文件 | `test_<模块>_api.py` | `test_order_api.py` |
| 测试类 | `Test<接口名>`，一个接口一个类 | `TestCreateOrder` |
| 测试方法 | `test_<场景>_<预期>`，动词开头 | `test_create_order_success`、`test_create_order_invalid_amount` |
| fixture | 名词短语 | `created_order`、`token` |

测试方法必须写 docstring，注明用例编号与验证点（如 `用例 TC-002：创建订单成功，返回订单号`）。

## 3. 断言规范

### 3.1 正常场景（三要素缺一不可）

```python
def test_create_user_success(self, http_client):
    """用例 TC-001：创建用户成功，返回用户 id"""
    resp = http_client.post("/api/users", json={
        "name": "test_user",
        "email": f"auto_{int(time.time())}@example.com",
    })
    data = assert_ok(resp, business_code=0)          # HTTP 状态码 + 业务 code + data 存在
    assert data["id"] > 0                             # 业务数据校验
    assert data["name"] == "test_user"
```

`assert_ok(resp, business_code=0)` 内部完成三件事：
1. `resp.status_code in (200, 201)` — HTTP 状态码
2. `resp.json()["code"] == business_code` — 业务码
3. `"data" in resp.json()` — 返回 data，并返回 `data` 供后续断言

### 3.2 异常场景（错误码 + 错误信息）

```python
def test_create_user_missing_name(self, http_client):
    """用例 TC-010：缺少必填字段 name，返回参数错误"""
    resp = http_client.post("/api/users", json={"email": "x@example.com"})
    assert_fail(resp, status_code=400, business_code=10001, message_keyword="name")
```

`assert_fail` 依次校验：HTTP 状态码 → 业务错误码 → 错误信息关键词。参数可省略，但**至少断言业务错误码和错误信息中的一项**。

### 3.3 响应结构适配

接口文档中的字段名可能不同，按实际结构断言：

| 常见响应 | 断言写法 |
|---------|---------|
| `{"code": 0, "data": {...}}` | `assert_ok(resp, business_code=0)` |
| `{"code": 0, "msg": "success", "data": ...}` | message 字段为 `msg`，需在断言中直接用 `body["msg"]` |
| 分页列表 `{"code":0, "data": {"list": [...], "total": n}}` | `data = assert_ok(resp)`；`assert data["total"] >= 0`；遍历 `data["list"]` |
| HTTP 状态码即语义（RESTful，无业务码） | `assert resp.status_code == 200` 并直接断言 body |

若文档未说明业务码取值，从文档的错误码表提取；文档缺失时按常见约定（0/200/1 表示成功）并在交付说明中标注假设。

## 4. Token 处理

- **固定 token**：写入 `config.ini` 的 `[auth] token` 或环境变量 `AUTH_TOKEN`，conftest 按 配置 > 环境变量 顺序读取
- **登录获取**：文档提供登录接口时，在 conftest 增加 `token` fixture：

```python
@pytest.fixture(scope="session")
def token(base_url):
    resp = requests.post(f"{base_url}/api/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    return resp.json()["data"]["token"]

@pytest.fixture(scope="session")
def http_client(base_url, token):
    return HttpClient(base_url=base_url, token=token)
```

- token 请求头位置按文档调整：默认 `Authorization: Bearer <token>`；文档为自定义头（如 `X-Token`）时修改 `HttpClient.__init__` 中的 header 键
- 生成代码中**不写死任何真实 token 值**，只留配置入口

## 5. 后置清理

创建型数据（新增用户/订单/文件等）必须清理。优先使用 `yield` fixture 或 `CleanupRegistry`：

### 方式一：yield fixture（推荐，简单直接）

```python
@pytest.fixture
def created_user(http_client):
    user_id = None
    try:
        resp = http_client.post("/api/users", json={...})
        data = assert_ok(resp)
        user_id = data["id"]
        yield user_id
    finally:
        if user_id:
            del_resp = http_client.delete(f"/api/users/{user_id}")
            assert del_resp.status_code in (200, 204), f"清理失败: {del_resp.text}"
```

### 方式二：CleanupRegistry（多个资源 / 用例内动态创建）

```python
@pytest.fixture
def created_user(http_client):
    cleanup = CleanupRegistry(http_client)
    data = assert_ok(http_client.post("/api/users", json={...}))
    cleanup.register("delete", "/api/users/{id}", id=data["id"])
    yield data["id"], cleanup
    cleanup.run()          # 后进先出执行全部清理
```

清理规则：
- 清理请求的断言失败不应掩盖用例结果，`CleanupRegistry.run()` 收集错误并记日志，不抛异常
- 删除类清理放行 404（资源已被外部删除视为清理成功）
- 多资源按创建顺序逆序删除（先删子资源再删父资源）
- 清理使用与被测相同的 `http_client`（同样带 token）

## 6. 测试数据生成

- 名称、邮箱、手机号等唯一性字段追加时间戳或随机后缀：`f"auto_{int(time.time())}"`、`uuid4().hex[:8]`
- 边界值用例（超长字符串、负数、超大数值、空值）在用例内直接构造，不依赖 fixture
- 多个用例共用一套创建逻辑时提取为 fixture；单用例独有逻辑直接写在用例内

## 7. 日志与可观测性

- `utils/http_client.py` 已内置请求日志（方法、URL、状态码、响应体），无需在用例中重复打印
- 断言失败信息必须包含响应体（`resp.text`），便于定位：`assert_fail` 与 `assert_ok` 的失败消息已包含 body

## 8. 易错点清单

1. **不要**在用例里直接 `requests.get(...)`，一律走 `http_client`（否则丢 token、丢 base_url）
2. **不要**在用例里写死 `http://...` 完整地址
3. **不要**忽略异常用例——接口文档中的每个错误码都应至少有一条用例覆盖
4. **不要**把清理写在 `assert` 之前跳过；用 `try/finally` 或 fixture teardown 保证失败也能清理
5. 断言尽量具体：`assert data["total"] == 3` 优于 `assert data["total"] > 0`（数据可预测时）
6. 用例之间**相互独立**：不依赖执行顺序、不共享可变数据；需要共享的创建逻辑用 fixture
7. 响应可能非 JSON（如 204/文件流），先判断 `resp.content` 再 `.json()`，`assert_ok` 只用于 JSON 响应
