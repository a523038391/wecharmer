"""Login page object."""

from ui_automation.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = 'xpath=//*[@id="formLogin"]/div[1]/div/div/div/span/input'
    PASSWORD = 'xpath=//*[@id="formLogin"]/div[2]/div/div/div/span/input'
    SUBMIT = "xpath=//*[contains(text(),'登')]"
    WELCOME = "xpath=//*[contains(text(),'欢迎使用微诚ERP系统')]"

    def login(self, username: str, password: str) -> "LoginPage":
        if not username or not password:
            raise ValueError("username and password are required")
        self.open("user/login")
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)
        self.visible(self.WELCOME)
        return self