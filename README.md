# QE Playwright Framework

A Python test automation framework built on [Playwright](https://playwright.dev/python/) and [pytest](https://docs.pytest.org/), using the Page Object Model (POM). It ships with automatic screenshot/video/trace capture on failure and [Allure](https://docs.qameta.io/allure/) reporting.

## Features

- **Page Object Model** — reusable, maintainable page classes under [src/pages](./src/pages), built on a shared [BasePage](./src/base/base_page.py).
- **Pytest fixtures** ([conftest.py](./conftest.py)) for per-test (`page_context`) and per-session (`session_page_context`) browser contexts.
- **Automatic failure artifacts** — screenshots, video recordings, and Playwright traces are captured and attached to the Allure report whenever a test fails.
- **Allure reporting** for rich, interactive HTML test reports, plus a self-contained `pytest-html` report.
- **Custom markers** (e.g. `sanity`) to group and selectively run tests.

## Project Structure

```
qe-playwright-framework/
├── conftest.py              # Shared pytest fixtures and hooks (browser/context setup, reporting)
├── pytest.ini               # Pytest configuration (markers, reporting add-opts)
├── pyproject.toml           # Poetry project/dependency config
├── poetry.lock              # Locked dependency versions
├── mcp.json                 # Playwright MCP server config (for AI-assisted browser automation tooling)
├── src/
│   ├── base/
│   │   └── base_page.py     # Base class all page objects inherit from
│   └── pages/                # Page Object classes (e.g. SauceDemoLoginPage, SearchPage)
├── tests/                    # Pytest test suites (test_*.py)
├── screenshots/               # Failure screenshots (auto-generated)
├── videos/                    # Failure videos (auto-generated)
├── allure-results/             # Raw Allure results (auto-generated)
└── test-output/                # Failure traces + pytest --output dir (auto-generated)
```

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- Node.js (optional) — only needed if you use the Playwright MCP server (`mcp.json`) for AI-assisted browser automation tooling

## Setup

1. **Install Poetry**, if not already installed:

   ```bash
   pipx install poetry      # or: brew install poetry (macOS)
   ```

2. **Install dependencies** (creates/uses a project-local virtualenv since `package-mode = false`):

   ```bash
   poetry install --no-root
   ```

3. **Install Playwright browsers**:

   ```bash
   poetry run playwright install --with-deps
   ```

4. **(Optional) Install Allure CLI**, to view the interactive HTML report locally:

   ```bash
   brew install allure   # macOS
   ```

## Running Tests

> Note: [conftest.py](./conftest.py) launches Chromium in **headed** mode (`headless=False`) by default, so running tests opens a visible browser window.

Run the full suite:

```bash
poetry run pytest
```

Run a specific file:

```bash
poetry run pytest tests/test_saucedemo_login.py
```

Run only tests tagged with a marker (e.g. `sanity`):

```bash
poetry run pytest -m sanity
```

Run tests in parallel (via `pytest-xdist`):

```bash
poetry run pytest -n auto
```

### Reports and Artifacts

Every run (configured in [pytest.ini](./pytest.ini)) produces:

| Artifact | Location | Notes |
|---|---|---|
| Self-contained HTML report | `report.html` | Generated via `pytest-html` |
| Allure results | `allure-results/` | Raw results; cleaned at the start of each run |
| Videos | `videos/` | Kept only for failed tests |
| Screenshots | `screenshots/` | Captured only on failure |
| Traces | `test-output/*_trace.zip` | Captured only on failure; see command below |

To view the Allure HTML report:

```bash
allure serve allure-results
```

To inspect a trace file (opens the interactive [Playwright Trace Viewer](https://playwright.dev/python/docs/trace-viewer)):

```bash
poetry run playwright show-trace test-output/<test_name>_trace.zip
```

## Writing Tests

1. **Add a page object** under [src/pages](./src/pages), extending [BasePage](./src/base/base_page.py) and exposing locators plus user-facing actions (e.g. `login`, `search`). Prefer Playwright's semantic locators (`page.get_by_role`, `get_by_label`, `get_by_placeholder`, etc.) over raw CSS/XPath selectors where a meaningful accessible role/name exists.
2. **Add a test** under [tests/](./tests) using the `page_context` (function-scoped) or `session_page_context` (session-scoped) fixture to obtain a `Page`.
3. **Tag the test** with an existing marker (e.g. `@pytest.mark.sanity`) or register a new one in [pytest.ini](./pytest.ini).
4. Use Playwright's `expect` assertions for auto-retrying, web-first assertions instead of hard sleeps.

Example:

```python
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
```

### BasePage reference

[BasePage](./src/base/base_page.py) provides reusable helpers that take a `Locator` built in your page object's `__init__`:

| Category | Methods |
|---|---|
| Navigation | `navigate`, `reload`, `go_back`, `go_forward`, `get_current_url`, `get_title`, `wait_for_url`, `wait_for_load_state` |
| Element interactions | `click`, `fill`, `wait_for_visible` (all wait for visibility first), `upload_file` |
| Utilities | `take_screenshot`, `execute_script` |

For actions not covered above (e.g. `hover`, `check`/`uncheck`, `select_option`), call the Playwright `Locator` method directly — there's no need to wrap a 1:1 pass-through.
