"""Reusable pytest fixtures for Playwright UI tests."""

import pytest

from ui_automation import BrowserSession, UISettings


@pytest.fixture
def ui_settings():
    try:
        return UISettings.from_env()
    except ValueError as exc:
        pytest.skip(str(exc))


@pytest.fixture
def browser_page(ui_settings):
    with BrowserSession(ui_settings) as page:
        yield page