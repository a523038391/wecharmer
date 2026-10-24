"""Playwright browser, context and page lifecycle helpers."""

from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ui_automation.config import UISettings


def _load_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is required: python -m pip install playwright") from exc
    return sync_playwright


class BrowserSession(AbstractContextManager):
    def __init__(self, settings: UISettings):
        self.settings = settings
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._tracing = False

    def __enter__(self):
        self.playwright = _load_playwright()().start()
        browser_name, channel = _browser_target(self.settings.browser)
        browser_type = getattr(self.playwright, browser_name)
        launch_options = {
            "headless": self.settings.headless,
            "slow_mo": self.settings.slow_mo,
        }
        if channel:
            launch_options["channel"] = channel
        self.browser = browser_type.launch(**launch_options)
        self.context = self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.context.set_default_timeout(self.settings.timeout * 1000)
        if self.settings.trace:
            self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
            self._tracing = True
        self.page = self.context.new_page()
        return self.page

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._save_artifacts(exc_type)
        finally:
            if self.context is not None:
                self.context.close()
            if self.browser is not None:
                self.browser.close()
            if self.playwright is not None:
                self.playwright.stop()
        return False

    def _save_artifacts(self, exc_type: Optional[type]) -> None:
        if exc_type is None and not self._tracing:
            return
        output_dir = Path(self.settings.artifacts_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        if exc_type is not None and self.page is not None:
            self.page.screenshot(path=output_dir / f"failure-{timestamp}.png", full_page=True)
        if self._tracing:
            path = output_dir / f"trace-{timestamp}.zip" if exc_type is not None else None
            self.context.tracing.stop(path=path)


def _browser_target(browser: str) -> tuple[str, Optional[str]]:
    targets = {
        "chromium": ("chromium", None),
        "chrome": ("chromium", "chrome"),
        "edge": ("chromium", "msedge"),
        "firefox": ("firefox", None),
        "webkit": ("webkit", None),
    }
    try:
        return targets[browser.lower()]
    except KeyError as exc:
        supported = ", ".join(targets)
        raise ValueError(f"Unsupported browser '{browser}'. Choose: {supported}") from exc