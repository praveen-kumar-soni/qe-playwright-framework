import pytest

from src.pages.search_page import SearchPage

@pytest.mark.sanity
def test_search(page_context):
    search_page = SearchPage(page_context)
    search_page.open()
    search_page.search("Playwright Python automation")
    count = search_page.get_result_count()
    assert count > 0
    print(f"\n🔍 Found {count} results")