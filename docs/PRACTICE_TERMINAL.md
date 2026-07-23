# Interactive Practice Terminal

## Purpose

Version 1.7.1 includes a safe, stateful Linux practice terminal inside Command Lab. It is designed to teach command syntax, path reasoning, text inspection, and evidence collection without exposing the Streamlit host.

The practice terminal is a simulator. It does not call `subprocess`, `os.system`, a shell interpreter, a network client, or the hosting filesystem.

## Reviewed command set

Practice mode supports 25 commands:

```text
pwd, ls, cd, cat, head, tail, wc, grep, cut, sort, uniq,
awk, sed, find, file, stat, whoami, id, uname, hostname,
date, df, free, ps, uptime
```

The wider 150-command catalogue remains available through **Guided command explorer**.

## Virtual filesystem

Every terminal reset creates an in-memory learning environment containing reviewed synthetic files under:

```text
/etc
/home/student
/opt/app
/var/log
```

Commands such as `cd`, `pwd`, and relative file reads remain stateful during the current browser session. No path maps to the hosting server.

## Run limit

- Each reset starts with 10 supported command attempts.
- A supported command consumes one attempt even when it returns a normal file or syntax error.
- Blank, blocked, unsupported, traversal, and over-limit requests do not consume an attempt.
- Reset creates a fresh virtual filesystem and restores the 10 attempts.
- This is a learning-session limit, not identity-based enforcement. A visitor can reset or start another browser session.

## Blocked input

The simulator blocks:

- shell chaining and separators (`;`, `&&`, `||`)
- pipelines and redirection (`|`, `>`, `>>`, `<`)
- command substitution and shell expansion
- shell interpreters and programming runtimes
- network clients and remote-access commands
- process control, service control, mounting, and shutdown commands
- destructive or change-oriented filesystem commands
- parent-directory traversal using `..`

Blocked input is explained to the learner and is never forwarded to an operating-system shell.

## Scenario-dependent commands

`df`, `free`, `ps`, and `uptime` use the latest Health Dashboard snapshot when one exists. This connects terminal evidence with the server-health simulation while keeping the data synthetic.

## Learner guidance

After every supported attempt, the app displays:

- the command and Linux-style output;
- a plain-language explanation of what happened;
- a recommended next command or diagnostic step;
- session history and remaining attempts.

## Extending the terminal

Add a command only after implementing:

1. strict parsing for reviewed options;
2. virtual-data execution only;
3. normal error behaviour;
4. learner explanation and next-step guidance;
5. tests for valid syntax, invalid syntax, injection attempts, and run-limit behaviour.

Do not add a generic shell fallback.

## Command-specific execution trace

After a successful command, the app builds a trace from the command and its arguments rather than displaying one generic network diagram.

Examples:

- `pwd`: terminal → shell built-in → `getcwd()` → process current directory → stdout
- `cat /etc/os-release`: terminal → shell → `cat` process → VFS `open/read` → `/etc/os-release` → stdout
- `free -m`: terminal → `free` process → `/proc/meminfo` → kernel memory manager → stdout
- `systemctl status nginx`: terminal → `systemctl` → `/run/systemd/private` → systemd PID 1 → `nginx.service` → output
- `ping 8.8.8.8`: terminal → ping process → socket layer → kernel network stack → interface → remote target

The trace is conceptual and read-only. It makes Linux layers visible but does not inspect the hosting server.
## Plain-language execution explanation

Guided traces now separate four ideas before the under-the-hood diagram:

- **Input:** the exact path, target, or command supplied
- **Action:** what the command actually does
- **Result:** what is printed or changed
- **System effect:** whether the example is read-only, state-changing, or network-facing

Path-text tools are distinguished from filesystem tools. For example, `basename` and `dirname` process argument text only; they do not open or remove the named path.
## Visible execution replay

After a successful Practice or Guided result, the execution map shows a large orange command token moving through the numbered Linux touchpoints. The route is animated once when the command is run. **Replay simulation** restarts only that motion; it does not execute the command again, consume another terminal attempt, change the output, or update progress.

