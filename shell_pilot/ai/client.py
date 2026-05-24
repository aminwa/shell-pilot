import os
from shell_pilot.config import load
from shell_pilot.ai.prompts import ERROR_SYSTEM, SUGGEST_SYSTEM, error_prompt, suggest_prompt
from shell_pilot.analyzers.redact import redact

def _call(system: str, user: str, max_tokens: int = 120) -> str | None:
    cfg = load()
    if not cfg["ai"]["enabled"]:
        return None
    api_key = os.environ.get(cfg["ai"]["api_key_env"])
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=cfg["ai"]["model"],
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        return msg.content[0].text.strip()
    except ImportError:
        return None
    except Exception:
        return None

def explain_error(command: str, exit_code: str) -> str | None:
    return _call(ERROR_SYSTEM, error_prompt(redact(command), exit_code))

def ai_suggest(command: str) -> str | None:
    result = _call(SUGGEST_SYSTEM, suggest_prompt(command), max_tokens=40)
    if result and result.upper() != "UNKNOWN":
        return result
    return None
