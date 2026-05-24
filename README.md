<div align="center">

# shell-pilot

**Agentic AI assistant living inside your terminal.**

[![PyPI](https://img.shields.io/pypi/v/shell-pilot?color=gold&label=PyPI)](https://pypi.org/project/shell-pilot/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-58%20passing-brightgreen)](#)

*Danger detection • typo correction • AI error explanations • usage analytics - all in one hook.*

![shell-pilot demo](shell_pilot_demo.gif)

</div>

---

```
$ rm -rf /var/log/../../../etc

💀 CRITICAL  This will delete files across multiple directories
   Tip: Use an explicit path and double-check with ls first

Block this command? [y/N] _
```

```
$ gitt commit -m "fix"
zsh: command not found: gitt
❓ shell-pilot: Did you mean: git commit -m "fix"
```

```
$ pip intall requests
ERROR: unknown command "intall" - maybe you meant "install"
💡 shell-pilot: pip uses 'install', not 'intall'. Run: pip install requests
```

---

## What it does

shell-pilot hooks into your shell and watches every command, silently and locally.

| Feature | How it works |
|---------|-------------|
| **Danger detection** | 14 regex rules catch `rm -rf`, force-pushes, `DROP TABLE`, `chmod 777`, `dd` disk wipes, fork bombs and more - **no API call, instant** |
| **Typo correction** | Fuzzy-matches your mistyped command against every executable on your `$PATH` - **100% local, offline** |
| **AI error explanations** | When a command fails, asks Claude Haiku for a one-sentence fix - **only triggered on failure, secrets redacted first** |
| **Usage analytics** | `shell-pilot stats` reads your history locally and shows top commands + alias suggestions |

---

## Install

### One-line installer (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/aw-labs/shell-pilot/main/install.sh | bash
```

### Manual install via pip

```bash
pip install shell-pilot
shell-pilot install   # adds hooks to .zshrc or .bashrc
source ~/.zshrc       # reload (or open a new terminal)
```

### From source

```bash
git clone https://github.com/aw-labs/shell-pilot.git
cd shell-pilot
pip install -e .
shell-pilot install
source ~/.zshrc
```

---

## Quick start

```bash
# Check your setup
shell-pilot status

# Test danger detection without running anything
shell-pilot check "rm -rf ~"
shell-pilot check "git push --force origin main"

# View your terminal analytics
shell-pilot stats

# Edit config
shell-pilot config

# Remove hooks cleanly
shell-pilot uninstall
```

---

## Configuration

Config lives at `~/.shell-pilot/config.toml`. Run `shell-pilot config` to open it in `$EDITOR`.

```toml
[general]
enabled = true
shell   = "zsh"          # or "bash"

[danger]
enabled      = true
min_severity = "medium"  # "low" | "medium" | "high" | "critical"

[ai]
enabled     = true
model       = "claude-haiku-4-5-20251001"
api_key_env = "ANTHROPIC_API_KEY"

[privacy]
redact_secrets = true
```

### Setting your API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # add to .zshrc/.bashrc to persist
```

AI explanations are **optional**. Danger detection and typo correction work with no API key at all.

---

## Privacy

shell-pilot is designed around a **local-first, minimal-disclosure** principle.

| Data | Sent to API? |
|------|-------------|
| Commands that are flagged as dangerous | ✗ Never - fully local |
| Commands that succeed (exit 0) | ✗ Never |
| Typo corrections | ✗ Never - `difflib` against your local `$PATH` |
| Shell history (`shell-pilot stats`) | ✗ Never - processed in-process |
| Failed commands (exit ≠ 0, AI enabled) | ✓ Yes - after secret redaction |

**Secret redaction** strips passwords, API keys, AWS credentials, bearer tokens, and hex secrets from the command string before it is sent. You can audit the patterns in [`shell_pilot/analyzers/redact.py`](shell_pilot/analyzers/redact.py).

You can also set `[ai] enabled = false` in the config and shell-pilot will **never make any network call, ever**.

---

## Danger rules

| Severity | Examples |
|----------|---------|
| 💀 Critical | `rm -rf /`, `dd if=... of=/dev/disk0`, fork bomb `:(){ :|:& }` |
| 🔴 High | `git push --force origin main`, `DROP TABLE`, `chmod 777 /` |
| 🟠 Medium | `pkill -9`, `kill 1`, `sudo chmod -R 777` |
| 🟡 Low | `git push --force` (non-protected branch) |

Run `shell-pilot check "<command>"` to test any command interactively.

---

## Stats demo

```
shell-pilot stats

Analysed 1,570 commands from shell history (all processing is local)

╭──────────────────────────────────────────────────────╮
│                  Top 20 Commands                     │
├────┬────────────┬───────┬──────────────────────────  │
│  # │ Command    │ Count │                            │
├────┼────────────┼───────┼──────────────────────────  │
│  1 │ git        │   269 │ █████████████████████████  │
│  2 │ cd         │   193 │ ██████████████████         │
│  3 │ python3    │    80 │ ████████                   │
│  4 │ pip        │    55 │ █████                      │
│  5 │ ls         │    49 │ █████                      │
╰────┴────────────┴───────┴──────────────────────────╯

╭─────────────────────────────────────────────────────────────────╮
│          Alias Suggestions  (commands you type often)           │
├─────────┬──────────────────────────────┬───────┬───────────────  │
│ Alias   │ Command                      │ Times │ Add to .zshrc  │
├─────────┼──────────────────────────────┼───────┼───────────────  │
│ gpom    │ git push -u origin main      │    26 │ alias gpom=... │
│ pir     │ pip install -r requirements  │    16 │ alias pir=...  │
╰─────────┴──────────────────────────────┴───────┴───────────────╯
```

---

## Project structure

```
shell_pilot/
├── analyzers/
│   ├── danger.py      # 14 regex danger rules
│   ├── suggest.py     # typo correction via difflib + PATH scan
│   └── redact.py      # secret redaction before API calls
├── hooks/
│   ├── precheck.py    # runs BEFORE command (danger detection)
│   └── postcheck.py   # runs AFTER failure (suggestion + AI)
├── ai/
│   ├── client.py      # Claude Haiku API wrapper
│   └── prompts.py     # system prompts
├── history.py         # shell history parsing + analytics
├── cache.py           # SQLite cache (7-day TTL)
├── config.py          # TOML config loader
└── cli.py             # Click CLI (install/uninstall/status/check/stats)
tests/
├── test_danger.py     # 33 tests
├── test_cache.py      # 5 tests
├── test_redact.py     # 6 tests
├── test_suggest.py    # 6 tests
└── test_history.py    # 8 tests
```

---

## Contributing

1. Fork the repo and create a branch: `git checkout -b feat/my-feature`
2. Install dev dependencies: `pip install -e ".[dev]"` *(or just `pip install -e .` + `pip install pytest`)*
3. Run the test suite: `pytest tests/ -v`
4. All 58 tests must pass before opening a PR
5. Open a pull request - describe *what* and *why*

**Ideas welcome:** more danger rules, new shell support (fish), Windows/WSL compatibility, a `--dry-run` mode, config validation, Homebrew formula.

---

## Built by

**AW Labs** - tools that make developers faster.

> "Privacy-first, local-first, fast."

---

## License

MIT © AW Labs
