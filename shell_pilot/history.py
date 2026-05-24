import re
from collections import Counter
from pathlib import Path

# ── Parsers ───────────────────────────────────────────────────────────────────

def _parse_zsh(path: Path) -> list[str]:
    commands = []
    for line in path.read_text(errors="ignore").splitlines():
        # extended format:  ': 1234567890:0;command'
        m = re.match(r'^:\s*\d+:\d+;(.+)$', line)
        if m:
            commands.append(m.group(1).strip())
        elif line.strip() and not line.startswith(':'):
            commands.append(line.strip())
    return commands

def _parse_bash(path: Path) -> list[str]:
    commands = []
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            commands.append(line)
    return commands

def load_history() -> list[str]:
    """Load shell history from zsh and/or bash history files."""
    commands: list[str] = []
    home = Path.home()

    zsh_file  = home / ".zsh_history"
    bash_file = home / ".bash_history"

    if zsh_file.exists():
        commands.extend(_parse_zsh(zsh_file))
    if bash_file.exists():
        commands.extend(_parse_bash(bash_file))

    return commands

# ── Analysers ─────────────────────────────────────────────────────────────────

def top_commands(commands: list[str], n: int = 20) -> list[tuple[str, int]]:
    """Return the n most-used base commands with counts."""
    bases = []
    for cmd in commands:
        parts = cmd.strip().split()
        if parts:
            bases.append(parts[0])
    return Counter(bases).most_common(n)

def alias_suggestions(commands: list[str], min_count: int = 5,
                      min_words: int = 3) -> list[tuple[str, str, int]]:
    """
    Suggest aliases for long commands typed frequently.
    Returns list of (suggested_alias, full_command, count).
    """
    counter   = Counter(commands)
    blacklist = {"git", "cd", "ls", "echo", "cat", "grep", "sudo"}
    seen_aliases: set[str] = set()
    suggestions: list[tuple[str, str, int]] = []

    for cmd, count in counter.most_common(50):
        if count < min_count:
            break
        parts = cmd.split()
        if len(parts) < min_words:
            continue
        # build alias from initials of the words
        alias = "".join(p[0] for p in parts if p and p[0].isalpha())[:6]
        if len(alias) < 2 or alias in seen_aliases or alias in blacklist:
            continue
        seen_aliases.add(alias)
        suggestions.append((alias, cmd, count))
        if len(suggestions) >= 10:
            break

    return suggestions

def failure_summary(n: int = 10) -> list[tuple[str, int]]:
    """Return the n most commonly failed commands logged by postcheck."""
    try:
        from shell_pilot.cache import top_failures
        return top_failures(n)
    except Exception:
        return []
