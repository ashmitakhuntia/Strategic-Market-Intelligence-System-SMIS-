"""
app.py — Streamlit UI for the Strategic Market Intelligence System (SMIS)
Calls run_research_pipeline(query) from pipeline.py and renders results beautifully.
"""

import streamlit as st
import sys
import io
import time
import textwrap
from datetime import datetime

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="SMIS · Strategic Market Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme tokens ─────────────────────────────────────────────────────────────
DARK = {
    "bg":           "#0A0C10",
    "surface":      "#111318",
    "card":         "#161A22",
    "border":       "#1E2330",
    "accent":       "#4F8EF7",
    "accent2":      "#7C4DFF",
    "accent3":      "#00D4A8",
    "text":         "#E8EAF0",
    "muted":        "#6B7280",
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "error":        "#EF4444",
    "agent1":       "#4F8EF7",
    "agent2":       "#7C4DFF",
    "agent3":       "#00D4A8",
    "agent4":       "#F59E0B",
}

LIGHT = {
    "bg":           "#F0F4FF",
    "surface":      "#FFFFFF",
    "card":         "#F8FAFF",
    "border":       "#DDE3F0",
    "accent":       "#2563EB",
    "accent2":      "#6D28D9",
    "accent3":      "#059669",
    "text":         "#111827",
    "muted":        "#6B7280",
    "success":      "#059669",
    "warning":      "#D97706",
    "error":        "#DC2626",
    "agent1":       "#2563EB",
    "agent2":       "#6D28D9",
    "agent3":       "#059669",
    "agent4":       "#D97706",
}

# ── Session state defaults ────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "page" not in st.session_state:
    st.session_state.page = "Research"
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "logs" not in st.session_state:
    st.session_state.logs = []

T = DARK if st.session_state.theme == "dark" else LIGHT

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Reset & base */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background: {T['bg']} !important;
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif;
}}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="collapsedControl"] {{ display: none !important; }}
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}

section[data-testid="stMain"] > div {{ padding-top: 0 !important; }}
.block-container {{ padding: 0 1.5rem 3rem !important; max-width: 1200px !important; margin: 0 auto; }}

/* ── NAVBAR ── */
.smis-nav {{
    position: sticky;
    top: 0;
    z-index: 999;
    background: {T['surface']};
    border-bottom: 1px solid {T['border']};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    height: 64px;
    margin: 0 -1.5rem 2rem;
}}
.smis-nav-logo {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: {T['text']};
    letter-spacing: -0.02em;
}}
.smis-nav-logo span {{
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.smis-nav-links {{
    display: flex;
    align-items: center;
    gap: 0.25rem;
}}
.nav-pill {{
    padding: 0.45rem 1rem;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    border: none;
    background: transparent;
    color: {T['muted']};
    transition: all 0.15s ease;
    text-decoration: none;
    display: inline-block;
}}
.nav-pill:hover {{ background: {T['border']}; color: {T['text']}; }}
.nav-pill.active {{
    background: linear-gradient(135deg, {T['accent']}22, {T['accent2']}22);
    color: {T['accent']};
    border: 1px solid {T['accent']}44;
}}
.theme-btn {{
    width: 38px; height: 38px;
    border-radius: 50%;
    border: 1px solid {T['border']};
    background: {T['card']};
    color: {T['text']};
    cursor: pointer;
    font-size: 1rem;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.15s;
    margin-left: 0.5rem;
}}
.theme-btn:hover {{ border-color: {T['accent']}; }}

/* ── HERO ── */
.hero {{
    text-align: center;
    padding: 3.5rem 1rem 2.5rem;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: {T['accent']}18;
    border: 1px solid {T['accent']}33;
    color: {T['accent']};
    padding: 0.3rem 0.85rem;
    border-radius: 100px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
}}
.hero h1 {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, {T['text']} 30%, {T['accent']} 70%, {T['accent2']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.hero p {{
    font-size: 1.05rem;
    color: {T['muted']};
    max-width: 520px;
    margin: 0 auto 2rem;
    line-height: 1.6;
}}

/* ── SEARCH BOX ── */
.search-wrap {{
    max-width: 680px;
    margin: 0 auto;
    position: relative;
}}
[data-testid="stTextInput"] input {{
    background: {T['surface']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 14px !important;
    color: {T['text']} !important;
    padding: 1rem 1.25rem !important;
    font-size: 1rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
    box-shadow: 0 2px 12px {T['accent']}11 !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent']}22 !important;
    outline: none !important;
}}
[data-testid="stTextInput"] label {{ display: none !important; }}

/* ── BUTTONS ── */
[data-testid="stButton"] button {{
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']}) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 20px {T['accent']}33 !important;
    letter-spacing: 0.01em !important;
    width: 100%;
}}
[data-testid="stButton"] button:hover {{
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}}

/* ── AGENT PIPELINE CARDS ── */
.pipeline-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 2rem 0;
}}
.agent-card {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 14px;
    padding: 1.25rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}}
.agent-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}}
.agent-card.a1::before {{ background: {T['agent1']}; }}
.agent-card.a2::before {{ background: {T['agent2']}; }}
.agent-card.a3::before {{ background: {T['agent3']}; }}
.agent-card.a4::before {{ background: {T['agent4']}; }}
.agent-card.active {{ transform: translateY(-3px); }}
.agent-card.a1.active {{ border-color: {T['agent1']}66; box-shadow: 0 8px 30px {T['agent1']}22; }}
.agent-card.a2.active {{ border-color: {T['agent2']}66; box-shadow: 0 8px 30px {T['agent2']}22; }}
.agent-card.a3.active {{ border-color: {T['agent3']}66; box-shadow: 0 8px 30px {T['agent3']}22; }}
.agent-card.a4.active {{ border-color: {T['agent4']}66; box-shadow: 0 8px 30px {T['agent4']}22; }}
.agent-card.done {{ opacity: 1; }}
.agent-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    color: {T['muted']};
    margin-bottom: 0.6rem;
    letter-spacing: 0.06em;
}}
.agent-name {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: {T['text']};
    margin-bottom: 0.3rem;
}}
.agent-desc {{
    font-size: 0.78rem;
    color: {T['muted']};
    line-height: 1.4;
}}
.agent-status {{
    margin-top: 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.65rem;
    border-radius: 100px;
    display: inline-block;
}}
.status-idle {{ background: {T['border']}; color: {T['muted']}; }}
.status-running {{ background: {T['accent']}22; color: {T['accent']}; }}
.status-done {{ background: {T['success']}22; color: {T['success']}; }}
.status-error {{ background: {T['error']}22; color: {T['error']}; }}

/* ── RESULT SECTIONS ── */
.result-section {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
}}
.result-section-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.result-section-content {{
    font-size: 0.95rem;
    line-height: 1.75;
    color: {T['text']};
    white-space: pre-wrap;
}}
.dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}}

/* ── LOG BOX ── */
.log-box {{
    background: {T['bg']};
    border: 1px solid {T['border']};
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: {T['muted']};
    max-height: 180px;
    overflow-y: auto;
    line-height: 1.7;
}}
.log-line {{ color: {T['accent3']}; }}

/* ── ABOUT ── */
.about-hero {{
    background: linear-gradient(135deg, {T['accent']}18 0%, {T['accent2']}18 100%);
    border: 1px solid {T['border']};
    border-radius: 20px;
    padding: 3rem;
    margin-bottom: 2rem;
    text-align: center;
}}
.about-hero h2 {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}}
.about-hero p {{
    color: {T['muted']};
    font-size: 1rem;
    line-height: 1.7;
    max-width: 640px;
    margin: 0 auto;
}}
.feature-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}}
.feature-card {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
}}
.feature-icon {{ font-size: 2rem; margin-bottom: 0.75rem; }}
.feature-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: {T['text']};
    margin-bottom: 0.5rem;
}}
.feature-text {{ font-size: 0.85rem; color: {T['muted']}; line-height: 1.5; }}

/* ── HISTORY ── */
.history-item {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: border-color 0.15s;
}}
.history-item:hover {{ border-color: {T['accent']}66; }}
.history-query {{
    font-weight: 500;
    font-size: 0.9rem;
    color: {T['text']};
}}
.history-meta {{ font-size: 0.78rem; color: {T['muted']}; margin-top: 0.2rem; }}
.history-badge {{
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.22rem 0.65rem;
    border-radius: 100px;
}}
.badge-ok {{ background: {T['success']}22; color: {T['success']}; }}
.badge-err {{ background: {T['error']}22; color: {T['error']}; }}

/* ── METRIC CHIPS ── */
.metrics-row {{
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}}
.metric-chip {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    flex: 1;
    min-width: 140px;
}}
.metric-chip-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: {T['accent']};
}}
.metric-chip-label {{ font-size: 0.78rem; color: {T['muted']}; margin-top: 0.15rem; }}

/* ── SPINNER OVERRIDE ── */
[data-testid="stSpinner"] {{ color: {T['accent']} !important; }}
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {T['accent']}, {T['accent2']}) !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.st-key-navbar {{
    position: sticky;
    top: 0;
    z-index: 999;
    background: {T['surface']};
    border-bottom: 1px solid {T['border']};
    margin: 0 -1.5rem 2rem;
    padding: 0.55rem 2rem 0.55rem 2rem;
}}
.st-key-navbar [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
    gap: 0.4rem;
}}
.nav-logo {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: {T['text']};
    letter-spacing: -0.02em;
    white-space: nowrap;
}}
.nav-logo span {{
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.st-key-navbar [data-testid="stButton"] button {{
    background: transparent !important;
    border: 1px solid {T['border']} !important;
    box-shadow: none !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.9rem !important;
    border-radius: 8px !important;
    color: {T['muted']} !important;
    font-weight: 500 !important;
    width: auto !important;
}}
.st-key-navbar [data-testid="stButton"] button:hover {{
    border-color: {T['accent']} !important;
    color: {T['text']} !important;
}}
</style>
""", unsafe_allow_html=True)

with st.container(key="navbar"):
    nav_cols = st.columns([5, 1, 1, 1, 0.5])
    with nav_cols[0]:
        st.markdown(
            '<div class="nav-logo">🧠&nbsp;<span>SMIS</span>&nbsp;·&nbsp;Strategic Market Intelligence System</div>',
            unsafe_allow_html=True,
        )
    with nav_cols[1]:
        active = st.session_state.page == "Research"
        if st.button("🔍 Research", key="nav_research", use_container_width=True,
                      type="primary" if active else "secondary"):
            st.session_state.page = "Research"; st.rerun()
    with nav_cols[2]:
        active = st.session_state.page == "History"
        if st.button("📋 History", key="nav_history", use_container_width=True,
                      type="primary" if active else "secondary"):
            st.session_state.page = "History"; st.rerun()
    with nav_cols[3]:
        active = st.session_state.page == "About"
        if st.button("✦ About", key="nav_about", use_container_width=True,
                      type="primary" if active else "secondary"):
            st.session_state.page = "About"; st.rerun()
    with nav_cols[4]:
        theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
        if st.button(theme_icon, key="theme_toggle"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RESEARCH
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Research":

    st.markdown(f"""
    <div class="hero">
      <div class="hero-badge">⚡ 4-Agent AI Pipeline</div>
      <h1>Market Intelligence,<br>Powered by AI Agents</h1>
      <p>Enter any market, company, or technology topic. Four specialized AI agents will research, analyze, and deliver strategic insights.</p>
    </div>
    """, unsafe_allow_html=True)

    # Search input
    col_inp, col_btn = st.columns([5, 1.2])
    with col_inp:
        query = st.text_input("query", placeholder="e.g. AI chip market 2025, EV battery trends, cloud security landscape…", label_visibility="collapsed")
    with col_btn:
        run_btn = st.button("⚡ Analyze", key="run_btn")

    # Example queries
    st.markdown(f"""
    <div style="text-align:center; margin-top:0.75rem; margin-bottom:2rem;">
      <span style="font-size:0.8rem; color:{T['muted']};">Try: &nbsp;</span>
      <span style="font-size:0.8rem; color:{T['accent']};">Generative AI market 2025</span>
      <span style="font-size:0.8rem; color:{T['muted']};"> &nbsp;·&nbsp; </span>
      <span style="font-size:0.8rem; color:{T['accent']};">Electric vehicle battery supply chain</span>
      <span style="font-size:0.8rem; color:{T['muted']};"> &nbsp;·&nbsp; </span>
      <span style="font-size:0.8rem; color:{T['accent']};">Quantum computing competitors</span>
    </div>
    """, unsafe_allow_html=True)

    # Agent pipeline visual
    def agent_pipeline_html(statuses):
        agents = [
            ("01", "Market Intelligence", "Searches the web for live signals, news & data.", "a1"),
            ("02", "Trend Analyst", "Extracts patterns and emerging market shifts.", "a2"),
            ("03", "Insights & Strategy", "Checks memory, generates strategic recommendations.", "a3"),
            ("04", "Critic", "Validates quality, stores verified insight in memory.", "a4"),
        ]
        html = '<div class="pipeline-grid">'
        for i, (num, name, desc, cls) in enumerate(agents):
            status = statuses[i]
            active_cls = "active" if status == "running" else ("done" if status == "done" else "")
            status_label = {"idle": "Idle", "running": "Running…", "done": "✓ Complete", "error": "✗ Error"}[status]
            status_cls = f"status-{status}"
            html += f"""
            <div class="agent-card {cls} {active_cls}">
              <div class="agent-num">AGENT {num}</div>
              <div class="agent-name">{name}</div>
              <div class="agent-desc">{desc}</div>
              <div class="agent-status {status_cls}">{status_label}</div>
            </div>"""
        html += "</div>"
        return html

    pipeline_placeholder = st.empty()
    pipeline_placeholder.markdown(agent_pipeline_html(["idle"] * 4), unsafe_allow_html=True)

    # ── Run pipeline ──────────────────────────────────────────────────────────
    if run_btn and query.strip():
        logs = []
        log_placeholder = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()

        def render_logs():
            lines = "".join(f'<div class="log-line">&gt; {l}</div>' for l in logs[-12:])
            log_placeholder.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)

        # Capture stdout from pipeline
        class StreamCapture(io.StringIO):
            def write(self, s):
                super().write(s)
                stripped = s.strip()
                if stripped:
                    logs.append(stripped)
                    render_logs()

        # Stage-by-stage status updates
        stage_statuses = ["idle", "idle", "idle", "idle"]
        stage_map = {
            "[1/4]": 0, "[2/4]": 1, "[3/4]": 2, "[4/4]": 3,
        }
        progress_steps = [0.0, 0.25, 0.5, 0.75, 1.0]

        def update_pipeline_status(log_line):
            for tag, idx in stage_map.items():
                if tag in log_line:
                    for i in range(idx):
                        stage_statuses[i] = "done"
                    stage_statuses[idx] = "running"
                    pipeline_placeholder.markdown(agent_pipeline_html(stage_statuses), unsafe_allow_html=True)
                    progress_bar.progress(progress_steps[idx])
                    status_text.markdown(f"<p style='color:{T['muted']};font-size:0.85rem;text-align:center;'>Running agent {idx+1} of 4…</p>", unsafe_allow_html=True)
                if "-> " in log_line and "complete" in log_line.lower() or "generated" in log_line.lower() or "stored" in log_line.lower():
                    for i in range(idx + 1):
                        if stage_statuses[i] == "running":
                            stage_statuses[i] = "done"
                    pipeline_placeholder.markdown(agent_pipeline_html(stage_statuses), unsafe_allow_html=True)

        # Monkey-patch print to capture
        old_stdout = sys.stdout
        capturer = StreamCapture()

        class TeeStream:
            """Writes to both the capturer and old stdout, and triggers UI updates."""
            def write(self, s):
                capturer.write(s)
                old_stdout.write(s)
                for line in s.strip().splitlines():
                    if line.strip():
                        update_pipeline_status(line)
            def flush(self):
                old_stdout.flush()

        sys.stdout = TeeStream()
        try:
            from pipeline import run_research_pipeline
            result = run_research_pipeline(query.strip())
        except ImportError:
            # Graceful fallback if pipeline not importable in this environment
            result = {
                "status": "error",
                "error_message": "Could not import pipeline.py — make sure app.py is in the same directory as pipeline.py and run `streamlit run app.py` from that folder.",
            }
        finally:
            sys.stdout = old_stdout

        # Mark all done / error
        if result.get("status") == "success":
            stage_statuses = ["done"] * 4
        else:
            stage_statuses = ["done", "done", "done", "error"] if result.get("status") == "error" else ["done"] * 4
        pipeline_placeholder.markdown(agent_pipeline_html(stage_statuses), unsafe_allow_html=True)
        progress_bar.progress(1.0)
        status_text.empty()

        st.session_state.result = result
        st.session_state.logs = logs
        st.session_state.history.insert(0, {
            "query": query.strip(),
            "status": result.get("status", "unknown"),
            "timestamp": datetime.now().strftime("%b %d, %Y %H:%M"),
            "result": result,
        })
        st.rerun()

    elif run_btn and not query.strip():
        st.warning("Please enter a research topic to analyze.")

    # ── Show results ──────────────────────────────────────────────────────────
    result = st.session_state.result
    if result:
        if result.get("status") == "error":
            st.markdown(f"""
            <div class="result-section" style="border-color:{T['error']}44;">
              <div class="result-section-label" style="color:{T['error']};">
                <span class="dot" style="background:{T['error']};"></span>Pipeline Error
              </div>
              <div class="result-section-content">{result.get('error_message', 'Unknown error')}</div>
            </div>""", unsafe_allow_html=True)
        else:
            # Metrics row
            raw = result.get("raw_results", [])
            started = result.get("started_at", "")
            finished = result.get("finished_at", "")
            elapsed = "—"
            if started and finished:
                try:
                    from datetime import timezone as tz
                    t0 = datetime.fromisoformat(started)
                    t1 = datetime.fromisoformat(finished)
                    secs = int((t1 - t0).total_seconds())
                    elapsed = f"{secs}s"
                except Exception:
                    pass

            st.markdown(f"""
            <div class="metrics-row">
              <div class="metric-chip">
                <div class="metric-chip-value">{len(raw)}</div>
                <div class="metric-chip-label">Sources Found</div>
              </div>
              <div class="metric-chip">
                <div class="metric-chip-value">{elapsed}</div>
                <div class="metric-chip-label">Pipeline Runtime</div>
              </div>
              <div class="metric-chip">
                <div class="metric-chip-value">4</div>
                <div class="metric-chip-label">Agents Completed</div>
              </div>
              <div class="metric-chip">
                <div class="metric-chip-value" style="color:{T['success']};">✓</div>
                <div class="metric-chip-label">Memory Updated</div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Result sections
            sections = [
                ("trend_analysis",      "Trend Analysis",              T["agent2"], "📈"),
                ("recommendation",      "Strategic Recommendation",    T["agent3"], "💡"),
                ("critique",            "Critic Review",               T["agent4"], "🔍"),
                ("final_insight",       "Final Verified Insight",      T["accent3"], "✦"),
                ("market_summary",      "Market Summary",              T["agent1"], "🌐"),
            ]

            for key, label, color, icon in sections:
                value = result.get(key)
                if value:
                    st.markdown(f"""
                    <div class="result-section" style="border-left: 3px solid {color};">
                      <div class="result-section-label" style="color:{color};">
                        {icon} &nbsp; {label}
                      </div>
                      <div class="result-section-content">{value}</div>
                    </div>""", unsafe_allow_html=True)

            # Show all remaining keys not already shown
            skip = {"query", "started_at", "finished_at", "status", "raw_results",
                    "trend_analysis", "recommendation", "critique", "final_insight", "market_summary", "error_message"}
            extras = {k: v for k, v in result.items() if k not in skip and isinstance(v, str) and v.strip()}
            if extras:
                with st.expander("⚙️ Additional pipeline data"):
                    for k, v in extras.items():
                        st.markdown(f"""
                        <div class="result-section">
                          <div class="result-section-label" style="color:{T['muted']};">{k.replace('_', ' ').upper()}</div>
                          <div class="result-section-content">{v}</div>
                        </div>""", unsafe_allow_html=True)

            # Logs
            if st.session_state.logs:
                with st.expander("📡 Pipeline logs"):
                    lines = "".join(f'<div class="log-line">&gt; {l}</div>' for l in st.session_state.logs)
                    st.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)

    elif not run_btn:
        # Pipeline diagram at rest
        st.markdown(f"""
        <div style="text-align:center; padding: 1rem 0 2rem; color:{T['muted']}; font-size:0.85rem;">
          ↑ Enter a query above to start the research pipeline
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "History":
    st.markdown(f"""
    <div style="padding: 2rem 0 1.5rem;">
      <h2 style="font-family:'Space Grotesk',sans-serif; font-size:1.8rem; font-weight:700; letter-spacing:-0.02em; color:{T['text']};">Research History</h2>
      <p style="color:{T['muted']}; font-size:0.9rem; margin-top:0.4rem;">All past queries run in this session.</p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown(f"""
        <div style="text-align:center; padding:4rem 0; color:{T['muted']};">
          <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
          <div style="font-size:1rem; font-weight:500;">No research runs yet</div>
          <div style="font-size:0.85rem; margin-top:0.4rem;">Head to the Research tab to get started.</div>
        </div>""", unsafe_allow_html=True)
    else:
        for i, h in enumerate(st.session_state.history):
            badge_cls = "badge-ok" if h["status"] == "success" else "badge-err"
            badge_txt = "✓ Success" if h["status"] == "success" else "✗ Error"
            st.markdown(f"""
            <div class="history-item">
              <div>
                <div class="history-query">{h['query']}</div>
                <div class="history-meta">{h['timestamp']}</div>
              </div>
              <span class="history-badge {badge_cls}">{badge_txt}</span>
            </div>""", unsafe_allow_html=True)
            if st.button(f"View results", key=f"load_{i}"):
                st.session_state.result = h["result"]
                st.session_state.page = "Research"
                st.rerun()

        if st.button("🗑 Clear history", key="clear_history"):
            st.session_state.history = []
            st.rerun()




# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "About":
    st.markdown(textwrap.dedent(f"""
    <div class="about-hero">
      <h2>20/20 — Strategic Market Intelligence System</h2>
      <p>
        Most AI "market research agents" run once and forget everything.
        Ask the same question next week and they start from zero — same
        searches, same blind spots, no memory of what they found before.
        <strong style="color:{T['text']};">20/20</strong> is built differently:
        a four-agent pipeline with <strong style="color:{T['text']};">persistent
        memory</strong>, so every research run builds on the last one instead
        of starting over. Hindsight is 20/20 — literally.
      </p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent(f"""
    <div class="result-section" style="border-left: 3px solid {T['accent2']};">
      <div class="result-section-label" style="color:{T['accent2']};">🧠 &nbsp; WHY HINDSIGHT MEMORY</div>
      <div class="result-section-content" style="color:{T['muted']};">
Generic multi-agent "crews" treat every query as a one-off snapshot. They can't
tell you if a trend they flagged last month actually played out, can't notice
they've already researched a market before, and never get smarter — they just
repeat the same work on a loop.
<br><br>
<strong style="color:{T['text']};">Hindsight</strong> gives our agents a persistent
memory layer across runs. The <strong style="color:{T['text']};">Insights Agent</strong>
cross-references new findings against everything researched before, and the
<strong style="color:{T['text']};">Critic Agent</strong> validates and stores only
verified insights — so the system's recommendations compound and improve over
time instead of resetting with every query.
      </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent(f"""
    <div style="margin: 1.5rem 0 0.75rem;">
      <h3 style="font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700; color:{T['text']};">The Pipeline</h3>
    </div>

    <div class="feature-grid">
      <div class="feature-card">
        <div class="feature-icon">🕵️</div>
        <div class="feature-title">Market Intelligence Agent</div>
        <div class="feature-text">Scours the web in real time via Tavily search, pulling news, reports, and signals relevant to your query.</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-title">Trend Analyst Agent</div>
        <div class="feature-text">Identifies macro and micro trends from raw data — what's rising, falling, or shifting in the market right now.</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">💡</div>
        <div class="feature-title">Insights & Strategy Agent</div>
        <div class="feature-text">Checks Hindsight memory for related past research, then generates strategic recommendations grounded in that history.</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Critic Agent</div>
        <div class="feature-text">Validates the recommendation for quality, consistency, and bias — then commits the verified insight back into memory.</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">Persistent Memory</div>
        <div class="feature-text">Every verified insight is stored in Hindsight, so future queries on the same market start smarter, not from scratch.</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Built on LangGraph</div>
        <div class="feature-text">The agent pipeline is orchestrated via LangGraph for clean, observable, and extensible multi-agent workflows.</div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent(f"""
    <div class="result-section" style="margin-top:1.5rem;">
      <div class="result-section-label" style="color:{T['accent']};">✦ &nbsp; HOW TO USE</div>
      <div class="result-section-content" style="color:{T['muted']};">
1.  Go to the <strong style="color:{T['text']};">Research</strong> tab.
2.  Type any market research question — a company, technology, sector, or trend.
3.  Click <strong style="color:{T['text']};">⚡ Analyze</strong> and watch the four-agent pipeline work in real time.
4.  Read the structured report: trends, strategy recommendation, and critic review.
5.  Revisit past queries anytime from the <strong style="color:{T['text']};">History</strong> tab — each one is informed by what came before it.
      </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent(f"""
    <div class="result-section">
      <div class="result-section-label" style="color:{T['accent2']};">⚙️ &nbsp; TECH STACK</div>
      <div style="display:flex; flex-wrap:wrap; gap:0.6rem; margin-top:0.5rem;">
        {"".join(f'<span style="background:{T["card"]};border:1px solid {T["border"]};border-radius:8px;padding:0.3rem 0.75rem;font-size:0.8rem;font-family:JetBrains Mono,monospace;color:{T["muted"]};">{t}</span>' for t in ["Python", "LangGraph", "Streamlit", "Tavily Search", "Hindsight Memory", "Groq / LLM", "Multi-Agent"])}
      </div>
    </div>
    """), unsafe_allow_html=True)