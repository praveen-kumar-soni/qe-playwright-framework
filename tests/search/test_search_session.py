import pytest
from playwright.sync_api import Page, expect

from src.pages.search.search_page import SearchPage


@pytest.fixture(autouse=True)
def setup(session_page_context: Page, team_config):
    """Navigate to DuckDuckGo before each test in this module."""
    search_page = SearchPage(session_page_context)
    search_page.open(team_config["duckduckgo_base_url"])
    yield


def test_search_returns_results(session_page_context: Page):
    """Search for a query and verify results are returned."""
    search_page = SearchPage(session_page_context)
    search_page.search("Playwright Python automation")
    count = search_page.get_result_count()
    assert count > 0, f"Expected results but got {count}"
    print(f"\n🔍 Found {count} results for 'Playwright Python automation'")


def test_search_different_query(session_page_context: Page):
    """Search for a different query and verify results are returned."""
    search_page = SearchPage(session_page_context)
    search_page.search("pytest fixtures tutorial")
    count = search_page.get_result_count()
    assert count > 0, f"Expected results but got {count}"
    print(f"\n🔍 Found {count} results for 'pytest fixtures tutorial'")


def test_page_title_contains_search_term(session_page_context: Page):
    """Verify page title contains the searched term after searching."""
    search_page = SearchPage(session_page_context)
    search_page.search("GitHub Copilot")
    title = search_page.get_title()
    assert "GitHub Copilot 1" in title, f"Expected 'GitHub Copilot' in title but got: '{title}'"
    print(f"\n📄 Page title: {title}")


def test_search_result_count_is_reasonable(session_page_context: Page):
    """Verify the number of results on a page is within a reasonable range."""
    search_page = SearchPage(session_page_context)
    search_page.search("Python programming")
    count = search_page.get_result_count()
    assert 1 <= count <= 20, f"Expected between 1–20 results but got {count}"
    print(f"\n📊 Result count on page: {count}")

