from pathlib import Path

from opsready_lab.services.execution_trace import build_execution_trace


def titles(trace):
    return [node.title for node in trace.nodes]


def details(trace):
    return [node.detail for node in trace.nodes]


def test_pwd_uses_shell_and_kernel_cwd_without_network() -> None:
    trace = build_execution_trace("pwd", "pwd", cwd="/home/student/projects")
    assert trace.kind == "Shell built-in"
    assert "Kernel syscall" in titles(trace)
    assert "getcwd()" in details(trace)
    assert not trace.networked
    assert all("Switch" != title and "Router" != title for title in titles(trace))


def test_cat_targets_the_actual_file_and_vfs() -> None:
    trace = build_execution_trace("cat", "cat /etc/os-release")
    assert "Kernel VFS" in titles(trace)
    assert "/etc/os-release" in details(trace)
    assert any("File: /etc/os-release" == item for item in trace.touchpoints)


def test_cd_resolves_relative_directory_from_previous_cwd() -> None:
    trace = build_execution_trace("cd", "cd projects", cwd="/home/student")
    assert "/home/student/projects" in details(trace)
    assert "Shell built-in" in titles(trace)


def test_systemctl_uses_dbus_systemd_and_unit() -> None:
    trace = build_execution_trace("systemctl", "systemctl status nginx")
    assert "D-Bus/control socket" in titles(trace)
    assert "systemd PID 1" in titles(trace)
    assert "nginx.service" in details(trace)


def test_ping_uses_network_stack_interface_and_remote_target() -> None:
    trace = build_execution_trace("ping", "ping -c 2 8.8.8.8")
    assert trace.networked
    assert "Kernel network stack" in titles(trace)
    assert "Network interface" in titles(trace)
    assert "8.8.8.8" in details(trace)


def test_df_uses_statvfs_mount_and_filesystem() -> None:
    trace = build_execution_trace("df", "df -h /")
    assert "Kernel syscall" in titles(trace)
    assert "statvfs()" in details(trace)
    assert "Filesystem" in titles(trace)


def test_execution_trace_uses_compact_numbered_layout_css() -> None:
    root = Path(__file__).resolve().parents[1]
    animation_source = (root / "opsready_lab" / "ui" / "animations.py").read_text(encoding="utf-8")
    theme_source = (root / "opsready_lab" / "ui" / "theme.py").read_text(encoding="utf-8")
    assert "execution-step" in animation_source
    assert "trace-diamond" in animation_source
    assert "trace-zigzag" in animation_source
    assert "min-width:560px" not in theme_source
    assert "grid-template-columns:repeat(3,minmax(0,1fr))" in theme_source
    assert "execution-moving-token" in animation_source
    assert "execution-route-progress" in animation_source
    assert "Watch the orange command token" in animation_source


def test_basename_is_a_string_operation_not_a_filesystem_read() -> None:
    trace = build_execution_trace("basename", "basename /var/log/nginx/error.log")
    assert trace.kind == "Path string transformation"
    assert "String operation" in titles(trace)
    assert "Kernel VFS" not in titles(trace)
    assert trace.effect is not None
    assert trace.effect.result == "Print: error.log"
    assert "No file or directory is opened" in trace.effect.impact
    assert "Filesystem opened: none" in trace.touchpoints


def test_dirname_is_a_string_operation_not_a_directory_removal() -> None:
    trace = build_execution_trace("dirname", "dirname /var/log/nginx/error.log")
    assert trace.kind == "Path string transformation"
    assert "Kernel VFS" not in titles(trace)
    assert trace.effect is not None
    assert trace.effect.result == "Print: /var/log/nginx"
    assert "No directory is opened, removed" in trace.effect.impact


def test_file_command_reads_target_and_magic_database() -> None:
    trace = build_execution_trace("file", "file /usr/bin/python3")
    assert trace.kind == "File type detection"
    assert "Kernel VFS" in titles(trace)
    assert any("magic.mgc" in detail for detail in details(trace))


def test_pipeline_shows_processes_and_kernel_pipe() -> None:
    trace = build_execution_trace("uniq", "sort access.log | uniq -c | sort -nr")
    assert trace.kind == "Shell pipeline"
    assert "Kernel pipe" in titles(trace)
    assert "Following stage(s)" in titles(trace)
    assert trace.effect is not None
    assert "final pipeline stage" in trace.effect.result


def test_every_catalog_command_has_plain_language_effect_summary() -> None:
    from opsready_lab.catalog.commands import COMMANDS

    for command, item in COMMANDS.items():
        trace = build_execution_trace(command, str(item["example"]))
        assert trace.effect is not None, command
        assert trace.effect.input_value.strip(), command
        assert trace.effect.operation.strip(), command
        assert trace.effect.result.strip(), command
        assert trace.effect.impact.strip(), command
