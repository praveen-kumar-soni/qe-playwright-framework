# QE Playwright Framework

A Python test automation framework built on [Playwright](https://playwright.dev/python/) and [pytest](https://docs.pytest.org/), using the Page Object Model (POM). It ships with automatic screenshot/video/trace capture on failure and [Allure](https://docs.qameta.io/allure/) reporting.

## Features

- **Page Object Model** — reusable, maintainable page classes under [src/pages](./src/pages), organized per team/application, built on a shared [BasePage](./src/base/base_page.py).
- **Multi-team structure** — each team/application owns its own page objects ([src/pages/\<team\>](./src/pages)), tests ([tests/\<team\>](./tests)), and YAML config ([src/config/\<team\>_config.yml](./src/config)), while core framework code (`BasePage`, fixtures, utilities) stays shared.
- **Pytest fixtures** ([conftest.py](./conftest.py)) for per-test (`page_context`) and per-session (`session_page_context`) browser contexts.
- **Automatic failure artifacts** — screenshots, video recordings, and Playwright traces are captured and attached to the Allure report whenever a test fails.
- **Allure reporting** for rich, interactive HTML test reports, plus a self-contained `pytest-html` report.
- **Custom markers** (e.g. `sanity`) to group and selectively run tests.
- **Shared utilities** ([src/utils](./src/utils)) — directory helpers, per-team YAML config loading via `--env`-selectable environments (with per-key env-var overrides), and structured logging, used by `conftest.py` and page objects.

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
│   ├── config/                # Per-team YAML config (e.g. ecommerce_config.yml, search_config.yml)
│   ├── pages/
│   │   ├── ecommerce/          # Page objects for the "ecommerce" team's app (SauceDemo)
│   │   └── search/              # Page objects for the "search" team's app (DuckDuckGo)
│   └── utils/                 # Shared helpers (file_utils, config loader, logger)
├── tests/                     # Test files only — organized to mirror src/pages by team
│   ├── ecommerce/
│   │   └── conftest.py        # team_config fixture (reads --env, loads ecommerce_config.yml)
│   └── search/
│       └── conftest.py        # team_config fixture (reads --env, loads search_config.yml)
├── screenshots/               # Failure screenshots (auto-generated, see conftest.py)
├── videos/                    # Videos kept per --video-mode (auto-generated, see conftest.py)
├── allure-results/             # Raw Allure results (auto-generated)
├── test-output/                # Failure traces (auto-generated, see conftest.py)
└── logs/                       # Per-run log files (auto-generated)
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

Run a specific team's tests:

```bash
poetry run pytest tests/ecommerce/
```

Run a specific file:

```bash
poetry run pytest tests/ecommerce/test_saucedemo_login.py
```

Run with a specific environment (default is `dev`):

```bash
poetry run pytest --env=staging
```

Control when videos are kept with `--video-mode` (default `on-failure`; see table below):

```bash
poetry run pytest --video-mode=always
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

Every run produces (HTML/Allure reporting configured in [pytest.ini](./pytest.ini); failure artifacts and `--video-mode` handled in [conftest.py](./conftest.py)):

| Artifact | Location | Notes |
|---|---|---|
| Self-contained HTML report | `report.html` | Generated via `pytest-html` |
| Allure results | `allure-results/` | Raw results; generated automatically by `--alluredir=allure-results` (set in [pytest.ini](./pytest.ini)); cleaned at the start of each run via `--clean-alluredir` |
| Videos | `videos/` | Kept based on `--video-mode` (default `on-failure`: only failed tests; `always`: every test; `never`: recording disabled) |
| Screenshots | `screenshots/` | Captured only on failure |
| Traces | `test-output/*_trace.zip` | Captured only on failure; see command below |
| Log file | `logs/test_run_<timestamp>.log` | One file per `pytest` invocation, mirrors console log output |

To view the Allure HTML report:

```bash
allure serve allure-results
```

> If the browser tab fails to load (e.g. `This site can't be reached` at a LAN IP like `http://192.168.x.x:PORT/`), Allure picked your machine's network hostname instead of `localhost`. Force it explicitly:
> ```bash
> allure serve allure-results -h localhost
> ```

To inspect a trace file (opens the interactive [Playwright Trace Viewer](https://playwright.dev/python/docs/trace-viewer)):

```bash
poetry run playwright show-trace test-output/<test_name>_trace.zip
```

## Writing Tests

1. **Add a new team** (if needed): create `src/pages/<team>/`, `tests/<team>/` (with its own `conftest.py` defining a `team_config` fixture), and `src/config/<team>_config.yml`.
2. **Add a page object** under `src/pages/<team>/`, extending [BasePage](./src/base/base_page.py) and exposing locators plus user-facing actions (e.g. `login`, `search`). Keep page objects config-agnostic — take the base URL as a parameter (e.g. `open(base_url: str)`) rather than loading config internally. Prefer Playwright's semantic locators (`page.get_by_role`, `get_by_label`, `get_by_placeholder`, etc.) over raw CSS/XPath selectors where a meaningful accessible role/name exists.
3. **Add a test** under `tests/<team>/` using the `page_context` (function-scoped) or `session_page_context` (session-scoped) fixture to obtain a `Page`, plus the team's `team_config` fixture for base URLs/settings.
4. **Tag the test** with an existing marker (e.g. `@pytest.mark.sanity`) or register a new one in [pytest.ini](./pytest.ini).
5. Use Playwright's `expect` assertions for auto-retrying, web-first assertions instead of hard sleeps.

Example:

```python
import pytest
from playwright.sync_api import Page, expect

from src.pages.ecommerce.saucedemo_login_page import SauceDemoLoginPage


@pytest.mark.sanity
def test_saucedemo_login_with_credentials_from_footer(page_context: Page, team_config):
    login_page = SauceDemoLoginPage(page_context)
    login_page.open(team_config["saucedemo_base_url"])

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

### Utilities reference

[src/utils](./src/utils) provides small, focused helpers shared across the suite:

| Module | Provides | Notes |
|---|---|---|
| [file_utils.py](./src/utils/file_utils.py) | `ensure_dir(path)` | Creates a directory (and parents) if missing, returns a `Path` |
| [config.py](./src/utils/config.py) | `load_team_config(team, env="dev")` | Loads the `env` block from `src/config/<team>_config.yml`; individual values can be overridden via an env var named after the uppercased YAML key, e.g. `SAUCEDEMO_BASE_URL=https://example.com poetry run pytest tests/ecommerce/` |
| [logger.py](./src/utils/logger.py) | `get_logger(name)` | Structured logging (timestamp/level) to both the console and `logs/test_run_<timestamp>.log` — use instead of `print()` in fixtures/tests |

### Team configuration

Each team's config lives in its own YAML file under [src/config](./src/config), keyed by environment, e.g. [ecommerce_config.yml](./src/config/ecommerce_config.yml):

```yaml
dev:
  saucedemo_base_url: "https://www.saucedemo.com/"
staging:
  saucedemo_base_url: "https://staging.saucedemo.com/"
```

Select the active environment with `--env` (default `dev`): `poetry run pytest --env=staging`.

Page objects stay config-agnostic — they don't load config themselves. Each team's `tests/<team>/conftest.py` defines a `team_config` fixture that reads `--env` and calls `load_team_config("<team>", env=...)`; tests then pass the needed value into the page object, e.g. `login_page.open(team_config["saucedemo_base_url"])`. Adding a new team only means adding its own `src/config/<team>_config.yml` and `tests/<team>/conftest.py` — no shared files need to change.
