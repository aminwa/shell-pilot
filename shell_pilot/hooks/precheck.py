"""
Runs BEFORE a command executes.
Called by the shell hook with the command string as argv[1].
Exit code 1 = block the command (user said no).
Exit code 0 = allow the command to proceed.
"""
import sys
import os

def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    command = " ".join(sys.argv[1:])

    # lazy import so the hook stays fast when no danger is found
    from shell_pilot.analyzers.danger import check, severity_emoji

    result = check(command)
    if result is None:
        sys.exit(0)

    # only prompt for medium and above
    if result.severity == "low":
        _print_warning(result, command)
        sys.exit(0)

    _print_warning(result, command)

    try:
        answer = input("Proceed anyway? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer == "y":
        sys.exit(0)
    else:
        print("  Blocked. Command did not run.")
        sys.exit(1)

def _print_warning(result, command):
    from shell_pilot.analyzers.danger import severity_emoji
    emoji = severity_emoji(result.severity)
    width = 60
    border = "─" * width
    print(f"\n{emoji}  shell-pilot  {border[:width - 16]}", file=sys.stderr)
    print(f"   Severity : {result.severity.upper()}", file=sys.stderr)
    print(f"   Warning  : {result.message}", file=sys.stderr)
    print(f"   Tip      : {result.suggestion}", file=sys.stderr)
    print(f"{'─' * width}", file=sys.stderr)

if __name__ == "__main__":
    main()
