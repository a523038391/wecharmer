# 项目代码风格约定

用户要求：先熟悉现有代码，以后按用户已有风格修改代码。以下约定来自当前代码抽样，后续以实际修改文件及相邻模块的写法为准。

## 结构与职责

- 这是 Python ERP 接口及 UI 自动化项目。`interface/` 按业务模块封装接口，`lib/` 编排业务链路，`testcase/` 组织测试，`conf/` 提供配置，`util/` 提供工具。
- 新接口优先放入对应业务模块的 `*_api.py`；业务步骤在 `lib/` 对应模块串联，沿用已有类与方法。
- 保留已有版本划分，例如 `v2`、`_v2`；根据调用关系确定目标版本，不擅自合并或替换版本。
- 用户要求旧链路升级时新建独立的 `_v2.py` 模块编写，不在原业务模块直接修改。新版待排柜入口为 `lib/container/waitcontainerbill_v2.py` 中的 `WaitContainerBillv2`；保留原 `waitcontainerbill.py` 的内容和调用。

## 接口与业务链路

- 用户提供的 Swagger 入口：`http://erp-test.wecharmer.cn:8090/index.html?urls.primaryName=Wecharmer.FirstLeg.Application.Contracts`。页面配置中的头程定义地址为 `/swagger/Wecharmer.FirstLeg.Application.Contracts/swagger.json`，同一入口还配置了采购、仓储、商品、供应商等模块。2026-10-22 已读取入口配置，但头程 JSON 请求超时，尚未验证其具体接口模型；后续按任务重新读取，不将入口可访问视为接口定义已验证。
- 接口类沿用所在模块的命名，例如 `Stockupbill_Api`、`PurchaseOrder_Api`；业务类沿用 `StockupBill`、`PurchaseOrderv2` 等现有形式。
- 方法通常使用下划线命名，链路方法常以 `_link` 结尾。保留已有公共方法签名、参数顺序及返回结构。
- 接口字段及对应变量可沿用 `shopId`、`warehouseId`、`stockUpBillId` 等驼峰名，无须统一改成下划线。
- 请求参数使用直接展开的字典和列表；按业务步骤构造 payload、调用接口、提取结果、传给后续步骤。
- 接口层常用 `requests`、配置中的 Host 和 f-string URL；现有 `cookies` 参数实际传给 `headers`，沿用其契约。
- 接口层通常返回原始 Response；业务层常以 `json.loads(resp.text)["result"]` 提取结果，使用 `_payload`、`_resp`、`_result`、`_dict` 等后缀区分数据。
- 链路结果常用字典返回单据 ID、单号等后续业务需要的数据。优先复用既有链路，不额外引入通用框架或抽象层。
- 用户明确要求直接调用已有链路方法，例如 `Inspectionv2().inspection_purchaseorder_report(...)`；新建 v2 模块不代表复制采购、入库、验货的已有实现。遇到依赖问题应定位并说明，不通过复制整段业务代码绕过。
- 链路入参尽量与已有采购/验货链路一致；可从接口结果取得的字段（例如仓库名称）自动提取。用户要求排柜固定业务值直接写在请求 payload 中，不增加方法入参或单独的配置字典。
- 新版待排柜按采购单号查询供应商良品库存，使用库存结果中的可用数量、箱规及采购明细组装排柜入参；用 `supplierInventoryId` 关联申请池取得 `waitApplyContainerId`，两种 ID 不得混用。2026-10-22 已成功读取头程及供应商 Swagger JSON，并核对相关模型。
- 用户要求新版排柜查询后直接往下执行，不增加客户端业务校验或等待重查：不检查可排柜标记、不比较库存与申请池数量、不重复核验店铺/仓库等返回字段。保留分页读取、必要的 ID 关联和接口失败处理，业务校验交给服务端。
- 排柜 `isNeedFnSku=False` 时，`packageSticker` 使用库存 `skuCode`，`sellerSku` 为空字符串；不使用 `FNSKU--每箱装量` 作为箱贴。
- 用户最新要求入仓类型 `inStorageType` 放在排柜主单 payload 中，不放在 `details` 明细中。
- 新版待排柜另有 `create_waitContainer_supplier_fba_v2_link` 入口，复用同一链路实现。FBA 目的仓类型为 3、`isNeedFnSku=True`，调用示例店铺为 `shopId=162`、`shopAccount="LIPENG_US"`；海外仓目的仓类型为 2、`isNeedFnSku=False`。Wayfair 入仓类型及名称仅用于海外仓场景。
- FBA 平台仓场景的主单 `inStorageType`、`inStorageTypeName` 和明细 `packageSticker` 均传 `None`（JSON null）。

## 表达方式

- 业务说明、步骤注释及接口输出优先用中文；方法文档沿用三引号及需要的 `:param`、`:return:` 格式，内容应对应实际签名。
- 按“创建、查询、明细组装、审核/分配、返回结果”等实际顺序展开代码，让业务过程直接可读。
- 沿用相邻代码的响应打印习惯；新增输出避免包含密码、令牌等凭据。
- 保留原有文件头和排版；只修改任务相关区域，不进行全文件格式化、批量重命名或无关清理。新增代码保持清晰的缩进及空格，无须复制历史排版瑕疵。
- 这些是风格约定，不要求保留逻辑错误；修复时保持外部契约，必要的行为变化应说明。

## 测试与 UI

- `testcase/` 主要使用 pytest 测试类、setup 初始化、中文 Allure 标题，以及“执行业务链路后查询结果并 assert”的方式；跟随具体文件。
- `pytest.ini` 当前将 `python_functions` 设置为 `*_link`，默认运行还包含重跑与 Allure 结果清理参数。验证时注意用例是否被收集及执行的副作用。
- 现有集成链路可能登录真实环境并创建或修改业务单据；不要为了解代码风格而执行这些链路。
- `lib/*_ui.py` 中有 Selenium 写法；`ui_automation/` 则已有 Playwright Page Object、类型注解、dataclass、显式等待及离线 unittest。修改时跟随所在模块，不将某一模块风格推广到全项目。
- 尊重工作区中用户已有的未提交修改，不覆盖或回退。
