from shell_pilot.analyzers.redact import redact

def test_redacts_password_flag():
    result = redact("db --password=supersecret123")
    assert "supersecret123" not in result
    assert "REDACTED" in result

def test_redacts_api_key():
    result = redact("export API_KEY=abc123xyz456abc123xyz456abc123xy")
    assert "abc123xyz456abc123xyz456abc123xy" not in result

def test_redacts_aws_key():
    result = redact("aws s3 ls --access-key AKIAIOSFODNN7EXAMPLE")
    assert "AKIAIOSFODNN7EXAMPLE" not in result

def test_redacts_bearer_token():
    result = redact("curl -H 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9'")
    assert "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9" not in result

def test_safe_commands_unchanged():
    cmd = "git status"
    assert redact(cmd) == cmd

def test_safe_commands_with_numbers_unchanged():
    cmd = "docker ps -a"
    assert redact(cmd) == cmd
