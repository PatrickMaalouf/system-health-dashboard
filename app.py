"""
app.py – System Health Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Streamlit application that visualises the five KPIs stored in
data/health.db.  Place this file at the project root so Streamlit Cloud
can discover it automatically.

Run locally:
    streamlit run app.py
"""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "data" / "health.db"
SQL_DIR = PROJECT_ROOT / "sql"


# ── Helpers ────────────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    """Return a cached SQLite connection (read-only)."""
    if not DB_PATH.exists():
        st.error(
            f"Database not found at `{DB_PATH}`.\n\n"
            "Run `python scripts/load_to_sqlite.py` first."
        )
        st.stop()
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=300)
def run_query(filename: str) -> pd.DataFrame:
    """Execute a SQL file from the sql/ directory and return a DataFrame."""
    sql_path = SQL_DIR / filename
    sql = sql_path.read_text(encoding="utf-8")
    conn = get_connection()
    return pd.read_sql_query(sql, conn)


# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="System Health Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS for a premium look ──────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Import Google Font ─────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Global ─────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header banner ──────────────────────────────────── */
    .dashboard-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        color: #ffffff;
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        margin: 0.3rem 0 0;
        opacity: 0.75;
        font-size: 0.95rem;
    }

    /* ── Scorecard (big KPI) ────────────────────────────── */
    .scorecard {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 2rem 1.8rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .scorecard:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    }
    .scorecard .label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #8b8fa3;
        margin-bottom: 0.5rem;
    }
    .scorecard .value {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
    }
    .scorecard .sub {
        font-size: 0.82rem;
        color: #6b7280;
        margin-top: 0.6rem;
    }
    .green  { color: #34d399; }
    .amber  { color: #fbbf24; }
    .red    { color: #f87171; }

    /* ── Chart card wrapper ─────────────────────────────── */
    .chart-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        margin-bottom: 1rem;
    }
    .chart-card h3 {
        margin: 0 0 0.25rem;
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .chart-card .chart-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 1rem;
    }

    /* Hide default Streamlit footer */
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="dashboard-header">
        <h1>🩺 System Health Dashboard</h1>
        <p>Real-time KPI overview &mdash; uptime, error trends, ticket distribution &amp; resolution times</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Load data ──────────────────────────────────────────────────────────
df_uptime = run_query("uptime_percentage.sql")
df_errors = run_query("weekly_error_rate.sql")
df_tickets = run_query("tickets_by_category.sql")
df_resolution = run_query("avg_resolution_time.sql")
df_backlog = run_query("open_vs_resolved.sql")

# ── Row 1: Scorecard metrics ──────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

# 1-a  Uptime %
uptime_pct = float(df_uptime["uptime_pct"].iloc[0])
up_hours = int(df_uptime["up_hours"].iloc[0])
total_hours = int(df_uptime["total_hours"].iloc[0])
color_class = "green" if uptime_pct >= 99.5 else ("amber" if uptime_pct >= 95 else "red")

with col1:
    st.markdown(
        f"""
        <div class="scorecard">
            <div class="label">Uptime</div>
            <div class="value {color_class}">{uptime_pct:.2f}%</div>
            <div class="sub">{up_hours:,} / {total_hours:,} hours up</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 1-b  Total tickets
total_tickets = int(df_tickets["total_tickets"].sum())
critical_tickets = int(df_tickets["critical"].sum())

with col2:
    st.markdown(
        f"""
        <div class="scorecard">
            <div class="label">Total Tickets</div>
            <div class="value" style="color:#818cf8;">{total_tickets:,}</div>
            <div class="sub">{critical_tickets} critical</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 1-c  Avg Resolution Time (overall)
overall_avg_hrs = (
    (df_resolution["avg_hours"] * df_resolution["resolved_tickets"]).sum()
    / df_resolution["resolved_tickets"].sum()
)

with col3:
    st.markdown(
        f"""
        <div class="scorecard">
            <div class="label">Avg Resolution Time</div>
            <div class="value" style="color:#38bdf8;">{overall_avg_hrs:.1f} h</div>
            <div class="sub">{int(df_resolution["resolved_tickets"].sum())} resolved tickets</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 1-d  Current week error count
latest_week_errors = int(df_errors["ticket_count"].iloc[-1])
prev_week_errors = int(df_errors["ticket_count"].iloc[-2]) if len(df_errors) > 1 else 0
delta = latest_week_errors - prev_week_errors
delta_icon = "▲" if delta > 0 else ("▼" if delta < 0 else "–")
delta_color = "red" if delta > 0 else "green"

with col4:
    st.markdown(
        f"""
        <div class="scorecard">
            <div class="label">Latest Week Errors</div>
            <div class="value" style="color:#fb923c;">{latest_week_errors}</div>
            <div class="sub"><span class="{delta_color}">{delta_icon} {abs(delta)}</span> vs prior week</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 2: Charts ─────────────────────────────────────────────────────
left_col, right_col = st.columns(2)

# Shared Plotly layout defaults (dark, minimal)
_layout = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13, color="#cbd5e1"),
    margin=dict(l=40, r=20, t=10, b=40),
    height=370,
)

# 2-a  Error Rate Over Time (line chart)
with left_col:
    st.markdown(
        """
        <div class="chart-card">
            <h3>📈 Error Rate Over Time</h3>
            <div class="chart-sub">Tickets opened per ISO week — spot slow degradation early</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig_errors = px.area(
        df_errors,
        x="week_start",
        y="ticket_count",
        labels={"week_start": "Week Starting", "ticket_count": "Tickets"},
    )
    fig_errors.update_traces(
        line=dict(color="#818cf8", width=2.5),
        fillcolor="rgba(129, 140, 248, 0.15)",
        hovertemplate="<b>%{x}</b><br>Tickets: %{y}<extra></extra>",
    )
    fig_errors.update_layout(**_layout)
    fig_errors.update_xaxes(showgrid=False)
    fig_errors.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    st.plotly_chart(fig_errors, use_container_width=True)

# 2-b  Tickets by Category (bar chart)
with right_col:
    st.markdown(
        """
        <div class="chart-card">
            <h3>📊 Tickets by Category</h3>
            <div class="chart-sub">Where problems cluster — guides engineering investment</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stacked bar by severity for richer insight
    severity_cols = ["critical", "high", "medium", "low"]
    colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#facc15", "low": "#34d399"}

    fig_tickets = go.Figure()
    for sev in severity_cols:
        fig_tickets.add_trace(
            go.Bar(
                x=df_tickets["category"],
                y=df_tickets[sev],
                name=sev.capitalize(),
                marker_color=colors[sev],
                hovertemplate="%{x}<br>" + sev.capitalize() + ": %{y}<extra></extra>",
            )
        )
    fig_tickets.update_layout(
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        **_layout,
    )
    fig_tickets.update_xaxes(showgrid=False)
    fig_tickets.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    st.plotly_chart(fig_tickets, use_container_width=True)

# ── Row 3: Resolution by Severity + Open vs Resolved ──────────────────
left_col2, right_col2 = st.columns(2)

# 3-a  Resolution time by severity (horizontal bar)
with left_col2:
    st.markdown(
        """
        <div class="chart-card">
            <h3>⏱️ Avg Resolution Time by Severity</h3>
            <div class="chart-sub">Mean hours to close — broken down by ticket severity</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sev_colors = {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#facc15",
        "low": "#34d399",
    }
    bar_colors = [sev_colors.get(s, "#818cf8") for s in df_resolution["severity"]]

    fig_res = go.Figure(
        go.Bar(
            x=df_resolution["avg_hours"],
            y=df_resolution["severity"],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=df_resolution["avg_hours"].apply(lambda v: f"{v:.1f} h"),
            textposition="auto",
            textfont=dict(color="#ffffff", size=13),
            hovertemplate="%{y}: %{x:.1f} hours<extra></extra>",
        )
    )
    fig_res.update_layout(**_layout, yaxis=dict(autorange="reversed"))
    fig_res.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title_text="Hours")
    fig_res.update_yaxes(showgrid=False)
    st.plotly_chart(fig_res, use_container_width=True)

# 3-b  Open vs Resolved (backlog trend)
with right_col2:
    st.markdown(
        """
        <div class="chart-card">
            <h3>🔄 Open vs Resolved (Backlog Trend)</h3>
            <div class="chart-sub">Growing gap means the team is falling behind</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig_backlog = go.Figure()
    fig_backlog.add_trace(
        go.Scatter(
            x=df_backlog["week_start"],
            y=df_backlog["opened"],
            name="Opened",
            mode="lines+markers",
            line=dict(color="#f97316", width=2),
            marker=dict(size=5),
            hovertemplate="%{x}<br>Opened: %{y}<extra></extra>",
        )
    )
    fig_backlog.add_trace(
        go.Scatter(
            x=df_backlog["week_start"],
            y=df_backlog["resolved"],
            name="Resolved",
            mode="lines+markers",
            line=dict(color="#34d399", width=2),
            marker=dict(size=5),
            hovertemplate="%{x}<br>Resolved: %{y}<extra></extra>",
        )
    )
    fig_backlog.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        **_layout,
    )
    fig_backlog.update_xaxes(showgrid=False)
    fig_backlog.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    st.plotly_chart(fig_backlog, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("System Health Dashboard • Data sourced from `data/health.db`")
