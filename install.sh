#!/usr/bin/env bash
# shell-pilot one-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/aw-labs/shell-pilot/main/install.sh | bash

set -euo pipefail

REPO="https://github.com/aw-labs/shell-pilot"
MIN_PYTHON="3.10"

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

info()    { echo -e "${CYAN}▶ $*${NC}"; }
success() { echo -e "${GREEN}✓ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠ $*${NC}"; }
die()     { echo -e "${RED}✗ $*${NC}" >&2; exit 1; }

# ── Python check ─────────────────────────────────────────────────────
find_python() {
    for py in python3.13 python3.12 python3.11 python3.10 python3 python; do
        if command -v "$py" &>/dev/null; then
            ver=$("$py" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            major=${ver%%.*}; minor=${ver##*.}
            if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
                echo "$py"; return
            fi
        fi
    done
    return 1
}

info "Checking Python..."
PY=$(find_python) || die "Python ${MIN_PYTHON}+ is required. Install from https://python.org"
success "Found $($PY --version)"

# ── pip check ────────────────────────────────────────────────────────
info "Checking pip..."
$PY -m pip --version &>/dev/null || die "pip not found. Run: $PY -m ensurepip --upgrade"
success "pip OK"

# ── Install shell-pilot ──────────────────────────────────────────────
info "Installing shell-pilot..."
$PY -m pip install --quiet --upgrade shell-pilot 2>&1 | tail -1 \
    || { warn "PyPI install failed - trying from source..."; install_from_source; }

success "shell-pilot installed"

# ── Run built-in install (adds shell hooks) ──────────────────────────
info "Adding shell hooks..."
shell_pilot_cmd=$(command -v shell-pilot 2>/dev/null || echo "$PY -m shell_pilot.cli")
$shell_pilot_cmd install

echo ""
success "shell-pilot is ready!"
echo -e "  ${CYAN}Run:${NC} source ~/.zshrc   (or open a new terminal)"
echo -e "  ${CYAN}Try:${NC} shell-pilot status"
echo -e "  ${CYAN}Try:${NC} shell-pilot check \"rm -rf /\""
echo -e "  ${CYAN}Try:${NC} shell-pilot stats"
echo ""

install_from_source() {
    command -v git &>/dev/null || die "git is required for source install"
    TMP=$(mktemp -d)
    trap 'rm -rf "$TMP"' EXIT
    git clone --depth=1 --quiet "$REPO" "$TMP/shell-pilot"
    $PY -m pip install --quiet -e "$TMP/shell-pilot"
}
