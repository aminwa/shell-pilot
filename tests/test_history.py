from shell_pilot.history import top_commands, alias_suggestions, _parse_zsh, _parse_bash
from pathlib import Path
import tempfile

SAMPLE = [
    "git status", "git status", "git status",
    "git pull", "git pull",
    "git push origin main", "git push origin main", "git push origin main",
    "git push origin main", "git push origin main",
    "docker compose up -d", "docker compose up -d",
    "docker compose up -d", "docker compose up -d",
    "docker compose up -d", "docker compose up -d",
    "ls -la", "ls -la", "ls -la",
    "cd ..", "cd ..",
    "python3 manage.py runserver",
    "python3 manage.py runserver",
    "python3 manage.py runserver",
    "python3 manage.py runserver",
    "python3 manage.py runserver",
    "npm run dev", "npm run dev",
]

def test_top_commands_returns_correct_order():
    top = top_commands(SAMPLE, n=5)
    # git appears most as a base command
    assert top[0][0] == "git"

def test_top_commands_respects_n():
    top = top_commands(SAMPLE, n=3)
    assert len(top) <= 3

def test_top_commands_counts_are_correct():
    top = dict(top_commands(SAMPLE, n=20))
    assert top["git"] == 10   # status(3) + pull(2) + push(5)

def test_alias_suggestions_for_long_repeated_commands():
    suggestions = alias_suggestions(SAMPLE, min_count=5, min_words=3)
    cmds = [cmd for _, cmd, _ in suggestions]
    assert any("docker" in c or "git push" in c or "python3" in c
               for c in cmds)

def test_alias_suggestions_min_count_respected():
    suggestions = alias_suggestions(SAMPLE, min_count=99)
    assert suggestions == []

def test_parse_zsh_extended_format():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.zsh_history',
                                     delete=False) as f:
        f.write(": 1716000000:0;git status\n")
        f.write(": 1716000001:0;docker ps\n")
        path = Path(f.name)
    result = _parse_zsh(path)
    assert "git status" in result
    assert "docker ps" in result
    path.unlink()

def test_parse_bash_skips_timestamps():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bash_history',
                                     delete=False) as f:
        f.write("#1716000000\n")
        f.write("git log\n")
        f.write("ls -la\n")
        path = Path(f.name)
    result = _parse_bash(path)
    assert "git log" in result
    assert "ls -la" in result
    assert "#1716000000" not in result
    path.unlink()

def test_empty_history_returns_empty():
    assert top_commands([]) == []
    assert alias_suggestions([]) == []
