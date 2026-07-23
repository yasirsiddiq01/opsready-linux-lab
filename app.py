from __future__ import annotations

import html
import os
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from opsready_lab.catalog.commands import COMMANDS, LEVELS, command_names, learning_guide
from opsready_lab.catalog.exercises import EXERCISES
from opsready_lab.catalog.incidents import INCIDENTS, incidents_for_level
from opsready_lab.config import APP_NAME, APP_VERSION
from opsready_lab.services.assessment_engine import (
    AssessmentGenerationError,
    AssessmentTest,
    build_curated_test,
    curated_bank_size,
    load_test,
    rebuild_curated_test,
    save_test,
)
from opsready_lab.services.commercial import CommercialSettings, is_email, is_https_url, load_commercial_settings
from opsready_lab.services.execution_trace import build_execution_trace
from opsready_lab.services.feedback import create_feedback_record, submit_feedback, validate_feedback
from opsready_lab.services.guided_output import guided_output_for
from opsready_lab.services.practice_terminal import (
    MAX_TERMINAL_RUNS,
    SUPPORTED_COMMANDS,
    TerminalResult,
    create_terminal_state,
    execute_command,
    normalise_terminal_state,
    prompt_for_state,
    runs_remaining,
)
from opsready_lab.services.progress import (
    initialise_progress,
    record_command,
    record_exercise,
    record_incident,
    reset_progress,
    score_percent,
)
from opsready_lab.ui.animations import execution_trace_diagram, hero_demo, operational_flow
from opsready_lab.ui.theme import apply_theme, hero, learning_card, panel, terminal

st.set_page_config(page_title=APP_NAME, page_icon="🐧", layout="wide", initial_sidebar_state="auto")
apply_theme()
initialise_progress(st.session_state)
if "feedback_session_id" not in st.session_state:
    st.session_state.feedback_session_id = str(uuid4())


def commercial_settings() -> CommercialSettings:
    """Load non-secret commercial links and launch gates from Streamlit secrets or environment variables."""

    values: dict[str, object] = {}
    try:
        commercial_section = st.secrets.get("commercial", {})
        values = dict(commercial_section) if commercial_section else {}
    except (FileNotFoundError, KeyError, TypeError):
        values = {}
    return load_commercial_settings(values)


def progress_sidebar() -> None:
    commands = len(st.session_state.completed_commands)
    incidents = len(st.session_state.completed_incidents)
    answered = len(st.session_state.answered_exercises)
    percent = score_percent(int(st.session_state.score), int(st.session_state.possible_score))
    st.markdown("### Session progress")
    st.metric("Score", f"{st.session_state.score}/{st.session_state.possible_score}")
    st.progress(percent / 100 if percent else 0.0, text=f"Accuracy: {percent}%")
    st.caption(f"Commands explored: {commands}/{len(COMMANDS)}")
    st.caption(f"Incidents completed: {incidents}/{len(INCIDENTS)}")
    st.caption(f"Assessment answers completed: {answered} • validated bank: {len(EXERCISES)}")
    if st.button("Reset session progress", width="stretch", key="reset_session_progress"):
        reset_progress(st.session_state)
        for key in list(st.session_state):
            if (
                key.startswith("assessment_results_")
                or key.startswith("assessment_choice_")
                or key
                in {
                    "active_assessment_test",
                    "assessment_generation_notice",
                    "practice_terminal_state",
                    "practice_terminal_last_result",
                    "practice_terminal_input",
                    "practice_terminal_run_token",
                }
            ):
                st.session_state.pop(key, None)
        for query_key in [
            "assessment_test",
            "assessment_level",
            "assessment_source",
            "assessment_seed",
            "assessment_count",
        ]:
            if query_key in st.query_params:
                del st.query_params[query_key]
        st.rerun()


def open_workspace_tab(tab_name: str) -> None:
    """Open a workspace section from an Overview call-to-action button."""

    st.session_state.workspace_tab = tab_name


def compact_workspace_header(title: str, body: str) -> None:
    st.markdown(
        f"<div class='workspace-compact-header'><small>Learning Workspace · {html.escape(APP_VERSION)}</small>"
        f"<h2>{html.escape(title)}</h2><span>{html.escape(body)}</span></div>",
        unsafe_allow_html=True,
    )


def overview_hero_section() -> None:
    st.session_state.setdefault("hero_replay_token", 0)
    st.session_state.setdefault("hero_paused", False)
    hero_demo(
        paused=bool(st.session_state.hero_paused),
        replay_token=int(st.session_state.hero_replay_token),
    )

    c1, c2, c3 = st.columns(3)
    c1.button(
        "Start Learning",
        type="primary",
        width="stretch",
        on_click=open_workspace_tab,
        args=("Command Lab",),
    )
    c2.button(
        "Run Health Simulation",
        width="stretch",
        on_click=open_workspace_tab,
        args=("Health Dashboard",),
    )
    c3.button(
        "Solve an Incident",
        width="stretch",
        on_click=open_workspace_tab,
        args=("Incident Lab",),
    )

    control_a, control_b, spacer = st.columns([1, 1, 4])
    paused = control_a.toggle("Pause animation", value=bool(st.session_state.hero_paused), key="hero_pause_control")
    if paused != bool(st.session_state.hero_paused):
        st.session_state.hero_paused = paused
        st.rerun()
    if control_b.button("Replay", width="stretch"):
        st.session_state.hero_replay_token = int(st.session_state.hero_replay_token) + 1
        st.rerun()
    spacer.caption("The overview animation uses inline SVG and CSS; it does not load an external video.")


def overview_tab() -> None:
    st.markdown("### What you can practise")
    a, b, c = st.columns(3)
    with a:
        panel(
            "Explore commands",
            "Learn what each command does, when to use it, how to read its output, and which evidence to collect next.",
        )
    with b:
        panel(
            "Diagnose systems",
            "Change CPU, memory, disk, load, I/O, and connection measurements and see how the simulated evidence changes.",
        )
    with c:
        panel(
            "Investigate incidents",
            "Work through realistic symptoms, event logs, root causes, and recovery actions using evidence-first troubleshooting.",
        )

    st.markdown("### Recommended first session")
    st.write(
        "Start with a Beginner command, run one health scenario, solve one matching incident, and then answer the Beginner assessment. "
        "Use the Feedback page after you have tried at least two sections."
    )
    st.warning(
        "This is an educational simulator. Thresholds and recommendations are learning aids, not universal production operating limits."
    )


def practice_health_context() -> dict[str, object]:
    """Return the latest simulated health values for terminal system commands."""

    snapshot = st.session_state.get("health_snapshot")
    if isinstance(snapshot, dict):
        return snapshot
    return {
        "cpu": st.session_state.get("health_cpu", 32),
        "memory": st.session_state.get("health_memory", 54),
        "disk": st.session_state.get("health_disk", 61),
        "load": st.session_state.get("health_load", 1.4),
        "io_wait": st.session_state.get("health_io_wait", 3),
        "connections": st.session_state.get("health_connections", 180),
    }


PRACTICE_EXAMPLES: dict[str, str] = {
    "Show current directory": "pwd",
    "List files and permissions": "ls -la",
    "Read operating-system identity": "cat /etc/os-release",
    "Inspect application errors": "grep -in error /opt/app/app.log",
    "Read recent system log entries": "tail -n 3 /var/log/syslog",
    "Extract users and login shells": "awk -F: '{print $1, $7}' /etc/passwd",
    "Find log files": "find /var/log -type f -name '*.log'",
    "Inspect disk capacity": "df -h /",
    "Inspect memory": "free -m",
    "Inspect processes": "ps aux",
}


def insert_practice_example() -> None:
    """Insert the selected reviewed example into the terminal input."""

    label = st.session_state.get("practice_example_choice", "Show current directory")
    st.session_state.practice_terminal_input = PRACTICE_EXAMPLES.get(label, "pwd")


def command_mode_guide() -> None:
    st.markdown(
        """
        <div class='command-mode-guide'>
          <article><b>Practice terminal</b><span>Type one of 25 safe read-only commands against a stateful virtual Linux filesystem. Use this for hands-on path and output practice.</span></article>
          <article><b>Guided command explorer</b><span>Select any of 150 commands. The app explains the command and shows the Linux subsystem, file, service, process, or network path it conceptually touches.</span></article>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_interactive_terminal() -> None:
    state = normalise_terminal_state(st.session_state.get("practice_terminal_state"))
    st.session_state.practice_terminal_state = state
    if "practice_terminal_input" not in st.session_state:
        st.session_state.practice_terminal_input = "pwd"

    st.markdown("### Practice terminal")
    st.caption(
        "Safe virtual Linux session. One reviewed command at a time; no host shell, server filesystem, or network access."
    )
    st.markdown(
        f"<div class='practice-status'><span>Runs: {runs_remaining(state)}/{MAX_TERMINAL_RUNS}</span>"
        f"<span>Directory: {html.escape(str(state['cwd']))}</span>"
        f"<span>Supported: {len(SUPPORTED_COMMANDS)}</span></div>",
        unsafe_allow_html=True,
    )

    example_col, reset_col = st.columns([4, 1])
    example_col.selectbox(
        "Example command — selecting an item inserts it into the terminal",
        list(PRACTICE_EXAMPLES),
        key="practice_example_choice",
        on_change=insert_practice_example,
        help="Choose a reviewed task. Its command is inserted below automatically; press Run when ready.",
    )
    if reset_col.button("Reset terminal", width="stretch"):
        st.session_state.practice_terminal_state = create_terminal_state()
        st.session_state.practice_terminal_input = "pwd"
        st.session_state.pop("practice_terminal_last_result", None)
        st.session_state.pop("practice_terminal_trace_cwd", None)
        st.session_state.practice_terminal_run_token = 0
        st.session_state.practice_terminal_animation_token = 0
        st.rerun()

    with st.form("interactive_practice_terminal", clear_on_submit=False):
        command_col, run_col = st.columns([5, 1])
        command_line = command_col.text_input(
            "Linux command",
            key="practice_terminal_input",
            placeholder="Try: grep -in error /opt/app/app.log",
            label_visibility="collapsed",
            help="One reviewed command only. Chaining, redirection, pipelines, network clients, process control, and destructive commands are blocked.",
        )
        submitted = run_col.form_submit_button(
            "Run",
            type="primary",
            width="stretch",
            disabled=runs_remaining(state) <= 0,
        )

    if submitted:
        st.session_state.practice_terminal_trace_cwd = str(state["cwd"])
        updated_state, result = execute_command(
            state,
            command_line,
            health=practice_health_context(),
        )
        st.session_state.practice_terminal_state = updated_state
        st.session_state.practice_terminal_last_result = result.to_dict()
        if result.consumed_run:
            st.session_state.practice_terminal_run_token = (
                int(st.session_state.get("practice_terminal_run_token", 0)) + 1
            )
            st.session_state.practice_terminal_animation_token = (
                int(st.session_state.get("practice_terminal_animation_token", 0)) + 1
            )
            if result.base_command in COMMANDS:
                record_command(st.session_state, result.base_command)
        st.rerun()

    result_data = st.session_state.get("practice_terminal_last_result")
    if isinstance(result_data, dict):
        result = TerminalResult(**result_data)
        if result.status == "blocked":
            st.warning(result.output)
        elif result.status == "unsupported":
            st.info(result.output)
        elif result.status == "limit":
            st.error(result.output)
        else:
            trace = build_execution_trace(
                result.base_command,
                result.command,
                cwd=str(st.session_state.get("practice_terminal_trace_cwd", "/home/student")),
            )
            replay_col, replay_note_col = st.columns([1, 3])
            replay_key = f"replay_practice_{len(state.get('history', []))}_{result.base_command}"
            if replay_col.button("Replay simulation", width="stretch", key=replay_key):
                st.session_state.practice_terminal_animation_token = (
                    int(st.session_state.get("practice_terminal_animation_token", 0)) + 1
                )
                st.rerun()
            replay_note_col.caption(
                "Replays the moving command token only. It does not use another terminal run or change the result."
            )
            trace_col, output_col = st.columns([1.35, 1])
            with trace_col:
                execution_trace_diagram(
                    trace,
                    run_token=int(st.session_state.get("practice_terminal_animation_token", 1)),
                )
            with output_col:
                st.markdown("<div class='compact-result-title'>Terminal result</div>", unsafe_allow_html=True)
                if result.status == "error":
                    st.caption("The simulator returned a normal Linux path or command error.")
                terminal(
                    result.command,
                    result.output,
                    prompt=prompt_for_state(state),
                    compact=True,
                )
            why_col, next_col = st.columns(2)
            with why_col:
                learning_card("What happened", result.explanation)
            with next_col:
                learning_card("Try next", result.next_step)

    help_col, history_col = st.columns(2)
    with help_col.expander("Supported commands and examples", expanded=False):
        st.code(
            """pwd                         ls -la
cd /var/log                 cat /etc/hosts
head -n 3 /opt/app/app.log  tail -n 3 /var/log/syslog
wc -l /var/log/auth.log     grep -in error /opt/app/app.log
cut -d: -f1,7 /etc/passwd  sort /etc/hosts
uniq -c /etc/hosts          awk -F: '{print $1, $7}' /etc/passwd
sed -n '1,3p' /opt/app/app.log
find /var/log -type f -name '*.log'
file /home/student/scripts/health_check.sh
stat /opt/app/config.ini    whoami
id                          uname -a
hostname                    date
df -h /                     free -m
ps aux                      uptime""",
            language="bash",
        )
    history = state.get("history", [])
    with history_col.expander(f"Command history ({len(history)}/{MAX_TERMINAL_RUNS})", expanded=False):
        if not history:
            st.caption("No supported command attempts have been recorded.")
        else:
            for entry in reversed(history):
                st.markdown(f"**{entry['index']}.** `{entry['command']}` · {str(entry['status']).title()}")


def render_guided_explorer() -> None:
    select_a, select_b = st.columns([1, 2])
    level = select_a.segmented_control("Level", LEVELS, default="Beginner", key="command_level") or "Beginner"
    names = command_names(level)
    command = select_b.selectbox("Command", names, key="command_select")
    item = COMMANDS[command]
    guide = learning_guide(command)

    c1, c2, c3 = st.columns(3)
    with c1:
        learning_card("What it does", str(item["summary"]))
    with c2:
        learning_card("When to use it", guide["when"])
    with c3:
        learning_card("What to look for", guide["read"])

    command_col, run_col = st.columns([5, 1])
    command_col.code(str(item["example"]), language="bash")
    run_clicked = run_col.button("Run guide", type="primary", width="stretch", key=f"run_{command}")
    if run_clicked:
        record_command(st.session_state, command)
        st.session_state.last_command = command
        st.session_state.command_run_token = int(st.session_state.get("command_run_token", 0)) + 1
        st.session_state.command_animation_token = int(st.session_state.get("command_animation_token", 0)) + 1

    if st.session_state.get("last_command") != command:
        st.info("Run the reviewed example to see its command-specific Linux execution path and simulated output.")
        return

    trace = build_execution_trace(command, str(item["example"]))
    replay_col, replay_note_col = st.columns([1, 3])
    if replay_col.button("Replay simulation", width="stretch", key=f"replay_guided_{command}"):
        st.session_state.command_animation_token = int(st.session_state.get("command_animation_token", 0)) + 1
        st.rerun()
    replay_note_col.caption("Replays the moving command token only. The reviewed output and progress stay unchanged.")
    trace_col, output_col = st.columns([1.35, 1])
    with trace_col:
        execution_trace_diagram(
            trace,
            run_token=int(st.session_state.get("command_animation_token", 1)),
        )
    with output_col:
        st.markdown("<div class='compact-result-title'>Simulated output</div>", unsafe_allow_html=True)
        terminal(
            str(item["example"]),
            guided_output_for(command, str(item["example"]), item["output"]),
            compact=True,
        )

    with st.expander("Interpretation, flags, safety, and next step", expanded=False):
        panel("Output interpretation", guide["read"])
        flags = pd.DataFrame(item["flags"], columns=["Flag / argument", "Meaning"])
        st.dataframe(flags, width="stretch", hide_index=True)
        safe_col, risk_col = st.columns(2)
        safe_col.markdown(
            f"<div class='safe'><b>Safe use</b><br>{html.escape(str(item['safe']))}</div>",
            unsafe_allow_html=True,
        )
        risk_col.markdown(
            f"<div class='risk'><b>Risk or limitation</b><br>{html.escape(str(item['risk']))}</div>",
            unsafe_allow_html=True,
        )
        panel("Suggested next step", guide["next"])


def command_lab_tab() -> None:
    st.subheader("Command Lab")
    st.write(
        "Choose one learning mode. The two modes are separate so you do not need to select a catalogue command before using the terminal."
    )
    command_mode_guide()
    mode = (
        st.segmented_control(
            "Learning mode",
            ["Practice terminal", "Guided command explorer"],
            default="Practice terminal",
            key="command_experience_mode",
        )
        or "Practice terminal"
    )

    if mode == "Practice terminal":
        render_interactive_terminal()
    else:
        render_guided_explorer()


def health_dashboard_tab() -> None:
    st.subheader("Health Dashboard Simulator")
    st.write(
        "Use this lab to simulate a server condition, run a health check, read command-style evidence, and decide what to investigate next. "
        "Nothing is connected to a real server."
    )
    panel(
        "Purpose of this simulation",
        "A monitoring dashboard is useful only when it connects measurements to operational decisions. This simulator models a 4-vCPU Linux server with 8 GiB RAM and an 80 GiB root filesystem. Choose a scenario or set custom values, run the simulation, then compare the generated evidence and diagnosis.",
    )

    scenarios = {
        "Healthy baseline": {
            "description": "Normal workload with comfortable resource headroom and no expected user impact.",
            "values": {"cpu": 32, "memory": 54, "disk": 61, "load": 1.4, "io_wait": 3, "connections": 180},
        },
        "CPU saturation": {
            "description": "A compute-heavy process consumes most CPU time and queues runnable work.",
            "values": {"cpu": 94, "memory": 58, "disk": 64, "load": 9.8, "io_wait": 4, "connections": 310},
        },
        "Memory pressure": {
            "description": "Available RAM is low and the system is likely to rely on swap.",
            "values": {"cpu": 57, "memory": 93, "disk": 66, "load": 5.2, "io_wait": 8, "connections": 420},
        },
        "Disk nearly full": {
            "description": "The root filesystem is close to capacity and application writes may fail.",
            "values": {"cpu": 38, "memory": 62, "disk": 96, "load": 2.1, "io_wait": 6, "connections": 230},
        },
        "Storage bottleneck": {
            "description": "Processes wait for slow storage, creating high load without matching CPU saturation.",
            "values": {"cpu": 46, "memory": 69, "disk": 78, "load": 10.4, "io_wait": 38, "connections": 360},
        },
        "Connection surge": {
            "description": "A sudden increase in active sockets may indicate traffic growth, retries, or connection leakage.",
            "values": {"cpu": 72, "memory": 76, "disk": 70, "load": 6.3, "io_wait": 7, "connections": 2460},
        },
        "Mixed degradation": {
            "description": "Several resources are stressed at once, requiring prioritised evidence collection.",
            "values": {"cpu": 72, "memory": 89, "disk": 92, "load": 11.7, "io_wait": 27, "connections": 1780},
        },
        "Custom": {
            "description": "Set every measurement manually and test your own hypothesis.",
            "values": {"cpu": 52, "memory": 68, "disk": 74, "load": 2.4, "io_wait": 4, "connections": 140},
        },
    }

    default_values = scenarios["Healthy baseline"]["values"]
    for metric, value in default_values.items():
        st.session_state.setdefault(f"health_{metric}", value)

    s1, s2 = st.columns([2, 1])
    scenario_name = s1.selectbox("Choose a server scenario", list(scenarios), key="health_scenario")
    s1.caption(str(scenarios[scenario_name]["description"]))
    if s2.button("Load scenario values", width="stretch"):
        for metric, value in scenarios[scenario_name]["values"].items():
            st.session_state[f"health_{metric}"] = value
        st.session_state.pop("health_snapshot", None)
        st.rerun()

    with st.expander("What each measurement means", expanded=False):
        d1, d2, d3 = st.columns(3)
        d1.markdown(
            "**CPU usage** — processor time currently in use. Sustained high use can indicate heavy computation or a runaway process."
        )
        d2.markdown(
            "**Memory usage** — occupied RAM. Diagnose it with available memory, swap activity, and process growth rather than percentage alone."
        )
        d3.markdown(
            "**Disk usage** — filesystem capacity consumed. Near-full filesystems can prevent logs, databases, and applications from writing."
        )
        d4, d5, d6 = st.columns(3)
        d4.markdown("**Load average** — runnable or uninterruptible tasks. This simulation assumes four virtual CPUs.")
        d5.markdown(
            "**I/O wait** — CPU time spent waiting for storage. High values can indicate slow or saturated disks."
        )
        d6.markdown(
            "**Active connections** — current network sockets. Sudden growth can reflect traffic, retries, or connection leakage."
        )

    c1, c2, c3 = st.columns(3)
    cpu = c1.slider("CPU usage (%)", 0, 100, key="health_cpu")
    memory = c2.slider("Memory usage (%)", 0, 100, key="health_memory")
    disk = c3.slider("Disk usage (%)", 0, 100, key="health_disk")
    c4, c5, c6 = st.columns(3)
    load = c4.slider("Load average", 0.0, 16.0, step=0.1, key="health_load")
    io_wait = c5.slider("I/O wait (%)", 0, 100, key="health_io_wait")
    connections = c6.slider("Active connections", 0, 3000, key="health_connections")

    if st.button("Run simulated health check", type="primary", width="stretch"):
        selected_values = {
            "cpu": int(cpu),
            "memory": int(memory),
            "disk": int(disk),
            "load": float(load),
            "io_wait": int(io_wait),
            "connections": int(connections),
        }
        preset_values = scenarios[scenario_name]["values"]
        scenario_label = (
            scenario_name if selected_values == preset_values else f"Custom values based on {scenario_name}"
        )
        st.session_state.health_snapshot = {"scenario": scenario_label, **selected_values}
        st.session_state.health_run_token = int(st.session_state.get("health_run_token", 0)) + 1

    snapshot = st.session_state.get("health_snapshot")
    if not isinstance(snapshot, dict):
        st.info(
            "Choose or customise a scenario, then click **Run simulated health check**. Results are generated only when the simulation is run."
        )
        return

    current_values = {
        "cpu": int(cpu),
        "memory": int(memory),
        "disk": int(disk),
        "load": float(load),
        "io_wait": int(io_wait),
        "connections": int(connections),
    }
    if any(snapshot[key] != value for key, value in current_values.items()):
        st.warning(
            "The controls have changed since the last run. Click **Run simulated health check** again to generate results for the new values."
        )

    cpu_v = int(snapshot["cpu"])
    memory_v = int(snapshot["memory"])
    disk_v = int(snapshot["disk"])
    load_v = float(snapshot["load"])
    io_v = int(snapshot["io_wait"])
    conn_v = int(snapshot["connections"])

    def classify(value: float, warning: float, critical: float) -> tuple[str, int]:
        if value >= critical:
            return "Critical", 2
        if value >= warning:
            return "Watch", 1
        return "Normal", 0

    statuses = {
        "CPU": classify(cpu_v, 70, 85),
        "Memory": classify(memory_v, 75, 90),
        "Disk": classify(disk_v, 80, 90),
        "Load": classify(load_v, 4.0, 8.0),
        "I/O wait": classify(io_v, 10, 20),
        "Connections": classify(conn_v, 800, 1500),
    }
    overall_rank = max(rank for _, rank in statuses.values())
    overall = ["Normal", "Degraded", "Critical"][overall_rank]

    operational_flow(
        title="Simulated server-health collection",
        subtitle="Signals move through the conceptual infrastructure path before monitoring evidence is analysed.",
        run_token=int(st.session_state.get("health_run_token", 1)),
        final_label="Diagnosis",
    )
    st.markdown(f"### Simulation result: {overall}")
    st.caption(
        f"Scenario used for this run: {snapshot['scenario']} · simulated host: 4 vCPU, 8 GiB RAM, 80 GiB root filesystem"
    )
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("CPU", f"{cpu_v}%", statuses["CPU"][0])
    m2.metric("Memory", f"{memory_v}%", statuses["Memory"][0])
    m3.metric("Disk", f"{disk_v}%", statuses["Disk"][0])
    m4.metric("Load", f"{load_v:.1f}", statuses["Load"][0])
    m5.metric("I/O wait", f"{io_v}%", statuses["I/O wait"][0])
    m6.metric("Connections", conn_v, statuses["Connections"][0])

    pressure = [cpu_v, memory_v, disk_v, min(load_v / 8 * 100, 120), io_v, min(conn_v / 1500 * 100, 120)]
    fig = go.Figure(
        go.Bar(
            x=["CPU", "Memory", "Disk", "Load pressure", "I/O wait", "Connection pressure"],
            y=pressure,
            text=[f"{value:.0f}" for value in pressure],
            textposition="outside",
        )
    )
    fig.update_layout(
        height=390,
        yaxis_title="Relative pressure against training threshold",
        margin=dict(l=20, r=20, t=35, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "The chart converts unlike units into a relative pressure scale. Exact measurements remain visible above."
    )

    st.markdown("### Simulated command evidence")
    active_cpu = min(cpu_v, max(0, 100 - io_v))
    user_cpu = round(active_cpu * 0.75)
    system_cpu = round(active_cpu - user_cpu)
    idle_cpu = max(0, 100 - active_cpu - io_v)
    evidence_tabs = st.tabs(["top", "free", "df", "vmstat", "ss"])
    with evidence_tabs[0]:
        terminal(
            "top -bn1 | head",
            f"""top - simulated snapshot, load average: {load_v:.1f}, {max(load_v - 0.5, 0):.1f}, {max(load_v - 1.0, 0):.1f}
%Cpu(s): {cpu_v:.1f} us, {io_v:.1f} wa, {max(0, 100 - cpu_v - io_v):.1f} id
Tasks: 214 total, {max(1, round(load_v))} running, {max(0, round(load_v / 3))} blocked""",
        )
    with evidence_tabs[1]:
        used_mib = round(8192 * memory_v / 100)
        available_mib = max(0, 8192 - used_mib)
        swap_mib = max(0, round((memory_v - 75) * 35))
        terminal(
            "free -m",
            f"""              total   used   available
Mem:           8192   {used_mib}   {available_mib}
Swap:          2048   {swap_mib}   {2048 - swap_mib}""",
        )
    with evidence_tabs[2]:
        used_gib = round(80 * disk_v / 100)
        terminal(
            "df -h /",
            f"""Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/sda1    80G   {used_gib}G   {80 - used_gib}G   {disk_v}%   /""",
        )
    with evidence_tabs[3]:
        blocked = max(0, round(load_v - 4)) if io_v >= 10 else 0
        terminal(
            "vmstat 1 3",
            f"""r b swpd free buff cache si so bi bo us sy id wa
{max(1, round(load_v))} {blocked} 128 {max(64, 8192 - round(8192 * memory_v / 100))} 220 1900 0 0 18 22 {user_cpu} {system_cpu} {idle_cpu} {io_v}""",
        )
    with evidence_tabs[4]:
        established = round(conn_v * 0.78)
        time_wait = round(conn_v * 0.16)
        terminal(
            "ss -s",
            f"""Total: {conn_v}
TCP: {conn_v} (estab {established}, closed 0, orphaned 2, timewait {time_wait})
UDP: {max(8, round(conn_v * 0.03))}""",
        )

    findings: list[tuple[str, str, str]] = []
    metric_details = [
        ("CPU", cpu_v, statuses["CPU"][0], "`top -bn1` and `ps aux --sort=-%cpu | head`"),
        ("Memory", memory_v, statuses["Memory"][0], "`free -h`, `vmstat 1 5`, and `ps aux --sort=-%mem | head`"),
        ("Disk", disk_v, statuses["Disk"][0], "`df -h`, then `du -xhd1` on the affected mount"),
        ("Load", load_v, statuses["Load"][0], "`uptime`, `vmstat 1 5`, and process-state inspection"),
        ("I/O wait", io_v, statuses["I/O wait"][0], "`iostat -xz 1 5` and `pidstat -d 1 5`"),
        ("Connections", conn_v, statuses["Connections"][0], "`ss -s`, `ss -tlnp`, and application logs"),
    ]
    for metric, value, status, commands in metric_details:
        if status != "Normal":
            findings.append(
                (
                    f"{metric}: {status}",
                    f"The simulated value is {value}. This crosses the {status.lower()} training threshold.",
                    commands,
                )
            )

    if not findings:
        findings.append(
            (
                "No threshold breach",
                "All simulated values are below the training warning thresholds.",
                "Collect trends over time and compare them with a known healthy baseline.",
            )
        )

    st.markdown("### What this run suggests")
    for title, meaning, commands in findings:
        with st.expander(title, expanded=True):
            st.write(meaning)
            st.markdown(f"**Recommended evidence collection:** {commands}")

    if io_v >= 20 and load_v >= 8 and cpu_v < 70:
        likely = "Storage bottleneck: high load is dominated by blocked I/O rather than CPU execution."
    elif cpu_v >= 85 and load_v >= 8:
        likely = "CPU saturation: runnable work is competing for processor time."
    elif memory_v >= 90:
        likely = "Memory pressure: low headroom may cause swap activity or OOM termination."
    elif disk_v >= 90:
        likely = "Capacity risk: application writes, package operations, or logs may fail soon."
    elif conn_v >= 1500:
        likely = "Connection surge: investigate traffic growth, retries, socket states, and application pooling."
    elif overall == "Normal":
        likely = "No immediate resource bottleneck is indicated by this single simulated snapshot."
    else:
        likely = "Early degradation: collect repeated samples before selecting a corrective action."
    panel("Likely operational interpretation", likely)
    st.info(
        "A real diagnosis requires repeated samples, workload baselines, hardware context, application logs, and user impact. Do not act on one threshold alone."
    )


def learning_paths_tab() -> None:
    st.subheader("Learning Paths")
    st.write("Complete commands in increasing difficulty instead of jumping between unrelated operational topics.")
    level = st.radio("Select path", LEVELS, horizontal=True, key="learning_path_level")
    names = command_names(level)
    completed = st.session_state.completed_commands
    progress = sum(1 for name in names if name in completed)
    st.progress(progress / len(names), text=f"{progress}/{len(names)} commands explored")
    for name in names:
        item = COMMANDS[name]
        guide = learning_guide(name)
        checked = "✓" if name in completed else "○"
        with st.expander(f"{checked} `{name}` · {item['category']}"):
            st.write(item["summary"])
            st.markdown(f"**When to use it:** {guide['when']}")
            st.code(item["example"], language="bash")
            st.markdown(f"**How to read the result:** {guide['read']}")
            st.markdown(f"**Suggested next step:** {guide['next']}")
            st.caption(f"Safe use: {item['safe']}")
            if st.button(f"Mark {name} complete", key=f"complete_{level}_{name}"):
                record_command(st.session_state, name)
                st.rerun()


def incident_lab_tab() -> None:
    st.subheader("Incident Diagnosis Simulator")
    st.write(
        "The Incident Lab teaches a repeatable troubleshooting method: understand the report, inspect a short simulated event log, choose the safest first diagnostic command, and then compare your decision with the root cause and remediation path."
    )
    panel(
        "Purpose of the Incident Lab",
        "Real incidents are rarely solved by guessing or restarting services. This lab trains evidence-first reasoning. The event log is a synthetic learning aid, not a real system log; it gives only enough context to choose the next command without revealing the answer.",
    )
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown("**1. Observe**\n\nRead the report and symptoms.")
    s2.markdown("**2. Decide**\n\nChoose a read-only diagnostic action.")
    s3.markdown("**3. Explain**\n\nCompare evidence with the root cause.")
    s4.markdown("**4. Recover**\n\nFollow a targeted remediation sequence.")

    level = st.radio("Incident level", LEVELS, horizontal=True, key="incident_level")
    level_incidents = incidents_for_level(level)
    categories = sorted({str(item["category"]) for item in level_incidents})
    category = st.selectbox("Filter by incident category", ["All categories", *categories], key="incident_category")
    available = [item for item in level_incidents if category == "All categories" or item["category"] == category]
    title_map: dict[str, dict[str, object]] = {f"{x['id']} · {x['title']}": x for x in available}
    label = st.selectbox("Choose an incident scenario", list(title_map), key="incident_select")
    incident = title_map[label]

    completed = len(st.session_state.completed_incidents)
    st.caption(f"Session progress: {completed}/{len(INCIDENTS)} incidents completed")
    st.markdown(f"### {incident['title']}")
    learning_card("Incident report", str(incident["brief"]))

    st.markdown("**Reported symptoms**")
    for symptom in incident["symptoms"]:
        st.write(f"- {symptom}")

    st.markdown("### Simulated incident event log")
    symptom_lines = list(incident["symptoms"])
    simulated_log = f"""17:40:00 monitoring[{incident["id"]}]: alert opened - {incident["title"]}
17:40:04 service-report: {symptom_lines[0]}
17:40:09 operator-note: {symptom_lines[1]}
17:40:15 triage: {symptom_lines[2]}
17:40:20 triage: next step must gather evidence before changing system state"""
    st.code(simulated_log, language="text")
    st.caption(
        "Use the report and simulated log only to select the next diagnostic command. Detailed evidence remains hidden until submission."
    )

    answer = st.radio(str(incident["question"]), list(incident["options"]), key=f"incident_answer_{incident['id']}")
    submitted_key = f"incident_submitted_{incident['id']}"
    if st.button("Submit diagnostic decision", type="primary", key=f"submit_{incident['id']}"):
        correct = answer == incident["answer"]
        awarded = int(incident["points"]) if correct else 0
        record_incident(st.session_state, str(incident["id"]), awarded, int(incident["points"]))
        st.session_state[submitted_key] = True
        st.session_state[f"incident_correct_{incident['id']}"] = correct
        st.session_state[f"incident_run_token_{incident['id']}"] = (
            int(st.session_state.get(f"incident_run_token_{incident['id']}", 0)) + 1
        )

    if st.session_state.get(submitted_key):
        operational_flow(
            title=f"Simulated incident path: {incident['title']}",
            subtitle="The alert is traced through the conceptual infrastructure path to evidence, diagnosis, and recovery.",
            run_token=int(st.session_state.get(f"incident_run_token_{incident['id']}", 1)),
            final_label="Recovery",
        )
        correct = bool(st.session_state.get(f"incident_correct_{incident['id']}"))
        if correct:
            st.success(f"Correct. `{incident['answer']}` is the appropriate first diagnostic action.")
        else:
            st.error(
                f"The safer first action is `{incident['answer']}`. The selected action either tests the wrong layer or changes the system before evidence is collected."
            )
        st.markdown("### Evidence revealed after your decision")
        for evidence in incident["evidence"]:
            st.write(f"- {evidence}")
        panel("Root cause", str(incident["root_cause"]))
        st.markdown("### Targeted remediation sequence")
        for index, step in enumerate(incident["remediation"], 1):
            st.write(f"{index}. {step}")
        st.warning(f"Unsafe shortcut to avoid: {incident['unsafe_action']}")


def learning_workspace_page() -> None:
    sections = ["Overview", "Command Lab", "Health Dashboard", "Learning Paths", "Incident Lab"]
    st.session_state.setdefault("workspace_tab", "Overview")
    current = str(st.session_state.workspace_tab)
    if current not in sections:
        current = "Overview"
        st.session_state.workspace_tab = current

    if current == "Overview":
        overview_hero_section()
    elif current == "Command Lab":
        compact_workspace_header(
            "Command Lab",
            "Practise a safe virtual command or explore how any catalogue command interacts with Linux.",
        )
    else:
        hero(
            f"Learning Workspace · {APP_VERSION}",
            current,
            "Use the workspace tabs to move between command practice, health simulation, structured paths, and incident diagnosis.",
        )

    selected = st.segmented_control(
        "Learning workspace tabs",
        sections,
        key="workspace_tab",
        label_visibility="collapsed",
    )
    selected = selected or "Overview"

    renderers = {
        "Overview": overview_tab,
        "Command Lab": command_lab_tab,
        "Health Dashboard": health_dashboard_tab,
        "Learning Paths": learning_paths_tab,
        "Incident Lab": incident_lab_tab,
    }
    renderers[selected]()


def clear_assessment_widget_state() -> None:
    for key in list(st.session_state):
        if key.startswith("assessment_choice_") or key.startswith("assessment_results_"):
            st.session_state.pop(key, None)


def persist_active_assessment(test: AssessmentTest) -> None:
    st.session_state.active_assessment_test = test.to_dict()
    try:
        save_test(test)
    except OSError:
        # Session-state persistence still works if the deployment filesystem is read-only.
        pass
    st.query_params["assessment_test"] = test.test_id
    st.query_params["assessment_level"] = test.level
    st.query_params["assessment_source"] = test.source
    st.query_params["assessment_seed"] = test.seed
    st.query_params["assessment_count"] = str(len(test.questions))


def restore_active_assessment() -> AssessmentTest | None:
    stored = st.session_state.get("active_assessment_test")
    if isinstance(stored, dict):
        try:
            restored = AssessmentTest.from_dict(stored)
            if restored.source not in {"curated-random", "reviewed-emergency-backup"}:
                st.session_state.pop("active_assessment_test", None)
            else:
                return restored
        except (KeyError, TypeError, AssessmentGenerationError):
            st.session_state.pop("active_assessment_test", None)

    test_id = str(st.query_params.get("assessment_test", "")).strip()
    if not test_id:
        return None
    cached = load_test(test_id)
    if cached is not None and cached.source in {"curated-random", "reviewed-emergency-backup"}:
        st.session_state.active_assessment_test = cached.to_dict()
        return cached

    source = str(st.query_params.get("assessment_source", ""))
    seed = str(st.query_params.get("assessment_seed", ""))
    level = str(st.query_params.get("assessment_level", ""))
    count_raw = str(st.query_params.get("assessment_count", "10"))
    if source == "curated-random" and seed and level in LEVELS:
        try:
            rebuilt = rebuild_curated_test(level, int(count_raw), seed, test_id)
            st.session_state.active_assessment_test = rebuilt.to_dict()
            return rebuilt
        except (ValueError, AssessmentGenerationError):
            return None
    return None


def assessment_page() -> None:
    hero(
        "Generated level test",
        "Assessment",
        "Generate a test explicitly, answer it once, and keep the same questions during normal app reruns. A new test is created only when you press Generate new test.",
    )

    active_test = restore_active_assessment()
    default_level = active_test.level if active_test and active_test.level in LEVELS else "Beginner"
    level = st.radio(
        "Assessment level",
        LEVELS,
        horizontal=True,
        index=LEVELS.index(default_level),
        key="assessment_level",
    )
    st.caption(
        f"Tests are selected randomly without duplicates from the {curated_bank_size()} reviewed questions included with the app. "
        "The active test stays unchanged until you press **Generate new test**."
    )

    requested_count = (
        st.segmented_control(
            "Questions in a generated test",
            [5, 10, 15],
            default=10,
            key="assessment_requested_count",
        )
        or 10
    )

    generate_label = "Generate new test" if active_test else "Generate test"
    if st.button(generate_label, type="primary", width="stretch", key="generate_assessment_test"):
        generated_test = build_curated_test(level, question_count=int(requested_count))
        clear_assessment_widget_state()
        persist_active_assessment(generated_test)
        st.session_state.assessment_generation_notice = generated_test.notice
        st.rerun()

    notice = st.session_state.pop("assessment_generation_notice", None)
    if notice:
        st.success(str(notice))

    active_test = restore_active_assessment()
    if active_test is None:
        st.info(
            "No test has been generated yet. Select a level, then press **Generate test**. "
            f"The reviewed bank currently contains {curated_bank_size()} questions."
        )
        return

    if active_test.level != level:
        st.info(
            f"The active test is {active_test.level}. Changing the level selector does not replace it automatically; "
            "press **Generate new test** when you are ready to switch."
        )

    source_labels = {
        "curated-random": "Reviewed random bank",
        "reviewed-emergency-backup": "Reviewed emergency backup",
    }
    m1, m2, m3 = st.columns(3)
    m1.metric("Active test", active_test.test_id)
    m2.metric("Source", source_labels.get(active_test.source, active_test.source))
    m3.metric("Questions", len(active_test.questions))
    st.caption(
        "This test stays fixed during ordinary Streamlit reruns. It changes only after Generate new test is pressed. "
        "Its identifier is also stored in the URL so a cached test can be restored after a browser reload."
    )
    if active_test.notice:
        st.info(active_test.notice)

    questions = active_test.questions
    results_key = f"assessment_results_{active_test.test_id}"

    if results_key not in st.session_state:
        selections: dict[str, str | None] = {}
        with st.form(f"assessment_form_{active_test.test_id}"):
            for index, question in enumerate(questions, 1):
                st.markdown(f"### Question {index} of {len(questions)} · {question['topic']}")
                question_id = str(question["id"])
                selections[question_id] = st.radio(
                    str(question["question"]),
                    list(question["options"]),
                    index=None,
                    key=f"assessment_choice_{active_test.test_id}_{question_id}",
                )
                st.markdown("---")
            submitted = st.form_submit_button("Submit all answers", type="primary", width="stretch")

        if submitted:
            missing = [str(q["id"]) for q in questions if selections[str(q["id"])] is None]
            if missing:
                st.error(
                    f"Answer all {len(questions)} questions before submitting. Unanswered questions: {len(missing)}."
                )
            else:
                stored_answers: dict[str, str] = {}
                for question in questions:
                    question_id = str(question["id"])
                    selected_answer = str(selections[question_id])
                    correct = selected_answer == question["answer"]
                    record_exercise(st.session_state, question_id, correct, int(question["points"]))
                    stored_answers[question_id] = selected_answer
                st.session_state[results_key] = stored_answers
                st.rerun()
    else:
        stored_answers = st.session_state[results_key]
        correct_count = sum(1 for question in questions if stored_answers[str(question["id"])] == question["answer"])
        earned_points = sum(
            int(question["points"])
            for question in questions
            if stored_answers[str(question["id"])] == question["answer"]
        )
        total_points = sum(int(question["points"]) for question in questions)
        percent = round(correct_count / len(questions) * 100)

        a, b, c = st.columns(3)
        a.metric("Correct answers", f"{correct_count}/{len(questions)}")
        b.metric("Assessment score", f"{earned_points}/{total_points}")
        c.metric("Percentage", f"{percent}%")
        if percent >= 75:
            st.success("Test passed. Review the explanations before generating another test.")
        else:
            st.warning(
                "Review the explanations and revisit the related workspace sections before generating another test."
            )

        st.markdown("### Answer review")
        for index, question in enumerate(questions, 1):
            question_id = str(question["id"])
            selected_answer = stored_answers[question_id]
            correct = selected_answer == question["answer"]
            status = "Correct" if correct else "Incorrect"
            with st.expander(f"{index}. {question['topic']} · {status}", expanded=not correct):
                st.write(question["question"])
                st.markdown(f"**Your answer:** {selected_answer}")
                st.markdown(f"**Correct answer:** {question['answer']}")
                st.markdown(f"**Explanation:** {question['explanation']}")
        st.info(
            "Generate another test only when you are finished reviewing this one. Open **Feedback** to report an inaccurate or ambiguous question."
        )


def configured_feedback_webhook() -> str:
    """Read the private feedback endpoint from an environment variable or Streamlit secrets."""

    force_local = os.getenv("OPSREADY_FEEDBACK_FORCE_LOCAL", "").strip().lower() in {"1", "true", "yes"}
    if force_local:
        return ""

    environment_url = os.getenv("OPSREADY_FEEDBACK_WEBHOOK_URL", "").strip()
    if environment_url:
        return environment_url
    try:
        feedback_secrets = st.secrets.get("feedback", {})
        if hasattr(feedback_secrets, "get"):
            return str(feedback_secrets.get("webhook_url", "")).strip()
    except Exception:
        return ""
    return ""


def feedback_page() -> None:
    hero(
        "Free public preview",
        "Help Shape the Next Release",
        "Share structured feedback after trying the learning workspace or an assessment. Responses will be used to prioritise fixes and future learning content.",
    )
    panel(
        "What useful feedback looks like",
        "Describe the task you attempted, what happened, what you expected, and which change would improve the learning experience. Do not submit passwords, private server logs, access tokens, IP addresses, or other confidential information.",
    )

    webhook_url = configured_feedback_webhook()
    if not webhook_url:
        st.warning(
            "Feedback collection is currently using local preview storage. Before public launch, the project owner should configure a persistent feedback webhook as described in `docs/FEEDBACK_SETUP.md`."
        )

    form_revision = int(st.session_state.get("feedback_form_revision", 0))
    current_suffix = f"_{form_revision}"
    for state_key in list(st.session_state):
        if state_key.startswith("feedback_field_") and not state_key.endswith(current_suffix):
            st.session_state.pop(state_key, None)

    def feedback_key(field_name: str) -> str:
        return f"feedback_field_{field_name}_{form_revision}"

    role_options = [
        "Student or self-learner",
        "Linux support professional",
        "Cloud or DevOps professional",
        "Instructor or trainer",
        "Hiring manager or recruiter",
        "Other",
    ]
    experience_options = ["New to Linux", "Beginner", "Intermediate", "Advanced"]
    feedback_type_options = ["Learning content", "Usability", "Bug report", "Feature request", "Accessibility", "Other"]
    section_options = [
        "Overview",
        "Command Lab",
        "Health Dashboard",
        "Learning Paths",
        "Incident Lab",
        "Assessment",
        "Help",
    ]

    with st.form(f"product_feedback_form_{form_revision}", clear_on_submit=False):
        st.markdown("### About your use of the lab")
        c1, c2 = st.columns(2)
        role = c1.selectbox(
            "Which option best describes you?",
            role_options,
            index=None,
            placeholder="Select one",
            key=feedback_key("role"),
        )
        linux_experience = c2.selectbox(
            "Your Linux experience",
            experience_options,
            index=None,
            placeholder="Select one",
            key=feedback_key("linux_experience"),
        )
        feedback_types = st.multiselect(
            "What kind of feedback are you giving?",
            feedback_type_options,
            key=feedback_key("feedback_types"),
        )
        sections_used = st.multiselect(
            "Which sections did you use?",
            section_options,
            key=feedback_key("sections_used"),
        )

        st.markdown("### Rate the current free version")
        r1, r2, r3 = st.columns(3)
        usefulness = r1.select_slider(
            "Usefulness",
            options=[1, 2, 3, 4, 5],
            value=4,
            help="1 = not useful, 5 = very useful",
            key=feedback_key("usefulness"),
        )
        ease = r2.select_slider(
            "Ease of use",
            options=[1, 2, 3, 4, 5],
            value=4,
            help="1 = difficult, 5 = very easy",
            key=feedback_key("ease"),
        )
        confidence = r3.select_slider(
            "Improved my Linux confidence",
            options=[1, 2, 3, 4, 5],
            value=3,
            help="1 = not at all, 5 = significantly",
            key=feedback_key("confidence"),
        )
        recommendation = st.slider(
            "How likely are you to recommend this free lab?",
            0,
            10,
            7,
            help="0 = not likely, 10 = extremely likely",
            key=feedback_key("recommendation"),
        )

        st.markdown("### Tell us what to change")
        most_useful = st.text_area(
            "What was most useful?",
            max_chars=4000,
            placeholder="For example: the command output explanation helped me understand what to check next.",
            key=feedback_key("most_useful"),
        )
        improvement_needed = st.text_area(
            "What should be improved first? *",
            max_chars=4000,
            placeholder="Describe at least one change, or write 'No change needed'.",
            key=feedback_key("improvement_needed"),
        )
        missing_content = st.text_area(
            "What command, incident, or topic is missing?",
            max_chars=4000,
            placeholder="For example: SSH troubleshooting, package management, or more networking incidents.",
            key=feedback_key("missing_content"),
        )
        issue_response = st.radio(
            "Did you encounter a bug or confusing behaviour?",
            ["No", "Yes"],
            horizontal=True,
            key=feedback_key("issue_response"),
        )
        issue_details = st.text_area(
            "Problem details",
            max_chars=4000,
            placeholder="State the section, action, observed result, and expected result.",
            key=feedback_key("issue_details"),
        )

        st.markdown("### Optional follow-up")
        email = st.text_input(
            "Email address (optional)",
            placeholder="Only provide this if you may want a reply",
            key=feedback_key("email"),
        )
        consent_to_contact = st.checkbox(
            "You may contact me about this feedback.", key=feedback_key("consent_to_contact")
        )
        consent_to_feedback_use = st.checkbox(
            "I agree that this feedback may be stored and used to improve OpsReady Linux Lab. *",
            key=feedback_key("consent_to_feedback_use"),
        )
        st.caption("Email is optional. Do not include confidential or sensitive technical information in any field.")
        submitted = st.form_submit_button("Submit feedback", type="primary", width="stretch")

    submission_notice = st.session_state.pop("feedback_submission_notice", None)
    if isinstance(submission_notice, dict):
        notice_message = str(submission_notice.get("message", ""))
        if submission_notice.get("kind") == "warning":
            st.warning(notice_message)
        else:
            st.success(notice_message)

    if submitted:
        record = create_feedback_record(
            app_version=APP_VERSION,
            session_id=str(st.session_state.feedback_session_id),
            role=role or "",
            linux_experience=linux_experience or "",
            feedback_types=list(feedback_types),
            sections_used=list(sections_used),
            usefulness_rating=int(usefulness),
            ease_rating=int(ease),
            confidence_rating=int(confidence),
            recommendation_score=int(recommendation),
            most_useful=most_useful,
            improvement_needed=improvement_needed,
            missing_content=missing_content,
            issue_found=issue_response == "Yes",
            issue_details=issue_details if issue_response == "Yes" else "",
            email=email,
            consent_to_feedback_use=consent_to_feedback_use,
            consent_to_contact=consent_to_contact,
        )
        errors = validate_feedback(record)
        if errors:
            for error in errors:
                st.error(error)
        else:
            result = submit_feedback(record, webhook_url=webhook_url)
            if result.accepted:
                st.session_state.feedback_form_revision = form_revision + 1
                if result.delivered_to_webhook:
                    st.session_state.feedback_submission_notice = {
                        "kind": "success",
                        "message": (
                            "Feedback submitted successfully. The form has been cleared and is ready for another response. "
                            f"Reference: `{result.submission_id}`"
                        ),
                    }
                else:
                    st.session_state.feedback_submission_notice = {
                        "kind": "warning",
                        "message": (
                            "Feedback was recorded in local preview storage and the form has been cleared. "
                            f"Reference: `{result.submission_id}`. Persistent delivery must be configured before public launch."
                        ),
                    }
                st.rerun()
            else:
                st.error(result.message)


def plans_page() -> None:
    settings = commercial_settings()
    hero(
        "Plans and access",
        "Community now. Pro after fulfilment is ready.",
        "The free simulator remains available while the paid edition is prepared with persistent progress, expanded content, and controlled access.",
    )

    if settings.ready_for_live_checkout:
        st.success("Paid checkout is enabled and the commercial readiness gate is complete.")
    else:
        st.info("Pre-launch status: no payment is accepted from this page yet.")

    community, pro = st.columns(2)
    with community:
        st.markdown("### Community")
        st.markdown("**Free public learning edition**")
        st.markdown(
            """
            - 150 guided Linux commands
            - 25-command safe practice terminal
            - 50 incident scenarios
            - 45 reviewed assessment questions
            - session-based progress
            - community feedback channel
            """
        )
        st.button("Current plan: Community", disabled=True, width="stretch")

    with pro:
        st.markdown("### Pro")
        st.markdown("**Planned paid learning edition**")
        st.markdown(
            """
            - persistent learner account and saved progress
            - expanded reviewed assessment bank
            - longer structured learning paths
            - advanced incident and troubleshooting labs
            - downloadable completion evidence
            - priority content and issue support
            """
        )
        price_a, price_b = st.columns(2)
        price_a.metric("Monthly", settings.monthly_price_label)
        price_b.metric("Annual", settings.annual_price_label)
        if settings.ready_for_live_checkout:
            st.link_button("Upgrade to Pro", settings.checkout_url, type="primary", width="stretch")
        elif settings.waitlist_available:
            st.link_button("Join the Pro launch list", settings.waitlist_url, type="primary", width="stretch")
        else:
            st.button("Pro launch list coming soon", disabled=True, width="stretch")

    st.markdown("### Pro delivery roadmap")
    st.markdown(
        """
        <div class="pro-roadmap">
          <article class="pro-roadmap-step current">
            <span>Current phase</span>
            <strong>1. Foundation</strong>
            <p>Stabilise Community, create the private Pro repository, add authentication, and save learner progress in a database.</p>
          </article>
          <article class="pro-roadmap-step">
            <span>Next</span>
            <strong>2. Founding beta</strong>
            <p>Add expanded assessments and advanced incidents, test Lemon Squeezy fulfilment, then onboard the first 10 paying learners.</p>
          </article>
          <article class="pro-roadmap-step">
            <span>Later</span>
            <strong>3. Instructor and cohort tools</strong>
            <p>Add assignment tracking, learner reports, cohort licences, and institution-facing administration after individual Pro is stable.</p>
          </article>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Checkout remains closed until account access, subscription changes, cancellation, expiry, and saved progress have all been tested end to end."
    )

    st.markdown("### What must be ready before payment opens")
    st.write(
        "A private Pro application, reliable account-based access, persistent progress, published legal policies, support contact details, and tested purchase fulfilment must all be operational before the checkout link is enabled."
    )

    policy_links: list[tuple[str, str]] = []
    for label, url in (
        ("Terms of use", settings.terms_url),
        ("Privacy policy", settings.privacy_url),
        ("Refund and cancellation policy", settings.refund_url),
    ):
        if is_https_url(url):
            policy_links.append((label, url))

    st.markdown("### Purchase policies")
    if policy_links:
        columns = st.columns(len(policy_links))
        for column, (label, url) in zip(columns, policy_links, strict=True):
            column.link_button(label, url, width="stretch")
    else:
        st.caption("The legal policy links are intentionally unpublished while sales remain disabled.")

    if is_email(settings.support_email):
        st.caption(f"Support contact: {settings.support_email}")
    if settings.portal_available:
        st.link_button("Manage an existing subscription", settings.customer_portal_url)


def help_page() -> None:
    hero(
        "Usage guide",
        "How to Use the Lab",
        "Use the simulator to learn diagnostic reasoning, then repeat the exercises in a disposable Linux environment.",
    )
    st.markdown(
        """
        1. Open **Learning Workspace** and use its tabs from left to right.
        2. In **Command Lab**, use the safe Practice terminal for hands-on practice or Guided command explorer for the wider command catalogue.
        3. In **Health Dashboard**, move one measurement at a time and explain why the recommended command is relevant.
        4. Follow a complete **Learning Path**, then solve matching incidents.
        5. Open **Assessment**, generate a test explicitly, answer every displayed question, and review the explanations before generating another test.
        6. Open **Feedback** and report what was useful, confusing, broken, or missing.
        7. Repeat safe read-only commands in WSL, an Ubuntu VM, or a controlled cloud lab.
        """
    )
    st.subheader("Safety boundary")
    st.write(
        "The Practice terminal never invokes a host shell. It parses one reviewed command at a time against an in-memory virtual filesystem. Guided command explorer also remains synthetic. Avoid copying destructive examples into a real terminal. Review paths, permissions, service impact, backups, and rollback plans before any change."
    )
    st.subheader("Progress limitation")
    st.write(
        "Scores and completed activities remain session-based. Assessment test identifiers and seeds are stored in the URL, and reviewed tests can be reconstructed from their saved seed after a browser reload. Persistent accounts and databases remain deferred until free-user validation."
    )


with st.sidebar:
    st.markdown(f"## 🐧 {APP_NAME}")
    page = st.radio("Navigation", ["Learning Workspace", "Assessment", "Plans", "Feedback", "Help"], index=0)
    st.markdown("---")
    progress_sidebar()
    st.markdown("---")
    st.caption("Safe simulation only. Interactive practice never invokes a host shell.")

PAGES = {
    "Learning Workspace": learning_workspace_page,
    "Assessment": assessment_page,
    "Plans": plans_page,
    "Feedback": feedback_page,
    "Help": help_page,
}
PAGES[page]()
