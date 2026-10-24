import unittest

from ui_automation.pages import ContainerListPage, LoginPage


class FakeLocator:
    def __init__(self, text=""):
        self.text = text
        self.filled = []
        self.clicks = 0
        self.waits = []

    def wait_for(self, **kwargs):
        self.waits.append(kwargs)

    def fill(self, value, **kwargs):
        self.filled.append(value)

    def click(self, **kwargs):
        self.clicks += 1

    def inner_text(self, **kwargs):
        return self.text


class FakePage:
    def __init__(self, elements):
        self.elements = elements
        self.visits = []

    def goto(self, url, **kwargs):
        self.visits.append((url, kwargs))

    def locator(self, selector):
        return self.elements[selector]


class PageObjectTests(unittest.TestCase):
    def test_login_enters_credentials_and_waits_for_welcome(self):
        elements = {selector: FakeLocator() for selector in (
            LoginPage.USERNAME, LoginPage.PASSWORD, LoginPage.SUBMIT, LoginPage.WELCOME
        )}
        page = FakePage(elements)

        LoginPage(page, "https://erp.example").login("tester", "secret")

        self.assertEqual(page.visits[0][0], "https://erp.example/user/login")
        self.assertEqual(elements[LoginPage.USERNAME].filled, ["tester"])
        self.assertEqual(elements[LoginPage.PASSWORD].filled, ["secret"])
        self.assertEqual(elements[LoginPage.SUBMIT].clicks, 1)

    def test_container_search_returns_detail(self):
        elements = {
            ContainerListPage.BILL_NUMBER: FakeLocator(),
            ContainerListPage.SEARCH: FakeLocator(),
            ContainerListPage.FIRST_CARRIER: FakeLocator("COSCO"),
            ContainerListPage.FIRST_STATUS: FakeLocator("已完成"),
            ContainerListPage.ENTRY_TIME: FakeLocator("2026-09-08 10:00"),
        }

        result = ContainerListPage(FakePage(elements), "https://erp.example").search("BL001")

        self.assertEqual(result.carrier_code, "COSCO")
        self.assertEqual(result.status, "已完成")
        self.assertEqual(result.entry_time, "2026-09-08 10:00")
        self.assertEqual(elements[ContainerListPage.FIRST_STATUS].clicks, 1)


if __name__ == "__main__":
    unittest.main()