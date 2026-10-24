"""通用断言工具：统一正常 / 异常场景校验，失败信息包含响应体便于定位。"""


def assert_ok(resp, business_code: int = 0):
    """正常场景断言三要素：HTTP 状态码、业务 code、返回 data。

    Args:
        resp: requests.Response 对象
        business_code: 期望的业务码，默认 0

    Returns:
        resp.json()["data"]，供用例继续断言业务数据
    """
    assert resp.status_code in (200, 201), (
        f"期望 HTTP 200/201，实际 {resp.status_code}，body={resp.text}"
    )
    body = resp.json()
    assert body.get("code") == business_code, (
        f"期望业务码 {business_code}，实际 {body.get('code')}，body={body}"
    )
    assert "data" in body, f"响应缺少 data 字段，body={body}"
    return body["data"]


def assert_fail(resp, status_code: int = None, business_code: int = None,
                message_keyword: str = None):
    """异常场景断言：HTTP 状态码 + 业务错误码 + 错误信息关键词（可省略部分项）。

    至少断言业务错误码或错误信息中的一项。

    Returns:
        resp.json()，供用例继续断言细节
    """
    if status_code is not None:
        assert resp.status_code == status_code, (
            f"期望 HTTP {status_code}，实际 {resp.status_code}，body={resp.text}"
        )
    try:
        body = resp.json()
    except ValueError:
        body = {"raw": resp.text}
    if business_code is not None:
        assert body.get("code") == business_code, (
            f"期望业务码 {business_code}，实际 {body.get('code')}，body={body}"
        )
    if message_keyword is not None:
        message = body.get("message") or body.get("msg") or ""
        assert message_keyword in message, (
            f"错误信息缺少关键词 {message_keyword!r}，实际 {message!r}，body={body}"
        )
    return body
