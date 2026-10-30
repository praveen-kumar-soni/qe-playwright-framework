import pytest

from src.utils.config import load_team_config


@pytest.fixture(scope="session")
def team_config(request):
    env = request.config.getoption("--env")
    return load_team_config("search", env=env)
