# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/9/2 上午9:50
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : concurrency_demo.py
# @Project : wecharmer

"""
多接口混合并发测试 demo

用法一：多个接口按权重一起并发（常用）
    from lib.concurrency_demo import ConcurrencyDemo

    demo = ConcurrencyDemo()                    # 自动登录获取 Authorization
    result = demo.run_mix(
        cases=[
            {"name": "备货单详情", "url": f"{waveecharmer_Host}/api/stockupbill/detailbysku/1001",
             "method": "get", "weight": 3},
            {"name": "发货单列表", "url": f"{waveecharmer_Host}/api/shipmentbill/page",
             "method": "post", "payload": {"pageIndex": 1, "pageSize": 10}, "weight": 1},
        ],
        concurrency=30,                         # 总并发数
        total=300,                              # 总请求数，按 weight 分摊到各接口
    )
    demo.print_mix_report(result)

用法二：单个接口压测
    result = demo.run(url=..., method="get", concurrency=20, total=200)
    demo.print_report(result)

用法三：每个接口只跑一次（冒烟用，total 不传即可）
    result = demo.run_mix(cases, concurrency=10)   # weight 都是 1，每个接口各发一次请求
    demo.print_mix_report(result)

    # 单个接口只跑一次
    demo.run(url=..., method="get", total=1)

命令行（单个接口）:
    python lib/concurrency_demo.py -u http://erp-test.wecharmer.cn:8090/api/account/login -m post -c 20 -n 200 --no-login

鉴权说明（需要登录的接口不用手动传 token，默认已处理）：
    1. 默认：初始化时登录一次，所有请求共用这一份 token
    2. 多用户：ConcurrencyDemo(per_thread_login=True)，每个并发线程各登录一次，各有各的 token
    3. 压别的系统：ConcurrencyDemo(login_func=Login.loginWecharmer_emc)  # 或 Login.loginFreightower
    4. 混合鉴权：case 里单独给 headers，如 {"name": "飞驼下单", "headers": Login.loginFreightower()}
    5. 压测途中 token 过期：自动重新登录并重试一次（relogin_on_401=False 可关掉）
       注意：微诚ERP 的 token 失效返回的是 HTTP 200 + body {"status":401}，这里两种都认
    6. 压登录接口本身：ConcurrencyDemo(auto_login=False)
"""

import argparse
import math
import random
import threading
import time
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter

from conf.baseconfig import waveecharmer_Host
from lib.login import Login


class ConcurrencyDemo:
    """基于线程池的接口并发测试，依赖 requests，无需额外安装组件"""

    def __init__(self, cookies=None, timeout=10, auto_login=True,
                 login_func=None, per_thread_login=False, relogin_on_401=True):
        """
        :param cookies: 请求头(鉴权信息)，如 {"Authorization": "xxx"}；给了就不走登录
        :param timeout: 单请求超时时间(秒)
        :param auto_login: cookies 为空时是否自动登录
        :param login_func: 登录函数，默认 Login.loginWecharmer；
                           压 EMC 传 Login.loginWecharmer_emc，压飞驼传 Login.loginFreightower
        :param per_thread_login: 每个并发线程各自登录一次(模拟多用户)，默认共用一份 token
        :param relogin_on_401: 遇到 401 自动重新登录后重试一次(应对压测途中 token 过期)
        """
        self.timeout = timeout
        self.per_thread_login = per_thread_login
        self.relogin_on_401 = relogin_on_401
        self._login = login_func or Login.loginWecharmer
        self._cookies = cookies
        self._token_lock = threading.Lock()
        self._thread_local = threading.local()
        if self._cookies is None and auto_login and not per_thread_login:
            self._cookies = self._login()

    def _session(self, pool_size):
        """每个线程复用一个 Session，保证连接池真正生效"""
        session = getattr(self._thread_local, "session", None)
        if session is None:
            session = requests.Session()
            adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self._thread_local.session = session
        return session

    def _resolve_headers(self, case):
        """取本次请求用的鉴权头：接口自定义 > 线程独立 token > 共享 token"""
        if case.get("headers"):
            return case["headers"]
        if self.per_thread_login:
            headers = getattr(self._thread_local, "headers", None)
            if headers is None:
                headers = self._login()
                self._thread_local.headers = headers
            return headers
        return self._cookies

    def _refresh_headers(self, case, old_headers):
        """token 失效时重新登录，case 自带 headers 的不处理"""
        if case.get("headers"):
            return
        if self.per_thread_login:
            self._thread_local.headers = self._login()
            return
        # 共享 token：加锁，且只有持有旧 token 的线程才刷新，避免并发重复登录
        with self._token_lock:
            if self._cookies is old_headers:
                self._cookies = self._login()

    @staticmethod
    def _json(resp):
        """安全地取响应 json，非 json 返回 None"""
        try:
            return resp.json()
        except ValueError:
            return None

    @staticmethod
    def _brief(text, limit=200):
        """截断超长内容，避免刷屏"""
        text = str(text)
        return text if len(text) <= limit else text[:limit] + "..."

    @staticmethod
    def _target(case):
        """接口标识：METHOD url"""
        return f"{case.get('method', 'get').upper()} {case['url']}"

    def _request_desc(self, case):
        """失败明细里的请求描述：METHOD url payload=xxx"""
        desc = self._target(case)
        if case.get("payload") is not None:
            desc += f" payload={self._brief(case['payload'])}"
        return desc

    def _effective_status(self, resp):
        """
        有效状态码：微诚ERP 的 token 失效是 HTTP 200 + body {"status":401}，只看 HTTP 码会漏掉
        """
        if resp.status_code >= 400:
            return resp.status_code
        body = self._json(resp)
        biz_status = body.get("status") if isinstance(body, dict) else None
        if isinstance(biz_status, int) and biz_status >= 400:
            return biz_status
        return resp.status_code

    @staticmethod
    def _error_message(resp):
        """业务失败时取 body 里的错误信息"""
        body = None
        try:
            body = resp.json()
        except ValueError:
            return None
        if isinstance(body, dict):
            return body.get("errorMessage") or body.get("message") or body.get("code")
        return None

    def _send(self, case, headers, pool_size):
        """发一次请求，返回 (有效状态码, 耗时ms, 响应对象)"""
        start = time.perf_counter()
        resp = self._session(pool_size).request(
            case.get("method", "get"),
            case["url"],
            headers=headers,
            json=case.get("payload"),
            timeout=self.timeout,
        )
        cost = (time.perf_counter() - start) * 1000
        return self._effective_status(resp), cost, resp

    def _response_snippet(self, resp, limit=200):
        """成功响应的内容摘要，优先取 body 里的 result"""
        body = self._json(resp)
        if body is None:
            return self._brief(resp.text, limit)
        if isinstance(body, dict) and "result" in body:
            return self._brief(body["result"], limit)
        return self._brief(body, limit)

    def _make_sample(self, case, status, cost, error, resp):
        """生成一条请求样例，用于报告里展示成功/失败的具体内容"""
        ok = status is not None and status < 400
        message = self._response_snippet(resp) if ok else (error or "")
        return {
            "ok": ok,
            "cost": cost,
            "payload": "" if case.get("payload") is None else self._brief(case["payload"]),
            "message": message or "<无返回内容>",
        }

    def _once(self, case, pool_size):
        """发起单次请求，返回 (接口名, 耗时ms, 有效状态码, 错误信息, 响应对象)"""
        headers = self._resolve_headers(case)
        start = time.perf_counter()
        try:
            status, _, resp = self._send(case, headers, pool_size)
            if status in (401, 403) and self.relogin_on_401:
                self._refresh_headers(case, headers)      # token 失效，重新登录后重试一次
                status, _, resp = self._send(case, self._resolve_headers(case), pool_size)

            error = None
            if status >= 400:
                message = self._error_message(resp)
                reason = f"HTTP {status}" + (f": {message}" if message else "")
                error = f"{self._request_desc(case)} -> {reason}"
            cost = (time.perf_counter() - start) * 1000
            return case["name"], cost, status, error, resp
        except requests.RequestException as e:
            reason = f"{type(e).__name__}: {self._brief(e)}"
            cost = (time.perf_counter() - start) * 1000
            return case["name"], cost, None, f"{self._request_desc(case)} -> {reason}", None

    @staticmethod
    def _build_tasks(cases, total):
        """按 weight 把总请求数分摊到各接口，并打乱顺序让接口真正交替并发"""
        weights = [case.get("weight", 1) for case in cases]
        total_weight = sum(weights)
        if total_weight <= 0:
            raise ValueError("weight 之和必须大于 0")

        # total 为 None 时按 weight 跑：weight 都是 1 就是每个接口各跑一次
        total = total_weight if total is None else total

        counts = [total * w // total_weight for w in weights]
        counts[0] += total - sum(counts)  # 除不尽的余数补给第一个接口

        tasks = []
        for case, count in zip(cases, counts):
            tasks.extend([case] * count)
        random.shuffle(tasks)
        return tasks

    def _execute(self, tasks, concurrency, verbose=False, order=None, sample_size=3):
        """把任务丢进同一个线程池执行，按接口汇总"""
        # 按声明顺序预建分组，避免结果按完成先后乱序
        group = {name: ([], Counter(), [], []) for name in (order or [])}
        targets = {task["name"]: self._target(task) for task in tasks}
        task_by_name = {task["name"]: task for task in tasks}
        all_costs, all_status, all_errors, all_samples = [], Counter(), [], []

        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(self._once, task, concurrency) for task in tasks]
            for future in as_completed(futures):
                name, cost, status, error, resp = future.result()
                costs, status_counter, errors, samples = group.setdefault(name, ([], Counter(), [], []))
                costs.append(cost)
                all_costs.append(cost)
                if error:
                    errors.append(error)
                    all_errors.append(error)
                if status is not None:      # 请求异常(超时/连不上)时 status 为 None
                    status_counter[status] += 1
                    all_status[status] += 1
                # 每个接口只留前 sample_size 条样例，避免大并发时占内存
                if len(samples) < sample_size:
                    sample = self._make_sample(task_by_name[name], status, cost, error, resp)
                    if not samples:
                        all_samples.append(sample)      # 汇总里每个接口留一条
                    samples.append(sample)
                if verbose:
                    print(f"[{name}] status={status} cost={cost:.1f}ms error={error}")
        duration = time.perf_counter() - start

        return {
            "overall": self._summary(all_costs, all_status, all_errors, duration,
                                     samples=all_samples),
            "cases": {
                name: self._summary(costs, status_counter, errors, duration,
                                    targets.get(name), samples)
                for name, (costs, status_counter, errors, samples) in group.items()
            },
        }

    def run_mix(self, cases, concurrency=10, total=None, verbose=False, sample_size=3):
        """
        多个接口一起并发
        :param cases: 接口列表，每项支持
                      name(必填，统计用) / url / method / payload / headers / weight(权重，默认1)
        :param concurrency: 总并发数(所有接口共用)
        :param total: 总请求数，按 weight 分摊；不传(默认 None)则每个接口各跑 weight 次，
                      weight 都是 1 就是每个接口只跑一次
        :param sample_size: 每个接口保留几条成功/失败样例(报告里展示)，默认 3，传 0 关闭
        :return: {"overall": 总统计, "cases": {接口名: 统计}}
        """
        for case in cases:
            if not case.get("name"):
                raise ValueError(f"接口缺少 name: {case}")
            if not case.get("url"):
                raise ValueError(f"接口 {case['name']} 缺少 url")

        order = [case["name"] for case in cases]
        return self._execute(self._build_tasks(cases, total), concurrency, verbose,
                             order, sample_size)

    def run(self, url, method="get", payload=None, headers=None,
            concurrency=10, total=100, verbose=False, sample_size=3):
        """
        单个接口压测
        :param url: 接口地址
        :param method: get/post/put/delete
        :param payload: 请求体(dict)，会以 json 方式发送
        :param headers: 自定义请求头，为空则使用登录态
        :param concurrency: 并发数
        :param total: 总请求数
        :param sample_size: 保留几条成功/失败样例(报告里展示)，默认 3，传 0 关闭
        :return: 统计结果 dict
        """
        case = {"name": url, "url": url, "method": method,
                "payload": payload, "headers": headers, "weight": 1}
        return self._execute([case] * total, concurrency, verbose,
                             sample_size=sample_size)["overall"]

    @staticmethod
    def _percentile(sorted_data, pct):
        """线性插值计算百分位"""
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * pct / 100
        floor, ceil = math.floor(k), math.ceil(k)
        if floor == ceil:
            return sorted_data[int(k)]
        return sorted_data[floor] * (ceil - k) + sorted_data[ceil] * (k - floor)

    def _summary(self, costs, status_counter, errors, duration, target=None, samples=None):
        costs = sorted(costs)
        success = sum(count for status, count in status_counter.items() if status < 400)
        return {
            "target": target,
            "samples": samples or [],
            "total": len(costs),
            "success": success,
            "failed": len(costs) - success,
            "duration": duration,
            "qps": len(costs) / duration if duration else 0,
            "min": costs[0] if costs else 0.0,
            "max": costs[-1] if costs else 0.0,
            "avg": sum(costs) / len(costs) if costs else 0.0,
            "p50": self._percentile(costs, 50),
            "p90": self._percentile(costs, 90),
            "p95": self._percentile(costs, 95),
            "p99": self._percentile(costs, 99),
            "status": dict(status_counter),
            "errors": Counter(errors).most_common(5),
        }

    @classmethod
    def print_report(cls, result):
        """打印单个接口的压测报告"""
        print(f"\n{'=' * 52}")
        print("  接口并发测试报告")
        print(f"{'=' * 52}")
        if result.get("target"):
            print(f"  接口:         {result['target']}")
        print(f"  总请求数:     {result['total']}")
        print(f"  成功:         {result['success']}")
        print(f"  失败:         {result['failed']}")
        print(f"  总耗时:       {result['duration']:.2f} s")
        print(f"  QPS:          {result['qps']:.1f}")
        print(f"  响应时间(ms): min={result['min']:.1f} avg={result['avg']:.1f} max={result['max']:.1f}")
        print(f"  百分位(ms):   p50={result['p50']:.1f} p90={result['p90']:.1f} "
              f"p95={result['p95']:.1f} p99={result['p99']:.1f}")
        print(f"  状态码分布:   {result['status']}")
        cls._print_samples(result, ok_only=True)   # 失败明细下面带次数，这里只展示成功样例
        if result["errors"]:
            print("  失败明细 TOP5:")
            for error, count in result["errors"]:
                print(f"    - [{count}次] {error}")
        print(f"{'=' * 52}")

    @classmethod
    def _print_samples(cls, result, prefix="  ", ok_only=False):
        """打印成功/失败样例：成功看响应内容摘要，失败看请求和原因"""
        samples = result.get("samples") or []
        kinds = ((True, "成功样例"),) if ok_only else ((True, "成功样例"), (False, "失败样例"))
        for ok, label in kinds:
            rows = [sample for sample in samples if sample["ok"] == ok]
            if not rows:
                continue
            print(f"{prefix}{label}:")
            for sample in rows:
                payload = f" payload={sample['payload']}" if sample["payload"] else ""
                print(f"{prefix}  - [{sample['cost']:.1f}ms]{payload} {sample['message']}")

    @staticmethod
    def _display_width(text):
        """中文按 2 个字符宽计算，用于表格对齐"""
        return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)

    @classmethod
    def print_mix_report(cls, result):
        """打印多接口混合压测报告（各接口明细 + 总体）"""
        cases = result["cases"]
        name_width = max([cls._display_width(name) for name in cases] + [4]) + 2
        # 接口地址列最多 60 个字符宽，超长截断
        target_width = min(max([cls._display_width(stat.get("target") or "")
                                for stat in cases.values()] + [8]) + 2, 60)
        total_width = name_width + target_width + 82

        print(f"\n{'=' * total_width}")
        print("  多接口混合并发测试报告")
        print(f"{'=' * total_width}")
        header = f"  {'接口':<{name_width}}{'接口地址':<{target_width}}" \
                 f"{'请求数':>8}{'成功':>8}{'失败':>8}{'QPS':>10}" \
                 f"{'avg(ms)':>12}{'p95(ms)':>12}{'p99(ms)':>12}{'状态码':>16}"
        print(header)
        print(f"  {'-' * (total_width - 2)}")
        for name, stat in cases.items():
            name_padding = " " * (name_width - cls._display_width(name))
            target = cls._brief(stat.get("target") or "", target_width - 2)
            target_padding = " " * (target_width - cls._display_width(target))
            print(f"  {name}{name_padding}{target}{target_padding}"
                  f"{stat['total']:>8}{stat['success']:>8}{stat['failed']:>8}"
                  f"{stat['qps']:>10.1f}{stat['avg']:>12.1f}{stat['p95']:>12.1f}"
                  f"{stat['p99']:>12.1f}{str(stat['status']):>16}")
        print(f"{'=' * total_width}")

        for name, stat in cases.items():
            if not stat["failed"] and not stat.get("samples"):
                continue
            print(f"\n  [{name}] {stat.get('target')}")
            for error, count in stat["errors"]:
                print(f"    失败[{count}次] {error}")
            cls._print_samples(stat, prefix="    ", ok_only=True)

        print("\n  汇总：")
        cls.print_report(result["overall"])


def main():
    parser = argparse.ArgumentParser(description="接口并发测试(单个接口)")
    parser.add_argument("-u", "--url", required=True, help="接口地址")
    parser.add_argument("-m", "--method", default="get", help="请求方法，默认 get")
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="并发数，默认 10")
    parser.add_argument("-n", "--total", type=int, default=100, help="总请求数，默认 100")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="单请求超时(秒)，默认 10")
    parser.add_argument("--no-login", action="store_true", help="不自动登录(压测登录接口时使用)")
    parser.add_argument("--per-thread-login", action="store_true", help="每个并发线程各自登录一次")
    args = parser.parse_args()

    demo = ConcurrencyDemo(timeout=args.timeout, auto_login=not args.no_login,
                           per_thread_login=args.per_thread_login)
    result = demo.run(
        url=args.url,
        method=args.method,
        concurrency=args.concurrency,
        total=args.total,
    )
    demo.print_report(result)


if __name__ == "__main__":
    # 命令行压测单个接口
    # main()

    # 多个接口按权重一起并发（改成你自己的接口即可）
    # per_thread_login=True 表示每个并发线程各登录一次，模拟多用户；False 则共用一份 token
    result = ConcurrencyDemo(per_thread_login=True).run_mix(
        cases=[
            {
                "name": "运营库存流水同步",
                "url": f"{waveecharmer_Host}/api/operatingstock/incremental/job",
                "method": "post",
                "payload": {},
                "weight": 1,
            },
            {
                "name": "重新计算流水",
                "url": f"{waveecharmer_Host}/api/operatingstock/recalculate",
                "method": "post",
                "payload": {"stockLogId":1555603},
                "weight": 1,
            }

        ],
        concurrency=2,   # 总并发数
        total=2,        # 总请求数，按 weight 分摊：登录30 / 备货单90 / 发货单180
    )
    ConcurrencyDemo.print_mix_report(result)
