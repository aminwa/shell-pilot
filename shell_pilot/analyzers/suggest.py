import os
import json
import time
from difflib import get_close_matches, SequenceMatcher
from pathlib import Path
from shell_pilot.config import CONFIG_DIR

_PATH_CACHE_FILE = CONFIG_DIR / "path_cache.json"
_PATH_CACHE_TTL  = 3600  # 1 hour

def _load_path_commands() -> list[str]:
    """Scan all directories on PATH for executable files."""
    commands: set[str] = set()
    for directory in os.environ.get("PATH", "").split(":"):
        p = Path(directory)
        if not p.is_dir():
            continue
        try:
            for f in p.iterdir():
                if f.is_file() and os.access(f, os.X_OK):
                    commands.add(f.name)
        except PermissionError:
            continue
    return sorted(commands)

def _get_path_commands() -> list[str]:
    """Return cached PATH commands, refreshing if stale."""
    CONFIG_DIR.mkdir(exist_ok=True)

    if _PATH_CACHE_FILE.exists():
        try:
            data = json.loads(_PATH_CACHE_FILE.read_text())
            if time.time() - data["ts"] < _PATH_CACHE_TTL:
                return data["commands"]
        except (json.JSONDecodeError, KeyError):
            pass

    commands = _load_path_commands()
    _PATH_CACHE_FILE.write_text(
        json.dumps({"ts": time.time(), "commands": commands})
    )
    return commands

def get_suggestion(failed_command: str) -> tuple[str | None, float]:
    """
    Returns (suggested_command, confidence) for a failed command.
    confidence is a float 0.0–1.0.
    Returns (None, 0.0) if no good match found.
    """
    parts = failed_command.strip().split()
    if not parts:
        return None, 0.0

    base     = parts[0]
    commands = _get_path_commands()

    # exact match means something else is wrong - not a typo
    if base in commands:
        return None, 0.0

    matches = get_close_matches(base, commands, n=1, cutoff=0.6)
    if not matches:
        return None, 0.0

    best       = matches[0]
    confidence = SequenceMatcher(None, base, best).ratio()

    # rebuild the full command with the corrected base
    corrected = " ".join([best] + parts[1:])
    return corrected, confidence
