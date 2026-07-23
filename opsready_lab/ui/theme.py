from __future__ import annotations

import html

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink:#0f172a;
            --blue:#2563eb;
            --blue-dark:#1d4ed8;
            --cyan:#0891b2;
            --line:#dbeafe;
            --surface:#ffffff;
            --surface-soft:#eff6ff;
            --body-size:18px;
            color-scheme:light;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background:linear-gradient(135deg,#f8fafc,#eef4ff 48%,#f8fafc);
            font-size:var(--body-size);
            color:var(--ink);
        }
        [data-testid="stSidebar"] { background:linear-gradient(180deg,#0f172a,#111827); }
        [data-testid="stSidebar"] * { color:#f8fafc !important; }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span { font-size:1rem !important; }

        /* Keep sidebar action text visible at rest, not only on hover. */
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] .st-key-reset_session_progress button {
            background:#334155 !important;
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            border:1px solid #64748b !important;
            opacity:1 !important;
            box-shadow:0 6px 16px rgba(2,6,23,.28) !important;
        }
        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] .stButton > button span,
        [data-testid="stSidebar"] .st-key-reset_session_progress button p,
        [data-testid="stSidebar"] .st-key-reset_session_progress button span {
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover,
        [data-testid="stSidebar"] .st-key-reset_session_progress button:hover {
            background:#1d4ed8 !important;
            border-color:#60a5fa !important;
        }
        [data-testid="stSidebar"] .stButton > button:focus-visible,
        [data-testid="stSidebar"] .st-key-reset_session_progress button:focus-visible {
            outline:3px solid #93c5fd !important;
            outline-offset:2px !important;
        }
        [data-testid="stSidebar"] .stButton > button:disabled {
            background:#475569 !important;
            color:#f8fafc !important;
            -webkit-text-fill-color:#f8fafc !important;
            opacity:.88 !important;
        }
        .block-container { max-width:1320px; padding-top:1.2rem; padding-bottom:3rem; }
        p, li, label, .stMarkdown, [data-testid="stWidgetLabel"] p,
        [data-testid="stCaptionContainer"] p, .stAlert p {
            font-size:1.06rem !important;
            line-height:1.62 !important;
        }
        h1 { font-size:2.5rem !important; }
        h2 { font-size:1.86rem !important; }
        h3 { font-size:1.38rem !important; }
        h1,h2,h3 { color:var(--ink); letter-spacing:-0.02em; }
        input, textarea, [data-baseweb="select"] * { font-size:1rem !important; }
        button p, button span { font-size:1rem !important; }
        [data-testid="stTabs"] button p { font-size:1.05rem !important; font-weight:700 !important; }
        [data-testid="stMetricValue"] { font-size:1.9rem !important; }
        [data-testid="stMetricLabel"] p { font-size:1rem !important; }

        /* Solid, high-contrast form controls and dropdown overlays. */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            background:#ffffff !important;
            color:#0f172a !important;
            border-color:#94a3b8 !important;
            box-shadow:0 1px 2px rgba(15,23,42,.05) !important;
        }
        div[data-baseweb="select"] > div:hover,
        div[data-baseweb="input"] > div:hover,
        div[data-baseweb="textarea"] > div:hover {
            border-color:#2563eb !important;
        }
        div[data-baseweb="select"] input,
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            color:#0f172a !important;
            -webkit-text-fill-color:#0f172a !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"],
        ul[role="listbox"] {
            background:#ffffff !important;
            color:#0f172a !important;
            border:1px solid #94a3b8 !important;
            border-radius:12px !important;
            box-shadow:0 18px 45px rgba(15,23,42,.18) !important;
        }
        li[role="option"],
        div[role="option"] {
            background:#ffffff !important;
            color:#0f172a !important;
            font-size:1rem !important;
            line-height:1.4 !important;
        }
        li[role="option"]:hover,
        div[role="option"]:hover {
            background:#dbeafe !important;
            color:#0f172a !important;
        }
        li[role="option"][aria-selected="true"],
        div[role="option"][aria-selected="true"] {
            background:#bfdbfe !important;
            color:#1e3a8a !important;
            font-weight:700 !important;
        }
        [data-baseweb="tag"] {
            background:#dbeafe !important;
            color:#1e3a8a !important;
        }

        /* Streamlit 1.59 can wrap select controls differently across browsers.
           Target the widget, combobox, portal, menu and option layers explicitly. */
        [data-testid="stSelectbox"] [data-baseweb="select"],
        [data-testid="stMultiSelect"] [data-baseweb="select"],
        [data-testid="stSelectbox"] [role="combobox"],
        [data-testid="stMultiSelect"] [role="combobox"] {
            background-color:#ffffff !important;
            color:#0f172a !important;
            border-color:#64748b !important;
            opacity:1 !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
        [data-testid="stSelectbox"] [data-baseweb="select"] div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] div {
            background-color:#ffffff !important;
            color:#0f172a !important;
            -webkit-text-fill-color:#0f172a !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"],
        [data-testid="stMultiSelect"] [data-baseweb="select"] {
            border:1px solid #64748b !important;
            border-radius:10px !important;
            box-shadow:0 2px 5px rgba(15,23,42,.10) !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
        [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within {
            border-color:#1d4ed8 !important;
            box-shadow:0 0 0 3px rgba(37,99,235,.20) !important;
        }
        body > div[data-baseweb="popover"],
        body > div[data-baseweb="popover"] > div,
        [data-baseweb="popover"],
        [data-baseweb="popover"] [data-baseweb="menu"],
        [data-baseweb="popover"] [role="listbox"],
        [data-baseweb="menu"] ul {
            background-color:#ffffff !important;
            color:#0f172a !important;
            opacity:1 !important;
        }
        [data-baseweb="popover"] [role="option"],
        [data-baseweb="menu"] [role="option"],
        ul[role="listbox"] > li {
            background-color:#ffffff !important;
            color:#0f172a !important;
            -webkit-text-fill-color:#0f172a !important;
            border-bottom:1px solid #e2e8f0 !important;
            min-height:2.65rem !important;
        }
        [data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="popover"] [role="option"][aria-selected="true"],
        [data-baseweb="menu"] [role="option"]:hover,
        [data-baseweb="menu"] [role="option"][aria-selected="true"] {
            background-color:#dbeafe !important;
            color:#1e3a8a !important;
            -webkit-text-fill-color:#1e3a8a !important;
        }
        [data-testid="stMultiSelect"] [data-baseweb="tag"],
        [data-testid="stMultiSelect"] [data-baseweb="tag"] div,
        [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
            background-color:#dbeafe !important;
            color:#1e3a8a !important;
            -webkit-text-fill-color:#1e3a8a !important;
        }

        .workspace-compact-header {
            display:flex; align-items:center; gap:.8rem; flex-wrap:wrap;
            margin:0 0 .7rem; padding:.72rem 1rem; border-radius:16px;
            background:linear-gradient(135deg,#0f172a,#1d4ed8); color:#ffffff;
            box-shadow:0 10px 25px rgba(37,99,235,.14);
        }
        .workspace-compact-header small { color:#bfdbfe; font-weight:800; }
        .workspace-compact-header h2 { color:#ffffff !important; margin:0 !important; font-size:1.55rem !important; }
        .workspace-compact-header span { color:#eff6ff; font-size:.92rem; }

        .hero {
            border-radius:24px;
            padding:1.8rem 2rem;
            color:white;
            background:radial-gradient(circle at top left,#38bdf8 0%,transparent 28%),linear-gradient(135deg,#0f172a,#1d4ed8 72%,#2563eb);
            box-shadow:0 22px 55px rgba(37,99,235,.2);
            margin-bottom:1.2rem;
        }
        .hero h1,.hero p,.hero small { color:white !important; }
        .hero p { font-size:1.15rem !important; max-width:980px; }
        .hero small { font-size:.95rem !important; font-weight:700; letter-spacing:.02em; }

        .overview-hero {
            border-radius:28px 28px 0 0;
            padding:2rem 2.2rem 1.55rem;
            color:white;
            background:radial-gradient(circle at 8% 0%,rgba(56,189,248,.7),transparent 28%),linear-gradient(135deg,#081226,#173b8f 63%,#2563eb);
            box-shadow:0 24px 65px rgba(37,99,235,.22);
        }
        .overview-hero h1 { color:#ffffff !important; margin:.4rem 0 .35rem; font-size:2.85rem !important; }
        .overview-hero p { color:#eff6ff !important; margin:.35rem 0; }
        .overview-beta {
            display:inline-flex;
            padding:.34rem .68rem;
            border-radius:999px;
            background:rgba(255,255,255,.16);
            border:1px solid rgba(255,255,255,.35);
            color:#ffffff;
            font-size:.82rem;
            font-weight:800;
            letter-spacing:.08em;
        }
        .overview-lead { font-size:1.32rem !important; font-weight:700; max-width:980px; }
        .overview-support { font-size:1.06rem !important; max-width:1020px; opacity:.95; }
        .overview-stats { display:flex; flex-wrap:wrap; gap:.65rem; margin-top:1rem; }
        .overview-stats span {
            display:inline-flex; gap:.35rem; align-items:center; padding:.42rem .72rem; border-radius:999px;
            background:rgba(2,6,23,.28); border:1px solid rgba(219,234,254,.25); color:#eff6ff;
        }
        .overview-stats b { color:#ffffff; }

        .hero-demo {
            position:relative;
            overflow:hidden;
            min-height:510px;
            padding:1.25rem 1.35rem 1rem;
            background:linear-gradient(180deg,#f8fbff,#eaf2ff);
            border:1px solid #bfdbfe;
            border-top:0;
            border-radius:0 0 28px 28px;
            box-shadow:0 24px 65px rgba(37,99,235,.15);
        }
        .hero-demo-head { display:flex; justify-content:space-between; gap:1rem; align-items:center; margin-bottom:.8rem; }
        .hero-demo-head strong { display:block; font-size:1.2rem; color:#0f172a; }
        .hero-demo-head span { display:block; color:#64748b; font-size:.9rem; }
        .hero-live-dot { display:flex; align-items:center; gap:.45rem; color:#1e3a8a; font-size:.88rem; font-weight:700; }
        .hero-live-dot span { width:9px; height:9px; border-radius:50%; background:#16a34a; box-shadow:0 0 0 5px rgba(22,163,74,.13); }
        .hero-terminal-mini {
            max-width:620px; margin:0 auto .9rem; padding:.85rem 1rem; border-radius:14px; background:#020617; color:#e2e8f0;
            font-family:Consolas,monospace; font-size:1rem; box-shadow:0 12px 28px rgba(2,6,23,.18); white-space:nowrap; overflow:hidden;
        }
        .hero-prompt { color:#67e8f9; }
        .hero-demo-typing { display:inline-block; color:#fef08a; animation-duration:18s; animation-iteration-count:infinite; animation-timing-function:linear; }
        .hero-network { position:relative; display:grid; grid-template-columns:repeat(4,minmax(140px,1fr)); gap:.8rem; padding:.7rem .4rem 1rem; }
        .hero-network-line { position:absolute; left:8%; right:8%; top:49%; height:5px; border-radius:999px; background:linear-gradient(90deg,#93c5fd,#2563eb,#0891b2); z-index:0; }
        .hero-demo-packet { position:absolute; top:calc(49% - 8px); width:18px; height:18px; border-radius:50%; z-index:4; opacity:0; background:#f59e0b; border:3px solid #fff; box-shadow:0 0 0 7px rgba(245,158,11,.16),0 8px 20px rgba(245,158,11,.35); animation-duration:18s; animation-iteration-count:infinite; animation-timing-function:ease-in-out; }
        .hero-demo-packet.two { background:#22c55e; animation-delay:.2s; }
        .hero-node { position:relative; z-index:2; animation-duration:18s; animation-iteration-count:infinite; animation-timing-function:ease-in-out; }
        .hero-node .ops-flow-node { min-height:145px; }
        .hero-result-stage { position:relative; min-height:170px; max-width:930px; margin:.35rem auto 0; }
        .hero-health-card,.hero-log-card,.hero-finish-card {
            position:absolute; inset:0; opacity:0; padding:1rem 1.2rem; border-radius:16px; background:#ffffff; border:1px solid #bfdbfe;
            box-shadow:0 14px 30px rgba(15,23,42,.09); animation-duration:18s; animation-iteration-count:infinite; animation-timing-function:ease-in-out;
        }
        .hero-health-card > b,.hero-log-card > b,.hero-finish-card > b { display:block; margin-bottom:.65rem; color:#1e3a8a; font-size:1.08rem; }
        .hero-meter { display:grid; grid-template-columns:90px 1fr 48px; gap:.6rem; align-items:center; margin:.52rem 0; }
        .hero-meter span,.hero-meter em { font-size:.9rem; color:#334155; font-style:normal; }
        .hero-meter i { display:block; height:10px; border-radius:999px; background:linear-gradient(90deg,#60a5fa,#2563eb); }
        .hero-log-card code { display:block; background:#020617; color:#fef08a; padding:.7rem .8rem; border-radius:10px; margin:.45rem 0 .7rem; }
        .hero-log-card strong,.hero-log-card span { display:block; margin:.35rem 0; color:#0f172a; }
        .hero-finish-card { text-align:center; padding-top:1.3rem; }
        .hero-finish-card span { display:inline-flex; margin:.4rem; padding:.55rem .75rem; border-radius:999px; background:#dbeafe; color:#1e3a8a; font-weight:700; }
        .hero-stage-labels { position:relative; min-height:34px; margin-top:.25rem; text-align:center; }
        .hero-stage-label { position:absolute; inset:0; opacity:0; color:#1e3a8a; font-weight:800; animation-duration:18s; animation-iteration-count:infinite; }
        .hero-static-fallback { display:none; text-align:center; padding:1rem; border-radius:12px; background:#dbeafe; color:#1e3a8a; font-weight:800; }
        .hero-demo.is-paused *, .hero-demo.is-paused *::before, .hero-demo.is-paused *::after { animation-play-state:paused !important; }
        .hero-disclaimer { margin:.65rem 0 1.15rem !important; color:#475569; text-align:center; font-size:.93rem !important; }

        .panel {
            border:1px solid var(--line);
            background:rgba(255,255,255,.94);
            border-radius:18px;
            padding:1rem 1.1rem;
            box-shadow:0 10px 26px rgba(15,23,42,.06);
            margin-bottom:.8rem;
        }
        .panel h3 { margin-top:0; }
        .terminal {
            background:#020617;
            color:#e2e8f0;
            border-radius:16px;
            padding:1.1rem;
            font-family:Consolas,monospace;
            font-size:1.02rem;
            line-height:1.55;
            white-space:pre-wrap;
            overflow-x:auto;
            border:1px solid #1e293b;
        }
        .terminal.compact { max-height:210px; min-height:142px; overflow-y:auto; font-size:.88rem; padding:.8rem; border-radius:12px; }
        .prompt { color:#67e8f9; } .cmd { color:#fef08a; }
        .risk, .safe, .learn-card {
            border-radius:12px;
            padding:.85rem 1rem;
            min-height:118px;
            font-size:1rem;
            line-height:1.55;
        }
        .risk { border-left:4px solid #f59e0b; background:#fffbeb; }
        .safe { border-left:4px solid #16a34a; background:#f0fdf4; }
        .learn-card { border:1px solid #bfdbfe; background:#eff6ff; }
        .learn-card b { display:block; margin-bottom:.35rem; color:#1e3a8a; }
        .stButton > button { border-radius:999px; font-weight:700; min-height:2.85rem; }
        [data-testid="stDataFrame"] { font-size:1rem; }

        /* Workspace navigation rendered as high-contrast tabs. */
        div[data-testid="stSegmentedControl"] { margin:.35rem 0 1rem; }
        div[data-testid="stSegmentedControl"] button {
            background:#ffffff !important; color:#1e293b !important; border-color:#94a3b8 !important; min-height:3rem;
        }
        div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
            background:#1d4ed8 !important; color:#ffffff !important; border-color:#1d4ed8 !important;
        }

        /* Compact Command Lab and command-specific execution traces. */
        .command-mode-guide {
            display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.75rem;
            margin:.4rem 0 .8rem;
        }
        .command-mode-guide article {
            border:1px solid #bfdbfe; border-radius:14px; background:#ffffff;
            padding:.75rem .85rem; box-shadow:0 7px 18px rgba(15,23,42,.05);
        }
        .command-mode-guide b { display:block; color:#1e3a8a; margin-bottom:.2rem; }
        .command-mode-guide span { color:#475569; font-size:.9rem; line-height:1.35; }
        .practice-status {
            display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:.25rem 0 .65rem;
        }
        .practice-status span {
            display:inline-flex; padding:.35rem .6rem; border-radius:999px;
            background:#eff6ff; color:#1e3a8a; border:1px solid #bfdbfe;
            font-size:.86rem; font-weight:700;
        }
        .execution-trace {
            margin:.55rem 0; padding:.72rem; border-radius:16px;
            background:linear-gradient(180deg,#ffffff,#eff6ff); border:1px solid #bfdbfe;
            box-shadow:0 8px 22px rgba(15,23,42,.06); overflow:hidden;
        }
        .execution-trace-head { display:flex; align-items:flex-start; justify-content:space-between; gap:.75rem; margin-bottom:.55rem; }
        .execution-trace-head strong { color:#1e3a8a; font-size:1rem; }
        .execution-trace-head p { margin:.12rem 0 0 !important; color:#475569; font-size:.82rem !important; line-height:1.35 !important; }
        .execution-trace-head > span { white-space:nowrap; padding:.25rem .5rem; border-radius:999px; background:#dbeafe; color:#1e3a8a; font-size:.76rem; font-weight:800; }
        .execution-effect { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.45rem; margin:.15rem 0 .6rem; }
        .execution-effect article { padding:.52rem .58rem; border-radius:11px; background:#ffffff; border:1px solid #dbeafe; }
        .execution-effect b { display:block; color:#1e3a8a; font-size:.74rem; text-transform:uppercase; letter-spacing:.035em; margin-bottom:.18rem; }
        .execution-effect span { display:block; color:#334155; font-size:.78rem; line-height:1.32; overflow-wrap:anywhere; }
        .execution-underhood { margin:.2rem 0 .35rem; color:#0f172a; font-size:.78rem; font-weight:800; }
        .execution-motion-key { display:flex; align-items:center; gap:.45rem; margin:.1rem 0 .55rem; color:#92400e; font-size:.76rem; font-weight:700; }
        .execution-motion-key > span { width:16px; height:16px; border-radius:50%; background:#f59e0b; border:3px solid #ffffff; box-shadow:0 0 0 4px rgba(245,158,11,.2); }
        .execution-grid-wrap { position:relative; overflow:visible; padding:.15rem 0 .2rem; isolation:isolate; }
        .execution-route-layer { position:absolute; inset:0; z-index:1; width:100%; height:100%; overflow:visible; pointer-events:none; }
        .execution-route-line { fill:none; stroke:#93c5fd; stroke-width:1.2; vector-effect:non-scaling-stroke; }
        .execution-route-arrow { fill:#60a5fa; }
        .execution-route-progress { fill:none; stroke:#f59e0b; stroke-width:2.4; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:8 7; vector-effect:non-scaling-stroke; animation-duration:7.2s; animation-iteration-count:1; animation-timing-function:linear; animation-fill-mode:forwards; }
        .execution-moving-token { position:absolute; z-index:5; left:0; top:0; width:34px; height:34px; transform:translate(-50%,-50%); border-radius:50%; display:flex; align-items:center; justify-content:center; background:#f59e0b; color:#ffffff; border:4px solid #ffffff; box-shadow:0 0 0 7px rgba(245,158,11,.2),0 8px 18px rgba(146,64,14,.35); animation-duration:7.2s; animation-iteration-count:1; animation-timing-function:linear; animation-fill-mode:forwards; pointer-events:none; }
        .execution-moving-token span { font-size:.8rem; margin-left:1px; }
        .execution-moving-token::after { content:''; position:absolute; inset:-10px; border:2px solid rgba(245,158,11,.45); border-radius:50%; animation:executionTokenRipple 1.05s ease-out infinite; }
        @keyframes executionTokenRipple { 0% { transform:scale(.65); opacity:.9; } 100% { transform:scale(1.25); opacity:0; } }
        .execution-grid { position:relative; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.48rem; width:100%; z-index:3; }
        .trace-diamond .execution-node:nth-child(1) { grid-column:2; grid-row:1; }
        .trace-diamond .execution-node:nth-child(2) { grid-column:1; grid-row:2; }
        .trace-diamond .execution-node:nth-child(3) { grid-column:2; grid-row:2; }
        .trace-diamond .execution-node:nth-child(4) { grid-column:3; grid-row:2; }
        .trace-diamond .execution-node:nth-child(5) { grid-column:2; grid-row:3; }
        .trace-zigzag .execution-node:nth-child(1) { grid-column:1; grid-row:1; }
        .trace-zigzag .execution-node:nth-child(2) { grid-column:2; grid-row:1; }
        .trace-zigzag .execution-node:nth-child(3) { grid-column:3; grid-row:1; }
        .trace-zigzag .execution-node:nth-child(4) { grid-column:3; grid-row:2; }
        .trace-zigzag .execution-node:nth-child(5) { grid-column:2; grid-row:2; }
        .trace-zigzag .execution-node:nth-child(6) { grid-column:1; grid-row:2; }
        .execution-line,.execution-packet { display:none; }
        .execution-node {
            position:relative; z-index:2; min-height:88px; padding:.58rem .42rem .48rem;
            background:#ffffff; border:1px solid #bfdbfe; border-radius:14px; text-align:center;
            animation-duration:1s; animation-iteration-count:1; animation-timing-function:ease-in-out; animation-fill-mode:both;
        }
        .execution-step {
            position:absolute; top:.3rem; left:.35rem; display:flex; align-items:center; justify-content:center;
            width:22px; height:22px; border-radius:50%; background:#2563eb; color:#ffffff;
            font-size:.68rem; font-weight:800; box-shadow:0 4px 10px rgba(37,99,235,.2);
        }
        .execution-icon {
            display:flex; align-items:center; justify-content:center; width:38px; height:30px;
            margin:0 auto .28rem; border-radius:8px; background:#0f172a; color:#67e8f9;
            font-family:Consolas,monospace; font-size:.72rem; font-weight:800;
        }
        .execution-node strong { display:block; color:#1e3a8a; font-size:.8rem; line-height:1.2; }
        .execution-node small { display:block; color:#64748b; font-size:.68rem; line-height:1.2; margin-top:.16rem; overflow-wrap:anywhere; }
        .execution-sequence-note { margin-top:.4rem; color:#64748b; font-size:.74rem; text-align:center; }
        .execution-touchpoints { display:flex; flex-wrap:wrap; gap:.35rem; margin-top:.48rem; }
        .execution-touchpoints span { padding:.25rem .45rem; border-radius:999px; background:#ffffff; border:1px solid #dbeafe; color:#475569; font-size:.72rem; }
        .compact-result-title { margin:.15rem 0 .35rem; color:#1e3a8a; font-weight:800; }
        .learn-card { min-height:92px; padding:.65rem .75rem; }

        /* Commercial pre-launch roadmap. */
        .pro-roadmap {
            display:grid;
            grid-template-columns:repeat(3,minmax(0,1fr));
            gap:.75rem;
            margin:.45rem 0 .75rem;
        }
        .pro-roadmap-step {
            position:relative;
            padding:.9rem;
            border:1px solid #cbd5e1;
            border-radius:14px;
            background:#ffffff;
        }
        .pro-roadmap-step.current {
            border:2px solid #2563eb;
            background:#eff6ff;
        }
        .pro-roadmap-step > span {
            display:inline-flex;
            margin-bottom:.45rem;
            padding:.2rem .45rem;
            border-radius:999px;
            background:#e2e8f0;
            color:#334155;
            font-size:.75rem !important;
            font-weight:800;
        }
        .pro-roadmap-step.current > span {
            background:#2563eb;
            color:#ffffff;
        }
        .pro-roadmap-step > strong {
            display:block;
            color:#1e3a8a;
            margin-bottom:.3rem;
        }
        .pro-roadmap-step > p {
            margin:0 !important;
            color:#475569;
            font-size:.9rem !important;
            line-height:1.45 !important;
        }

        /* Reusable infrastructure simulation flow. */
        .ops-flow { margin:1rem 0 1.2rem; padding:1rem; border-radius:20px; background:linear-gradient(180deg,#ffffff,#eff6ff); border:1px solid #bfdbfe; box-shadow:0 12px 30px rgba(15,23,42,.07); }
        .ops-flow-heading { display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; margin-bottom:.75rem; }
        .ops-flow-heading strong { color:#0f172a; font-size:1.08rem; }
        .ops-flow-heading span { color:#64748b; font-size:.9rem; text-align:right; }
        .ops-flow-track { position:relative; display:grid; grid-template-columns:repeat(6,minmax(100px,1fr)); gap:.62rem; align-items:stretch; }
        .ops-flow-line { position:absolute; left:5%; right:5%; top:52px; height:4px; border-radius:999px; background:linear-gradient(90deg,#93c5fd,#2563eb,#0891b2); z-index:0; }
        .ops-flow-ball { position:absolute; top:43px; width:20px; height:20px; border-radius:50%; opacity:0; z-index:4; background:#f59e0b; border:3px solid #ffffff; box-shadow:0 0 0 6px rgba(245,158,11,.16); animation-duration:5.6s; animation-iteration-count:1; animation-fill-mode:forwards; animation-timing-function:ease-in-out; }
        .ops-flow-ball.b { background:#22c55e; animation-delay:.32s; }
        .ops-flow-node { position:relative; z-index:2; min-height:132px; padding:.72rem .55rem; border-radius:14px; border:1px solid #bfdbfe; background:#ffffff; text-align:center; box-shadow:0 10px 28px rgba(15,23,42,.08); animation-duration:2.6s; animation-iteration-count:1; animation-timing-function:ease-in-out; }
        .ops-flow-node strong { display:block; color:#1e3a8a; font-size:.92rem; }
        .ops-flow-node span { display:block; color:#64748b; font-size:.78rem; line-height:1.3; margin-top:.25rem; }
        .ops-flow-icon { height:60px; display:flex; align-items:center; justify-content:center; }
        .ops-flow-icon svg { width:56px; height:56px; }
        .ops-flow-note { margin-top:.7rem; color:#64748b; font-size:.85rem; text-align:center; }

        @media (max-width:900px) {
            .pro-roadmap { grid-template-columns:1fr; }
            .command-mode-guide { grid-template-columns:1fr; }
            .execution-route-layer { display:none; }
            .execution-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .trace-diamond .execution-node, .trace-zigzag .execution-node { grid-column:auto !important; grid-row:auto !important; }
            .overview-hero { padding:1.5rem 1.2rem 1.1rem; }
            .overview-hero h1 { font-size:2.2rem !important; }
            .hero-demo { min-height:auto; padding:1rem; }
            .hero-demo-head { align-items:flex-start; }
            .hero-network { grid-template-columns:repeat(2,minmax(130px,1fr)); }
            .hero-network-line,.hero-demo-packet { display:none; }
            .hero-node .ops-flow-node { min-height:126px; }
            .hero-result-stage { min-height:190px; }
            .ops-flow-track { grid-template-columns:repeat(2,minmax(130px,1fr)); }
            .ops-flow-line,.ops-flow-ball { display:none; }
            .ops-flow-heading { display:block; }
            .ops-flow-heading span { display:block; text-align:left; margin-top:.25rem; }
        }
        @media (max-width:560px) {
            .execution-trace-head { display:block; }
            .execution-trace-head > span { display:inline-flex; margin-top:.35rem; }
            .execution-effect { grid-template-columns:1fr; }
            .execution-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .execution-node { min-height:82px; }
            .overview-stats { display:grid; grid-template-columns:1fr; }
            .hero-demo-head { display:block; }
            .hero-live-dot { margin-top:.45rem; }
            .hero-terminal-mini { font-size:.82rem; }
            .hero-network { grid-template-columns:1fr; }
            .hero-result-stage { min-height:240px; }
            .hero-health-card,.hero-log-card,.hero-finish-card { padding:.85rem; }
            .hero-meter { grid-template-columns:70px 1fr 42px; }
            .ops-flow-track { grid-template-columns:1fr; }
        }
        @media (max-width:560px) {
            .terminal { font-size:.88rem; padding:.85rem; border-radius:12px; }
            [data-testid="stMetricValue"] { font-size:1.35rem !important; }
        }
        @media (prefers-reduced-motion:reduce) {
            .hero-demo .hero-demo-typing,.hero-demo .hero-demo-packet,.hero-demo .hero-node,
            .hero-demo .hero-health-card,.hero-demo .hero-log-card,.hero-demo .hero-finish-card,
            .hero-demo .hero-stage-label,.ops-flow-ball,.ops-flow-node,.execution-packet,.execution-node,.execution-moving-token,.execution-route-progress { animation:none !important; }
            .execution-moving-token { display:none !important; }
            .hero-demo .hero-network,.hero-demo .hero-result-stage,.hero-demo .hero-stage-labels { display:none; }
            .hero-demo .hero-static-fallback { display:block; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(kicker: str, title: str, body: str) -> None:
    st.markdown(
        f"<div class='hero'><small>{html.escape(kicker)}</small><h1>{html.escape(title)}</h1><p>{html.escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def terminal(
    command: str,
    output: str,
    prompt: str = "student@linux-lab:~$",
    *,
    compact: bool = False,
) -> None:
    classes = "terminal compact" if compact else "terminal"
    st.markdown(
        f"<div class='{classes}'><span class='prompt'>{html.escape(prompt)}</span> <span class='cmd'>{html.escape(command)}</span>\n{html.escape(output)}</div>",
        unsafe_allow_html=True,
    )


def panel(title: str, body: str) -> None:
    st.markdown(
        f"<div class='panel'><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def learning_card(title: str, body: str) -> None:
    st.markdown(
        f"<div class='learn-card'><b>{html.escape(title)}</b>{html.escape(body)}</div>",
        unsafe_allow_html=True,
    )
