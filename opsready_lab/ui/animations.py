from __future__ import annotations

import html
from collections.abc import Sequence

import streamlit as st

_ICON_SVGS: dict[str, str] = {
    "computer": """
    <svg viewBox='0 0 64 64' aria-hidden='true'>
      <rect x='8' y='9' width='48' height='34' rx='5' fill='#0f172a'/>
      <rect x='13' y='14' width='38' height='24' rx='2' fill='#dbeafe'/>
      <path d='M25 48h14M21 54h22' stroke='#1d4ed8' stroke-width='4' stroke-linecap='round'/>
      <path d='M20 24l6 4-6 4M31 32h12' stroke='#0891b2' stroke-width='3' stroke-linecap='round'/>
    </svg>
    """,
    "switch": """
    <svg viewBox='0 0 64 64' aria-hidden='true'>
      <rect x='7' y='19' width='50' height='27' rx='6' fill='#1d4ed8'/>
      <rect x='13' y='27' width='7' height='6' rx='1' fill='#dbeafe'/>
      <rect x='23' y='27' width='7' height='6' rx='1' fill='#dbeafe'/>
      <rect x='33' y='27' width='7' height='6' rx='1' fill='#dbeafe'/>
      <rect x='43' y='27' width='7' height='6' rx='1' fill='#dbeafe'/>
      <circle cx='17' cy='39' r='2' fill='#22c55e'/><circle cx='27' cy='39' r='2' fill='#22c55e'/>
      <circle cx='37' cy='39' r='2' fill='#fbbf24'/><circle cx='47' cy='39' r='2' fill='#22c55e'/>
    </svg>
    """,
    "router": """
    <svg viewBox='0 0 64 64' aria-hidden='true'>
      <rect x='10' y='29' width='44' height='21' rx='6' fill='#0891b2'/>
      <path d='M21 25c6-7 16-7 22 0M15 18c10-12 24-12 34 0' fill='none' stroke='#2563eb' stroke-width='3' stroke-linecap='round'/>
      <path d='M20 39h24M24 35l-4 4 4 4M40 35l4 4-4 4' fill='none' stroke='#ecfeff' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>
    </svg>
    """,
    "server": """
    <svg viewBox='0 0 64 64' aria-hidden='true'>
      <rect x='15' y='6' width='34' height='52' rx='5' fill='#0f172a'/>
      <rect x='21' y='13' width='22' height='10' rx='2' fill='#bfdbfe'/>
      <rect x='21' y='27' width='22' height='10' rx='2' fill='#93c5fd'/>
      <rect x='21' y='41' width='22' height='10' rx='2' fill='#60a5fa'/>
      <circle cx='39' cy='18' r='2' fill='#22c55e'/><circle cx='39' cy='32' r='2' fill='#fbbf24'/><circle cx='39' cy='46' r='2' fill='#22c55e'/>
    </svg>
    """,
    "evidence": """
    <svg viewBox='0 0 64 64' aria-hidden='true'>
      <path d='M17 7h24l9 9v41H17z' fill='#ffffff' stroke='#2563eb' stroke-width='3'/>
      <path d='M41 7v11h9M24 28h18M24 36h18M24 44h12' fill='none' stroke='#1e3a8a' stroke-width='3' stroke-linecap='round'/>
      <circle cx='21' cy='28' r='2' fill='#ef4444'/><circle cx='21' cy='36' r='2' fill='#f59e0b'/><circle cx='21' cy='44' r='2' fill='#22c55e'/>
    </svg>
    """,
    "diagnosis": """
    <svg viewBox='0 0 64 64' aria-hidden='true'>
      <circle cx='28' cy='27' r='16' fill='#dbeafe' stroke='#2563eb' stroke-width='4'/>
      <path d='M40 39l13 13' stroke='#1e3a8a' stroke-width='5' stroke-linecap='round'/>
      <path d='M21 27h14M28 20v14' stroke='#0891b2' stroke-width='3' stroke-linecap='round'/>
    </svg>
    """,
}


def _node(icon: str, title: str, detail: str) -> str:
    svg = _ICON_SVGS.get(icon, _ICON_SVGS["server"])
    return (
        "<div class='ops-flow-node'>"
        f"<div class='ops-flow-icon'>{svg}</div>"
        f"<strong>{html.escape(title)}</strong>"
        f"<span>{html.escape(detail)}</span>"
        "</div>"
    )


def hero_demo(*, paused: bool = False, replay_token: int = 0) -> None:
    """Render the animated Overview product demonstration."""

    suffix = f"{replay_token % 100000}"
    pause_class = " is-paused" if paused else ""
    st.markdown(
        f"""
        <section class='overview-hero' aria-label='OpsReady Linux Lab product introduction'>
          <div class='overview-beta'>FREE PUBLIC BETA</div>
          <h1>OpsReady Linux Lab</h1>
          <p class='overview-lead'>Learn Linux operations through interactive commands, server-health simulation, and incident diagnosis.</p>
          <p class='overview-support'>Explore 150 commands, investigate 50 operational incidents, and test your knowledge with 45 assessment questions—all in a safe learning environment.</p>
          <div class='overview-stats' aria-label='Product content totals'>
            <span><b>150</b> commands</span><span><b>50</b> incidents</span><span><b>45</b> assessment questions</span>
          </div>
        </section>
        <div class='hero-demo{pause_class}' id='hero-demo-{suffix}' role='img' aria-label='Animated demonstration: a command travels from a workstation through a switch and router to a Linux server, where health evidence and an incident diagnosis are produced.'>
          <style>
            #hero-demo-{suffix} .hero-demo-typing {{ animation-name:heroTyping{suffix}; }}
            #hero-demo-{suffix} .hero-demo-packet.one {{ animation-name:heroPacketOne{suffix}; }}
            #hero-demo-{suffix} .hero-demo-packet.two {{ animation-name:heroPacketTwo{suffix}; }}
            #hero-demo-{suffix} .hero-node {{ animation-name:heroNodePulse{suffix}; }}
            #hero-demo-{suffix} .hero-health-card {{ animation-name:heroHealth{suffix}; }}
            #hero-demo-{suffix} .hero-log-card {{ animation-name:heroLog{suffix}; }}
            #hero-demo-{suffix} .hero-finish-card {{ animation-name:heroFinish{suffix}; }}
            #hero-demo-{suffix} .hero-stage-label.s1 {{ animation-name:heroLabelOne{suffix}; }}
            #hero-demo-{suffix} .hero-stage-label.s2 {{ animation-name:heroLabelTwo{suffix}; }}
            #hero-demo-{suffix} .hero-stage-label.s3 {{ animation-name:heroLabelThree{suffix}; }}
            #hero-demo-{suffix} .hero-stage-label.s4 {{ animation-name:heroLabelFour{suffix}; }}
            #hero-demo-{suffix} .hero-stage-label.s5 {{ animation-name:heroLabelFive{suffix}; }}
            @keyframes heroTyping{suffix} {{
              0%,2% {{ clip-path:inset(0 100% 0 0); }}
              14%,100% {{ clip-path:inset(0 0 0 0); }}
            }}
            @keyframes heroPacketOne{suffix} {{
              0%,15% {{ opacity:0; left:7%; }} 17% {{ opacity:1; }} 38% {{ opacity:1; left:92%; }} 40%,100% {{ opacity:0; left:92%; }}
            }}
            @keyframes heroPacketTwo{suffix} {{
              0%,18% {{ opacity:0; left:7%; }} 20% {{ opacity:1; }} 41% {{ opacity:1; left:92%; }} 43%,100% {{ opacity:0; left:92%; }}
            }}
            @keyframes heroNodePulse{suffix} {{
              0%,15%,42%,100% {{ transform:translateY(0); box-shadow:0 10px 28px rgba(15,23,42,.08); }}
              24%,33% {{ transform:translateY(-5px); box-shadow:0 16px 34px rgba(37,99,235,.23); }}
            }}
            @keyframes heroHealth{suffix} {{ 0%,37%,63%,100% {{ opacity:0; transform:translateY(18px); }} 41%,59% {{ opacity:1; transform:translateY(0); }} }}
            @keyframes heroLog{suffix} {{ 0%,59%,85%,100% {{ opacity:0; transform:translateY(18px); }} 64%,81% {{ opacity:1; transform:translateY(0); }} }}
            @keyframes heroFinish{suffix} {{ 0%,80%,100% {{ opacity:0; transform:scale(.97); }} 85%,96% {{ opacity:1; transform:scale(1); }} }}
            @keyframes heroLabelOne{suffix} {{ 0%,1%,17%,100% {{ opacity:0; }} 3%,14% {{ opacity:1; }} }}
            @keyframes heroLabelTwo{suffix} {{ 0%,15%,40%,100% {{ opacity:0; }} 18%,36% {{ opacity:1; }} }}
            @keyframes heroLabelThree{suffix} {{ 0%,37%,63%,100% {{ opacity:0; }} 41%,59% {{ opacity:1; }} }}
            @keyframes heroLabelFour{suffix} {{ 0%,59%,85%,100% {{ opacity:0; }} 64%,81% {{ opacity:1; }} }}
            @keyframes heroLabelFive{suffix} {{ 0%,80%,100% {{ opacity:0; }} 85%,96% {{ opacity:1; }} }}
          </style>
          <div class='hero-demo-head'>
            <div>
              <strong>From command to diagnosis</strong>
              <span>18-second conceptual walkthrough</span>
            </div>
            <div class='hero-live-dot'><span></span> Interactive preview</div>
          </div>
          <div class='hero-terminal-mini'>
            <span class='hero-prompt'>student@opsready:~$</span>
            <span class='hero-demo-typing'> systemctl status nginx</span>
          </div>
          <div class='hero-network'>
            <div class='hero-network-line'></div>
            <div class='hero-demo-packet one'></div><div class='hero-demo-packet two'></div>
            <div class='hero-node' style='animation-delay:3.0s'>{_node('computer', 'Workstation', 'Enter command')}</div>
            <div class='hero-node' style='animation-delay:3.7s'>{_node('switch', 'Switch', 'Forward signal')}</div>
            <div class='hero-node' style='animation-delay:4.4s'>{_node('router', 'Router', 'Select path')}</div>
            <div class='hero-node' style='animation-delay:5.1s'>{_node('server', 'Linux server', 'Collect evidence')}</div>
          </div>
          <div class='hero-result-stage'>
            <div class='hero-health-card'>
              <b>Health evidence</b>
              <div class='hero-meter'><span>CPU</span><i style='width:82%'></i><em>82%</em></div>
              <div class='hero-meter'><span>Memory</span><i style='width:68%'></i><em>68%</em></div>
              <div class='hero-meter'><span>I/O wait</span><i style='width:38%'></i><em>21%</em></div>
            </div>
            <div class='hero-log-card'>
              <b>Incident evidence</b>
              <code>bind() to 0.0.0.0:80 failed</code>
              <strong>Likely cause: port 80 already occupied</strong>
              <span>Next: ss -tulnp | grep :80</span>
            </div>
            <div class='hero-finish-card'>
              <b>Learn by troubleshooting</b>
              <span>Command explored</span><span>Incident diagnosed</span><span>Knowledge checked</span>
            </div>
          </div>
          <div class='hero-stage-labels' aria-hidden='true'>
            <span class='hero-stage-label s1'>1. Run a Linux command</span>
            <span class='hero-stage-label s2'>2. Follow the operational path</span>
            <span class='hero-stage-label s3'>3. Interpret system evidence</span>
            <span class='hero-stage-label s4'>4. Connect symptoms to a root cause</span>
            <span class='hero-stage-label s5'>5. Choose the next action</span>
          </div>
          <div class='hero-static-fallback'>Command → System path → Evidence → Diagnosis → Learning</div>
        </div>
        <p class='hero-disclaimer'>Educational simulation only. No commands are executed on a real server.</p>
        """,
        unsafe_allow_html=True,
    )


def operational_flow(
    *,
    title: str,
    subtitle: str,
    run_token: int,
    final_label: str = "Interpretation",
    nodes: Sequence[tuple[str, str, str]] | None = None,
) -> None:
    """Render a reusable animated command/health/incident infrastructure path."""

    flow_nodes = list(
        nodes
        or [
            ("computer", "Workstation", "Start request"),
            ("switch", "Switch", "Forward traffic"),
            ("router", "Router", "Select route"),
            ("server", "Linux server", "Inspect state"),
            ("evidence", "Evidence", "Read output"),
            ("diagnosis", final_label, "Choose next step"),
        ]
    )
    suffix = str(abs(hash((title, run_token))) % 10_000_000)
    node_html = "".join(_node(icon, label, detail) for icon, label, detail in flow_nodes)
    st.markdown(
        f"""
        <div class='ops-flow' id='ops-flow-{suffix}' role='img' aria-label='{html.escape(title)}'>
          <style>
            #ops-flow-{suffix} .ops-flow-ball.a {{ animation-name:opsBallA{suffix}; }}
            #ops-flow-{suffix} .ops-flow-ball.b {{ animation-name:opsBallB{suffix}; }}
            #ops-flow-{suffix} .ops-flow-node {{ animation-name:opsNode{suffix}; }}
            @keyframes opsBallA{suffix} {{ 0% {{ left:3%; opacity:0; }} 4% {{ opacity:1; }} 86% {{ left:96%; opacity:1; }} 100% {{ left:96%; opacity:0; }} }}
            @keyframes opsBallB{suffix} {{ 0%,13% {{ left:3%; opacity:0; }} 17% {{ opacity:1; }} 92% {{ left:96%; opacity:1; }} 100% {{ left:96%; opacity:0; }} }}
            @keyframes opsNode{suffix} {{ 0%,100% {{ transform:translateY(0); border-color:#bfdbfe; }} 45%,65% {{ transform:translateY(-4px); border-color:#2563eb; }} }}
          </style>
          <div class='ops-flow-heading'><strong>{html.escape(title)}</strong><span>{html.escape(subtitle)}</span></div>
          <div class='ops-flow-track'>
            <div class='ops-flow-line'></div><div class='ops-flow-ball a'></div><div class='ops-flow-ball b'></div>
            {node_html}
          </div>
          <div class='ops-flow-note'>Conceptual learning animation. The exact path depends on whether a command is local, service-based, or network-facing.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
