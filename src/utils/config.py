import os
from pathlib import Path
from typing import Any, Dict

import yaml

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEFAULT_ENV = "dev"


def load_team_config(team: str, env: str = DEFAULT_ENV) -> Dict[str, Any]:
    """Load a team's config for a given environment from ``src/config/<team>_config.yml``.

    Each YAML file is keyed by environment name (e.g. ``dev``, ``staging``).
    Individual values can be overridden via an environment variable named
    after the uppercased YAML key, e.g. ``SAUCEDEMO_BASE_URL=...`` overrides
    ``saucedemo_base_url`` — handy for an ad hoc run without editing the YAML.
    """
    config_path = _CONFIG_DIR / f"{team}_config.yml"
    with open(config_path, "r") as config_file:
        all_envs = yaml.safe_load(config_file) or {}

    config = dict(all_envs.get(env, {}))

    for key, value in config.items():
        config[key] = os.environ.get(key.upper(), value)

    return config
