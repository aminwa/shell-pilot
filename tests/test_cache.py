import time
import pytest
from shell_pilot import cache

def test_set_and_get():
    cache.set("npm install", "1", "npm not found - install Node.js first")
    result = cache.get("npm install", "1")
    assert result == "npm not found - install Node.js first"

def test_miss_returns_none():
    result = cache.get("this_command_was_never_cached_xyzabc", "99")
    assert result is None

def test_different_exit_codes_are_separate():
    cache.set("python3 app.py", "1", "explanation for exit 1")
    cache.set("python3 app.py", "2", "explanation for exit 2")
    assert cache.get("python3 app.py", "1") == "explanation for exit 1"
    assert cache.get("python3 app.py", "2") == "explanation for exit 2"

def test_overwrite_updates_value():
    cache.set("docker build .", "1", "old explanation")
    cache.set("docker build .", "1", "new explanation")
    assert cache.get("docker build .", "1") == "new explanation"

def test_clear_removes_all():
    cache.set("cmd_a", "1", "explanation a")
    cache.set("cmd_b", "1", "explanation b")
    count = cache.clear()
    assert count >= 2
    assert cache.get("cmd_a", "1") is None
