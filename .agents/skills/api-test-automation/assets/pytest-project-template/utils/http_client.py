"""requests 封装：统一 base_url、token 请求头、超时与请求日志。"""
import logging

import requests

logger = logging.getLogger("api-test")


class HttpError(Exception):
    """HTTP 请求失败异常，携带状态码与响应体。"""

    def __init__(self, status_code: int, response_body: str):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"HTTP {status_code}: {response_body}")


class HttpClient:
    """轻量 HTTP 客户端，所有用例请求经由本类发起。"""

    def __init__(self, base_url: str, token: str = "", timeout: int = 10,
                 token_header: str = "Authorization", token_prefix: str = "Bearer"):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if token:
            value = f"{token_prefix} {token}".strip() if token_prefix else token
            self.session.headers.update({token_header: value})

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        url = self._url(path)
        logger.info(">>> %s %s", method.upper(), url)
        resp = self.session.request(method, url, **kwargs)
        logger.info("<<< status=%s body=%s", resp.status_code, resp.text[:2000])
        return resp

    # -- 常用方法，直接对应 requests 语义 --
    def get(self, path: str, params: dict = None, **kwargs):
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: dict = None, data: dict = None, **kwargs):
        return self._request("POST", path, json=json, data=data, **kwargs)

    def put(self, path: str, json: dict = None, **kwargs):
        return self._request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: dict = None, **kwargs):
        return self._request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)
