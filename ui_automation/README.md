# UI 自动化模块

该模块基于 Python Playwright 和 Page Object 模式，将浏览器生命周期、通用页面操作和业务页面分离。

## 环境变量

- `UI_BASE_URL`：ERP 页面地址（必填）
- `UI_USERNAME`、`UI_PASSWORD`：登录凭据
- `UI_BROWSER`：`chromium`、`chrome`、`edge`、`firefox` 或 `webkit`
- `UI_HEADLESS`：是否使用无头模式，默认 `true`
- `UI_TIMEOUT`：元素等待秒数，默认 `10`
- `UI_SLOW_MO`：每步延迟毫秒数，默认 `0`
- `UI_TRACE`：失败时是否保存 Playwright Trace，默认 `false`
- `UI_ARTIFACTS_DIR`：失败截图和 Trace 目录
- `UI_BILL_NUMBER`：头程柜列表冒烟用例使用的提单号

## 使用方式

先安装 Python 包和 Chromium：

    python -m pip install playwright
    python -m playwright install chromium

配置以上环境变量后，通过
`UISettings.from_env()` 读取配置，使用 `BrowserSession` 管理浏览器，在会话内依次调用
`LoginPage.login()` 和 `ContainerListPage.search()`。会话结束时浏览器会自动关闭。

执行 Playwright 冒烟用例：

    pytest testcase/test_ui_playwright.py -m ui

离线单元测试：

    python -m unittest discover -s ui_automation/tests -v