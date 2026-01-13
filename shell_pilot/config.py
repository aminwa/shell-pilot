import os
import tomllib
from pathlib import Path
from typing import Any

CONFIG_DIR  = Path.home() / ".shell-pilot"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULTS: dict[str, Any] = {
    "general": {
        "enabled": True,
        "shell": os.environ.get("SHELL", "zsh").split("/")[-1],
    },
    "danger": {
        "enabled": True,
        "min_severity": "low",   # low | medium | high | critical
    },
    "ai": {
        "enabled": False,        # turned on in Phase 2
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "privacy": {
        "send_stderr": True,
        "send_command": True,
        "never_send": ["password", "passwd", "secret", "token", "key",
                       "api_key", "auth", "credential", "private"],
    },
}

def load() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULTS
    with open(CONFIG_FILE, "rb") as f:
        user = tomllib.load(f)
    merged = dict(DEFAULTS)
    for section, values in user.items():
        if section in merged and isinstance(merged[section], dict):
            merged[section] = {**merged[section], **values}
        else:
            merged[section] = values
    return merged

def ensure_config_dir():
    CONFIG_DIR.mkdir(exist_ok=True)

def write_default_config():
    ensure_config_dir()
    if CONFIG_FILE.exists():
        return
    content = """\
[general]
enabled = true

[danger]
enabled = true
min_severity = "low"

[ai]
enabled = false
provider = "anthropic"
model = "claude-haiku-4-5-20251001"
api_key_env = "ANTHROPIC_API_KEY"

[privacy]
send_stderr = true
send_command = true
never_send = ["password", "passwd", "secret", "token", "key", "api_key", "auth", "credential", "private"]
"""
    CONFIG_FILE.write_text(content)
