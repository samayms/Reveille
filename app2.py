"""Reveille Deal Scout — Internal Deal Sourcing Dashboard"""

import streamlit as st
import pandas as pd
from database import fetch_leads, update_status

# ── PAGE CONFIG  (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Reveille Deal Scout",
    layout="wide",
    initial_sidebar_state="expanded",
)

STATUS_OPTIONS = ["New", "Reviewing", "Pass"]

# ── GLOBAL STYLES ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');
:root {
    --bg:           #07090d;
    --bg2:          #0c1018;
    --bg3:          #0e1320;
    --border:       #1a2035;
    --border2:      #243050;
    --text:         #cdd1e0;
    --muted:        #515c75;
    --amber:        #c98b0e;
    --amber2:       #e09a12;
    --amber-dim:    #7a5208;
    --amber-tint:   rgba(201,139,14,.09);
    --steel:        #3d6b8f;
    --steel-tint:   rgba(61,107,143,.09);
    --font-mono:    'IBM Plex Mono', 'Courier New', monospace;
    --font-display: 'Bebas Neue', Impact, sans-serif;
}

html, body, [class*="css"], .stMarkdown, p, span, div, td, th, label {
    font-family: var(--font-mono) !important;
}

/* hide Streamlit chrome */
#MainMenu, footer, .stDeployButton, header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.4rem 2rem;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 1px solid var(--border) !important;
    background: transparent !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── buttons ── */
.stButton > button {
    font-family: var(--font-mono) !important;
    font-size: 0.57rem !important;
    letter-spacing: 0.13em !important;
    text-transform: uppercase !important;
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--muted) !important;
    border-radius: 0 !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.12s !important;
}
.stButton > button:hover {
    border-color: var(--amber-dim) !important;
    color: var(--amber) !important;
    background: var(--amber-tint) !important;
}

/* ── selectbox ── */
.stSelectbox > div > div {
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    color: var(--text) !important;
}
.stSelectbox [data-baseweb="select"] ul {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 0 !important;
}

/* ── multiselect ── */
.stMultiSelect > div > div {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    font-size: 0.62rem !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 0 !important;
    font-size: 0.55rem !important;
}
.stMultiSelect label,
.stSlider label,
.stSelectbox label {
    font-size: 0.55rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── slider ── */
.stSlider [data-testid="stTickBar"] { display: none; }

/* ── dataframe ── */
[data-testid="stDataFrame"] thead th,
[data-testid="stDataFrame"] td {
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
}

/* ── divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 0.4rem 0 !important;
}

/* ── sidebar components ── */
.sidebar-wordmark {
    font-family: var(--font-display) !important;
    font-size: 1.5rem;
    letter-spacing: 0.15em;
    color: var(--amber);
    line-height: 1;
    margin-bottom: 0.1rem;
}
.sidebar-sub {
    font-size: 0.53rem;
    line-height: 1.75;
    color: var(--muted);
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.2rem;
    margin-bottom: 1.2rem;
}
.sidebar-pillars {
    display: flex;
    gap: 0.3rem;
    flex-wrap: wrap;
    margin-bottom: 1.6rem;
}
.pillar-tag {
    font-size: 0.46rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    padding: 0.13rem 0.38rem;
    border: 1px solid var(--border2);
    color: var(--muted);
}
.sidebar-kv { margin-bottom: 1.1rem; }
.sidebar-kv-label {
    font-size: 0.5rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.2rem;
}
.sidebar-kv-value {
    font-size: 1.9rem;
    font-weight: 400;
    color: var(--text);
    line-height: 1;
}
.sidebar-kv-value.amber { color: var(--amber); }
.sidebar-divider {
    border-top: 1px solid var(--border);
    margin: 1.2rem 0;
}

/* ── page header ── */
.page-header {
    display: flex;
    align-items: baseline;
    gap: 1.2rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.8rem;
    margin-bottom: 0.25rem;
}
.page-wordmark {
    font-family: var(--font-display) !important;
    font-size: 1.2rem;
    letter-spacing: 0.22em;
    color: var(--amber);
}
.page-tagline {
    font-size: 0.56rem;
    letter-spacing: 0.1em;
    color: var(--muted);
    text-transform: uppercase;
}

/* ── signal cards ── */
.signal-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-left: 3px solid var(--border2);
    padding: 0.9rem 1.05rem 0.8rem;
}
.signal-card-high { border-left-color: var(--amber); }
.signal-card-mid  { border-left-color: var(--steel); }
.signal-card-low  { border-left-color: var(--border2); }
.card-toprow {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.45rem;
}
.score-chip {
    font-family: var(--font-display) !important;
    font-size: 0.95rem;
    line-height: 1.55;
    min-width: 1.7rem;
    text-align: center;
    padding: 0 0.28rem;
    border: 1px solid var(--amber-dim);
    background: var(--amber-tint);
    color: var(--amber);
}
.score-chip-mid {
    border-color: #2d4f6a;
    background: var(--steel-tint);
    color: #5b9bd5;
}
.score-chip-low {
    border-color: var(--border2);
    background: transparent;
    color: var(--muted);
}
.source-badge {
    font-size: 0.46rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.11rem 0.38rem;
    border: 1px solid var(--border2);
    color: var(--muted);
}
.source-badge-openalex { border-color: #2d4f7a; color: #5b8fd5; }
.source-badge-nsf      { border-color: #1f5c35; color: #3da66e; }
.source-badge-sbir     { border-color: #5c3a1f; color: #c97040; }
.card-date {
    margin-left: auto;
    font-size: 0.5rem;
    color: var(--muted);
}
.card-title {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.45;
    margin-bottom: 0.38rem;
}
.card-insight {
    font-size: 0.67rem;
    color: #8a94ad;
    line-height: 1.65;
    margin-bottom: 0.45rem;
}
.card-meta {
    font-size: 0.57rem;
    color: var(--muted);
    margin-bottom: 0.35rem;
}
.card-link {
    font-size: 0.53rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--amber-dim);
    text-decoration: none;
}
.card-link:hover { color: var(--amber); }

/* ── section label + record count ── */
.section-label {
    font-size: 0.53rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.38rem;
    margin-bottom: 0.9rem;
}
.record-count {
    font-size: 0.53rem;
    letter-spacing: 0.09em;
    color: var(--muted);
    margin-bottom: 0.7rem;
}

/* ── NSF metrics grid ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    margin-bottom: 1.4rem;
}
.metric-cell {
    background: var(--bg3);
    padding: 0.9rem 1.2rem;
}
.metric-cell-label {
    font-size: 0.48rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.3rem;
}
.metric-cell-value {
    font-size: 1.5rem;
    font-weight: 400;
    color: var(--amber);
    line-height: 1;
}

/* ── research cards (rc-*) ── */
.rc {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-top: 2px solid var(--border2);
    padding: 0.95rem 1.15rem 0.85rem;
}
.rc-toprow {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.65rem;
}
.rc-date {
    margin-left: auto;
    font-size: 0.5rem;
    color: var(--muted);
}
.rc-byline { margin-bottom: 0.5rem; }
.rc-authors {
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.35;
    margin-bottom: 0.08rem;
}
.rc-institutions {
    font-size: 0.55rem;
    color: var(--muted);
    line-height: 1.4;
}
.rc-title {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--amber2);
    line-height: 1.42;
    margin-bottom: 0.65rem;
}
.rc-abstract {
    background: rgba(7,9,13,0.55);
    border: 1px solid var(--border);
    border-left: 2px solid var(--border2);
    padding: 0.55rem 0.8rem;
    margin-bottom: 0.65rem;
}
.rc-abstract-label {
    font-size: 0.43rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.28rem;
}
.rc-abstract-text {
    font-size: 0.63rem;
    color: #6d7a92;
    line-height: 1.72;
}
.rc-signal {
    border-left: 2px solid var(--amber-dim);
    padding-left: 0.7rem;
    margin-bottom: 0.65rem;
}
.rc-signal-label {
    font-size: 0.43rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--amber-dim);
    margin-bottom: 0.25rem;
}
.rc-signal-text {
    font-size: 0.67rem;
    color: #9ba5bc;
    line-height: 1.65;
}
.rc-footer {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    padding-top: 0.55rem;
    border-top: 1px solid var(--border);
}
.rc-keywords { flex: 1; }
.rc-meta-block {
    text-align: right;
    font-size: 0.54rem;
    color: var(--muted);
    line-height: 1.9;
    white-space: nowrap;
    flex-shrink: 0;
}
.rc-meta-block b { color: #6b7590; font-weight: 500; }
.kw-chip {
    display: inline-block;
    font-size: 0.46rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    padding: 0.1rem 0.33rem;
    border: 1px solid var(--border2);
    color: var(--muted);
    margin-right: 0.22rem;
    margin-bottom: 0.22rem;
}

/* ── staged placeholder ── */
.staged-box {
    border: 1px dashed var(--border2);
    padding: 2.5rem 2.5rem;
    text-align: center;
    margin: 1.5rem 0;
}
.staged-title {
    font-family: var(--font-display) !important;
    font-size: 0.9rem;
    letter-spacing: 0.22em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.staged-body {
    font-size: 0.62rem;
    line-height: 1.9;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.staged-code {
    display: inline-block;
    font-size: 0.6rem;
    background: var(--bg2);
    border: 1px solid var(--border);
    color: var(--amber-dim);
    padding: 0.5rem 1.2rem;
    letter-spacing: 0.05em;
    margin: 0.6rem 0 0.5rem;
}

/* ── grain overlay ── */
body::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
    opacity: 0.022;
    pointer-events: none;
    z-index: 99999;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    return fetch_leads()


try:
    leads = load_data()
except Exception as exc:
    st.error(f"Database unreachable — {exc}")
    st.stop()


# ── CALLBACKS ─────────────────────────────────────────────────────────────────
def on_status_change(paper_id: str) -> None:
    new_status = st.session_state[f"status_{paper_id}"]
    update_status(paper_id, new_status)
    st.cache_data.clear()


def on_oa_status_change(paper_id: str) -> None:
    new_status = st.session_state[f"oa_status_{paper_id}"]
    update_status(paper_id, new_status)
    st.cache_data.clear()


# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_amount(val) -> str:
    if val is None:
        return "—"
    try:
        v = float(str(val).replace(",", "").replace("$", "").strip())
        if v >= 1_000_000:
            return f"${v / 1_000_000:.1f}M"
        if v >= 1_000:
            return f"${v:,.0f}"
        return f"${v:.0f}"
    except (ValueError, TypeError):
        return str(val) if val else "—"


def fmt_date(val) -> str:
    if not val:
        return "—"
    return str(val)[:10]


def coerce_str(val) -> str:
    if not val:
        return ""
    if isinstance(val, list):
        return ", ".join(str(v) for v in val if v)
    return str(val)


def coerce_list(val) -> list:
    if not val:
        return []
    if isinstance(val, list):
        return val
    return [v.strip() for v in str(val).split(",") if v.strip()]


def score_chip_cls(score) -> str:
    s = score or 0
    if s >= 7:
        return "score-chip"
    if s >= 5:
        return "score-chip score-chip-mid"
    return "score-chip score-chip-low"


def card_cls(score) -> str:
    s = score or 0
    if s >= 7:
        return "signal-card signal-card-high"
    if s >= 5:
        return "signal-card signal-card-mid"
    return "signal-card signal-card-low"


def source_badge(source: str) -> str:
    s = (source or "").lower()
    if "openalex" in s:
        return '<span class="source-badge source-badge-openalex">OpenAlex</span>'
    if "nsf" in s:
        return '<span class="source-badge source-badge-nsf">NSF</span>'
    if "sbir" in s:
        return '<span class="source-badge source-badge-sbir">SBIR.gov</span>'
    return f'<span class="source-badge">{source or "Unknown"}</span>'


def safe_status(val) -> str:
    return val if val in STATUS_OPTIONS else "New"


# ── DERIVED DATA ──────────────────────────────────────────────────────────────
total_leads    = len(leads)
high_signal    = [l for l in leads if (l.get("relevance_score") or 0) >= 7]
openalex_leads = [l for l in leads if l.get("source") == "OpenAlex"]
nsf_leads      = [l for l in leads if l.get("source") == "NSF"]
sbir_leads     = [l for l in leads if l.get("source") == "SBIR.gov"]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-wordmark">REVEILLE VC</div>
        <div class="sidebar-sub">
            Backing founders building critical<br>
            technologies that keep nations running
        </div>
        <div class="sidebar-pillars">
            <span class="pillar-tag">Power</span>
            <span class="pillar-tag">Protection</span>
            <span class="pillar-tag">Productivity</span>
        </div>
        <div class="sidebar-kv">
            <div class="sidebar-kv-label">Total Leads</div>
            <div class="sidebar-kv-value">{total_leads}</div>
        </div>
        <div class="sidebar-kv">
            <div class="sidebar-kv-label">High Signal &mdash; 7+</div>
            <div class="sidebar-kv-value amber">{len(high_signal)}</div>
        </div>
        <div class="sidebar-divider"></div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <span class="page-wordmark">DEAL SCOUT</span>
        <span class="page-tagline">Signal Intelligence &mdash; Reveille VC</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Signal Brief", "All Leads", "Research Signals", "Funded Companies", "Federal Grants"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SIGNAL BRIEF
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    sorted_hs = sorted(high_signal, key=lambda x: x.get("relevance_score") or 0, reverse=True)

    st.markdown(
        '<div class="section-label">High-Signal Leads &mdash; Score 7 or Above &mdash; All Sources</div>',
        unsafe_allow_html=True,
    )

    if not sorted_hs:
        st.markdown(
            '<div class="record-count">No high-signal leads found.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="record-count">{len(sorted_hs)} records</div>',
            unsafe_allow_html=True,
        )

    for lead in sorted_hs:
        paper_id = lead.get("paper_id", "")
        score    = lead.get("relevance_score") or 0
        source   = lead.get("source", "")
        title    = lead.get("title", "Untitled")
        insight  = lead.get("why_this_matters", "")
        authors  = coerce_str(lead.get("authors")) or lead.get("pi_email", "")
        date_str = fmt_date(lead.get("publication_date") or lead.get("created_at"))
        url      = lead.get("source_url", "")
        cur_stat = safe_status(lead.get("status"))

        link_html = (
            f'<a class="card-link" href="{url}" target="_blank">View Source &rarr;</a>'
            if url else ""
        )

        card_html = f"""
        <div class="{card_cls(score)}">
            <div class="card-toprow">
                <span class="{score_chip_cls(score)}">{score}</span>
                {source_badge(source)}
                <span class="card-date">{date_str}</span>
            </div>
            <div class="card-title">{title}</div>
            {"<div class='card-insight'>" + insight + "</div>" if insight else ""}
            {"<div class='card-meta'>" + authors + "</div>" if authors else ""}
            {link_html}
        </div>
        """

        col_card, col_status = st.columns([6, 1])
        with col_card:
            st.markdown(card_html, unsafe_allow_html=True)
        with col_status:
            st.selectbox(
                "Status",
                options=STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(cur_stat),
                key=f"status_{paper_id}",
                on_change=on_status_change,
                args=(paper_id,),
                label_visibility="collapsed",
            )
        st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ALL LEADS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        '<div class="section-label">All Leads</div>',
        unsafe_allow_html=True,
    )

    all_sources = sorted({l.get("source", "") for l in leads if l.get("source")})

    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        sel_sources = st.multiselect("Source", options=all_sources, default=all_sources)
    with col_f2:
        min_score = st.slider("Min Score", min_value=1, max_value=10, value=1)
    with col_f3:
        sel_statuses = st.multiselect("Status", options=STATUS_OPTIONS, default=STATUS_OPTIONS)

    filtered = [
        l for l in leads
        if (l.get("source") or "") in sel_sources
        and (l.get("relevance_score") or 0) >= min_score
        and safe_status(l.get("status")) in sel_statuses
    ]
    filtered = sorted(filtered, key=lambda x: x.get("relevance_score") or 0, reverse=True)

    st.markdown(
        f'<div class="record-count">{len(filtered)} records</div>',
        unsafe_allow_html=True,
    )

    if filtered:
        rows = []
        for l in filtered:
            sig = l.get("why_this_matters") or ""
            rows.append({
                "Score":  l.get("relevance_score") or 0,
                "Source": l.get("source", ""),
                "Title":  l.get("title", ""),
                "Signal": sig[:130] + ("…" if len(sig) > 130 else ""),
                "Status": safe_status(l.get("status")),
                "Date":   fmt_date(l.get("publication_date") or l.get("created_at")),
            })
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
            height=580,
            column_config={
                "Score":  st.column_config.NumberColumn("Score",  width="small", format="%d"),
                "Source": st.column_config.TextColumn("Source",  width="small"),
                "Title":  st.column_config.TextColumn("Title",   width="large"),
                "Signal": st.column_config.TextColumn("Signal",  width="large"),
                "Status": st.column_config.TextColumn("Status",  width="small"),
                "Date":   st.column_config.TextColumn("Date",    width="small"),
            },
        )
    else:
        st.markdown(
            '<div class="record-count">No records match the current filters.</div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RESEARCH SIGNALS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    # ── filter bar ───────────────────────────────────────────────────────────
    col_fl1, col_fl2, col_fl3 = st.columns([2, 2, 2])
    with col_fl1:
        oa_min_score = st.slider(
            "Min Score", min_value=1, max_value=10, value=1, key="oa_score_filter"
        )
    with col_fl2:
        oa_status_filter = st.multiselect(
            "Status",
            options=STATUS_OPTIONS,
            default=STATUS_OPTIONS,
            key="oa_status_filter",
        )
    with col_fl3:
        pass  # intentional spacer

    # ── apply filters ────────────────────────────────────────────────────────
    oa_filtered = [
        l for l in openalex_leads
        if (l.get("relevance_score") or 0) >= oa_min_score
        and safe_status(l.get("status")) in oa_status_filter
    ]
    oa_sorted = sorted(oa_filtered, key=lambda x: x.get("relevance_score") or 0, reverse=True)

    st.markdown(
        f'<div class="section-label">Research Signals &mdash; OpenAlex'
        f'&nbsp;&middot;&nbsp; {len(oa_sorted)} records</div>',
        unsafe_allow_html=True,
    )

    if not oa_sorted:
        st.markdown(
            '<div class="record-count">No records match the current filters.</div>',
            unsafe_allow_html=True,
        )

    for lead in oa_sorted:
        paper_id     = lead.get("paper_id", "")
        score        = lead.get("relevance_score") or 0
        title        = lead.get("title", "Untitled")
        raw_abstract = lead.get("abstract") or ""
        abstract     = raw_abstract[:600]
        authors_str  = coerce_str(lead.get("authors"))
        inst_str     = coerce_str(lead.get("institutions"))
        keywords     = coerce_list(lead.get("keywords"))
        funding      = coerce_str(lead.get("funding_source"))
        venue        = coerce_str(lead.get("publication_venue"))
        insight      = lead.get("why_this_matters", "")
        url          = lead.get("source_url", "")
        date_str     = fmt_date(lead.get("publication_date") or lead.get("created_at"))
        cur_stat     = safe_status(lead.get("status"))

        kw_html = "".join(
            f'<span class="kw-chip">{kw}</span>' for kw in keywords[:8]
        )

        meta_lines = []
        if funding:
            meta_lines.append(f"<b>Funding</b>&ensp;{funding}")
        if venue:
            meta_lines.append(f"<b>Venue</b>&ensp;{venue}")
        meta_html = "".join(f"<div>{m}</div>" for m in meta_lines)

        link_html = (
            f'<div style="margin-top:0.35rem"><a class="card-link" href="{url}"'
            f' target="_blank">View Paper &rarr;</a></div>'
            if url else ""
        )

        abstract_block = (
            f"<div class='rc-abstract'>"
            f"<div class='rc-abstract-label'>Abstract</div>"
            f"<div class='rc-abstract-text'>{abstract}"
            f"{'&hellip;' if len(raw_abstract) > 600 else ''}</div>"
            f"</div>"
            if abstract else ""
        )

        byline_block = ""
        if authors_str or inst_str:
            byline_block = (
                f"<div class='rc-byline'>"
                + (f"<div class='rc-authors'>{authors_str}</div>" if authors_str else "")
                + (f"<div class='rc-institutions'>{inst_str}</div>" if inst_str else "")
                + "</div>"
            )

        signal_block = (
            f"<div class='rc-signal'>"
            f"<div class='rc-signal-label'>Investment Signal</div>"
            f"<div class='rc-signal-text'>{insight}</div>"
            f"</div>"
            if insight else ""
        )

        card_html = f"""
        <div class="rc">
            <div class="rc-toprow">
                <span class="{score_chip_cls(score)}">{score}</span>
                <span class="source-badge source-badge-openalex">OpenAlex</span>
                <span class="rc-date">{date_str}</span>
            </div>
            {byline_block}
            <div class="rc-title">{title}</div>
            {abstract_block}
            {signal_block}
            <div class="rc-footer">
                <div class="rc-keywords">{kw_html if kw_html else "&nbsp;"}</div>
                <div class="rc-meta-block">{meta_html}{link_html}</div>
            </div>
        </div>
        """

        col_card, col_status = st.columns([6, 1])
        with col_card:
            st.markdown(card_html, unsafe_allow_html=True)
        with col_status:
            st.selectbox(
                "Status",
                options=STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(cur_stat),
                key=f"oa_status_{paper_id}",
                on_change=on_oa_status_change,
                args=(paper_id,),
                label_visibility="collapsed",
            )
        st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FUNDED COMPANIES
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(
        '<div class="section-label">Funded Companies &mdash; NSF SBIR / STTR</div>',
        unsafe_allow_html=True,
    )

    if not nsf_leads:
        st.markdown(
            '<div class="record-count">No NSF records found.</div>',
            unsafe_allow_html=True,
        )
    else:
        amounts = []
        for l in nsf_leads:
            try:
                v = float(
                    str(l.get("award_amount") or "").replace(",", "").replace("$", "").strip()
                )
                amounts.append(v)
            except (ValueError, TypeError):
                pass

        avg_str  = fmt_amount(sum(amounts) / len(amounts)) if amounts else "—"
        pi_count = sum(1 for l in nsf_leads if l.get("pi_email"))

        st.markdown(
            f"""
            <div class="metric-grid">
                <div class="metric-cell">
                    <div class="metric-cell-label">NSF Leads</div>
                    <div class="metric-cell-value">{len(nsf_leads)}</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-cell-label">Avg Award</div>
                    <div class="metric-cell-value">{avg_str}</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-cell-label">With PI Email</div>
                    <div class="metric-cell-value">{pi_count}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nsf_sorted = sorted(nsf_leads, key=lambda x: x.get("relevance_score") or 0, reverse=True)
        rows = []
        for l in nsf_sorted:
            sig = l.get("why_this_matters") or ""
            rows.append({
                "Score":      l.get("relevance_score") or 0,
                "Title":      l.get("title", ""),
                "Grant Type": l.get("grant_type") or "—",
                "Award":      fmt_amount(l.get("award_amount")),
                "PI Email":   l.get("pi_email") or "—",
                "City":       l.get("company_city") or "—",
                "State":      l.get("company_state") or "—",
                "Expiry":     fmt_date(l.get("grant_expiry")),
                "Signal":     sig[:110] + ("…" if len(sig) > 110 else ""),
            })

        st.markdown(
            f'<div class="record-count">{len(rows)} records</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
            height=520,
            column_config={
                "Score":      st.column_config.NumberColumn("Score",      width="small", format="%d"),
                "Title":      st.column_config.TextColumn("Title",        width="large"),
                "Grant Type": st.column_config.TextColumn("Grant Type",   width="small"),
                "Award":      st.column_config.TextColumn("Award",        width="small"),
                "PI Email":   st.column_config.TextColumn("PI Email",     width="medium"),
                "City":       st.column_config.TextColumn("City",         width="small"),
                "State":      st.column_config.TextColumn("State",        width="small"),
                "Expiry":     st.column_config.TextColumn("Expiry",       width="small"),
                "Signal":     st.column_config.TextColumn("Signal",       width="large"),
            },
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — FEDERAL GRANTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(
        '<div class="section-label">Federal Grants &mdash; SBIR.gov</div>',
        unsafe_allow_html=True,
    )

    if not sbir_leads:
        st.markdown(
            """
            <div class="staged-box">
                <div class="staged-title">SBIR.gov Feed &mdash; Staged</div>
                <div class="staged-body">
                    This data source is currently staged and not yet active.<br>
                    Expected data: DoD and DoE SBIR / STTR awards.<br>
                    To activate, set the following flag in <b>config.py</b>:
                </div>
                <div class="staged-code">ENABLE_SBIR_GOV = True</div>
                <div class="staged-body" style="margin-top:0.6rem;">
                    Once enabled, this tab will display live award data from the SBIR.gov API,<br>
                    including agency, branch, topic code, and awardee contact information.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        sbir_sorted = sorted(sbir_leads, key=lambda x: x.get("relevance_score") or 0, reverse=True)
        rows = []
        for l in sbir_sorted:
            sig = l.get("why_this_matters") or ""
            rows.append({
                "Score":      l.get("relevance_score") or 0,
                "Title":      l.get("title", ""),
                "Agency":     l.get("agency") or "—",
                "Branch":     l.get("branch") or "—",
                "Grant Type": l.get("grant_type") or "—",
                "Award":      fmt_amount(l.get("award_amount")),
                "Employees":  l.get("number_employees") or "—",
                "City":       l.get("company_city") or "—",
                "State":      l.get("company_state") or "—",
                "PI Email":   l.get("pi_email") or "—",
                "POC Name":   l.get("poc_name") or "—",
                "Topic":      l.get("topic_code") or "—",
                "UEI":        l.get("uei") or "—",
                "Signal":     sig[:110] + ("…" if len(sig) > 110 else ""),
            })

        st.markdown(
            f'<div class="record-count">{len(rows)} records</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
            height=520,
            column_config={
                "Score":      st.column_config.NumberColumn("Score",      width="small", format="%d"),
                "Title":      st.column_config.TextColumn("Title",        width="large"),
                "Agency":     st.column_config.TextColumn("Agency",       width="small"),
                "Branch":     st.column_config.TextColumn("Branch",       width="small"),
                "Grant Type": st.column_config.TextColumn("Grant Type",   width="small"),
                "Award":      st.column_config.TextColumn("Award",        width="small"),
                "Employees":  st.column_config.TextColumn("Employees",    width="small"),
                "City":       st.column_config.TextColumn("City",         width="small"),
                "State":      st.column_config.TextColumn("State",        width="small"),
                "PI Email":   st.column_config.TextColumn("PI Email",     width="medium"),
                "POC Name":   st.column_config.TextColumn("POC",          width="medium"),
                "Topic":      st.column_config.TextColumn("Topic",        width="small"),
                "UEI":        st.column_config.TextColumn("UEI",          width="small"),
                "Signal":     st.column_config.TextColumn("Signal",       width="large"),
            },
        )
