from playwright.sync_api import Page, Locator, expect

from src.base.base_page import BasePage


class SearchPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # use xpath to locate the search box and results //textarea[@aria-label='Search with DuckDuckGo']

        self.search_box = page.locator('//textarea[@aria-label="Search with DuckDuckGo"]')
        self.results = page.locator('article[data-testid="result"]')

    def open(self):
        self.page.goto("https://duckduckgo.com")

    def search(self, text: str):
        expect(self.search_box).to_be_visible()
        self.search_box.fill(text)
        self.search_box.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def get_result_count(self) -> int:
        return self.results.count()