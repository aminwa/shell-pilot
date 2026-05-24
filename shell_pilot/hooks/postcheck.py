"""
Runs AFTER a command exits with a non-zero code.
argv[1] = exit code, argv[2...] = the command that failed.
"""
import sys

CONFIDENCE_LOCAL_THRESHOLD = 0.7

def main():
    if len(sys.argv) < 3:
        sys.exit(0)

    exit_code = sys.argv[1]
    command   = " ".join(sys.argv[2:]).strip()

    if not command:
        sys.exit(0)

    from shell_pilot.config import load
    cfg = load()

    if not cfg["general"]["enabled"]:
        sys.exit(0)

    from shell_pilot import cache as _cache
    _cache.log_failure(command, exit_code)

    # ── Step 1: Typo suggestion (always before explanation) ───────
    suggestion = _get_suggestion(command, exit_code, cfg)
    if suggestion:
        print(f"\n❓ shell-pilot: Did you mean: {suggestion}",
              file=sys.stderr)

    # ── Step 2: Error explanation ─────────────────────────────────
    from shell_pilot import cache
    cached = cache.get(command, exit_code)
    if cached:
        print(f"💡 shell-pilot [cached]: {cached}", file=sys.stderr)
        sys.exit(0)

    if cfg["ai"]["enabled"]:
        from shell_pilot.ai.client import explain_error
        explanation = explain_error(command, exit_code)
        if explanation:
            cache.set(command, exit_code, explanation)
            print(f"💡 shell-pilot: {explanation}", file=sys.stderr)
            sys.exit(0)

    # ── Fallback ──────────────────────────────────────────────────
    if not suggestion:
        print(
            f"\n💡 shell-pilot: exit {exit_code} - "
            "enable AI explanations: shell-pilot config",
            file=sys.stderr
        )
    sys.exit(0)

def _get_suggestion(command: str, exit_code: str, cfg: dict) -> str | None:
    # Only attempt suggestions for "command not found" (exit 127)
    # or any non-zero exit when base command is unknown
    from shell_pilot.analyzers.suggest import get_suggestion
    corrected, confidence = get_suggestion(command)

    if corrected and confidence >= CONFIDENCE_LOCAL_THRESHOLD:
        return corrected  # confident local match

    if corrected and confidence < CONFIDENCE_LOCAL_THRESHOLD:
        # low confidence - try AI if enabled
        if cfg["ai"]["enabled"]:
            from shell_pilot.ai.client import ai_suggest
            ai_result = ai_suggest(command)
            return ai_result or corrected  # fall back to local guess

    return corrected  # None if no match at all

if __name__ == "__main__":
    main()
