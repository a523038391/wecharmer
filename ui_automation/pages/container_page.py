"""First-leg container-list page object."""

from dataclasses import dataclass
from typing import Optional

from ui_automation.base_page import BasePage


@dataclass(frozen=True)
class ContainerResult:
    carrier_code: str
    status: str
    entry_time: Optional[str] = None


class ContainerListPage(BasePage):
    BILL_NUMBER = "xpath=//textarea[@placeholder='提单号']"
    SEARCH = "xpath=//*[contains(text(),'查 询')]"
    FIRST_CARRIER = 'xpath=//tbody[@class="ant-table-tbody"]/tr[2]/td[27]'
    FIRST_STATUS = 'xpath=//tbody[@class="ant-table-tbody"]/tr[2]/td[26]/a'
    ENTRY_TIME = "xpath=//div[contains(text(),'进场')]/following-sibling::div[1]"
    DETAIL_STATUSES = {"进行中", "已完成"}

    def search(self, bill_number: str) -> ContainerResult:
        if not bill_number.strip():
            raise ValueError("bill_number is required")
        self.open("express/container/list")
        self.fill(self.BILL_NUMBER, bill_number)
        self.click(self.SEARCH)

        carrier_code = self.text(self.FIRST_CARRIER)
        status = self.text(self.FIRST_STATUS)
        entry_time = None
        if status in self.DETAIL_STATUSES:
            self.click(self.FIRST_STATUS)
            entry_time = self.text(self.ENTRY_TIME)
        return ContainerResult(carrier_code, status, entry_time)