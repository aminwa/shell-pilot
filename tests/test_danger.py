import pytest
from shell_pilot.analyzers.danger import check

# ── Should be flagged ─────────────────────────────────────────────
@pytest.mark.parametrize("cmd", [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf .",
    "rm -rf *",
    "rm -fr /tmp",
    "git push --force origin main",
    "git push -f origin master",
    "git push --force origin production",
    "git reset --hard",
    "DROP TABLE users;",
    "DROP DATABASE mydb;",
    "TRUNCATE TABLE orders;",
    "chmod 777 /var/www",
    "chmod -R 777 .",
    "dd if=/dev/zero of=/dev/sda",
    "dd if=backup.img of=/dev/disk0",
    "kill 1",
    "kill -9 1",
])
def test_dangerous_commands_are_flagged(cmd):
    result = check(cmd)
    assert result is not None, f"Expected '{cmd}' to be flagged"
    assert result.is_dangerous

# ── Should NOT be flagged ─────────────────────────────────────────
@pytest.mark.parametrize("cmd", [
    "ls -la",
    "git status",
    "git push origin feature/my-branch",
    "git push origin main",             # no --force
    "echo hello world",
    "python3 manage.py migrate",
    "npm install",
    "docker ps",
    "cd /tmp && ls",
    "grep -r 'TODO' .",
    "rm -rf node_modules",              # no path match (not / ~ . *)
])
def test_safe_commands_are_not_flagged(cmd):
    result = check(cmd)
    assert result is None, f"Expected '{cmd}' to be safe but got: {result}"

# ── Severity levels ───────────────────────────────────────────────
def test_rm_rf_root_is_critical():
    assert check("rm -rf /").severity == "critical"

def test_force_push_main_is_high():
    r = check("git push --force origin main")
    assert r is not None
    assert r.severity == "high"

def test_chmod_777_is_high():
    assert check("chmod 777 /var/www").severity == "high"

def test_npm_publish_is_low():
    assert check("npm publish").severity == "low"
