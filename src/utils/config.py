import os

# Base URLs for the applications under test, centralized here instead of being
# hardcoded in each page object. Override via environment variables when
# pointing tests at a different environment (e.g. staging), for example:
#   SAUCEDEMO_BASE_URL=https://staging.saucedemo.com pytest

SAUCEDEMO_BASE_URL = os.environ.get("SAUCEDEMO_BASE_URL", "https://www.saucedemo.com/")
DUCKDUCKGO_BASE_URL = os.environ.get("DUCKDUCKGO_BASE_URL", "https://duckduckgo.com")
