# 输出模板

所有产出使用以下模板。模板中的编号规则：需求 R-xx、业务规则 BR-xx、测试点 TP-xx、用例 TC-xx。

## 1. 测试需求分析模板

```markdown
# 测试需求分析：<需求/功能名>

## 1. 需求概述
- 需求来源：（PRD v2.1 / 会议纪要 2026-03-12 / 口头描述…，可多源并列）
- 需求背景与目标：
- 涉及角色：

## 2. 功能点清单
| 编号 | 模块 | 功能点 | 优先级 | 信息来源 |
|---|---|---|---|---|
| R-01 | 登录 | 手机号+验证码登录 | P0 | PRD v2.1 §2.1 |

## 3. 业务规则
| 编号 | 规则描述 | 关联需求 | 信息来源 |
|---|---|---|---|
| BR-01 | 验证码 60 秒内不可重复发送 | R-01 | PRD v2.1 §2.1.3 |

## 4. 数据字段（如有）
| 字段 | 类型 | 必填 | 校验规则 | 边界值 | 关联需求 |
|---|---|---|---|---|---|
| 手机号 | string | 是 | 11 位数字，以 1 开头 | 10/11/12 位 | R-01 |

## 5. 测试点分析
| 测试点 | 描述 | 覆盖维度 | 设计方法 | 优先级 | 关联需求/规则 |
|---|---|---|---|---|---|
| TP-01 | 合法手机号+正确验证码登录成功 | 正常功能流程 | 场景法 | P0 | R-01 |
| TP-02 | 手机号位数校验（10/11/12 位） | 边界值场景 | 边界值 | P1 | BR-02 |

## 6. 测试范围说明
- 本次覆盖：
- 本次不覆盖（原因）：

## 7. 假设与待确认
- 假设 A-01：…（假设内容）→ 影响 TP-xx
- 待确认：见《需求澄清问题清单》
```

## 2. 需求澄清问题清单模板

```markdown
# 需求澄清问题清单：<需求名>

> 共 N 个问题，按阻塞程度排序。P0 未澄清前，相关用例基于标注假设编写。

| 编号 | 问题 | 为什么需要澄清（影响什么） | 关联需求 | 阻塞级别 | 状态 |
|---|---|---|---|---|---|
| Q-01 | 手机号是否支持+86前缀格式？ | 影响 TP-02 等价类划分 | R-01 | P0 | 待澄清 |

## 冲突项
- [C-01] PRD v2.1 写「60 秒重发」，3/12 纪要写「120 秒」→ 以哪份为准？

## 缺失材料
- [M-01] PRD 引用的《支付流程图》未提供
```

## 3. 维度覆盖检查表模板

第 4 步生成测试点后必须填写本表，作为第 5 步审核材料。「⚠ 未覆盖」的维度需测试人员决定：补充测试点，或确认「不适用（写明具体理由）」。

```markdown
# 维度覆盖检查表：<需求名>

| # | 维度 | 测试点数 | 状态 | 说明 / 不适用理由 |
|---|---|---|---|---|
| 1 | 正常功能流程 | 6 | ✅ 已覆盖 | TP-01、TP-03… |
| 2 | 异常流程 | 4 | ✅ 已覆盖 | |
| 3 | 边界值场景 | 3 | ✅ 已覆盖 | |
| 4 | 权限控制 | 0 | ⚠ 未覆盖 | 待补充：登录分管理员/普通用户两种角色 |
| 5 | 数据校验 | 2 | ✅ 已覆盖 | |
| 6 | 状态流转 | 0 | ➖ 不适用 | 本需求无状态字段 |
| 7 | 前后端交互 | 2 | ✅ 已覆盖 | |
| 8 | 数据库一致性 | 0 | ⚠ 未覆盖 | 需开发协助验证 SQL，已标注 |
| 9 | 兼容性 | 1 | ✅ 已覆盖 | 按团队基线假设（Chrome/Edge），需求未声明 |
| 10 | 性能风险 | 1 | ✅ 已覆盖 | 仅风险识别，移交专项压测 |
| 11 | 安全风险 | 2 | ✅ 已覆盖 | 输入过滤 + 输出转义 |
| 12 | 历史缺陷可能复发点 | 0 | ⚠ 未覆盖 | 无历史缺陷数据，按常见复发模式检查中 |

## 审核结论
- [ ] 12 个维度全部为「✅ 已覆盖」或「➖ 不适用（有理由）」
- 「⚠ 未覆盖」处理决定：补充 TP-xx / 确认不适用 + 理由：…
```

填写规则：

- 测试点数 = 该维度下 TP 的数量（一个 TP 只计一个主维度）。
- 状态只有三种：✅ 已覆盖（≥1 个测试点）/ ⚠ 未覆盖（测试点数为 0，待处理）/ ➖ 不适用（有具体理由）。
- 「不适用」的理由必须可核查（如「纯样式调整，无数据写入」「本需求无状态流转」）；「不涉及」「应该没问题」无效。
- 用例集 JSON 生成脑图时，脚本自动产出「维度覆盖」视图（12 维度分支 + 未覆盖警示），与本表数据同源。

## 4. 测试用例模板（Markdown）

```markdown
# 测试用例：<需求/功能名>

## 模块：登录

| 用例编号 | 用例标题 | 优先级 | 覆盖维度 | 前置条件 | 操作步骤 | 预期结果 | 关联测试点 |
|---|---|---|---|---|---|---|---|
| TC-LOGIN-001 | 正确手机号验证码登录成功 | P0 | 正常功能流程 | 已注册手机号 13800138000 | 1. 打开登录页<br>2. 输入 13800138000<br>3. 点击获取验证码<br>4. 输入收到的验证码<br>5. 点击登录 | 登录成功，跳转首页，顶部显示用户昵称 | TP-01 |
| TC-LOGIN-002 | 手机号不足 11 位时点击登录 | P1 | 边界值场景 | 未登录 | 1. 打开登录页<br>2. 输入 1380013800<br>3. 点击登录 | 提示「请输入正确的手机号」，停留登录页 | TP-02 |
```

## 5. 测试用例 JSON Schema（xlsx 转换用）

将用例按下述结构生成为 JSON 文件，再调用 `scripts/testcase_to_xlsx.py` 转换（该结构同时是 `testcase_to_xmind.py` 的用例集输入）。**字段名必须与下述完全一致**；`steps` 为字符串数组（每步一项，不含序号，脚本自动编号）。

脚本用法：

```bash
python scripts/testcase_to_xlsx.py cases.json -o 测试用例.xlsx   # xlsx 输出
python scripts/testcase_to_xlsx.py cases.json --format csv      # csv 输出（无第三方依赖）
```

```json
{
  "meta": {
    "project": "项目名",
    "requirement": "需求名/编号",
    "version": "V1.0",
    "author": "测试人员",
    "date": "2026-08-26"
  },
  "cases": [
    {
      "id": "TC-LOGIN-001",
      "module": "登录",
      "title": "正确手机号验证码登录成功",
      "priority": "P0",
      "type": "功能测试",
      "dimension": "正常功能流程",
      "precondition": "已注册手机号 13800138000",
      "steps": [
        "打开登录页",
        "输入 13800138000",
        "点击获取验证码",
        "输入收到的验证码",
        "点击登录"
      ],
      "expected": "登录成功，跳转首页，顶部显示用户昵称",
      "test_points": ["TP-01"],
      "requirements": ["R-01"],
      "remark": ""
    }
  ]
}
```

字段说明：

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| meta | 否 | object | 项目级信息，写入 xlsx 概要 sheet |
| cases | 是 | array | 用例数组 |
| id | 是 | string | 用例编号，唯一 |
| module | 是 | string | 所属模块，同模块的用例在 xlsx 中归组 |
| title | 是 | string | 用例标题 |
| priority | 是 | string | P0/P1/P2/P3 |
| type | 否 | string | 功能/接口/边界/异常/兼容…，默认「功能测试」 |
| dimension | 否 | string | **覆盖维度**，12 维度之一：正常功能流程/异常流程/边界值场景/权限控制/数据校验/状态流转/前后端交互/数据库一致性/兼容性/性能风险/安全风险/历史缺陷可能复发点；跨维度用顿号分隔（如「数据校验、边界值场景」）。用于 xlsx 覆盖维度列、xmind 用例标签与维度覆盖视图 |
| scene | 否 | string | 兼容字段：`dimension` 缺省时按 正常场景→正常功能流程、边界场景→边界值场景、异常场景→异常流程 自动映射 |
| precondition | 否 | string | 前置条件 |
| steps | 是 | array[string] | 操作步骤，每步一项 |
| expected | 是 | string | 预期结果 |
| test_points | 否 | array[string] | 关联测试点 |
| requirements | 否 | array[string] | 关联需求 |
| remark | 否 | string | 备注 |

> **接口用例**（工作流 B）在本 schema 基础上增加 `method` / `path` / `headers` / `body` / `expected_code` / `response_checks` 字段，且 `type` 取「正向/反向/边界/权限/幂等/并发」——完整说明与示例见第 10 节。两种用例集 JSON 同构，脚本自动检测接口字段并输出对应列。

## 6. 需求变更影响分析模板

```markdown
# 需求变更影响分析：<变更名/编号>

## 1. 变更摘要
- 变更编号/提出时间：
- 变更内容：新增/修改/删除了什么（逐条列出）
- 变更原因：

## 2. 变更前后对比
| 项目 | 变更前 | 变更后 |
|---|---|---|
| 验证码重发间隔 | 60 秒 | 120 秒 |

## 3. 影响面分析
### 直接影响
| 模块/功能 | 影响说明 | 关联需求 |
|---|---|---|
| 登录页 | 发送按钮倒计时文案与逻辑 | R-01 |

### 间接影响
| 上下游 | 影响说明 |
|---|---|
| 短信网关 | 发送频率限制变化，需确认网关侧配额 |

## 4. 测试资产影响
- 需新增用例：TC-LOGIN-0xx（列出编号与标题）
- 需更新用例：TC-LOGIN-003（更新点：…）
- 可废弃用例：TC-LOGIN-005（原因：对应旧逻辑已删除）
- 不受影响用例：其余登录用例

## 5. 回归范围建议
- 建议：（最小回归集 / 完整回归）
- 理由：
- 最小回归集清单：TC-xxx、TC-xxx、…

## 6. 风险与待确认
- 历史数据兼容：…
- 基线说明（变更前版本来源）：…
```

## 7. 脑图树 JSON 规范（xmind 导出用）

第 5 步人工审核确认后，将最终内容组织为下述树形 JSON，调用 `scripts/testcase_to_xmind.py` 生成 .xmind 脑图。**层级固定：根（需求名）→ 模块 → 测试点 → 用例**。

```json
{
  "root": {
    "title": "登录功能 测试用例",
    "note": "需求来源: PRD v2.1 | 生成: 2026-08-26",
    "children": [
      {
        "title": "登录模块",
        "children": [
          {
            "title": "TP-01 验证码登录主流程",
            "children": [
              {
                "title": "TC-LOGIN-001 正确手机号验证码登录成功",
                "priority": "P0",
                "labels": ["正常功能流程"],
                "note": "前置条件: 已注册手机号 13800138000\n操作步骤:\n1. 打开登录页\n2. 输入 13800138000\n3. 点击获取验证码\n4. 输入收到的验证码\n5. 点击登录\n预期结果: 登录成功，跳转首页，顶部显示用户昵称"
              },
              {
                "title": "TC-LOGIN-003 验证码错误时登录失败",
                "priority": "P1",
                "labels": ["异常流程"],
                "note": "前置条件: 已注册手机号 13800138000\n操作步骤:\n1. 打开登录页\n2. 输入手机号并获取验证码\n3. 输入错误验证码\n4. 点击登录\n预期结果: 提示「验证码错误」，停留登录页"
              }
            ]
          }
        ]
      },
      {
        "title": "短信验证码模块",
        "children": [
          {
            "title": "TP-05 验证码重发限制",
            "children": [
              {
                "title": "TC-SMS-001 60 秒内重复点击发送按钮",
                "priority": "P1",
                "labels": ["异常流程"],
                "note": "前置条件: ...\n操作步骤:\n...\n预期结果: ..."
              }
            ]
          }
        ]
      }
    ]
  }
}
```

节点字段：

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| title | 是 | string | 节点标题；测试点带 TP 编号、用例带 TC 编号，保证脑图与文档互查 |
| priority | 用例层必填 | string | P0/P1/P2/P3；脚本自动映射 XMind 优先级图标（priority-1..4）并加优先级标签 |
| labels | 否 | array[string] | 用例层填**覆盖维度**（12 维度之一或多个），可附加其他标签 |
| note | 否 | string | 用例节点固定三段：前置条件 / 操作步骤（编号）/ 预期结果。默认（`--detail-style topics`）脚本将其自动展开为**子主题**展示（操作步骤每条一个子节点）；加 `--detail-style note` 则折叠进脑图便签（紧凑版） |
| children | 否 | array | 子节点数组 |

组织约定：

- 根节点 note 记录需求来源与生成日期，保证可追溯。
- 测试点节点下不同维度的用例统一挂载、用 labels 区分——筛选标签即可按维度过滤。
- 脚本用法：

```bash
python scripts/testcase_to_xmind.py tree.json -o 测试用例.xmind   # 生成 xmind（详情默认子主题展示）
python scripts/testcase_to_xmind.py tree.json --detail-style note -o 测试用例.xmind  # 紧凑版：详情折叠进便签
python scripts/testcase_to_xmind.py tree.json --format md -o 大纲.md  # Markdown 大纲备选
```

- 兼容输入：直接传入第 5 节的用例集 JSON（含 `cases` 数组）也可，脚本自动生成**双 sheet**：「按模块」视图（需求 → 模块 → 用例）+「维度覆盖」视图（12 个维度分支、每维度的用例数，空维度挂「⚠ 未覆盖」警示节点，供审核维度缺口）。正式交付优先用树形 JSON（多一层测试点结构，单 sheet）。

## 8. 需求追踪矩阵模板

```markdown
# 需求追踪矩阵：<需求名>

| 需求编号 | 需求描述 | 业务规则 | 测试点 | 测试用例 | 用例结果 |
|---|---|---|---|---|---|
| R-01 | 手机号验证码登录 | BR-01, BR-02 | TP-01 | TC-LOGIN-001 | 未执行 |
| R-01 | 手机号验证码登录 | BR-03 | TP-02 | TC-LOGIN-002 | 未执行 |

覆盖率统计：
- 需求覆盖：n/n（无对应测试点的需求单独列出并说明原因）
- 业务规则覆盖：n/n
- 用例状态汇总：未执行 x / 通过 x / 失败 x / 阻塞 x
```

## 9. 接口契约模型模板（工作流 B 第 1 步产出）

接口文档解析完成后输出本模型，作为第 2-5 步生成与审核接口用例的依据。**接口字段解析表（§3）是本模板核心**。

```markdown
# 接口契约模型：<项目/模块名>

## 1. 接口清单
| 编号 | 接口名称 | 方法 | 路径 | 模块 | 认证要求 | 优先级 | 幂等 |
|---|---|---|---|---|---|---|---|
| API-01 | 创建订单 | POST | /api/v1/orders | 订单 | Bearer | P0 | 是（幂等键） |

## 2. 认证与授权
- 认证方式：Bearer token（登录接口返回）／签名／无认证
- 角色权限：管理员可调 API-03；普通用户仅 API-01/02/04
- 无鉴权接口：API-05（健康检查）

## 3. 接口字段解析表（逐接口）
### API-01 创建订单 POST /api/v1/orders
| 字段 | 位置 | 类型 | 必填 | 校验规则 | 边界值 | 示例 |
|---|---|---|---|---|---|---|
| userId | body | int | 是 | >0 | 0/1/2^31 | 1001 |
| items[].skuId | body | string | 是 | 存在且上架 | - | SKU001 |
| items[].qty | body | int | 是 | 1~99 | 0/1/99/100 | 2 |
| couponId | body | long | 否 | 属于当前用户 | - | 88001 |
| X-Request-Id | header | string | 是 | UUID 格式 | - | 550e8400… |

### 请求头（公共）
- Content-Type: application/json；Authorization: Bearer <token>

### 响应结构
- 成功（200）：`{ "code": 0, "msg": "success", "data": { "orderNo": "SO20260827xxxx", "amount": 199.00, "status": "CREATED" } }`
- 失败：业务码表（40001 参数错误 / 40010 库存不足 / 40011 优惠券不可用 / 40100 未登录 / 40300 无权限 / 40400 资源不存在 / 42900 请求过于频繁）
- 错误信息格式：`{ "code": <业务码>, "msg": "<可读文案>", "data": null }`

## 4. 业务规则（BR-xx）
| 编号 | 规则 | 关联接口 |
|---|---|---|
| BR-01 | 订单总金额 = Σ(sku 单价×qty) - 优惠，必须 >0 | API-01 |
| BR-02 | 库存不足时下单失败，业务码 40010 | API-01 |
| BR-03 | 已支付订单不可取消 | API-06 |

## 5. 频率限制
- API-01 限流 10 次/分钟/用户（42900）
```

## 10. 接口测试用例模板（工作流 B 第 6 步产出）

### Markdown 模板

```markdown
# 接口测试用例：<模块名>（接口文档 <版本>）

## 接口：创建订单 POST /api/v1/orders

| 用例编号 | 场景 | 用例标题 | 优先级 | 覆盖维度 | 请求(方法+路径) | 请求头/参数 | 预期状态码 | 预期结果 | 关联测试点 |
|---|---|---|---|---|---|---|---|---|---|
| TC-ORDER-001 | 正向 | 合法参数创建订单成功 | P0 | 正常功能流程 | POST /api/v1/orders | Bearer token + userId=1001 + items=[{skuId:SKU001,qty:2}] | 200 | code=0；data.orderNo 非空、status=CREATED、amount=198.00 | TP-01 |
| TC-ORDER-002 | 反向 | 库存不足时下单失败 | P0 | 异常流程 | POST /api/v1/orders | items=[{skuId:SKU001,qty:9999}] | 200 | code=40010；msg 含「库存不足」；不产生订单数据 | TP-02 |
| TC-ORDER-003 | 幂等 | 相同幂等键重复提交只创建一单 | P1 | 数据校验 | POST /api/v1/orders | 相同 X-Request-Id 提交 2 次 | 200 | 两次 code=0 但 orderNo 相同，DB 仅 1 条 | TP-03 |
```

### 9 列表格模板（「资深接口测试工程师 · 15 场景」提示词的快捷交付格式）

用户按 15 场景提示词模板要求「用表格输出」时，交付下列 9 列表格（列名与用户要求一一对应，不改列名）：

| 用例编号 | 测试场景 | 请求方法 | 请求路径 | 请求参数 | 前置条件 | 预期状态码 | 预期返回 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| TC-ORDER-001 | 正常请求 | POST | /api/v1/orders | `{"userId":1001,"items":[{"skuId":"SKU001","qty":2}]}` + Bearer token | 已登录；SKU001 库存≥2 | 200 | code=0；orderNo 非空；status=CREATED；amount=198.00 | P0 |
| TC-ORDER-002 | 必填参数缺失 | POST | /api/v1/orders | body 缺 `items` 字段 | 已登录 | 400 | code=40001；msg 含「items 必填」 | P0 |
| TC-ORDER-003 | 参数为空 | POST | /api/v1/orders | `items` 传空数组 `[]` | 已登录 | 400 | code=40002；msg 含「至少一件商品」 | P1 |
| TC-ORDER-004 | 参数类型错误 | POST | /api/v1/orders | `items` 传字符串 `"abc"` | 已登录 | 400 | code=40003；msg 含「items 格式错误」 | P1 |
| TC-ORDER-005 | 参数长度边界 | POST | /api/v1/orders | `remark` 传 200 字（上限 200）与 201 字 | 已登录 | 200/400 | 200 时成功；201 字返回 code=40004「备注超长」 | P2 |
| TC-ORDER-006 | 枚举值非法 | POST | /api/v1/orders | `payType=CREDIT_CARD_X`（非法枚举） | 已登录 | 400 | code=40005；msg 含「payType 非法」 | P1 |
| TC-ORDER-007 | token 缺失 | POST | /api/v1/orders | 不带 Authorization 头 | 无 | 401 | code=40101；msg 含「未登录」 | P0 |
| TC-ORDER-008 | token 过期 | POST | /api/v1/orders | 携带已过期 token | 预先生成过期 token | 401 | code=40102；msg 含「token 已过期」 | P0 |
| TC-ORDER-009 | token 无权限 | DELETE | /api/v1/orders/{orderId} | 普通用户 token 删他人订单 | 普通用户账号；存在他人订单 | 403 | code=40301；msg 含「无权限」 | P1 |
| TC-ORDER-010 | 数据不存在 | GET | /api/v1/orders/999999 | orderId=999999 | 无 | 404 | code=40401；msg 含「订单不存在」 | P1 |
| TC-ORDER-011 | 重复提交 | POST | /api/v1/orders | 相同 body 连发 2 次（无幂等键） | 已登录 | 200 | 两次 orderNo 不同或第二次 code=40902「重复下单」；DB 仅 1 单 | P0 |
| TC-ORDER-012 | 幂等性 | POST | /api/v1/orders | 相同 `X-Request-Id` 连发 2 次 | 已登录 | 200 | 两次 orderNo 相同；DB 仅 1 条记录 | P0 |
| TC-ORDER-013 | 并发请求 | POST | /api/v1/orders | 10 并发同 SKU 下单（库存 5） | 库存 5；测试工具并发 | 200/业务码 | 成功数≤5；不超卖；库存扣至 0 | P0 |
| TC-ORDER-014 | 业务状态不允许 | POST | /api/v1/orders/{orderId}/cancel | 已支付订单取消 | 存在已支付订单 | 400 | code=40910；msg 含「已支付订单不可取消」 | P1 |
| TC-ORDER-015 | 返回字段校验 | POST | /api/v1/orders | 合法参数 | 已登录 | 200 | orderNo 非空字符串、amount 数值且=Σ(单价×数量)、status∈{CREATED} | P1 |

生成约定：

- **9 列与 JSON 字段映射**：测试场景 → `type`；请求参数 → `headers`+`body`（含 query/path 参数）；前置条件 → `precondition`；预期状态码 → `expected_code`；预期返回 → `expected`（含业务码与关键断言）；优先级 → `priority`。表格仅展示，**同一份用例仍须组织为接口用例集 JSON 沉淀**。
- 一张接口一张表（或按模块分表），表格前注明接口（方法+路径）；多接口时按接口分组编号。
- 接口不适用某场景（如纯查询接口无「重复提交」）→ 保留行但预期返回注明「N/A：<理由>」，并在维度覆盖检查表中声明。
- 表格交付后按第 6 步同时导出 xlsx/xmind 供测试人员审核使用。

### 接口用例 JSON Schema（接口用例集 = 第 5 节用例 schema + 下列接口字段）

在普通用例字段（id/module/title/priority/dimension/precondition/steps/expected/test_points/requirements/remark）基础上，接口用例增加可选字段：

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| type | 是 | string | 用例场景：**正向/反向/边界/权限/幂等/并发**（普通用例可为 功能/异常/兼容…） |
| method | 接口用例必填 | string | HTTP 方法：GET/POST/PUT/PATCH/DELETE |
| path | 接口用例必填 | string | 请求路径（含路径参数模板，如 `/api/v1/orders/{orderId}`） |
| headers | 否 | object/string | 请求头，如 `{"Authorization": "Bearer {token}", "Content-Type": "application/json"}` |
| body | 否 | object/string | 请求体（GET/查询类可为空） |
| expected_code | 接口用例必填 | int/string | 预期 HTTP 状态码，如 200、400 |
| response_checks | 否 | string | 响应校验要点（业务码 + 关键字段断言），如「code=0；data.status=CREATED」 |
| test_point_id | 否 | string | 关联测试点（与 test_points 二选一即可，统一用 test_points） |

示例：

```json
{
  "meta": { "project": "商城", "requirement": "订单接口", "version": "V1.0", "author": "测试人员", "date": "2026-08-27" },
  "cases": [
    {
      "id": "TC-ORDER-001",
      "module": "订单",
      "title": "合法参数创建订单成功",
      "priority": "P0",
      "type": "正向",
      "dimension": "正常功能流程",
      "method": "POST",
      "path": "/api/v1/orders",
      "headers": { "Authorization": "Bearer {token}", "Content-Type": "application/json" },
      "body": { "userId": 1001, "items": [{ "skuId": "SKU001", "qty": 2 }], "couponId": null },
      "expected_code": 200,
      "response_checks": "code=0；data.orderNo 非空；data.status=CREATED；data.amount=198.00",
      "precondition": "已登录获得有效 token；SKU001 库存≥2；单价 99 元",
      "steps": ["构造上述请求", "携带 Bearer token 发送 POST /api/v1/orders", "校验响应码与响应体"],
      "expected": "返回 200，code=0，orderNo 生成，status=CREATED，amount=198.00",
      "test_points": ["TP-01"],
      "requirements": ["R-01"],
      "remark": "对应 BR-01 正向"
    }
  ]
}
```

字段约定：

- 接口用例的 `steps` 描述**请求构造与断言动作**（脚本自动编号），`body`/`headers` 以结构化 JSON 呈现，方便直接交接接口自动化执行（如生成 pytest+requests 脚本）。
- `expected` 与 `response_checks` 都写时，`expected` 为自然语言预期，`response_checks` 为可断言的要点列表；脚本将两者都输出到交付物。
- 接口用例集 JSON 与普通用例集 JSON 同构（根为 `meta` + `cases`），脚本自动检测用例是否含 `method`/`path` 字段：含则输出接口列，不含则维持普通用例列。

## 输出方式约定

- 交付 markdown 文档写入当前工作目录；xlsx 交付时 JSON 中间文件放临时目录、xlsx 放工作目录。
- 用例交付时《维度覆盖检查表》一并交付（合入同一文档或脑图「维度覆盖」视图即视为满足）。
- 多份产出（如分析+用例+矩阵）合并为一个文档交付，或按用户要求分开。
- 文档头部标注需求来源与版本（哪些材料、什么版本/日期），保证可追溯。
