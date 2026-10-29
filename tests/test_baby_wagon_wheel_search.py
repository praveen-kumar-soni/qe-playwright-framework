import pytest

from src.pages.search_page import SearchPage


@pytest.mark.sanity
def test_search_baby_wagon_wheel(page_context):
    search_page = SearchPage(page_context)
    search_page.open()
    search_page.search("Baby wagon wheel")
    count = search_page.get_result_count()
    assert count > 0, f"Expected results but got {count}"
    print(f"\n🔍 Found {count} results for 'Baby wagon wheel'")
