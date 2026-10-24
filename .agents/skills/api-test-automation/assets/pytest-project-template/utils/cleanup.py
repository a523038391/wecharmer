"""后置清理注册器：统一管理测试创建的资源，后进先出执行删除。"""
import logging

logger = logging.getLogger("api-test.cleanup")


class CleanupRegistry:
    """注册清理任务，用例结束时统一执行。

    用法：
        cleanup = CleanupRegistry(http_client)
        data = assert_ok(http_client.post("/api/users", json={...}))
        cleanup.register("delete", "/api/users/{id}", id=data["id"])
        ...
        cleanup.run()
    """

    def __init__(self, client):
        self.client = client
        self._tasks = []  # (method, path, path_kwargs)

    def register(self, method: str, path: str, **path_kwargs):
        """注册一个清理请求。

        Args:
            method: HTTP 方法，如 "delete"
            path: 路径模板，支持 {} 占位，如 "/api/users/{id}"
            path_kwargs: 填充占位符的参数，如 id=data["id"]
        """
        self._tasks.append((method, path, path_kwargs))

    def run(self):
        """按注册顺序逆序执行全部清理任务。

        - 删除类清理放行 404（资源已被外部删除视为清理成功）
        - 收集错误并记日志，不抛异常，避免掩盖用例结果
        """
        errors = []
        for method, path, path_kwargs in reversed(self._tasks):
            try:
                resp = getattr(self.client, method.lower())(path.format(**path_kwargs))
                if resp.status_code not in (200, 201, 204, 404):
                    errors.append((method, path.format(**path_kwargs), resp.status_code, resp.text))
            except Exception as exc:  # noqa: BLE001 - 清理失败不应中断
                errors.append((method, path.format(**path_kwargs), "ERROR", str(exc)))
        if errors:
            logger.warning("cleanup completed with %d error(s): %s", len(errors), errors)
        return errors
