from shell_pilot.analyzers.suggest import get_suggestion

def test_git_typo():
    corrected, confidence = get_suggestion("gitt status")
    assert corrected is not None
    assert "git" in corrected
    assert confidence > 0.6

def test_python_typo():
    corrected, confidence = get_suggestion("pyhton3 app.py")
    assert corrected is not None
    assert "python" in corrected.lower()
    assert confidence > 0.6

def test_exact_command_returns_none():
    # git is a real command - not a typo
    corrected, confidence = get_suggestion("git status")
    assert corrected is None
    assert confidence == 0.0

def test_completely_unknown_returns_none():
    corrected, confidence = get_suggestion("xyzqwertynotacommand123")
    assert corrected is None
    assert confidence == 0.0

def test_args_preserved_in_suggestion():
    corrected, confidence = get_suggestion("gitt commit -m 'test'")
    assert corrected is not None
    # args should be preserved after the corrected base
    assert "-m" in corrected or "commit" in corrected

def test_empty_command_returns_none():
    corrected, confidence = get_suggestion("")
    assert corrected is None
    assert confidence == 0.0
