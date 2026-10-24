"""pytest 全局 fixture：base_url、token、http_client。"""
import configparser
import os

import pytest
import requests

from utils.http_client import HttpClient

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")


def load_config() -> configparser.ConfigParser:
    """读取 config.ini，支持外部覆盖（环境变量优先于配置文件）。"""
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")
    return config


@pytest.fixture(scope="session")
def base_url() -> str:
    """被测服务地址，来自 config.ini [api] base_url。"""
    return load_config().get("api", "base_url", fallback="http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def token(base_url: str) -> str:
    """认证 token。

    优先级：config.ini [auth] token > 环境变量 AUTH_TOKEN。
    若接口文档提供登录接口，将此处替换为登录获取逻辑。
    """
    config = load_config()
    token = config.get("auth", "token", fallback="").strip()
    if not token:
        token = os.environ.get("AUTH_TOKEN", "")
    return token


@pytest.fixture(scope="session")
def http_client(base_url: str, token: str) -> HttpClient:
    """带 base_url 与 token 的请求客户端。"""
    config = load_config()
    timeout = config.getint("api", "timeout", fallback=10)
    return HttpClient(base_url=base_url, token=token, timeout=timeout)


@pytest.fixture(scope="session")
def raw_session(base_url: str) -> requests.Session:
    """无 token 的原始会话，用于登录等认证前置请求。"""
    return requests.Session()
