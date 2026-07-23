"""Command-specific conceptual Linux execution traces.

The traces are educational models. They show which userspace utility, kernel
interface, subsystem, virtual file, service, or network endpoint a command
normally interacts with. They never execute the submitted command.
"""

from __future__ import annotations

import posixpath
import re
import shlex
from dataclasses import dataclass, replace
from urllib.parse import urlparse


@dataclass(frozen=True)
class TraceNode:
    icon: str
    title: str
    detail: str


@dataclass(frozen=True)
class EffectSummary:
    input_value: str
    operation: str
    result: str
    impact: str


@dataclass(frozen=True)
class ExecutionTrace:
    command: str
    kind: str
    summary: str
    nodes: tuple[TraceNode, ...]
    touchpoints: tuple[str, ...]
    networked: bool = False
    effect: EffectSummary | None = None


_LOCAL_TEXT = {
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
    "less",
    "paste",
    "tr",
    "diff",
    "cmp",
    "xargs",
    "tee",
    "sha256sum",
}
_FILE_LIST = {"ls", "tree", "find", "locate"}
_PATH_STRING = {"basename", "dirname"}
_FILE_META = {"stat", "readlink", "realpath"}
_FILE_TYPE = {"file"}
_FILE_CHANGE = {"touch", "mkdir", "rmdir", "cp", "mv", "rm", "ln"}
_ARCHIVE = {"tar", "gzip", "gunzip", "zip", "unzip"}
_PROCESS_READ = {"ps", "top", "pgrep", "lsof", "jobs"}
_PROCESS_CHANGE = {"pkill", "kill", "killall", "nice", "renice", "nohup", "bg", "fg"}
_PERFORMANCE = {"uptime", "vmstat", "iostat", "pidstat", "mpstat", "sar", "perf stat", "time", "watch"}
_SERVICE = {"systemctl", "service", "loginctl", "systemd-analyze"}
_JOURNAL = {"journalctl", "coredumpctl"}
_LOG_FILES = {"dmesg", "logger", "logrotate"}
_NETWORK_REMOTE = {
    "ping",
    "tracepath",
    "traceroute",
    "curl",
    "wget",
    "nc",
    "ssh",
    "scp",
    "rsync",
    "openssl s_client",
    "nmap",
}
_NETWORK_LOCAL = {"ss", "ip", "ip addr", "ip route", "ip neigh", "ethtool", "tcpdump"}
_DNS = {"dig", "host"}
_FIREWALL = {"ufw", "nft", "iptables"}
_STORAGE = {"df", "du", "lsblk", "blkid", "mount", "umount", "findmnt", "fdisk -l", "parted -l", "swapon"}
_MEMORY = {"free"}
_USERS_READ = {"whoami", "id", "who", "groups"}
_USERS_CHANGE = {"passwd", "useradd", "usermod", "groupadd", "sudo", "su"}
_PERMISSIONS = {"chmod", "chown", "chgrp", "umask", "getfacl", "setfacl"}
_KERNEL = {"uname", "hostname", "date", "sysctl", "lsmod", "modinfo", "modprobe"}
_SECURITY = {"auditctl", "ausearch", "sestatus", "getenforce", "restorecon"}
_CONTAINERS = {"docker ps", "docker logs", "docker inspect", "docker stats", "docker exec"}
_SCHEDULING = {"crontab", "at", "flock"}
_SHELL_LOOKUP = {"which", "type", "whereis", "man"}
_RESOURCES = {"ulimit", "prlimit"}

_DEFAULT_PATHS = {
    "cat": "/etc/os-release",
    "head": "/opt/app/app.log",
    "tail": "/var/log/syslog",
    "wc": "/var/log/auth.log",
    "grep": "/opt/app/app.log",
    "cut": "/etc/passwd",
    "sort": "/etc/hosts",
    "uniq": "/etc/hosts",
    "awk": "/etc/passwd",
    "sed": "/opt/app/app.log",
    "less": "/var/log/syslog",
    "find": "/var/log",
    "ls": "/home/student",
    "tree": "/home/student",
    "stat": "/opt/app/config.ini",
    "file": "/home/student/scripts/health_check.sh",
    "readlink": "/opt/app/current",
    "df": "/",
    "du": "/var/log",
    "logrotate": "/etc/logrotate.conf",
    "restorecon": "/var/www/html",
}


def _tokens(command_line: str) -> list[str]:
    try:
        return shlex.split(command_line, posix=True)
    except ValueError:
        return command_line.split()


def _resolve_path(token: str, cwd: str) -> str:
    cleaned = token.strip(" ,:;()[]{}\"'")
    if not cleaned:
        return cwd
    if cleaned.startswith("/"):
        return posixpath.normpath(cleaned)
    if cleaned.startswith("./") or "/" in cleaned or cleaned.endswith((".log", ".txt", ".conf", ".ini", ".md", ".sh")):
        return posixpath.normpath(posixpath.join(cwd, cleaned))
    return ""


def _path_target(command_line: str, command: str, cwd: str) -> str:
    tokens = _tokens(command_line)
    candidates: list[str] = []
    for token in tokens[1:]:
        if token.startswith("-") or token.startswith("{") or token.startswith("'"):
            continue
        resolved = _resolve_path(token, cwd)
        if resolved:
            candidates.append(resolved)
    if candidates:
        return candidates[-1]

    # Commands whose first non-option operand is itself a path may use a plain
    # relative directory name such as ``cd projects`` or ``ls logs``.
    path_operand_commands = {
        "cd",
        "ls",
        "tree",
        "find",
        "stat",
        "file",
        "readlink",
        "realpath",
        "touch",
        "mkdir",
        "rmdir",
        "cp",
        "mv",
        "rm",
        "ln",
        "du",
    }
    if command in path_operand_commands:
        for token in tokens[1:]:
            if token.startswith("-"):
                continue
            cleaned = token.strip(" ,:;()[]{}\"'")
            if cleaned and not cleaned.startswith("{"):
                return posixpath.normpath(posixpath.join(cwd, cleaned))
    return _DEFAULT_PATHS.get(command, cwd)


def _explicit_path_target(command_line: str, cwd: str) -> str:
    """Return only a path explicitly present in a command stage."""

    for token in _tokens(command_line)[1:]:
        if token.startswith("-"):
            continue
        resolved = _resolve_path(token, cwd)
        if resolved:
            return resolved
    return ""


def _service_target(command_line: str) -> str:
    tokens = _tokens(command_line)
    actions = {"status", "start", "stop", "restart", "reload", "enable", "disable", "show", "is-active"}
    for token in reversed(tokens[1:]):
        if token.startswith("-") or token in actions:
            continue
        return token if token.endswith(".service") else f"{token}.service"
    return "nginx.service"


def _network_target(command_line: str) -> str:
    for token in reversed(_tokens(command_line)[1:]):
        if token.startswith("-") or token.startswith(":"):
            continue
        if token.startswith(("http://", "https://")):
            return urlparse(token).hostname or token
        if re.fullmatch(r"[A-Za-z0-9_.:-]+", token):
            return token
    return "remote endpoint"


def _n(icon: str, title: str, detail: str) -> TraceNode:
    return TraceNode(icon=icon, title=title, detail=detail)


def _build_execution_trace(
    command_name: str,
    command_line: str,
    *,
    cwd: str = "/home/student",
) -> ExecutionTrace:
    """Build a command-specific Linux execution path."""

    command = command_name.strip()
    base = command.split()[0]
    path = _path_target(command_line, base, cwd)

    if command == "pwd":
        return ExecutionTrace(
            command,
            "Shell built-in",
            "The shell asks the kernel for this process's current working directory.",
            (
                _n("terminal", "Terminal", "type pwd"),
                _n("shell", "Shell built-in", "no child process"),
                _n("kernel", "Kernel syscall", "getcwd()"),
                _n("process", "Process state", f"cwd: {cwd}"),
                _n("output", "stdout", "print path"),
            ),
            ("No network access", f"Process cwd: {cwd}", "Kernel: getcwd()"),
        )
    if command == "cd":
        return ExecutionTrace(
            command,
            "Shell built-in",
            "The shell resolves the directory and updates its own working-directory state.",
            (
                _n("terminal", "Terminal", "type cd"),
                _n("shell", "Shell built-in", "parse target"),
                _n("vfs", "Kernel VFS", "resolve path"),
                _n("folder", "Directory", path),
                _n("process", "Shell process", "update cwd"),
            ),
            ("No child utility", f"Directory: {path}", "Kernel: path resolution"),
        )
    if command in _PATH_STRING:
        operand = next(
            (token for token in _tokens(command_line)[1:] if not token.startswith("-")),
            path or "path",
        )
        if command == "basename":
            result = posixpath.basename(operand.rstrip("/")) or "/"
            operation = "keep the text after the final /"
        else:
            result = posixpath.dirname(operand.rstrip("/")) or "."
            operation = "keep the parent portion before the final /"
        return ExecutionTrace(
            command,
            "Path string transformation",
            "This command transforms the path text supplied as an argument. It does not open, delete, or modify that path.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell", "split command and arguments"),
                _n("process", f"{command} utility", "receive path text"),
                _n("filter", "String operation", operation),
                _n("output", "stdout", result),
            ),
            (f"Input text: {operand}", "Filesystem opened: none", "Filesystem changed: no"),
        )
    if "|" in command_line:
        stages = [stage.strip() for stage in command_line.split("|") if stage.strip()]
        first_stage = stages[0] if stages else command_line
        remaining = " → ".join(stages[1:]) if len(stages) > 1 else "stdout"
        source = _explicit_path_target(first_stage, cwd)
        source_detail = f"read {source}" if source else "produce records"
        return ExecutionTrace(
            command,
            "Shell pipeline",
            "The shell launches multiple processes and connects one process's stdout to the next process's stdin through kernel pipe buffers.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell", f"create {len(stages)}-stage pipeline"),
                _n("process", "First stage", f"{first_stage}: {source_detail}"),
                _n("socket", "Kernel pipe", "stdout → pipe buffer → stdin"),
                _n("filter", "Following stage(s)", remaining),
                _n("output", "stdout", "final pipeline result"),
            ),
            (
                f"Stages: {' | '.join(stages)}",
                "Kernel resource: anonymous pipe buffer",
                "No switch or router involved",
            ),
        )
    if command == "file":
        target = path or _DEFAULT_PATHS.get(base, cwd)
        return ExecutionTrace(
            command,
            "File type detection",
            "The utility reads identifying bytes and compares them with the local magic database; it does not rely only on the filename extension.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell", "launch file"),
                _n("process", "file utility", "request type detection"),
                _n("vfs", "Kernel VFS", "open/read target"),
                _n("file", "Target + magic rules", f"{target} + magic.mgc"),
                _n("output", "stdout", "identified file type"),
            ),
            (f"Target: {target}", "Reads file header/content", "Magic database: magic.mgc", "No content changed"),
        )
    if command in _FILE_LIST:
        target = path or cwd
        return ExecutionTrace(
            command,
            "Filesystem read",
            "A userspace utility asks the kernel to enumerate directory entries.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell", f"launch {base}"),
                _n("process", "Utility process", base),
                _n("vfs", "Kernel VFS", "openat()/getdents()"),
                _n("folder", "Directory tree", target),
                _n("output", "stdout", "names and metadata"),
            ),
            (f"Directory: {target}", "Kernel: VFS", "No network access"),
        )
    if command in _FILE_META:
        target = path or _DEFAULT_PATHS.get(base, cwd)
        return ExecutionTrace(
            command,
            "Filesystem metadata",
            "The utility resolves a path and reads inode, link, or file-type metadata.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell", f"launch {base}"),
                _n("process", "Utility process", base),
                _n("vfs", "Kernel VFS", "stat/readlink"),
                _n("file", "Path metadata", target),
                _n("output", "stdout", "formatted result"),
            ),
            (f"Path: {target}", "Kernel: inode/VFS metadata", "No file content changed"),
        )
    if command in _LOCAL_TEXT:
        target = path or _DEFAULT_PATHS.get(base, cwd)
        operation = "open()/read()"
        if command == "tee":
            operation = "read()/write()"
        return ExecutionTrace(
            command,
            "Local text processing",
            "The shell starts a utility, which reads virtual file data through the kernel VFS and writes results to stdout.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell", f"parse + launch {base}"),
                _n("process", "Utility process", base),
                _n("vfs", "Kernel VFS", operation),
                _n("file", "Target file", target),
                _n("output", "stdout", "filtered/formatted text"),
            ),
            (f"File: {target}", f"Userspace: {base}", f"Kernel: {operation}", "No network access"),
        )
    if command in _FILE_CHANGE:
        target = path or cwd
        return ExecutionTrace(
            command,
            "Filesystem change",
            "The utility requests a filesystem change; the kernel validates permissions and updates directory or inode state.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell", f"launch {base}"),
                _n("process", "Utility process", base),
                _n("security", "Permission check", "UID/GID + mode bits"),
                _n("vfs", "Kernel VFS", "update inode/dentry"),
                _n("folder", "Target path", target),
            ),
            (f"Target: {target}", "Kernel: VFS/inode", "State-changing example"),
        )
    if command in _ARCHIVE:
        target = path or cwd
        return ExecutionTrace(
            command,
            "Archive/compression",
            "The utility reads source paths through the VFS, transforms the byte stream, and writes an archive or decompressed file.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Archive utility", command),
                _n("vfs", "Kernel VFS", "open/read source"),
                _n("folder", "Source paths", target),
                _n("archive", "Compression stream", "encode/decode"),
                _n("file", "Archive output", "destination file"),
            ),
            (f"Source: {target}", "Filesystem read/write", "No network unless remote path used"),
        )
    if command in _MEMORY:
        return ExecutionTrace(
            command,
            "Memory inspection",
            "The utility reads kernel-exported memory counters rather than scanning application files.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Utility process", "free"),
                _n("procfs", "procfs", "/proc/meminfo"),
                _n("memory", "Kernel memory", "RAM + swap counters"),
                _n("output", "stdout", "human-readable totals"),
            ),
            ("Virtual file: /proc/meminfo", "Kernel memory manager", "No network access"),
        )
    if command == "df":
        target = path or "/"
        return ExecutionTrace(
            command,
            "Filesystem capacity",
            "df asks the kernel for filesystem statistics for the mount containing the selected path.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Utility process", "df"),
                _n("kernel", "Kernel syscall", "statvfs()"),
                _n("vfs", "VFS mount", target),
                _n("storage", "Filesystem", "blocks used/free"),
                _n("output", "stdout", "capacity table"),
            ),
            (f"Mount lookup: {target}", "Kernel: statvfs/VFS", "Block filesystem counters"),
        )
    if command in _STORAGE:
        return ExecutionTrace(
            command,
            "Storage subsystem",
            "The utility reads mount, filesystem, partition, or block-device state exposed by the kernel.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Storage utility", command),
                _n("procfs", "Kernel interfaces", "/proc + /sys/block"),
                _n("storage", "Block layer", "devices + filesystems"),
                _n("vfs", "Mount table", "/proc/self/mountinfo"),
                _n("output", "stdout", "storage state"),
            ),
            ("Kernel: block layer", "Virtual files: /proc and /sys", "May be state-changing for mount tools"),
        )
    if command in _PROCESS_READ:
        return ExecutionTrace(
            command,
            "Process inspection",
            "The utility reads process and file-descriptor state exported by the kernel.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Utility process", command),
                _n("procfs", "procfs", "/proc/<pid>"),
                _n("kernel", "Kernel process table", "PID/scheduler state"),
                _n("output", "stdout", "process snapshot"),
            ),
            ("Virtual files: /proc", "Kernel scheduler/process table", "No network access"),
        )
    if command in _PROCESS_CHANGE:
        return ExecutionTrace(
            command,
            "Process control",
            "The utility resolves a process and asks the kernel to change priority, background state, or deliver a signal.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell/job control", command),
                _n("procfs", "Process lookup", "/proc/<pid>"),
                _n("kernel", "Kernel scheduler", "signal/priority"),
                _n("process", "Target process", "PID or job"),
                _n("output", "Shell status", "result"),
            ),
            ("Kernel process table", "Target PID/job", "State-changing example"),
        )
    if command in _PERFORMANCE:
        return ExecutionTrace(
            command,
            "Performance counters",
            "The utility samples kernel counters from procfs, sysfs, or performance-event interfaces.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Monitoring utility", command),
                _n("procfs", "Kernel counters", "/proc + /sys"),
                _n("kernel", "Scheduler/I/O", "CPU, load, wait"),
                _n("memory", "Sample window", "aggregate metrics"),
                _n("output", "stdout", "performance report"),
            ),
            ("Virtual files: /proc and /sys", "Kernel counters", "Repeated samples improve diagnosis"),
        )
    if command in _SERVICE:
        unit = _service_target(command_line)
        return ExecutionTrace(
            command,
            "Service manager",
            "The client contacts systemd over its control interface; systemd reads unit state and inspects the managed process.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "systemctl/service", "client utility"),
                _n("socket", "D-Bus/control socket", "/run/systemd/private"),
                _n("service", "systemd PID 1", "unit manager"),
                _n("file", "Unit + process", unit),
                _n("output", "stdout", "status/action result"),
            ),
            ("Socket: /run/systemd/private", f"Unit: {unit}", "Manager: systemd PID 1"),
        )
    if command in _JOURNAL:
        return ExecutionTrace(
            command,
            "Journal query",
            "The utility requests indexed records from the systemd journal and applies unit, time, priority, or boot filters.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Journal client", command),
                _n("socket", "Journal API", "/run/systemd/journal"),
                _n("journal", "Journal storage", "/var/log/journal"),
                _n("filter", "Query filters", "unit/time/priority"),
                _n("output", "stdout", "matching records"),
            ),
            ("Runtime socket: /run/systemd/journal", "Persistent data: /var/log/journal", "Read-only query"),
        )
    if command in _LOG_FILES:
        resource = "/dev/kmsg" if command == "dmesg" else "/var/log"
        return ExecutionTrace(
            command,
            "Logging subsystem",
            "The command reads, writes, or rotates log records through kernel or syslog interfaces.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Logging utility", command),
                _n("socket", "Log interface", "/dev/log or kernel ring"),
                _n("journal", "Log storage", resource),
                _n("output", "Result", "records/action"),
            ),
            (f"Log resource: {resource}", "syslog/journal pipeline", "May change logs for logger/logrotate"),
        )
    if command in _DNS:
        target = _network_target(command_line)
        return ExecutionTrace(
            command,
            "DNS lookup",
            "The resolver reads local DNS configuration, sends a DNS query, and formats the answer.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Resolver client", command),
                _n("file", "Resolver config", "/etc/resolv.conf"),
                _n("socket", "UDP/TCP 53", "kernel socket"),
                _n("dns", "DNS server", target),
                _n("output", "stdout", "resource records"),
            ),
            ("File: /etc/resolv.conf", "Protocol: DNS UDP/TCP 53", f"Query: {target}"),
            networked=True,
        )
    if command in _NETWORK_REMOTE:
        target = _network_target(command_line)
        client_detail = "ICMP/TTL probe" if command in {"ping", "tracepath", "traceroute"} else "client request"
        return ExecutionTrace(
            command,
            "Network request",
            "A userspace client creates sockets; the kernel network stack routes packets through an interface to a remote endpoint.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Client process", f"{command}: {client_detail}"),
                _n("socket", "Socket layer", "DNS/TCP/UDP/ICMP"),
                _n("network", "Kernel network stack", "routing + protocol"),
                _n("nic", "Network interface", "packet transmit/receive"),
                _n("remote", "Remote endpoint", target),
            ),
            (f"Target: {target}", "Kernel: socket + routing", "Interface/NIC + external network"),
            networked=True,
        )
    if command in _NETWORK_LOCAL:
        return ExecutionTrace(
            command,
            "Local network inspection",
            "The utility queries kernel network state through netlink, packet capture, or interface APIs.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Network utility", command),
                _n("socket", "Kernel interface", "netlink/packet socket"),
                _n("network", "Network stack", "routes/sockets/neighbours"),
                _n("nic", "Interface state", "link/address/counters"),
                _n("output", "stdout", "network evidence"),
            ),
            ("Kernel: netlink/socket tables", "Interface state", "No remote request for read-only inspection"),
        )
    if command in _FIREWALL:
        return ExecutionTrace(
            command,
            "Firewall rules",
            "The command communicates with the kernel netfilter subsystem to inspect or update packet-filtering rules.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Firewall CLI", command),
                _n("socket", "Netlink interface", "userspace ↔ kernel"),
                _n("security", "Netfilter hooks", "input/forward/output"),
                _n("file", "Ruleset", "tables/chains/rules"),
                _n("output", "stdout", "rules or action result"),
            ),
            ("Kernel: netfilter", "Ruleset: tables/chains", "May change packet handling"),
        )
    if command in _CONTAINERS:
        return ExecutionTrace(
            command,
            "Container runtime",
            "The Docker CLI sends an API request over a local Unix socket; the daemon inspects container namespaces and cgroups.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Docker CLI", command),
                _n("socket", "Unix socket", "/var/run/docker.sock"),
                _n("container", "Docker daemon", "container API"),
                _n("kernel", "Namespaces/cgroups", "process + resource isolation"),
                _n("output", "stdout", "container result"),
            ),
            ("Socket: /var/run/docker.sock", "Daemon: dockerd", "Kernel: namespaces/cgroups"),
        )
    if command in _USERS_READ:
        return ExecutionTrace(
            command,
            "Identity lookup",
            "The utility reads process credentials and resolves names through NSS user and group databases.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Identity utility", command),
                _n("kernel", "Process credentials", "UID/GID/groups"),
                _n("user", "NSS lookup", "/etc/passwd + /etc/group"),
                _n("output", "stdout", "identity result"),
            ),
            ("Kernel credentials", "Files: /etc/passwd, /etc/group", "No network in this simulation"),
        )
    if command in _USERS_CHANGE:
        return ExecutionTrace(
            command,
            "Account/privilege control",
            "PAM, NSS, and account tools validate identity and may update protected account databases or credentials.",
            (
                _n("terminal", "Terminal", command_line),
                _n("security", "PAM/privilege", "authenticate/authorize"),
                _n("user", "Account database", "/etc/passwd + /etc/shadow"),
                _n("kernel", "Credential state", "UID/GID/capabilities"),
                _n("output", "Result", "success or denial"),
            ),
            ("PAM/NSS", "Protected files: /etc/passwd, /etc/shadow", "State-changing example"),
        )
    if command in _PERMISSIONS:
        target = path or cwd
        return ExecutionTrace(
            command,
            "Permission metadata",
            "The utility resolves a path, checks privileges, and reads or updates inode ownership, mode, or ACL metadata.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Permission utility", command),
                _n("security", "Credential check", "UID/GID/capabilities"),
                _n("vfs", "Kernel VFS", "inode/ACL operation"),
                _n("file", "Target metadata", target),
                _n("output", "Result", "metadata/action"),
            ),
            (f"Target: {target}", "Kernel: inode/ACL", "May change access control"),
        )
    if command in _KERNEL:
        resource = {
            "sysctl": "/proc/sys",
            "lsmod": "/proc/modules",
            "modinfo": "/lib/modules",
            "modprobe": "/lib/modules",
            "hostname": "/proc/sys/kernel/hostname",
            "date": "kernel clock",
            "uname": "kernel utsname",
        }.get(command, "/proc or /sys")
        return ExecutionTrace(
            command,
            "Kernel interface",
            "The utility reads or updates kernel-exported identity, parameters, clock, or module state.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "System utility", command),
                _n("procfs", "Kernel interface", resource),
                _n("kernel", "Kernel subsystem", "identity/parameter/module"),
                _n("output", "stdout", "kernel state"),
            ),
            (f"Resource: {resource}", "Kernel subsystem", "Some commands can change kernel state"),
        )
    if command in _SECURITY:
        return ExecutionTrace(
            command,
            "Security subsystem",
            "The utility communicates with audit or SELinux interfaces and reads policy, labels, or security-event data.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Security utility", command),
                _n("security", "Kernel security", "audit/LSM hooks"),
                _n("file", "Policy or audit data", "/etc/selinux or /var/log/audit"),
                _n("output", "stdout", "security state"),
            ),
            ("Kernel: audit/LSM", "Policy/log files", "May change policy or labels"),
        )
    if command in _SCHEDULING:
        return ExecutionTrace(
            command,
            "Job scheduling",
            "The utility writes or reads a schedule, and a daemon later launches the job at the requested time.",
            (
                _n("terminal", "Terminal", command_line),
                _n("process", "Scheduling utility", command),
                _n("file", "Schedule/spool", "/var/spool/cron or /var/spool/at"),
                _n("service", "Scheduler daemon", "cron/atd"),
                _n("process", "Future job", "spawn at trigger"),
                _n("output", "stdout", "schedule result"),
            ),
            ("Spool files", "Daemon: cron/atd", "Execution occurs later"),
        )
    if command in _SHELL_LOOKUP:
        resource = "$PATH" if command in {"which", "type", "whereis"} else "/usr/share/man"
        return ExecutionTrace(
            command,
            "Shell/help lookup",
            "The shell or utility searches command lookup paths or the local manual-page database.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell lookup", command),
                _n("file", "Search source", resource),
                _n("vfs", "Kernel VFS", "read directories/files"),
                _n("output", "stdout", "resolved path/help"),
            ),
            (f"Lookup source: {resource}", "Local filesystem", "No network access"),
        )
    if command in _RESOURCES:
        return ExecutionTrace(
            command,
            "Process resource limits",
            "The shell or utility reads or changes resource limits stored in process kernel state.",
            (
                _n("terminal", "Terminal", command_line),
                _n("shell", "Shell/utility", command),
                _n("kernel", "prlimit interface", "RLIMIT values"),
                _n("process", "Target process", "soft/hard limits"),
                _n("output", "stdout", "limit table"),
            ),
            ("Kernel: RLIMIT/prlimit", "Target process", "May constrain future operations"),
        )

    # Safe generic fallback based on a normal userspace process and kernel interface.
    return ExecutionTrace(
        command,
        "Userspace command",
        "The shell parses the command, launches a utility, and the utility requests data or an operation from the kernel.",
        (
            _n("terminal", "Terminal", command_line),
            _n("shell", "Shell", "parse arguments"),
            _n("process", "Utility process", command),
            _n("kernel", "Kernel interface", "system call/API"),
            _n("output", "stdout/stderr", "result"),
        ),
        ("Userspace utility", "Kernel interface", "Exact resources depend on arguments"),
    )


def _first_touchpoint(trace: ExecutionTrace) -> str:
    return trace.touchpoints[0] if trace.touchpoints else trace.command


def _example_changes_state(command: str, command_line: str) -> bool:
    """Return whether the reviewed example would change real system state."""

    line = command_line.strip()
    if command in _FILE_CHANGE:
        return True
    if command in {"pkill", "kill", "killall", "nice", "renice", "nohup", "bg", "fg"}:
        return True
    if command in {"chmod", "chown", "chgrp", "setfacl", "umask"}:
        return True
    if command in {"useradd", "usermod", "groupadd", "su"}:
        return True
    if command in {"umount", "at", "flock", "logger"}:
        return True
    if command in {"tar", "gzip", "gunzip", "zip"}:
        return True
    if command == "tee":
        return True
    if command == "systemctl":
        return any(action in line.split() for action in {"start", "stop", "restart", "reload", "enable", "disable"})
    if command == "service":
        return any(action in line.split() for action in {"start", "stop", "restart", "reload"})
    if command in {"ufw", "nft", "iptables"}:
        return not any(word in line.split() for word in {"status", "list", "list-rules", "-L"})
    if command == "restorecon":
        return not any(token.startswith("-") and "n" in token[1:] for token in line.split())
    if command == "modprobe":
        return "--dry-run" not in line.split() and "-n" not in line.split()
    if command == "logrotate":
        return "-d" not in line.split() and "--debug" not in line.split()
    if command == "rsync":
        return not any(flag in line.split() for flag in {"-n", "--dry-run", "-aHvn"})
    return False


def _effect_summary(
    command: str,
    command_line: str,
    trace: ExecutionTrace,
    *,
    cwd: str,
) -> EffectSummary:
    """Create a plain-language before/action/result/impact explanation."""

    tokens = _tokens(command_line)
    operands = [token for token in tokens[1:] if not token.startswith("-")]
    operand = operands[-1] if operands else command_line

    if command == "basename":
        result = posixpath.basename(operand.rstrip("/")) or "/"
        return EffectSummary(
            input_value=f"Path text: {operand}",
            operation="Keep only the characters after the final slash.",
            result=f"Print: {result}",
            impact="No file or directory is opened, removed, renamed, or changed.",
        )
    if command == "dirname":
        result = posixpath.dirname(operand.rstrip("/")) or "."
        return EffectSummary(
            input_value=f"Path text: {operand}",
            operation="Keep the parent portion before the final slash.",
            result=f"Print: {result}",
            impact="No directory is opened, removed, renamed, or changed.",
        )
    if command == "pwd":
        return EffectSummary(
            input_value=f"Current shell directory: {cwd}",
            operation="Ask the kernel for the shell process's current working directory.",
            result=f"Print: {cwd}",
            impact="Read-only; the current directory is not changed.",
        )
    if command == "cd":
        return EffectSummary(
            input_value=f"Directory argument: {operand}",
            operation="Resolve the directory and update the shell's current-directory state.",
            result=f"New working directory: {_path_target(command_line, command, cwd)}",
            impact="Changes only the simulated shell session; it does not alter directory contents.",
        )

    result_by_kind = {
        "Filesystem read": "Print matching directory entries or paths.",
        "Filesystem metadata": "Print metadata or a resolved path.",
        "File type detection": "Print the detected file type.",
        "Shell pipeline": "Print the result produced by the final pipeline stage.",
        "Local text processing": "Print filtered, transformed, or counted text.",
        "Filesystem change": "Report the requested filesystem state change.",
        "Archive/compression": "Create, inspect, or extract an archive stream.",
        "Process inspection": "Print a process or resource snapshot.",
        "Process control": "Report the requested process-control action.",
        "Performance counters": "Print sampled performance measurements.",
        "Service manager": "Print service-manager status or action results.",
        "Journal query": "Print matching journal or coredump records.",
        "Logging subsystem": "Print log records or report a logging action.",
        "DNS lookup": "Print DNS resource records or resolution details.",
        "Network request": "Print a response, route, transfer, or connectivity result.",
        "Local network inspection": "Print local kernel network state.",
        "Firewall rules": "Print or update the packet-filtering ruleset.",
        "Container runtime": "Print container runtime state or command output.",
        "Identity lookup": "Print the resolved user, group, or session identity.",
        "Account/privilege control": "Report the account or privilege operation.",
        "Permission metadata": "Print or update ownership, mode, or ACL state.",
        "Kernel interface": "Print kernel-exported state or report a requested change.",
        "Security subsystem": "Print audit or security-policy state.",
        "Job scheduling": "Print or update a scheduled-job definition.",
        "Shell/help lookup": "Print the resolved executable, shell definition, or manual entry.",
        "Process resource limits": "Print or update process resource limits.",
        "Memory inspection": "Print memory and swap counters.",
        "Filesystem capacity": "Print filesystem capacity counters.",
        "Storage subsystem": "Print block-device, mount, or storage state.",
    }
    if trace.networked:
        impact = "Generates conceptual network activity in the lesson; the simulator makes no real network request."
    elif _example_changes_state(command, command_line):
        impact = "This exact example would change real Linux state; OpsReady shows only a synthetic result."
    else:
        impact = "Read-only in this example; the simulator does not change the host system."
    return EffectSummary(
        input_value=f"Command input: {command_line}",
        operation=trace.summary,
        result=result_by_kind.get(trace.kind, f"Return: {trace.nodes[-1].detail if trace.nodes else 'command result'}"),
        impact=impact,
    )


def build_execution_trace(
    command_name: str,
    command_line: str,
    *,
    cwd: str = "/home/student",
) -> ExecutionTrace:
    """Build and enrich a command-specific Linux execution path."""

    trace = _build_execution_trace(command_name, command_line, cwd=cwd)
    if trace.effect is not None:
        return trace
    return replace(
        trace,
        effect=_effect_summary(command_name.strip(), command_line, trace, cwd=cwd),
    )
