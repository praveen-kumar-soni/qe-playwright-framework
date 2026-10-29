from pathlib import Path

import allure
import pytest
from playwright.sync_api import Playwright, Browser, Page, BrowserContext


@pytest.fixture(scope="session")
def browser_instance(playwright: Playwright) -> Browser:
    browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page_context(request, browser_instance: Browser) -> Page:
    print("\nSetting up a new browser context for the test...", request.node.name)

    context: BrowserContext = browser_instance.new_context(
        ignore_https_errors=True,
        record_video_dir="videos/"
    )
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page: Page = context.new_page()
    yield page


    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    video = page.video

    if failed:
        trace_dir = Path("test-output")
        trace_dir.mkdir(parents=True, exist_ok=True)
        trace_path = trace_dir / f"{request.node.name}_trace.zip"
        context.tracing.stop(path=str(trace_path))
    else:
        context.tracing.stop()

    context.close()

    if failed:
        allure.attach.file(str(trace_path), name=f"{request.node.name}_trace", extension="zip")

    if failed and video:
        video_path = Path(video.path())
        video_dir = Path("videos")
        video_dir.mkdir(parents=True, exist_ok=True)
        new_video_path = video_dir / f"{request.node.name}.webm"
        video.save_as(new_video_path)
        if video_path != new_video_path and video_path.exists():
            video_path.unlink()
        print(f"Video saved to {new_video_path}")
        allure.attach.file(str(new_video_path), name=f"{request.node.name}_video", attachment_type=allure.attachment_type.WEBM)


@pytest.fixture(scope="session")
def session_page_context(browser_instance: Browser) -> Page:
    context: BrowserContext = browser_instance.new_context(
        ignore_https_errors=True,
        record_video_dir="videos/"
    )
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page: Page = context.new_page()
    yield page
    trace_dir = Path("test-output")
    trace_dir.mkdir(parents=True, exist_ok=True)
    context.tracing.stop(path=str(trace_dir / "session_trace.zip"))
    context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        if report.failed:
            print(f"\nTest {item.name} ❌ FAILED")
        else:
            print(f"\nTest {item.name} ✅ PASSED")

    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" and report.failed:
        active_page = item.funcargs.get("page_context") or item.funcargs.get("session_page_context")
        if active_page:
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = f"screenshots/{item.name}.png"
            active_page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to {screenshot_path}")

            allure.attach.file(
                str(screenshot_path),
                name=f"{item.name}_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
