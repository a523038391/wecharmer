"""Playwright UI smoke test; values are supplied through environment variables."""

import os

import pytest

from ui_automation.pages import ContainerListPage, LoginPage

pytest_plugins = ["ui_automation.fixtures"]


class Test:
    @pytest.mark.smoke
    @pytest.mark.firstleg
    @pytest.mark.ui
    def container_query_link(self, browser_page, ui_settings):
        bill_number = os.getenv("UI_BILL_NUMBER", "").strip()
        if not bill_number:
            pytest.skip("UI_BILL_NUMBER is required")

        LoginPage(browser_page, ui_settings.base_url, ui_settings.timeout).login(
            ui_settings.username,
            ui_settings.password,
        )
        result = ContainerListPage(
            browser_page, ui_settings.base_url, ui_settings.timeout
        ).search(bill_number)

        assert result.status