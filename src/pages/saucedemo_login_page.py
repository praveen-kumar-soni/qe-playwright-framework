import re

from playwright.sync_api import Page, expect

from src.base.base_page import BasePage
from src.utils.config import SAUCEDEMO_BASE_URL


class SauceDemoLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.get_by_role("textbox", name="Username")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.credentials = page.locator(".login_credentials")
        self.password_hint = page.locator(".login_password")

    def open(self):
        self.navigate(SAUCEDEMO_BASE_URL)

    def get_credentials(self) -> tuple[str, str]:
        username_match = re.search(r"standard_user", self.credentials.inner_text())
        password_match = re.search(r"Password for all users:\s*(\S+)", self.password_hint.inner_text())

        assert username_match, "The standard user credential was not found on the login page."
        assert password_match, "The shared password was not found on the login page."
        return username_match.group(0), password_match.group(1)

    def login(self, username: str, password: str):
        expect(self.username_input).to_be_visible()
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
