import json
import os
from pathlib import Path

from ctfr_reloaded.constants import CONFIG_DIR_NAME

DEFAULT_CONFIG = {
    "defaults": {
        "source": "all",
        "timeout": 30,
        "retries": 3,
        "threads": 5,
        "cache": True,
        "cache_ttl": 3600,
        "rate_limit": 1.0,
        "resolve": False,
        "alive": False,
        "no_wildcards": False,
        "score": True,
    },
    "exclude_patterns": [],
    "history_enabled": True,
    "history_db": "",
}


def default_config_path():
    return Path.home() / ".config" / CONFIG_DIR_NAME / "config.json"


def default_history_path():
    return Path.home() / ".cache" / CONFIG_DIR_NAME / "history.db"


def load_config(path=None):
    config_path = Path(path) if path else default_config_path()
    config = json.loads(json.dumps(DEFAULT_CONFIG))

    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as handle:
                user_config = json.load(handle)
            _deep_merge(config, user_config)
        except (OSError, ValueError):
            pass

    if not config.get("history_db"):
        config["history_db"] = str(default_history_path())

    return config


def _deep_merge(base, override):
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def apply_config_defaults(args, config):
    """Aplica defaults del config solo si el usuario no paso el flag explicitamente."""
    defaults = config.get("defaults", {})
    flag_map = {
        "source": "source",
        "timeout": "timeout",
        "retries": "retries",
        "threads": "threads",
        "cache": "cache",
        "cache_ttl": "cache_ttl",
        "rate_limit": "rate_limit",
        "resolve": "resolve",
        "alive": "alive",
        "no_wildcards": "no_wildcards",
        "score": "score",
    }
    for config_key, arg_attr in flag_map.items():
        if config_key not in defaults:
            continue
        if arg_attr not in args:
            continue
        if not args.get("_explicit", {}).get(arg_attr, False):
            args[arg_attr] = defaults[config_key]
    return args


def save_default_config(path=None):
    config_path = Path(path) if path else default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(DEFAULT_CONFIG, handle, indent=2)
            handle.write("\n")
    return config_path


def get_exclude_patterns(config):
    return [p.lower() for p in config.get("exclude_patterns", []) if p]
