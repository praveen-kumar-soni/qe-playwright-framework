from pathlib import Path

import allure
import pytest
from playwright.sync_api import Playwright, Browser, Page, BrowserContext

from src.utils.file_utils import ensure_dir
from src.utils.logger import get_logger

logger = get_logger(__name__)

_session_video_failures: set[str] = set()


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Target environment for team configs (e.g. dev, staging)",
    )
    parser.addoption(
        "--video-mode",
        action="store",
        default="on-failure",
        choices=["on-failure", "always", "never"],
        help="When to keep captured videos: on-failure (default), always, or never (disables recording)",
    )


@pytest.fixture(scope="session")
def browser_instance(playwright: Playwright) -> Browser:
    browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page_context(request, browser_instance: Browser) -> Page:
    logger.info("Setting up a new browser context for the test... %s", request.node.name)

    video_mode = request.config.getoption("--video-mode")
    context_kwargs = {"ignore_https_errors": True}
    if video_mode != "never":
        context_kwargs["record_video_dir"] = "videos/"

    context: BrowserContext = browser_instance.new_context(**context_kwargs)
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

    if video:
        video_path = Path(video.path())
        if failed or video_mode == "always":
            video_dir = ensure_dir("videos")
            new_video_path = video_dir / f"{request.node.name}.webm"
            video.save_as(new_video_path)
            if video_path != new_video_path and video_path.exists():
                video_path.unlink()
            logger.info("Video saved to %s", new_video_path)
            allure.attach.file(str(new_video_path), name=f"{request.node.name}_video", attachment_type=allure.attachment_type.WEBM)
        elif video_path.exists():
            # Test passed and --video-mode is "on-failure" — discard the recording.
            video_path.unlink()


@pytest.fixture(scope="session")
def session_page_context(request, browser_instance: Browser) -> Page:
    video_mode = request.config.getoption("--video-mode")
    context_kwargs = {"ignore_https_errors": True}
    if video_mode != "never":
        context_kwargs["record_video_dir"] = "videos/"

    context: BrowserContext = browser_instance.new_context(**context_kwargs)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page: Page = context.new_page()
    yield page

    video = page.video
    trace_dir = ensure_dir("test-output")
    context.tracing.stop(path=str(trace_dir / "session_trace.zip"))
    context.close()

    if video:
        video_path = Path(video.path())
        if _session_video_failures or video_mode == "always":
            video_dir = ensure_dir("videos")
            new_video_path = video_dir / "session_recording.webm"
            video.save_as(new_video_path)
            if video_path != new_video_path and video_path.exists():
                video_path.unlink()
            logger.info(
                "Session video saved to %s (failed tests: %s)",
                new_video_path,
                sorted(_session_video_failures),
            )
        elif video_path.exists():
            # No failures among session_page_context tests and --video-mode
            # is "on-failure" — discard the recording.
            video_path.unlink()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        if report.failed:
            logger.error("Test %s ❌ FAILED", item.name)
            if "session_page_context" in item.funcargs:
                _session_video_failures.add(item.name)
        else:
            logger.info("Test %s ✅ PASSED", item.name)

    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" and report.failed:
        active_page = item.funcargs.get("page_context") or item.funcargs.get("session_page_context")
        if active_page:
            screenshot_dir = ensure_dir("screenshots")
            screenshot_path = screenshot_dir / f"{item.name}.png"
            try:
                active_page.screenshot(path=str(screenshot_path), full_page=True, timeout=5_000)
            except Exception as exc:
                logger.warning("Could not capture failure screenshot for %s: %s", item.name, exc)
            else:
                logger.info("Screenshot saved to %s", screenshot_path)

                allure.attach.file(
                    str(screenshot_path),
                    name=f"{item.name}_screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
