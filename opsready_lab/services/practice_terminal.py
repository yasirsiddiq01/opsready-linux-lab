"""Safe, stateful Linux practice terminal used by the public learning app.

The terminal is a simulator. It never invokes a host shell, subprocess, or the
hosting platform filesystem. All commands operate on an in-memory virtual
filesystem and reviewed synthetic system data.
"""

from __future__ import annotations

import fnmatch
import posixpath
import re
import shlex
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

MAX_TERMINAL_RUNS = 10

SUPPORTED_COMMANDS: tuple[str, ...] = (
    "pwd",
    "ls",
    "cd",
    "cat",
    "head",
    "tail",
    "wc",
    "grep",
    "cut",
    "sort",
    "uniq",
    "awk",
    "sed",
    "find",
    "file",
    "stat",
    "whoami",
    "id",
    "uname",
    "hostname",
    "date",
    "df",
    "free",
    "ps",
    "uptime",
)

BLOCKED_COMMANDS = {
    "sudo",
    "su",
    "bash",
    "sh",
    "zsh",
    "fish",
    "python",
    "python3",
    "perl",
    "ruby",
    "php",
    "node",
    "ssh",
    "scp",
    "sftp",
    "curl",
    "wget",
    "nc",
    "ncat",
    "netcat",
    "telnet",
    "mount",
    "umount",
    "reboot",
    "shutdown",
    "poweroff",
    "systemctl",
    "service",
    "kill",
    "pkill",
    "killall",
    "rm",
    "rmdir",
    "mv",
    "cp",
    "chmod",
    "chown",
    "chgrp",
    "dd",
    "mkfs",
    "fdisk",
    "parted",
    "docker",
    "podman",
}

CONTROL_PATTERNS: tuple[tuple[str, str], ...] = (
    ("&&", "command chaining"),
    ("||", "conditional command chaining"),
    (";", "multiple-command separators"),
    ("|", "shell pipelines"),
    (">>", "output redirection"),
    (">", "output redirection"),
    ("<", "input redirection"),
    ("`", "command substitution"),
    ("$(", "command substitution"),
    ("${", "shell variable expansion"),
    ("\n", "multiple-line commands"),
    ("\r", "multiple-line commands"),
)


@dataclass(frozen=True)
class TerminalResult:
    command: str
    output: str
    explanation: str
    next_step: str
    status: str
    consumed_run: bool
    base_command: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


FILE_CONTENTS: dict[str, str] = {
    "/etc/os-release": '''PRETTY_NAME="Ubuntu 24.04.2 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.2 LTS (Noble Numbat)"
ID=ubuntu
HOME_URL="https://www.ubuntu.com/"''',
    "/etc/passwd": """root:x:0:0:root:/root:/bin/bash
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
appuser:x:1001:1001:Application User:/opt/app:/bin/bash
student:x:1000:1000:OpsReady Learner:/home/student:/bin/bash
backup:x:1002:1002:Backup Account:/srv/backup:/usr/sbin/nologin""",
    "/etc/hosts": """127.0.0.1 localhost
127.0.1.1 opsready-lab
10.20.0.10 api.internal.example
10.20.0.11 db.internal.example""",
    "/etc/nginx/nginx.conf": """user www-data;
worker_processes auto;
events { worker_connections 1024; }
http {
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    include /etc/nginx/conf.d/*.conf;
}""",
    "/home/student/.profile": """# OpsReady learner profile
export EDITOR=nano
export PAGER=less""",
    "/home/student/notes.txt": """OpsReady practice notes
1. Collect evidence before changing system state.
2. Compare a measurement with a healthy baseline.
3. Confirm user impact before remediation.""",
    "/home/student/projects/readme.md": """# Demo API
The service listens on port 8080.
Health endpoint: /health
Logs: /opt/app/app.log""",
    "/home/student/scripts/health_check.sh": """#!/bin/bash
# Review-only example; this simulator does not execute scripts.
df -h /
free -m
uptime""",
    "/opt/app/app.log": """2026-07-18T09:40:00Z INFO service started on port 8080
2026-07-18T09:41:12Z INFO health check status=200 latency_ms=42
2026-07-18T09:43:07Z WARN database response latency_ms=880
2026-07-18T09:43:10Z ERROR database timeout after 3 retries
2026-07-18T09:44:02Z INFO retry succeeded""",
    "/opt/app/config.ini": """[server]
port=8080
workers=4

[database]
host=db.internal.example
pool_size=20""",
    "/var/log/auth.log": """Jul 18 09:01:14 opsready sshd[812]: Accepted publickey for appuser from 203.0.113.20 port 51210
Jul 18 09:12:42 opsready sshd[902]: Failed password for invalid user admin from 198.51.100.77 port 42011
Jul 18 09:12:45 opsready sshd[902]: Failed password for invalid user admin from 198.51.100.77 port 42011
Jul 18 09:20:03 opsready sudo[1042]: appuser : TTY=pts/0 ; COMMAND=/usr/bin/systemctl status nginx""",
    "/var/log/syslog": """Jul 18 09:30:01 opsready systemd[1]: Started nginx.service
Jul 18 09:35:18 opsready kernel: eth0: Link is Up - 1Gbps/Full
Jul 18 09:40:00 opsready app[2142]: API started on port 8080
Jul 18 09:43:10 opsready app[2142]: database timeout after 3 retries
Jul 18 09:44:02 opsready app[2142]: database connection restored""",
    "/var/log/nginx/access.log": """203.0.113.10 - - [18/Jul/2026:09:40:11 +0000] \"GET /health HTTP/1.1\" 200 32
203.0.113.10 - - [18/Jul/2026:09:41:18 +0000] \"GET /api/users HTTP/1.1\" 200 948
198.51.100.44 - - [18/Jul/2026:09:43:10 +0000] \"POST /api/orders HTTP/1.1\" 502 173
198.51.100.44 - - [18/Jul/2026:09:44:03 +0000] \"POST /api/orders HTTP/1.1\" 201 211""",
    "/var/log/nginx/error.log": """2026/07/18 09:43:10 [error] 1842#1842: *901 upstream timed out while reading response header from upstream
2026/07/18 09:44:03 [info] 1842#1842: *902 client request completed normally""",
}

DIRECTORIES: set[str] = {
    "/",
    "/etc",
    "/etc/nginx",
    "/home",
    "/home/student",
    "/home/student/projects",
    "/home/student/scripts",
    "/opt",
    "/opt/app",
    "/var",
    "/var/log",
    "/var/log/nginx",
}

FILE_MODES: dict[str, str] = {
    "/etc/os-release": "-rw-r--r--",
    "/etc/passwd": "-rw-r--r--",
    "/etc/hosts": "-rw-r--r--",
    "/etc/nginx/nginx.conf": "-rw-r-----",
    "/home/student/.profile": "-rw-r--r--",
    "/home/student/notes.txt": "-rw-r--r--",
    "/home/student/projects/readme.md": "-rw-r--r--",
    "/home/student/scripts/health_check.sh": "-rwxr-xr-x",
    "/opt/app/app.log": "-rw-r-----",
    "/opt/app/config.ini": "-rw-r-----",
    "/var/log/auth.log": "-rw-r-----",
    "/var/log/syslog": "-rw-r-----",
    "/var/log/nginx/access.log": "-rw-r-----",
    "/var/log/nginx/error.log": "-rw-r-----",
}

EXPLANATIONS: dict[str, tuple[str, str]] = {
    "pwd": (
        "`pwd` prints the current working directory inside the virtual Linux filesystem.",
        "Try `ls -la` to inspect the directory contents.",
    ),
    "ls": (
        "`ls` lists virtual files and directories. Options such as `-l` add metadata and `-a` include hidden entries.",
        "Try `cd projects`, then run `pwd` and `ls -la`.",
    ),
    "cd": (
        "`cd` changes the terminal's current directory. The updated location is retained for later commands in this browser session.",
        "Run `pwd` to confirm the new location.",
    ),
    "cat": (
        "`cat` reads the complete contents of one or more virtual text files.",
        "For long files, compare it with `head` or `tail`.",
    ),
    "head": (
        "`head` displays the first lines of a file. `-n` controls how many lines are shown.",
        "Use `tail -n 5` on the same file to compare its newest entries.",
    ),
    "tail": (
        "`tail` displays the final lines of a file, which is useful for recent log events.",
        "Try `grep -i error /opt/app/app.log` to narrow the evidence.",
    ),
    "wc": (
        "`wc` counts lines, words, or bytes in a file. The selected option determines which count is displayed.",
        "Use the count to decide whether a broader or narrower inspection command is appropriate.",
    ),
    "grep": (
        "`grep` searches file lines for a text pattern. `-i` ignores case, `-n` adds line numbers, and `-c` returns only a count.",
        "Add `-n` to preserve the location of matching evidence.",
    ),
    "cut": (
        "`cut` extracts selected delimited fields. In `/etc/passwd`, fields are separated by `:`.",
        "Compare the output with `awk -F: '{print $1, $7}' /etc/passwd`.",
    ),
    "sort": (
        "`sort` orders file lines lexically or numerically. `-r` reverses the result and `-n` enables numeric comparison.",
        "Run `uniq -c` on a file that already contains adjacent duplicate lines.",
    ),
    "uniq": (
        "`uniq` removes adjacent duplicate lines. `-c` also reports how many times each adjacent value occurs.",
        "Remember that non-adjacent duplicates normally need sorting first in a real shell workflow.",
    ),
    "awk": (
        "This safe subset of `awk` uses a field separator and prints selected fields from each record.",
        "Try extracting usernames and login shells from `/etc/passwd`.",
    ),
    "sed": (
        "This safe subset of `sed` either prints a selected line range or performs a simple text substitution without changing the source file.",
        "Use `sed -n '1,3p' /opt/app/app.log` to inspect a bounded range.",
    ),
    "find": (
        "`find` walks the virtual directory tree and filters entries by type or name.",
        "Narrow the starting path before adding broader patterns.",
    ),
    "file": (
        "`file` identifies the simulated type of a virtual path from its name and content.",
        "Use `stat` to inspect metadata for the same path.",
    ),
    "stat": (
        "`stat` reports synthetic metadata including type, size, mode, owner, and timestamps.",
        "Compare file permissions with the purpose of the file.",
    ),
    "whoami": (
        "`whoami` prints the effective user represented by this learning session.",
        "Run `id` to view the simulated UID, GID, and groups.",
    ),
    "id": (
        "`id` displays the simulated user and group identifiers for the learner account.",
        "Inspect `/etc/passwd` to connect account records with IDs and login shells.",
    ),
    "uname": (
        "`uname` prints simulated kernel and platform information. `-a` combines the common fields.",
        "Use this evidence when checking package or kernel compatibility.",
    ),
    "hostname": (
        "`hostname` prints the synthetic host name used by this training environment.",
        "Compare it with the `127.0.1.1` entry in `/etc/hosts`.",
    ),
    "date": (
        "`date` shows the current UTC time generated by the application, not the host's private configuration.",
        "Use timestamps to correlate events across the synthetic logs.",
    ),
    "df": (
        "`df` reports simulated filesystem capacity. The result follows the last health scenario when one has been run.",
        "If usage is high, inspect likely directories with `find` and log files with `stat`.",
    ),
    "free": (
        "`free` reports simulated memory and swap usage based on the current health scenario.",
        "Compare memory pressure with `ps aux` and the simulated load from `uptime`.",
    ),
    "ps": (
        "`ps` lists a small synthetic process table. Resource values adapt to the current health scenario.",
        "Identify the highest simulated CPU or memory consumer before proposing an action.",
    ),
    "uptime": (
        "`uptime` reports a synthetic uptime and load averages based on the health scenario.",
        "Compare load with the four-vCPU training baseline and memory or I/O evidence.",
    ),
}


def create_terminal_state() -> dict[str, Any]:
    """Create a fresh serialisable terminal session."""

    return {
        "cwd": "/home/student",
        "runs_used": 0,
        "history": [],
        "files": dict(FILE_CONTENTS),
        "directories": sorted(DIRECTORIES),
    }


def normalise_terminal_state(state: Any) -> dict[str, Any]:
    """Return a valid state, repairing incomplete session-state values."""

    if not isinstance(state, dict):
        return create_terminal_state()
    repaired = create_terminal_state()
    repaired.update({key: value for key, value in state.items() if key in repaired})
    if repaired["cwd"] not in set(repaired["directories"]):
        repaired["cwd"] = "/home/student"
    if not isinstance(repaired["history"], list):
        repaired["history"] = []
    try:
        repaired["runs_used"] = max(0, min(MAX_TERMINAL_RUNS, int(repaired["runs_used"])))
    except (TypeError, ValueError):
        repaired["runs_used"] = 0
    return repaired


def runs_remaining(state: dict[str, Any]) -> int:
    return max(0, MAX_TERMINAL_RUNS - int(state.get("runs_used", 0)))


def command_base(command_line: str) -> str:
    try:
        tokens = shlex.split(command_line.strip())
    except ValueError:
        return ""
    return tokens[0] if tokens else ""


def is_supported_command_line(command_line: str) -> bool:
    return command_base(command_line) in SUPPORTED_COMMANDS


def prompt_for_state(state: dict[str, Any]) -> str:
    cwd = str(state.get("cwd", "/home/student"))
    display = (
        "~"
        if cwd == "/home/student"
        else cwd.replace("/home/student", "~", 1)
        if cwd.startswith("/home/student/")
        else cwd
    )
    return f"student@opsready:{display}$"


def _health_values(health: dict[str, Any] | None) -> dict[str, float]:
    defaults: dict[str, float] = {
        "cpu": 32,
        "memory": 54,
        "disk": 61,
        "load": 1.4,
        "io_wait": 3,
        "connections": 180,
    }
    if isinstance(health, dict):
        for key in defaults:
            try:
                defaults[key] = float(health.get(key, defaults[key]))
            except (TypeError, ValueError):
                pass
    return defaults


def _path(state: dict[str, Any], raw: str | None) -> str:
    value = raw or str(state["cwd"])
    if value == "~":
        value = "/home/student"
    elif value.startswith("~/"):
        value = "/home/student/" + value[2:]
    if not value.startswith("/"):
        value = posixpath.join(str(state["cwd"]), value)
    return posixpath.normpath(value)


def _all_directories(state: dict[str, Any]) -> set[str]:
    return set(str(item) for item in state.get("directories", []))


def _all_files(state: dict[str, Any]) -> dict[str, str]:
    files = state.get("files", {})
    return (
        {str(path): str(content) for path, content in files.items()} if isinstance(files, dict) else dict(FILE_CONTENTS)
    )


def _children(state: dict[str, Any], directory: str, include_hidden: bool = False) -> list[str]:
    prefix = "/" if directory == "/" else directory.rstrip("/") + "/"
    names: set[str] = set()
    for item in [*_all_directories(state), *_all_files(state)]:
        if item == directory or not item.startswith(prefix):
            continue
        remainder = item[len(prefix) :]
        if "/" in remainder or not remainder:
            continue
        if not include_hidden and remainder.startswith("."):
            continue
        names.add(remainder)
    return sorted(names)


def _entry_path(directory: str, name: str) -> str:
    return "/" + name if directory == "/" else directory.rstrip("/") + "/" + name


def _metadata(state: dict[str, Any], path: str) -> tuple[str, int, str, str, str]:
    files = _all_files(state)
    directories = _all_directories(state)
    if path in directories:
        return (
            "directory",
            4096,
            "drwxr-xr-x",
            "student" if path.startswith("/home/student") else "root",
            "student" if path.startswith("/home/student") else "root",
        )
    content = files[path]
    owner = "student" if path.startswith("/home/student") else "appuser" if path.startswith("/opt/app") else "root"
    group = (
        "student"
        if path.startswith("/home/student")
        else "appgroup"
        if path.startswith("/opt/app")
        else "adm"
        if path.startswith("/var/log")
        else "root"
    )
    return "regular file", len(content.encode("utf-8")), FILE_MODES.get(path, "-rw-r--r--"), owner, group


def _error(command: str, message: str, base: str = "", consumed: bool = True) -> TerminalResult:
    explanation, next_step = EXPLANATIONS.get(
        base,
        (
            "The command was parsed safely but could not complete in the virtual environment.",
            "Check the path and supported syntax, then try again.",
        ),
    )
    return TerminalResult(command, message, explanation, next_step, "error", consumed, base)


def _success(command: str, output: str, base: str) -> TerminalResult:
    explanation, next_step = EXPLANATIONS[base]
    return TerminalResult(command, output or "(no output)", explanation, next_step, "success", True, base)


def _parse_count_option(tokens: list[str], default: int = 10) -> tuple[int, list[str]]:
    remaining = tokens[:]
    count = default
    if remaining and remaining[0] == "-n":
        if len(remaining) < 2:
            raise ValueError("option -n requires a number")
        count = int(remaining[1])
        remaining = remaining[2:]
    elif remaining and re.fullmatch(r"-\d+", remaining[0]):
        count = int(remaining[0][1:])
        remaining = remaining[1:]
    return max(0, min(count, 100)), remaining


def _cmd_pwd(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    if args:
        return _error("pwd " + " ".join(args), "pwd: too many arguments", "pwd")
    return _success("pwd", str(state["cwd"]), "pwd")


def _cmd_ls(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    show_all = False
    long_format = False
    paths: list[str] = []
    for token in args:
        if token.startswith("-") and token != "-":
            flags = token[1:]
            if any(flag not in "alh" for flag in flags):
                return _error("ls " + " ".join(args), f"ls: unsupported option -- '{token}'", "ls")
            show_all = show_all or "a" in flags
            long_format = long_format or "l" in flags
        else:
            paths.append(token)
    target = _path(state, paths[0] if paths else None)
    files = _all_files(state)
    directories = _all_directories(state)
    if target in files:
        names = [posixpath.basename(target)]
        directory = posixpath.dirname(target) or "/"
    elif target in directories:
        names = _children(state, target, include_hidden=show_all)
        directory = target
        if show_all:
            names = [".", "..", *names]
    else:
        return _error(
            "ls " + " ".join(args),
            f"ls: cannot access '{paths[0] if paths else target}': No such file or directory",
            "ls",
        )
    if not long_format:
        return _success("ls " + " ".join(args), "  ".join(names), "ls")
    lines: list[str] = []
    for name in names:
        if name == ".":
            path = directory
        elif name == "..":
            path = posixpath.dirname(directory.rstrip("/")) or "/"
        else:
            path = _entry_path(directory, name)
        kind, size, mode, owner, group = _metadata(state, path)
        display_size = (
            f"{size}"
            if "h" not in "".join(token[1:] for token in args if token.startswith("-"))
            else f"{max(1, round(size / 1024))}K"
        )
        lines.append(
            f"{mode} 1 {owner:<8} {group:<8} {display_size:>6} Jul 18 09:40 {name}{'/' if kind == 'directory' and name not in {'.', '..'} else ''}"
        )
    return _success("ls " + " ".join(args), "\n".join(lines), "ls")


def _cmd_cd(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    if len(args) > 1:
        return _error("cd " + " ".join(args), "cd: too many arguments", "cd")
    target = _path(state, args[0] if args else "/home/student")
    if target not in _all_directories(state):
        return _error("cd " + " ".join(args), f"cd: {args[0] if args else target}: No such directory", "cd")
    state["cwd"] = target
    return _success("cd " + " ".join(args), f"current directory: {target}", "cd")


def _read_file(state: dict[str, Any], raw_path: str, command: str) -> tuple[str | None, TerminalResult | None]:
    path = _path(state, raw_path)
    files = _all_files(state)
    if path in _all_directories(state):
        return None, _error(command, f"{command.split()[0]}: {raw_path}: Is a directory", command.split()[0])
    if path not in files:
        return None, _error(command, f"{command.split()[0]}: {raw_path}: No such file", command.split()[0])
    return files[path], None


def _cmd_cat(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    if not args:
        return _error("cat", "cat: provide one or more virtual file paths", "cat")
    outputs: list[str] = []
    command = "cat " + " ".join(args)
    for raw_path in args:
        content, error = _read_file(state, raw_path, command)
        if error:
            return error
        outputs.append(str(content))
    return _success(command, "\n".join(outputs), "cat")


def _cmd_head_tail(base: str, state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = base + (" " + " ".join(args) if args else "")
    try:
        count, remaining = _parse_count_option(args)
    except (ValueError, TypeError):
        return _error(command, f"{base}: option -n requires an integer", base)
    if len(remaining) != 1:
        return _error(command, f"{base}: provide exactly one virtual file path", base)
    content, error = _read_file(state, remaining[0], command)
    if error:
        return error
    lines = str(content).splitlines()
    selected = lines[:count] if base == "head" else lines[-count:] if count else []
    return _success(command, "\n".join(selected), base)


def _cmd_wc(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "wc" + (" " + " ".join(args) if args else "")
    option = ""
    remaining = args[:]
    if remaining and remaining[0] in {"-l", "-w", "-c"}:
        option = remaining.pop(0)
    if len(remaining) != 1:
        return _error(command, "wc: provide one virtual file path", "wc")
    content, error = _read_file(state, remaining[0], command)
    if error:
        return error
    text = str(content)
    lines = len(text.splitlines())
    words = len(text.split())
    bytes_count = len(text.encode("utf-8"))
    if option == "-l":
        output = f"{lines:>7} {remaining[0]}"
    elif option == "-w":
        output = f"{words:>7} {remaining[0]}"
    elif option == "-c":
        output = f"{bytes_count:>7} {remaining[0]}"
    else:
        output = f"{lines:>7} {words:>7} {bytes_count:>7} {remaining[0]}"
    return _success(command, output, "wc")


def _cmd_grep(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "grep" + (" " + " ".join(args) if args else "")
    ignore_case = False
    line_numbers = False
    count_only = False
    remaining: list[str] = []
    for token in args:
        if token.startswith("-") and token != "-" and not remaining:
            flags = token[1:]
            if any(flag not in "inc" for flag in flags):
                return _error(command, f"grep: unsupported option '{token}'", "grep")
            ignore_case = ignore_case or "i" in flags
            line_numbers = line_numbers or "n" in flags
            count_only = count_only or "c" in flags
        else:
            remaining.append(token)
    if len(remaining) != 2:
        return _error(command, "grep: expected a pattern and one virtual file", "grep")
    pattern, raw_path = remaining
    content, error = _read_file(state, raw_path, command)
    if error:
        return error
    needle = pattern.lower() if ignore_case else pattern
    matches: list[str] = []
    for index, line in enumerate(str(content).splitlines(), 1):
        haystack = line.lower() if ignore_case else line
        if needle in haystack:
            matches.append(f"{index}:{line}" if line_numbers else line)
    if count_only:
        return _success(command, str(len(matches)), "grep")
    return _success(command, "\n".join(matches) if matches else "(no matches)", "grep")


def _cmd_cut(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "cut" + (" " + " ".join(args) if args else "")
    delimiter = "\t"
    fields_spec = ""
    remaining: list[str] = []
    index = 0
    while index < len(args):
        token = args[index]
        if token == "-d":
            if index + 1 >= len(args):
                return _error(command, "cut: option -d requires a delimiter", "cut")
            delimiter = args[index + 1]
            index += 2
        elif token.startswith("-d") and len(token) > 2:
            delimiter = token[2:]
            index += 1
        elif token == "-f":
            if index + 1 >= len(args):
                return _error(command, "cut: option -f requires a field list", "cut")
            fields_spec = args[index + 1]
            index += 2
        elif token.startswith("-f") and len(token) > 2:
            fields_spec = token[2:]
            index += 1
        else:
            remaining.append(token)
            index += 1
    if not fields_spec or len(remaining) != 1:
        return _error(command, "cut: use -d DELIMITER -f FIELDS with one virtual file", "cut")
    try:
        fields = [int(value) for value in fields_spec.split(",")]
        if any(value < 1 for value in fields):
            raise ValueError
    except ValueError:
        return _error(command, "cut: fields must be positive comma-separated integers", "cut")
    content, error = _read_file(state, remaining[0], command)
    if error:
        return error
    output: list[str] = []
    for line in str(content).splitlines():
        parts = line.split(delimiter)
        selected = [parts[value - 1] for value in fields if value <= len(parts)]
        output.append(delimiter.join(selected))
    return _success(command, "\n".join(output), "cut")


def _cmd_sort(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "sort" + (" " + " ".join(args) if args else "")
    reverse = "-r" in args
    numeric = "-n" in args
    remaining = [token for token in args if token not in {"-r", "-n"}]
    if len(remaining) != 1:
        return _error(command, "sort: provide one virtual file; supported options are -r and -n", "sort")
    content, error = _read_file(state, remaining[0], command)
    if error:
        return error
    lines = str(content).splitlines()
    if numeric:

        def numeric_key(value: str) -> float:
            try:
                return float(value.strip().split()[0])
            except (ValueError, IndexError):
                return 0.0

        lines.sort(key=numeric_key, reverse=reverse)
    else:
        lines.sort(key=str.lower, reverse=reverse)
    return _success(command, "\n".join(lines), "sort")


def _cmd_uniq(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "uniq" + (" " + " ".join(args) if args else "")
    count = "-c" in args
    remaining = [token for token in args if token != "-c"]
    if len(remaining) != 1:
        return _error(command, "uniq: provide one virtual file; supported option is -c", "uniq")
    content, error = _read_file(state, remaining[0], command)
    if error:
        return error
    result: list[str] = []
    previous: str | None = None
    occurrences = 0
    for line in [*str(content).splitlines(), None]:
        if line == previous:
            occurrences += 1
            continue
        if previous is not None:
            result.append(f"{occurrences:>7} {previous}" if count else previous)
        previous = line
        occurrences = 1
    return _success(command, "\n".join(result), "uniq")


def _cmd_awk(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "awk" + (" " + " ".join(args) if args else "")
    delimiter = None
    remaining: list[str] = []
    index = 0
    while index < len(args):
        token = args[index]
        if token == "-F":
            if index + 1 >= len(args):
                return _error(command, "awk: option -F requires a field separator", "awk")
            delimiter = args[index + 1]
            index += 2
        elif token.startswith("-F") and len(token) > 2:
            delimiter = token[2:]
            index += 1
        else:
            remaining.append(token)
            index += 1
    if len(remaining) != 2:
        return _error(command, "awk: supported form is awk -F: '{print $1, $7}' FILE", "awk")
    program, raw_path = remaining
    match = re.fullmatch(r"\{\s*print\s+(.+?)\s*\}", program)
    if not match:
        return _error(command, "awk: only a simple {print $N, $M} program is supported", "awk")
    references = re.findall(r"\$(\d+)", match.group(1))
    if not references:
        return _error(command, "awk: the print expression must contain field references such as $1", "awk")
    fields = [int(value) for value in references]
    content, error = _read_file(state, raw_path, command)
    if error:
        return error
    output: list[str] = []
    for line in str(content).splitlines():
        parts = line.split(delimiter) if delimiter is not None else line.split()
        output.append(" ".join(parts[field - 1] if field <= len(parts) else "" for field in fields).rstrip())
    return _success(command, "\n".join(output), "awk")


def _cmd_sed(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "sed" + (" " + " ".join(args) if args else "")
    print_only = False
    remaining = args[:]
    if remaining and remaining[0] == "-n":
        print_only = True
        remaining.pop(0)
    if len(remaining) != 2:
        return _error(command, "sed: supported forms are sed -n '1,3p' FILE or sed 's/old/new/' FILE", "sed")
    expression, raw_path = remaining
    content, error = _read_file(state, raw_path, command)
    if error:
        return error
    lines = str(content).splitlines()
    range_match = re.fullmatch(r"(\d+)(?:,(\d+))?p", expression)
    if print_only and range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2) or start)
        selected = lines[max(0, start - 1) : max(0, end)]
        return _success(command, "\n".join(selected), "sed")
    substitution = re.fullmatch(r"s/([^/]*)/([^/]*)/(g?)", expression)
    if substitution:
        old, new, global_flag = substitution.groups()
        if old == "":
            return _error(command, "sed: empty search patterns are not supported", "sed")
        count = 0 if global_flag == "g" else 1
        return _success(command, "\n".join(line.replace(old, new, count) for line in lines), "sed")
    return _error(command, "sed: unsupported expression; use a line range or simple substitution", "sed")


def _cmd_find(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "find" + (" " + " ".join(args) if args else "")
    start_raw = args[0] if args and not args[0].startswith("-") else "."
    remaining = args[1:] if args and not args[0].startswith("-") else args[:]
    target_type: str | None = None
    name_pattern: str | None = None
    max_depth: int | None = None
    index = 0
    while index < len(remaining):
        token = remaining[index]
        if token == "-type" and index + 1 < len(remaining):
            target_type = remaining[index + 1]
            if target_type not in {"f", "d"}:
                return _error(command, "find: -type supports only f or d", "find")
            index += 2
        elif token == "-name" and index + 1 < len(remaining):
            name_pattern = remaining[index + 1]
            index += 2
        elif token == "-maxdepth" and index + 1 < len(remaining):
            try:
                max_depth = max(0, int(remaining[index + 1]))
            except ValueError:
                return _error(command, "find: -maxdepth requires an integer", "find")
            index += 2
        else:
            return _error(command, f"find: unsupported or incomplete expression near '{token}'", "find")
    start = _path(state, start_raw)
    files = _all_files(state)
    directories = _all_directories(state)
    if start not in directories and start not in files:
        return _error(command, f"find: '{start_raw}': No such file or directory", "find")
    candidates = sorted([*directories, *files])
    results: list[str] = []
    prefix = start.rstrip("/") + "/"
    for path in candidates:
        if path != start and not path.startswith(prefix):
            continue
        relative = path[len(prefix) :] if path.startswith(prefix) else ""
        depth = 0 if path == start else relative.count("/") + 1
        if max_depth is not None and depth > max_depth:
            continue
        if target_type == "f" and path not in files:
            continue
        if target_type == "d" and path not in directories:
            continue
        if name_pattern and not fnmatch.fnmatch(posixpath.basename(path), name_pattern):
            continue
        results.append(path)
    return _success(command, "\n".join(results) if results else "(no matches)", "find")


def _cmd_file(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "file" + (" " + " ".join(args) if args else "")
    if len(args) != 1:
        return _error(command, "file: provide one virtual path", "file")
    path = _path(state, args[0])
    if path in _all_directories(state):
        description = "directory"
    elif path in _all_files(state):
        if path.endswith(".sh"):
            description = "Bourne-Again shell script, ASCII text executable"
        elif path.endswith((".log", ".txt", ".md", ".ini", ".conf", ".profile")) or posixpath.basename(path) in {
            "passwd",
            "hosts",
        }:
            description = "ASCII text"
        else:
            description = "data"
    else:
        return _error(command, f"file: {args[0]}: No such file or directory", "file")
    return _success(command, f"{args[0]}: {description}", "file")


def _cmd_stat(state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = "stat" + (" " + " ".join(args) if args else "")
    if len(args) != 1:
        return _error(command, "stat: provide one virtual path", "stat")
    path = _path(state, args[0])
    if path not in _all_directories(state) and path not in _all_files(state):
        return _error(command, f"stat: cannot stat '{args[0]}': No such file or directory", "stat")
    kind, size, mode, owner, group = _metadata(state, path)
    output = f"""  File: {path}
  Size: {size}\tBlocks: {max(1, (size + 511) // 512)}\tIO Block: 4096   {kind}
Access: ({mode})  Uid: ({owner})   Gid: ({group})
Modify: 2026-07-18 09:40:00 +0000"""
    return _success(command, output, "stat")


def _cmd_simple(base: str, state: dict[str, Any], args: list[str], health: dict[str, float]) -> TerminalResult:
    command = base + (" " + " ".join(args) if args else "")
    if base == "whoami":
        if args:
            return _error(command, "whoami: no options are supported", base)
        output = "student"
    elif base == "id":
        if args:
            return _error(command, "id: this simulator supports the current user only", base)
        output = "uid=1000(student) gid=1000(student) groups=1000(student),27(sudo),1001(opsready)"
    elif base == "uname":
        if args == ["-a"]:
            output = "Linux opsready-lab 6.8.0-virtual #1 SMP x86_64 GNU/Linux"
        elif args == ["-r"]:
            output = "6.8.0-virtual"
        elif not args:
            output = "Linux"
        else:
            return _error(command, "uname: supported options are -a and -r", base)
    elif base == "hostname":
        if args:
            return _error(command, "hostname: read-only simulation; no options are supported", base)
        output = "opsready-lab"
    elif base == "date":
        if args:
            return _error(command, "date: this simulator supports the default UTC display only", base)
        output = datetime.now(timezone.utc).strftime("%a %b %d %H:%M:%S UTC %Y")
    elif base == "df":
        if any(token not in {"-h", "/"} for token in args):
            return _error(command, "df: supported form is df -h /", base)
        disk = int(health["disk"])
        used = round(80 * disk / 100)
        output = f"Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        80G   {used}G   {80 - used}G  {disk}% /"
    elif base == "free":
        if any(token not in {"-m", "-h"} for token in args):
            return _error(command, "free: supported options are -m and -h", base)
        memory = int(health["memory"])
        used = round(8192 * memory / 100)
        available = max(0, 8192 - used)
        swap = max(0, round((memory - 75) * 35))
        output = f"              total   used   available\nMem:           8192   {used}   {available}\nSwap:          2048   {swap}   {2048 - swap}"
    elif base == "ps":
        if args not in ([], ["aux"], ["-ef"]):
            return _error(command, "ps: supported forms are ps, ps aux, and ps -ef", base)
        cpu = float(health["cpu"])
        memory = float(health["memory"])
        output = f"""USER       PID %CPU %MEM COMMAND
root         1  0.1  0.5 /sbin/init
appuser   2142 {max(1.0, cpu * 0.58):4.1f} {max(1.0, memory * 0.31):4.1f} python app.py
www-data  1842 {max(0.3, cpu * 0.12):4.1f}  2.1 nginx: worker process
student   3220  0.2  0.4 practice-terminal"""
    elif base == "uptime":
        if args:
            return _error(command, "uptime: no options are supported in this simulator", base)
        load = float(health["load"])
        output = f"10:14:22 up 6 days, 3:11, 1 user, load average: {load:.2f}, {max(0, load - 0.35):.2f}, {max(0, load - 0.75):.2f}"
    else:
        return _error(command, f"{base}: unsupported", base, consumed=False)
    return _success(command, output, base)


CommandHandler = Callable[[dict[str, Any], list[str], dict[str, float]], TerminalResult]

HANDLERS: dict[str, CommandHandler] = {
    "pwd": _cmd_pwd,
    "ls": _cmd_ls,
    "cd": _cmd_cd,
    "cat": _cmd_cat,
    "head": lambda state, args, health: _cmd_head_tail("head", state, args, health),
    "tail": lambda state, args, health: _cmd_head_tail("tail", state, args, health),
    "wc": _cmd_wc,
    "grep": _cmd_grep,
    "cut": _cmd_cut,
    "sort": _cmd_sort,
    "uniq": _cmd_uniq,
    "awk": _cmd_awk,
    "sed": _cmd_sed,
    "find": _cmd_find,
    "file": _cmd_file,
    "stat": _cmd_stat,
    "whoami": lambda state, args, health: _cmd_simple("whoami", state, args, health),
    "id": lambda state, args, health: _cmd_simple("id", state, args, health),
    "uname": lambda state, args, health: _cmd_simple("uname", state, args, health),
    "hostname": lambda state, args, health: _cmd_simple("hostname", state, args, health),
    "date": lambda state, args, health: _cmd_simple("date", state, args, health),
    "df": lambda state, args, health: _cmd_simple("df", state, args, health),
    "free": lambda state, args, health: _cmd_simple("free", state, args, health),
    "ps": lambda state, args, health: _cmd_simple("ps", state, args, health),
    "uptime": lambda state, args, health: _cmd_simple("uptime", state, args, health),
}


def execute_command(
    state: dict[str, Any],
    command_line: str,
    health: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], TerminalResult]:
    """Safely execute a reviewed command against the in-memory simulator.

    The returned state is the same mutable object after validation and updates.
    Blocked, blank, unsupported, and over-limit requests do not consume a run.
    Supported command attempts consume one run even when they return a normal
    file/path error, mirroring a learner's submitted practice attempt.
    """

    state = normalise_terminal_state(state)
    raw = command_line.strip()
    if not raw:
        return state, TerminalResult(
            "",
            "Enter a command before pressing Run.",
            "No command was submitted.",
            "Try `pwd` or `ls -la`.",
            "empty",
            False,
        )

    for pattern, reason in CONTROL_PATTERNS:
        if pattern in raw:
            return state, TerminalResult(
                raw,
                f"Blocked for safety: {reason} are not available in the public practice terminal.",
                "The practice terminal accepts one reviewed command at a time and never forwards input to a host shell.",
                "Remove the shell control operator and run one supported read-only command.",
                "blocked",
                False,
            )
    try:
        tokens = shlex.split(raw)
    except ValueError as exc:
        return state, TerminalResult(
            raw,
            f"Command could not be parsed: {exc}",
            "Quoted arguments must be balanced before a command can be simulated.",
            "Correct the quotation marks and submit again.",
            "blocked",
            False,
        )
    if not tokens:
        return state, TerminalResult(
            "",
            "Enter a command before pressing Run.",
            "No command was submitted.",
            "Try `pwd` or `ls -la`.",
            "empty",
            False,
        )
    base = tokens[0]
    if base in BLOCKED_COMMANDS:
        return state, TerminalResult(
            raw,
            f"Blocked for safety: `{base}` can change a system, start a shell, access a network, or control processes.",
            "The public terminal intentionally allows only reviewed read-only learning commands.",
            "Use Guided command explorer for change-oriented commands, or choose a supported inspection command.",
            "blocked",
            False,
            base,
        )
    if base not in SUPPORTED_COMMANDS:
        return state, TerminalResult(
            raw,
            f"Command not available in Practice mode: {base}",
            "Practice mode currently supports a reviewed set of 25 inspection and text-processing commands.",
            "Open Supported commands below, or use Guided command explorer for the wider 150-command catalogue.",
            "unsupported",
            False,
            base,
        )
    if any(
        token == ".." or token.startswith("../") or "/../" in token or token.endswith("/..") for token in tokens[1:]
    ):
        return state, TerminalResult(
            raw,
            "Blocked for safety: parent-directory traversal (`..`) is not available in this public simulator.",
            "Paths are restricted to explicit locations in the virtual filesystem so learners cannot confuse the simulator with the hosting filesystem.",
            "Use an absolute virtual path such as `/var/log/syslog` or navigate with `cd /home/student`.",
            "blocked",
            False,
            base,
        )
    if runs_remaining(state) <= 0:
        return state, TerminalResult(
            raw,
            "Practice limit reached: 10 command attempts have been used in this terminal session.",
            "The limit keeps the free public exercise short and predictable. It is a session-learning limit, not an identity-based quota.",
            "Review the command history or reset the virtual terminal to begin a fresh practice session.",
            "limit",
            False,
            base,
        )

    result = HANDLERS[base](state, tokens[1:], _health_values(health))
    if result.consumed_run:
        state["runs_used"] = int(state.get("runs_used", 0)) + 1
        history = state.setdefault("history", [])
        history.append(
            {
                "index": len(history) + 1,
                "command": raw,
                "status": result.status,
                "output": result.output,
            }
        )
        if len(history) > MAX_TERMINAL_RUNS:
            del history[:-MAX_TERMINAL_RUNS]
    return state, TerminalResult(
        command=raw,
        output=result.output,
        explanation=result.explanation,
        next_step=result.next_step,
        status=result.status,
        consumed_run=result.consumed_run,
        base_command=base,
    )
