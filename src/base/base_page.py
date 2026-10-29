from pathlib import Path
from typing import Optional, Union

from playwright.sync_api import Locator, Page, expect


class BasePage:
    """Shared, reusable Playwright interactions for all page objects.

    Element-interaction methods take a ``Locator`` — page objects are expected
    to build their own locators in ``__init__``, preferring semantic locators
    (``page.get_by_role``, ``get_by_label``, ``get_by_placeholder``, etc.) over
    raw CSS/XPath selectors where a meaningful accessible role/name exists.
    """

    DEFAULT_TIMEOUT_MS = 10_000

    def __init__(self, page: Page):
        self.page = page

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def navigate(self, url: str):
        self.page.goto(url)

    def reload(self):
        self.page.reload()

    def go_back(self):
        self.page.go_back()

    def go_forward(self):
        self.page.go_forward()

    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()

    def wait_for_url(self, url: str, timeout: Optional[int] = None):
        self.page.wait_for_url(url, timeout=timeout or self.DEFAULT_TIMEOUT_MS)

    def wait_for_load_state(self, state: str = "load"):
        self.page.wait_for_load_state(state)

    # ------------------------------------------------------------------ #
    # Element interactions
    # ------------------------------------------------------------------ #
    def click(self, locator: Locator, timeout: Optional[int] = None):
        expect(locator).to_be_visible(timeout=timeout or self.DEFAULT_TIMEOUT_MS)
        locator.click()

    def fill(self, locator: Locator, text: str, timeout: Optional[int] = None):
        expect(locator).to_be_visible(timeout=timeout or self.DEFAULT_TIMEOUT_MS)
        locator.fill(text)

    def wait_for_visible(self, locator: Locator, timeout: Optional[int] = None):
        expect(locator).to_be_visible(timeout=timeout or self.DEFAULT_TIMEOUT_MS)

    def upload_file(self, locator: Locator, file_path: Union[str, Path]):
        locator.set_input_files(str(file_path))

    # ------------------------------------------------------------------ #
    # utilities
    # ------------------------------------------------------------------ #
    def take_screenshot(self, path: Union[str, Path], full_page: bool = True):
        self.page.screenshot(path=str(path), full_page=full_page)

    def execute_script(self, script: str, arg=None):
        return self.page.evaluate(script, arg)