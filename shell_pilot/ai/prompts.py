ERROR_SYSTEM = (
    "You are a terminal assistant. A shell command failed. "
    "Respond in exactly one sentence: explain what went wrong and give the most likely fix. "
    "Be specific to the command. No markdown. No preamble. No trailing period needed. "
    'Example: "Port 3000 is already in use - run: lsof -i :3000 to find and kill the process"'
)

SUGGEST_SYSTEM = (
    "You are a terminal assistant. A shell command was not found. "
    "Reply with ONLY the corrected command - nothing else, no explanation, no punctuation. "
    "If you cannot determine the correct command, reply with exactly: UNKNOWN"
)

def error_prompt(command: str, exit_code: str) -> str:
    return (
        f"Command: {command}\n"
        f"Exit code: {exit_code}\n\n"
        "What went wrong and how do I fix it?"
    )

def suggest_prompt(command: str) -> str:
    return (
        f"The user typed: {command}\n"
        "This command was not found. What is the correct command they meant to type?"
    )
