import pytest
from playwright.sync_api import Page, expect

from src.pages.saucedemo_login_page import SauceDemoLoginPage


@pytest.mark.sanity
def test_saucedemo_login_with_credentials_from_footer(page_context: Page):
    login_page = SauceDemoLoginPage(page_context)
    login_page.open()

    username, password = login_page.get_credentials()
    login_page.login(username, password)

    expect(page_context).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page_context.get_by_text("Products", exact=True)).to_be_visible()
