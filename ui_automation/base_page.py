"""Shared Playwright page-object operations."""

from typing import Any
from urllib.parse import urljoin


class BasePage:
    def __init__(self, page: Any, base_url: str, timeout: float = 10.0):
        self.page = page
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout_ms = timeout * 1000

    def open(self, path: str) -> None:
        url = urljoin(self.base_url, path.lstrip("/"))
        self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)

    def locator(self, selector: str) -> Any:
        return self.page.locator(selector)

    def visible(self, selector: str) -> Any:
        locator = self.locator(selector)
        locator.wait_for(state="visible", timeout=self.timeout_ms)
        return locator

    def fill(self, selector: str, value: str) -> None:
        self.visible(selector).fill(value, timeout=self.timeout_ms)

    def click(self, selector: str) -> None:
        self.visible(selector).click(timeout=self.timeout_ms)

    def text(self, selector: str) -> str:
        return self.visible(selector).inner_text(timeout=self.timeout_ms).strip()