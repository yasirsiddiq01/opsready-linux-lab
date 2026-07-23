from pathlib import Path

from opsready_lab.services.practice_terminal import (
    MAX_TERMINAL_RUNS,
    SUPPORTED_COMMANDS,
    create_terminal_state,
    execute_command,
    prompt_for_state,
    runs_remaining,
)


def run(state: dict, command: str, health: dict | None = None):
    return execute_command(state, command, health=health)


def test_supported_command_catalog_is_reviewed_and_unique() -> None:
    assert len(SUPPORTED_COMMANDS) == 25
    assert len(set(SUPPORTED_COMMANDS)) == 25
    assert {"pwd", "ls", "cd", "grep", "awk", "find", "df", "free", "ps", "uptime"}.issubset(SUPPORTED_COMMANDS)


def test_terminal_is_stateful_and_uses_only_virtual_paths() -> None:
    state = create_terminal_state()
    state, result = run(state, "cd projects")
    assert result.status == "success"
    assert state["cwd"] == "/home/student/projects"
    assert prompt_for_state(state) == "student@opsready:~/projects$"

    state, result = run(state, "cat readme.md")
    assert "Demo API" in result.output
    assert runs_remaining(state) == MAX_TERMINAL_RUNS - 2


def test_awk_and_grep_return_reviewed_virtual_content() -> None:
    state = create_terminal_state()
    state, awk_result = run(state, "awk -F: '{print $1, $7}' /etc/passwd")
    assert awk_result.status == "success"
    assert "student /bin/bash" in awk_result.output
    assert "root /bin/bash" in awk_result.output

    state, grep_result = run(state, "grep -in error /opt/app/app.log")
    assert grep_result.status == "success"
    assert "ERROR database timeout" in grep_result.output


def test_health_commands_follow_the_selected_simulation() -> None:
    state = create_terminal_state()
    health = {"disk": 96, "memory": 93, "cpu": 94, "load": 9.8, "io_wait": 4, "connections": 310}
    state, df_result = run(state, "df -h /", health)
    assert "96%" in df_result.output
    state, free_result = run(state, "free -m", health)
    assert "7619" in free_result.output
    state, ps_result = run(state, "ps aux", health)
    assert "appuser" in ps_result.output
    state, uptime_result = run(state, "uptime", health)
    assert "9.80" in uptime_result.output


def test_blocked_shell_features_do_not_consume_runs() -> None:
    blocked_commands = [
        "ls; whoami",
        "cat /etc/passwd | grep student",
        "pwd && id",
        "echo $(whoami)",
        "cat /etc/passwd > output.txt",
        "sudo cat /etc/passwd",
        "python -c 'print(1)'",
        "curl https://example.com",
        "rm -rf /",
        "cat ../../etc/passwd",
    ]
    state = create_terminal_state()
    for command in blocked_commands:
        state, result = run(state, command)
        assert result.status in {"blocked", "unsupported"}
        assert not result.consumed_run
    assert runs_remaining(state) == MAX_TERMINAL_RUNS
    assert state["history"] == []


def test_supported_path_error_consumes_one_practice_attempt() -> None:
    state = create_terminal_state()
    state, result = run(state, "cat missing.txt")
    assert result.status == "error"
    assert result.consumed_run
    assert runs_remaining(state) == MAX_TERMINAL_RUNS - 1
    assert len(state["history"]) == 1


def test_session_limit_stops_the_eleventh_command() -> None:
    state = create_terminal_state()
    for _ in range(MAX_TERMINAL_RUNS):
        state, result = run(state, "pwd")
        assert result.status == "success"
    assert runs_remaining(state) == 0

    state, result = run(state, "ls")
    assert result.status == "limit"
    assert not result.consumed_run
    assert len(state["history"]) == MAX_TERMINAL_RUNS


def test_practice_terminal_service_never_imports_shell_execution_modules() -> None:
    source = (Path(__file__).resolve().parents[1] / "opsready_lab" / "services" / "practice_terminal.py").read_text(
        encoding="utf-8"
    )
    assert "import subprocess" not in source
    assert "os.system" not in source
    assert "shell=True" not in source


def test_virtual_os_release_file_supports_the_loaded_example() -> None:
    state = create_terminal_state()
    state, result = run(state, "cat /etc/os-release")
    assert result.status == "success"
    assert "Ubuntu 24.04.2 LTS" in result.output
