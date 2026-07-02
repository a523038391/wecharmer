# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/4/14 下午5:24
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : asyncio_aiohttp.py
# @Project : wecharmer


import asyncio
import aiohttp
import time
import json
from dataclasses import dataclass

# 登录配置（与 lib/login.py 保持一致）
LOGIN_URL = "http://192.168.5.197:8090/api/account/login"
LOGIN_PAYLOAD = {
    "tenantName": "Wecharmer.Hero",
    "account": "lipeng",
    "password": "Aa123456!"
}


@dataclass
class Stats:
    total: int = 0
    success: int = 0
    failed: int = 0
    total_time: float = 0.0
    errors: list = None

    def __post_init__(self):
        self.errors = []


async def login(session) -> dict:
    """异步登录微诚ERP，返回 headers 字典"""
    async with session.post(LOGIN_URL, json=LOGIN_PAYLOAD) as resp:
        data = await resp.json()
        if data.get("code") == "Success":
            token = data["result"]
            headers = {"Authorization": token}
            print(f"登录成功，token: {token[:20]}...")
            return headers
        else:
            raise Exception(f"登录失败: {data}")


async def send_request(session, url, method="POST", headers=None, **kwargs):
    """发送单个请求并记录耗时"""
    start = time.perf_counter()
    try:
        async with session.request(method, url, headers=headers, **kwargs) as resp:
            await resp.read()
            elapsed = time.perf_counter() - start
            return resp.status, elapsed, None
    except Exception as e:
        elapsed = time.perf_counter() - start
        return None, elapsed, str(e)


async def worker(queue, stats, session, headers):
    """工作协程：从队列取任务并执行"""
    while True:
        task_info = await queue.get()
        if task_info is None:  # 毒丸，结束信号
            break
        url, method, kwargs = task_info
        status, elapsed, error = await send_request(session, url, method, headers=headers, **kwargs)
        stats.total += 1
        stats.total_time += elapsed
        if error:
            stats.failed += 1
            if len(stats.errors) < 20:
                stats.errors.append(error)
        else:
            stats.success += 1
        queue.task_done()


async def stress_test(
    url: str,
    concurrency: int = 100,
    total_requests: int = 10000,
    method: str = "POST",
    auto_login: bool = True,
    **kwargs
):
    """主压测函数，先登录再压测"""
    headers = kwargs.pop("headers", None)

    # 创建连接池
    connector = aiohttp.TCPConnector(limit=concurrency, limit_per_host=concurrency)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # 自动登录
        if auto_login:
            headers = await login(session)

        if not headers:
            print("警告：未获取到认证信息，请求可能被拦截")

        stats = Stats()
        queue = asyncio.Queue()

        # 预填充任务队列
        for _ in range(total_requests):
            await queue.put((url, method, kwargs))

        # 启动 worker 协程
        workers = [asyncio.create_task(worker(queue, stats, session, headers))
                   for _ in range(concurrency)]

        # 等待所有任务完成
        await queue.join()

        # 发送毒丸停止 worker
        for _ in range(concurrency):
            await queue.put(None)
        await asyncio.gather(*workers)

    return stats


def print_report(stats: Stats, duration: float):
    """打印压测报告"""
    print(f"\n{'='*50}")
    print(f"  压测报告")
    print(f"{'='*50}")
    print(f"  总耗时:       {duration:.2f} 秒")
    print(f"  总请求数:     {stats.total}")
    print(f"  成功:         {stats.success}")
    print(f"  失败:         {stats.failed}")
    print(f"  QPS:          {stats.total / duration:.1f}")
    print(f"  平均响应时间: {stats.total_time / max(stats.total, 1) * 1000:.1f} ms")
    if stats.errors:
        print(f"  错误示例:")
        for e in stats.errors[:5]:
            print(f"    - {e}")
    print(f"{'='*50}")


# 使用示例
if __name__ == "__main__":
    async def test_json_post():
        # 替换成你要压测的实际接口地址
        stats = await stress_test(
            url="http://192.168.5.197:8090/api/xxx/xxx",
            method="POST",
            json={"key": "value"},
            concurrency=50,
            total_requests=500,
            auto_login=True  # 自动登录获取token，默认开启
        )
        return stats

    async def main():
        start = time.perf_counter()
        stats = await test_json_post()
        duration = time.perf_counter() - start
        print_report(stats, duration)

    asyncio.run(main())
