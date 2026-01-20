import re

# patterns that indicate the next token is a secret
_SECRET_PATTERNS = [
    r'(password|passwd|pass|secret|token|api[_-]?key|auth|credential|private[_-]?key'
    r'|access[_-]?key|client[_-]?secret|db[_-]?pass|database[_-]?url'
    r'|connection[_-]?string)\s*[=:]\s*\S+',

    # AWS key format
    r'AKIA[0-9A-Z]{16}',
    # Generic hex secrets (32+ chars)
    r'[0-9a-fA-F]{32,}',
    # Bearer tokens
    r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
    # Base64-ish long strings after = or :
    r'(?<=[=\s])[A-Za-z0-9+/]{40,}={0,2}',
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _SECRET_PATTERNS]

def redact(text: str) -> str:
    for pattern in _COMPILED:
        text = pattern.sub(lambda m: _mask(m.group()), text)
    return text

def _mask(value: str) -> str:
    # keep first 4 chars visible, mask the rest
    if len(value) <= 8:
        return '[REDACTED]'
    return value[:4] + '[REDACTED]'
