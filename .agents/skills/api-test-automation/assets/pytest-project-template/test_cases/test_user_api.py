"""用户接口测试示例。

演示：正常场景断言、异常场景断言、创建数据的后置清理、边界值用例。
对应接口文档（示例）：
    POST /api/users         创建用户
    GET  /api/users/{id}    查询用户详情
    DELETE /api/users/{id}  删除用户
响应结构：{"code": 0, "data": {...}, "message": "..."}
"""
import time

import pytest

from utils.assertions import assert_fail, assert_ok
from utils.cleanup import CleanupRegistry


def _unique_email(prefix: str = "auto") -> str:
    """生成唯一邮箱，避免用例重复执行时数据冲突。"""
    return f"{prefix}_{int(time.time() * 1000)}@example.com"


class TestCreateUser:
    """创建用户接口 POST /api/users"""

    @pytest.fixture
    def created_user(self, http_client):
        """前置：创建用户；后置：删除用户（无论用例成败均清理）。"""
        user_id = None
        try:
            resp = http_client.post("/api/users", json={
                "name": "auto_test_user",
                "email": _unique_email(),
            })
            data = assert_ok(resp)
            user_id = data["id"]
            yield user_id
        finally:
            if user_id:
                del_resp = http_client.delete(f"/api/users/{user_id}")
                assert del_resp.status_code in (200, 204), f"清理失败: {del_resp.text}"

    def test_create_user_success(self, http_client, created_user):
        """用例 TC-001 正常场景：创建用户成功，返回用户 id 且状态可用"""
        # 创建已在 fixture 中完成，此处验证返回结果
        user_id = created_user
        assert user_id > 0

        # 验证创建的用户可通过查询接口读到
        resp = http_client.get(f"/api/users/{user_id}")
        data = assert_ok(resp)
        assert data["id"] == user_id
        assert data["name"] == "auto_test_user"
        assert data["email"].startswith("auto_")

    def test_create_user_missing_name(self, http_client):
        """用例 TC-010 异常场景：缺少必填字段 name，返回参数错误"""
        resp = http_client.post("/api/users", json={"email": _unique_email()})
        assert_fail(resp, status_code=400, business_code=10001, message_keyword="name")

    def test_create_user_invalid_email(self, http_client):
        """用例 TC-011 异常场景：邮箱格式非法，返回参数错误"""
        resp = http_client.post("/api/users", json={"name": "t", "email": "not-an-email"})
        assert_fail(resp, status_code=400, business_code=10002, message_keyword="email")

    def test_create_user_empty_name(self, http_client):
        """用例 TC-012 边界值场景：name 为空字符串，返回参数错误"""
        resp = http_client.post("/api/users", json={"name": "", "email": _unique_email()})
        assert_fail(resp, status_code=400, business_code=10001, message_keyword="name")


class TestGetUser:
    """查询用户接口 GET /api/users/{id}"""

    def test_get_user_not_found(self, http_client):
        """用例 TC-020 异常场景：查询不存在的用户，返回 404 与错误码"""
        resp = http_client.get("/api/users/999999999")
        assert_fail(resp, status_code=404, business_code=40400, message_keyword="不存在")


class TestDeleteUser:
    """删除用户接口 DELETE /api/users/{id}（使用 CleanupRegistry 演示多资源清理）"""

    def test_delete_user_success(self, http_client):
        """用例 TC-030 正常场景：删除用户成功，再次查询返回 404"""
        cleanup = CleanupRegistry(http_client)

        # 先创建再删除
        resp = http_client.post("/api/users", json={
            "name": "to_delete",
            "email": _unique_email("del"),
        })
        data = assert_ok(resp)
        user_id = data["id"]
        # 注册兜底清理：用例中途失败也会删除该用户
        cleanup.register("delete", "/api/users/{id}", id=user_id)

        del_resp = http_client.delete(f"/api/users/{user_id}")
        assert del_resp.status_code in (200, 204), f"删除失败: {del_resp.text}"

        # 删除后查询应 404
        get_resp = http_client.get(f"/api/users/{user_id}")
        assert get_resp.status_code == 404, f"删除后仍可查询到: {get_resp.text}"

        cleanup.run()
