import re
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DangerResult:
    is_dangerous: bool
    severity: str          # "low" | "medium" | "high" | "critical"
    message: str
    suggestion: str

RULES = [
    {
        "pattern": r"\brm\s+(-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*|-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*)\s+[/~.]",
        "severity": "critical",
        "message": "Recursive force delete on root, home, or current directory.",
        "suggestion": "Double-check the path. Consider moving to trash instead.",
    },
    {
        "pattern": r"\brm\s+(-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*|-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*)\s+\*",
        "severity": "critical",
        "message": "Recursive force delete on wildcard - will delete everything here.",
        "suggestion": "Run ls first to see what would be deleted.",
    },
    {
        "pattern": r"\bgit\s+push\s+.*(-f|--force|--force-with-lease)\s.*(main|master|prod|production|release)",
        "severity": "high",
        "message": "Force push to a protected branch.",
        "suggestion": "Are you sure? This rewrites shared history. Consider --force-with-lease if you haven't already.",
    },
    {
        "pattern": r"\bgit\s+push\s+.*(-f|--force)\b",
        "severity": "medium",
        "message": "Force push detected.",
        "suggestion": "Check which branch you're pushing to before proceeding.",
    },
    {
        "pattern": r"\bgit\s+reset\s+--hard\b",
        "severity": "high",
        "message": "Hard reset will permanently discard all uncommitted changes.",
        "suggestion": "Run git stash first if you want to keep your changes.",
    },
    {
        "pattern": r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b",
        "severity": "critical",
        "message": "Destructive SQL operation - this cannot be undone.",
        "suggestion": "Take a backup first. Are you connected to the right database?",
    },
    {
        "pattern": r"\bTRUNCATE\s+TABLE\b",
        "severity": "high",
        "message": "TRUNCATE will delete all rows in the table permanently.",
        "suggestion": "Take a backup or use DELETE with a WHERE clause if partial.",
    },
    {
        "pattern": r"\bchmod\s+(-R\s+)?777\b",
        "severity": "high",
        "message": "chmod 777 gives everyone full read/write/execute - a serious security risk.",
        "suggestion": "Use the minimum permissions needed, e.g. 755 for dirs, 644 for files.",
    },
    {
        "pattern": r">\s*/etc/(?!hosts\.d|resolver)[a-zA-Z]",
        "severity": "critical",
        "message": "Overwriting a system config file.",
        "suggestion": "Back up the file first: sudo cp /etc/filename /etc/filename.bak",
    },
    {
        "pattern": r"\bdd\s+.*of=/dev/(sd[a-z]|nvme|disk[0-9]?)\b",
        "severity": "critical",
        "message": "dd writing directly to a disk device - will overwrite the entire disk.",
        "suggestion": "Triple-check the of= target. A wrong device letter destroys data.",
    },
    {
        "pattern": r":\s*\(\s*\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",
        "severity": "critical",
        "message": "Fork bomb detected - this will crash your system.",
        "suggestion": "Do not run this.",
    },
    {
        "pattern": r"\bkill\s+(-9\s+)?1\b",
        "severity": "critical",
        "message": "Killing PID 1 (init/launchd) will crash the system immediately.",
        "suggestion": "Do not run this.",
    },
    {
        "pattern": r"\bnpm\s+publish\b",
        "severity": "low",
        "message": "Publishing a package to npm - this is public and permanent.",
        "suggestion": "Make sure you're publishing the right version: check package.json.",
    },
    {
        "pattern": r"\bgit\s+branch\s+(-D|--delete\s+-f)\b",
        "severity": "low",
        "message": "Force deleting a git branch.",
        "suggestion": "Make sure this branch has been merged or is no longer needed.",
    },
]

def check(command: str) -> Optional[DangerResult]:
    cmd = command.strip()
    if not cmd or cmd.startswith('#'):
        return None

    for rule in RULES:
        if re.search(rule["pattern"], cmd, re.IGNORECASE):
            return DangerResult(
                is_dangerous=True,
                severity=rule["severity"],
                message=rule["message"],
                suggestion=rule["suggestion"],
            )
    return None

def severity_emoji(severity: str) -> str:
    return {"low": "⚠️", "medium": "🔶", "high": "🔴", "critical": "💀"}.get(severity, "⚠️")
