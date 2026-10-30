from pathlib import Path

import allure
import pytest
from playwright.sync_api import Playwright, Browser, Page, BrowserContext

from src.utils.file_utils import ensure_dir
from src.utils.logger import get_logger

logger = get_logger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Target environment for team configs (e.g. dev, staging)",
    )


@pytest.fixture(scope="session")
def browser_instance(playwright: Playwright) -> Browser:
    browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page_context(request, browser_instance: Browser) -> Page:
    logger.info("Setting up a new browser context for the test... %s", request.node.name)

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
        trace_dir = ensure_dir("test-output")
        trace_path = trace_dir / f"{request.node.name}_trace.zip"
        context.tracing.stop(path=str(trace_path))
    else:
        context.tracing.stop()

    context.close()

    if failed:
        allure.attach.file(str(trace_path), name=f"{request.node.name}_trace", extension="zip")

    if failed and video:
        video_path = Path(video.path())
        video_dir = ensure_dir("videos")
        new_video_path = video_dir / f"{request.node.name}.webm"
        video.save_as(new_video_path)
        if video_path != new_video_path and video_path.exists():
            video_path.unlink()
        logger.info("Video saved to %s", new_video_path)
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
    trace_dir = ensure_dir("test-output")
    context.tracing.stop(path=str(trace_dir / "session_trace.zip"))
    context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        if report.failed:
            logger.error("Test %s ❌ FAILED", item.name)
        else:
            logger.info("Test %s ✅ PASSED", item.name)

    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" and report.failed:
        active_page = item.funcargs.get("page_context") or item.funcargs.get("session_page_context")
        if active_page:
            screenshot_dir = ensure_dir("screenshots")
            screenshot_path = screenshot_dir / f"{item.name}.png"
            active_page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info("Screenshot saved to %s", screenshot_path)

            allure.attach.file(
                str(screenshot_path),
                name=f"{item.name}_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
