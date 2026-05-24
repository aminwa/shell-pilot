import sys
import os
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from shell_pilot import __version__
from shell_pilot.config import load, write_default_config, CONFIG_FILE, CONFIG_DIR

console = Console()

SHELL_HOOK_ZSH = """\

# ── shell-pilot ────────────────────────────────────────────────────
_sp_preexec() {
    python3 -m shell_pilot.hooks.precheck "$1" || return 1
}
_sp_precmd() {
    local _sp_code=$?
    if [ $_sp_code -ne 0 ]; then
        python3 -m shell_pilot.hooks.postcheck "$_sp_code" "$history[1]" 2>/dev/null
    fi
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec _sp_preexec
add-zsh-hook precmd  _sp_precmd
# ───────────────────────────────────────────────────────────────────
"""

SHELL_HOOK_BASH = """\

# ── shell-pilot ────────────────────────────────────────────────────
_sp_last_cmd=""
trap '_sp_last_cmd=$BASH_COMMAND' DEBUG
_sp_preexec() {
    python3 -m shell_pilot.hooks.precheck "$_sp_last_cmd" || return 1
}
_sp_precmd() {
    local _sp_code=$?
    if [ $_sp_code -ne 0 ] && [ -n "$_sp_last_cmd" ]; then
        python3 -m shell_pilot.hooks.postcheck "$_sp_code" "$_sp_last_cmd" 2>/dev/null
    fi
}
PROMPT_COMMAND="_sp_precmd${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
# ───────────────────────────────────────────────────────────────────
"""

@click.group()
@click.version_option(__version__, prog_name="shell-pilot")
def cli():
    """shell-pilot - agentic AI terminal assistant."""
    pass

@cli.command()
def install():
    """Add shell-pilot hooks to your .zshrc or .bashrc."""
    write_default_config()
    cfg = load()
    shell = cfg["general"]["shell"]

    if shell == "zsh":
        rc_file = Path.home() / ".zshrc"
        hook    = SHELL_HOOK_ZSH
    else:
        rc_file = Path.home() / ".bashrc"
        hook    = SHELL_HOOK_BASH

    content = rc_file.read_text() if rc_file.exists() else ""

    if "shell-pilot" in content:
        console.print("[yellow]shell-pilot hooks already present in "
                      f"{rc_file.name}.[/yellow]")
        console.print("Run [bold]source ~/" + rc_file.name +
                      "[/bold] to reload, or open a new terminal.")
        return

    with open(rc_file, "a") as f:
        f.write(hook)

    console.print(Panel.fit(
        f"[bold green]✓ shell-pilot installed![/bold green]\n\n"
        f"Hooks added to [cyan]{rc_file}[/cyan]\n\n"
        f"Run:  [bold]source {rc_file}[/bold]\n"
        f"Or open a new terminal window.",
        title="[bold]AW Labs · shell-pilot[/bold]",
        border_style="green",
    ))

@cli.command()
def uninstall():
    """Remove shell-pilot hooks from your shell config."""
    for rc in [Path.home() / ".zshrc", Path.home() / ".bashrc"]:
        if not rc.exists():
            continue
        lines = rc.read_text().splitlines(keepends=True)
        in_block = False
        cleaned  = []
        for line in lines:
            if "── shell-pilot ──" in line:
                in_block = True
            if not in_block:
                cleaned.append(line)
            if in_block and line.strip().startswith("# ──") and "shell-pilot" not in line:
                in_block = False
        rc.write_text("".join(cleaned))
        console.print(f"[green]Removed hooks from {rc}[/green]")

@cli.command()
def status():
    """Show current configuration and status."""
    cfg = load()
    t = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    t.add_column("Key",   style="bold cyan", width=22)
    t.add_column("Value", style="white")

    t.add_row("Version",          __version__)
    t.add_row("Config file",      str(CONFIG_FILE))
    t.add_row("Enabled",          str(cfg["general"]["enabled"]))
    t.add_row("Shell",            cfg["general"]["shell"])
    t.add_row("Danger detection", str(cfg["danger"]["enabled"]))
    t.add_row("Min severity",     cfg["danger"]["min_severity"])
    t.add_row("AI explanations",  str(cfg["ai"]["enabled"]))
    t.add_row("AI model",         cfg["ai"]["model"])

    api_key_env = cfg["ai"]["api_key_env"]
    key_set     = bool(os.environ.get(api_key_env))
    t.add_row("API key",          f"[green]set[/green]" if key_set
                                  else f"[red]not set[/red] (${api_key_env})")

    console.print(Panel(t, title="[bold]shell-pilot status[/bold]",
                        border_style="cyan"))

@cli.command()
def config():
    """Open the config file in $EDITOR."""
    write_default_config()
    editor = os.environ.get("EDITOR", "nano")
    safe = all(c.isalnum() or c in "/.\\-_ " for c in editor)
    if not safe:
        console.print("[red]Invalid $EDITOR value — set EDITOR to a valid editor path.[/red]")
        return
    subprocess.run([editor, str(CONFIG_FILE)])

@cli.command()
@click.argument("command", nargs=-1, required=True)
def check(command):
    """Check whether a command would be flagged (for testing)."""
    from shell_pilot.analyzers.danger import check as danger_check, severity_emoji
    cmd    = " ".join(command)
    result = danger_check(cmd)
    if result is None:
        console.print(f"[green]✓ Safe:[/green] {cmd}")
    else:
        emoji = severity_emoji(result.severity)
        console.print(f"{emoji} [bold]{result.severity.upper()}:[/bold] {result.message}")
        console.print(f"   [dim]Tip: {result.suggestion}[/dim]")

@cli.command()
def stats():
    """Show your terminal usage patterns and alias suggestions."""
    from shell_pilot.history import load_history, top_commands, alias_suggestions, failure_summary

    console.print("\n[bold cyan]shell-pilot · Terminal Stats[/bold cyan]\n")

    commands = load_history()

    if not commands:
        console.print("[yellow]No shell history found.[/yellow]")
        return

    console.print(f"[dim]Analysed {len(commands):,} commands from shell history "
                  f"(all processing is local)[/dim]\n")

    # ── Top commands ──────────────────────────────────────────────
    top = top_commands(commands, n=20)
    t1  = Table(
        title="Top 20 Commands",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=False,
    )
    t1.add_column("#",       style="dim",        width=4,  justify="right")
    t1.add_column("Command", style="bold white",  width=20)
    t1.add_column("Count",   style="bold green",  width=8,  justify="right")
    t1.add_column("",        width=30)

    max_count = top[0][1] if top else 1
    for i, (cmd, count) in enumerate(top, 1):
        bar_len = int((count / max_count) * 25)
        bar     = "█" * bar_len
        t1.add_row(str(i), cmd, str(count), f"[green]{bar}[/green]")
    console.print(t1)

    # ── Most common failures ──────────────────────────────────────
    failures = failure_summary(n=10)
    if failures:
        console.print()
        t_fail = Table(
            title="Most Common Failures",
            box=box.ROUNDED,
            border_style="red",
            show_lines=False,
        )
        t_fail.add_column("#",       style="dim",       width=4,  justify="right")
        t_fail.add_column("Command", style="bold white", width=40)
        t_fail.add_column("Times",   style="bold red",   width=8,  justify="right")
        for i, (cmd, count) in enumerate(failures, 1):
            t_fail.add_row(str(i), cmd, str(count))
        console.print(t_fail)

    # ── Alias suggestions ─────────────────────────────────────────
    suggestions = alias_suggestions(commands)
    if suggestions:
        console.print()
        t2 = Table(
            title="Alias Suggestions  (commands you type often)",
            box=box.ROUNDED,
            border_style="yellow",
        )
        t2.add_column("Alias",   style="bold yellow", width=10)
        t2.add_column("Command", style="white",        width=40)
        t2.add_column("Times",   style="green",        width=8, justify="right")
        t2.add_column("Add to .zshrc",  style="dim",  width=35)

        for alias, cmd, count in suggestions:
            t2.add_row(
                alias, cmd, str(count),
                f'alias {alias}="{cmd}"'
            )
        console.print(t2)
    else:
        console.print("\n[dim]Not enough repeated long commands for alias suggestions yet.[/dim]")

    # ── Cache stats ───────────────────────────────────────────────
    console.print()
    from shell_pilot.cache import DB_PATH
    import sqlite3
    if DB_PATH.exists():
        try:
            con  = sqlite3.connect(DB_PATH)
            cnt  = con.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            con.close()
            console.print(
                f"[dim]💾  {cnt} error explanation(s) cached locally "
                f"at {DB_PATH}[/dim]"
            )
        except Exception:
            pass

    console.print()

def main():
    cli()

if __name__ == "__main__":
    main()
