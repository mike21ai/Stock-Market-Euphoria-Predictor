# ============================================================
# EUPHORIA PREDICTOR TERMINAL - app.py
# Single-file Streamlit Financial Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz
from datetime import datetime, timedelta
import random
import json
import base64
import os
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Euphoria Predictor Terminal",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# CONSTANTS - 15 tickers
# ──────────────────────────────────────────────────────────────
TICKERS = [
    "KARW", "FORU", "SRAJ", "PANI", "DSSA",
    "SGER", "TPIA", "BRMS", "MLPT", "BRPT",
    "TOBA", "AUTO", "IMAS", "PSAB", "KONI",
]

COMPANY_INFO = {
    "KARW": {"name": "Meratus Jasa Prima",               "sector": "Industrials",     "founded": 2000, "director": "Hendra Gunawan"},
    "FORU": {"name": "Fortune Indonesia",                "sector": "Industrials",     "founded": 1970, "director": "Dony Subagyo"},
    "SRAJ": {"name": "Sejahteraraya Anugrahjaya",        "sector": "Health Care",     "founded": 1993, "director": "Budi Setiawan"},
    "PANI": {"name": "Pantai Indah Kapuk Dua",           "sector": "Real Estate",     "founded": 2018, "director": "Setiawan Halim"},
    "DSSA": {"name": "Dian Swastatika Sentosa",          "sector": "Energy",          "founded": 1995, "director": "Hendrik Tio"},
    "SGER": {"name": "Sumber Global Energy",             "sector": "Energy",          "founded": 2007, "director": "Agus Widjaja"},
    "TPIA": {"name": "Chandra Asri Petrochemicals",      "sector": "Basic Materials", "founded": 1984, "director": "Suryandi"},
    "BRMS": {"name": "Bumi Resources Minerals",          "sector": "Basic Materials", "founded": 2003, "director": "Saptari Hoedaja"},
    "MLPT": {"name": "Multipolar Technology",            "sector": "Technology",      "founded": 1975, "director": "Hendri Mulya"},
    "BRPT": {"name": "Barito Pacific",                   "sector": "Basic Materials", "founded": 1979, "director": "Agus Salim Pangestu"},
    "TOBA": {"name": "TBS Energi Utama",                 "sector": "Energy",          "founded": 2007, "director": "Pandu Patria Sjahrir"},
    "AUTO": {"name": "Astra Otoparts",                   "sector": "Consumer Disc.",  "founded": 1996, "director": "Djony Bunarto Tjondro"},
    "IMAS": {"name": "Indomobil Sukses Internasional",   "sector": "Consumer Disc.",  "founded": 1976, "director": "Gunadi Sindhuwinata"},
    "PSAB": {"name": "J Resources Asia Pasifik",         "sector": "Basic Materials", "founded": 2007, "director": "Edi Permadi"},
    "KONI": {"name": "Perdana Bangun Pusaka",            "sector": "Industrials",     "founded": 1981, "director": "Syamsul Hidayat"},
}

THRESHOLDS = {
    "KARW": 0.60, "FORU": 0.55, "SRAJ": 0.58, "PANI": 0.62, "DSSA": 0.70,
    "SGER": 0.50, "TPIA": 0.65, "BRMS": 0.52, "MLPT": 0.68, "BRPT": 0.60,
    "TOBA": 0.55, "AUTO": 0.50, "IMAS": 0.52, "PSAB": 0.55, "KONI": 0.50,
}

COLORS = {
    "bg":     "#0d1117",
    "panel":  "#161b22",
    "border": "#30363d",
    "text":   "#c9d1d9",
    "accent": "#58a6ff",
    "green":  "#3fb950",
    "red":    "#f85149",
    "yellow": "#d29922",
    "purple": "#a371f7",
    "cyan":   "#39d353",
}

# ──────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────
def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: #c9d1d9 !important; }
    .main { background-color: #0d1117 !important; }
    .block-container {
        padding-top: 56px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        background-color: #0d1117 !important;
    }

    #MainMenu, footer { visibility: hidden; display: none !important; }

    /* The sidebar expand button is a child of the header, so the header must keep
       a real height. Forcing height:0 clips that button, which is what made the
       sidebar impossible to reopen. Keep the header, make it see-through, and let
       clicks fall through to the page everywhere except on its own buttons. */
    header[data-testid="stHeader"] {
        background: transparent !important;
        pointer-events: none !important;
        z-index: 10001 !important;
    }
    header[data-testid="stHeader"] * { pointer-events: auto !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }

    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d !important;
    }
    [data-testid="stSidebar"] .block-container { padding-top: 70px !important; }

    /* Expand control, shown when the sidebar is closed. Pinned with fixed
       coordinates so it can never be clipped by the header or covered by the
       marquee. Test id names differ across Streamlit versions, so all known
       variants are targeted. */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        position: fixed !important;
        top: 54px !important;
        left: 10px !important;
        z-index: 10050 !important;
    }
    /* Collapse arrow inside the open sidebar. */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 10050 !important;
    }
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stExpandSidebarButton"] button,
    [data-testid="stSidebarCollapseButton"] button {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        color: #58a6ff !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.7) !important;
        pointer-events: auto !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #58a6ff !important;
        color: #58a6ff !important;
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .fade-in { animation: fadeIn 0.45s ease-out both; }

    @keyframes pulse {
        0%   { opacity: 1; transform: scale(1); }
        50%  { opacity: 0.6; transform: scale(1.2); }
        100% { opacity: 1; transform: scale(1); }
    }
    .pulse { animation: pulse 1.8s ease-in-out infinite; }

    @keyframes marqueeScroll {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    .metric-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 14px 18px; text-align: center; transition: all 0.2s ease-in-out;
        cursor: default; min-width: 140px;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(88,166,255,0.12); border-color: #58a6ff; }
    .metric-card .label { font-size:13px; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; }
    .metric-card .value { font-family: 'JetBrains Mono', monospace !important; font-size: 24px; font-weight: 600; color: #c9d1d9; }
    .metric-card .sub   { font-family: 'JetBrains Mono', monospace !important; font-size:14px; margin-top: 4px; }

    .ai-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 16px; margin-bottom: 12px; transition: all 0.2s ease-in-out;
    }
    .ai-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(88,166,255,0.1); }

    .drill-card {
        background: #161b22; border: 1px solid #30363d; border-left: 4px solid;
        border-radius: 10px; padding: 16px 20px; margin-bottom: 14px; transition: all 0.2s ease-in-out;
    }
    .drill-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(88,166,255,0.12); }

    .profile-card {
        background: #161b22; border: 1px solid #30363d; border-top: 3px solid #58a6ff;
        border-radius: 10px; padding: 20px; transition: all 0.2s ease-in-out; height: 100%;
    }
    .profile-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(88,166,255,0.12); }

    .styled-table { width: 100%; border-collapse: collapse; font-size:14px; font-family: 'Inter', sans-serif; }
    .styled-table th {
        background-color: #1c2128; color: #8b949e; text-transform: uppercase; font-size:13px;
        letter-spacing: 0.07em; padding: 10px 12px; border-bottom: 1px solid #30363d;
        text-align: left; position: sticky; top: 0;
    }
    .styled-table td {
        padding: 9px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9;
        font-family: 'JetBrains Mono', monospace; font-size:14px; vertical-align: middle;
    }
    .styled-table tr:hover td { background-color: #1c2128 !important; }
    .styled-table a { color: #58a6ff; text-decoration: none; }
    .styled-table a:hover { text-decoration: underline; }

    .euphoria-banner {
        background: linear-gradient(135deg,rgba(248,81,73,0.15),rgba(210,153,34,0.15));
        border: 1px solid #f85149; border-radius: 8px; padding: 12px 16px;
        display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label,
    div[data-testid="stCheckbox"] label {
        color: #8b949e !important; font-size: 11px !important;
        font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;
    }
    div[data-testid="stSelectbox"] > div > div {
        background-color: #1c2128 !important; border-color: #30363d !important; color: #c9d1d9 !important;
    }
    div[data-testid="stTabs"] button { color: #8b949e !important; font-size: 13px !important; font-weight: 500; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }
    div[data-testid="stTab"] { background: transparent !important; }
    [data-testid="stSpinner"] { color: #58a6ff !important; }

    /* Never let a stray rule hide the sidebar controls again. */
    button[aria-label*="idebar" i],
    button[title*="idebar" i] {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }

    .section-title {
        font-size: 14px; font-weight: 700; color: #58a6ff; text-transform: uppercase;
        letter-spacing: 0.12em; border-bottom: 1px solid #21262d;
        padding-bottom: 6px; margin-bottom: 14px;
    }

    [data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important; flex-wrap: wrap; gap: 8px;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label {
        background: #161b22 !important; border: 1px solid #30363d !important;
        border-radius: 20px; padding: 6px 14px !important; margin: 0 !important;
        cursor: pointer; transition: all 0.15s ease-in-out;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label:hover {
        border-color: #58a6ff !important; color: #c9d1d9 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
        border-color: #58a6ff !important; background: rgba(88,166,255,0.15) !important; color: #58a6ff !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label > div:first-child {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Belt and braces: Streamlit renames these test ids between versions, so a
    # small watcher re-shows the expand control if any rule ever hides it again.
    st.markdown("""
    <script>
    (function () {
        const SELECTORS = [
            '[data-testid="collapsedControl"]',
            '[data-testid="stSidebarCollapsedControl"]',
            '[data-testid="stExpandSidebarButton"]',
            '[data-testid="stSidebarCollapseButton"]',
            'button[aria-label*="idebar"]'
        ];
        function reveal() {
            const doc = window.parent ? window.parent.document : document;
            SELECTORS.forEach(function (sel) {
                doc.querySelectorAll(sel).forEach(function (el) {
                    el.style.setProperty('display', 'flex', 'important');
                    el.style.setProperty('visibility', 'visible', 'important');
                    el.style.setProperty('opacity', '1', 'important');
                    el.style.setProperty('pointer-events', 'auto', 'important');
                });
            });
        }
        reveal();
        setInterval(reveal, 1000);
    })();
    </script>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# INSTITUTION LOGOS
# Files are optional. If a logo is missing the layout simply skips it.
# ──────────────────────────────────────────────────────────────
LOGO_FILES = {
    "binus": ["Logo Binus.png", "logo_binus.png", "assets/logo_binus.png"],
    "unpad": ["Logo Unpad.png", "logo_unpad.png", "assets/logo_unpad.png"],
}

@st.cache_data(show_spinner=False)
def load_logo_b64(key: str) -> str:
    for path in LOGO_FILES.get(key, []):
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                continue
    return ""

# ──────────────────────────────────────────────────────────────
# TOP BAR MARQUEE
# ──────────────────────────────────────────────────────────────
def render_top_bar(screener_df: pd.DataFrame):
    wib = pytz.timezone("Asia/Jakarta")
    now_wib = datetime.now(wib)
    status_label = "HISTORICAL DATA"
    dot_color = "#58a6ff"
    cut_off  = screener_df["SnapDate"].iloc[0] if "SnapDate" in screener_df.columns and not screener_df.empty else ""
    time_str = f"Data up to {cut_off}" if cut_off else "Historical dataset"

    items = []
    for _, row in screener_df.iterrows():
        chg = row.get("Change%", 0.0)
        arrow = "+" if chg >= 0 else ""
        color = "#3fb950" if chg >= 0 else "#f85149"
        price_str = f"{row.get('Close', 0):,.0f}"
        chg_str = f"{chg:.2f}%"
        items.append(
            f'<span style="margin:0 24px; white-space:nowrap;">'
            f'<span style="color:#8b949e;font-weight:600;letter-spacing:0.04em;">{row["Ticker"]}</span>'
            f'<span style="color:#c9d1d9;font-family:\'JetBrains Mono\',monospace;margin-left:8px;">{price_str}</span>'
            f'<span style="color:{color};font-size:11px;margin-left:6px;">{arrow}{chg_str}</span>'
            f'</span>'
        )
    double_tape = "".join(items) * 2
    st.markdown(f"""
    <div style="
        position:fixed;top:0;left:0;right:0;z-index:9000;
        background:linear-gradient(90deg,#0d1117,#161b22,#0d1117);
        border-bottom:1px solid #30363d;height:44px;
        display:flex;align-items:center;overflow:hidden;
        box-shadow:0 2px 12px rgba(0,0,0,0.5);
    ">
        <div style="flex:1;overflow:hidden;">
            <div style="
                display:inline-block;white-space:nowrap;font-size:14px;
                animation:marqueeScroll 55s linear infinite;
            ">{double_tape}</div>
        </div>
        <div style="
            display:flex;align-items:center;gap:14px;
            padding:0 18px;flex-shrink:0;
            border-left:1px solid #30363d;height:100%;
            background:#0d1117;
        ">
            <div style="display:flex;align-items:center;gap:7px;">
                <div style="
                    width:8px;height:8px;border-radius:50%;
                    background:{dot_color};box-shadow:0 0 6px {dot_color};
                "></div>
                <span style="font-size:11px;font-weight:600;color:{dot_color};">{status_label}</span>
            </div>
            <span style="font-size:11px;font-family:'JetBrains Mono',monospace;color:#8b949e;">{time_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# DATA FETCHING
# ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(ticker: str) -> pd.DataFrame:
    try:
        df = pd.read_csv("Streamlit_Daily_Data.csv")
        df = df.rename(columns={
            "date": "Date", "ticker": "Ticker", "open": "Open", "high": "High",
            "low": "Low", "close": "Close", "volume": "Volume", "rsi_14": "RSI14",
        })
        df["Date"] = pd.to_datetime(df["Date"])
        df = df[df["Ticker"] == ticker].sort_values("Date")
        # A model output only exists for the held-out split. Record that mask now:
        # filling NaN below would otherwise make every row look evaluated.
        df["in_eval"] = df["prob"].notna()
        df["is_euphoric"] = df["is_euphoric"].fillna(0).astype(int)
        df["prob"] = df["prob"].fillna(0.0).astype(float)
        df["sentiment"] = df["sentiment"].fillna(0.0).astype(float)
        return df.dropna(subset=["Close"])
    except Exception as e:
        st.error(f"Error loading daily data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def build_screener_df() -> pd.DataFrame:
    try:
        df = pd.read_csv("Streamlit_Daily_Data.csv")
        df = df.rename(columns={
            "date": "Date", "ticker": "Ticker", "open": "Open", "high": "High",
            "low": "Low", "close": "Close", "volume": "Volume", "rsi_14": "RSI14",
        })
        df["Date"] = pd.to_datetime(df["Date"])
        rows = []
        for ticker in TICKERS:
            df_t = df[df["Ticker"] == ticker].sort_values("Date")
            if df_t.empty:
                continue
            latest = df_t.iloc[-1]
            
            close = float(latest["Close"])
            chg_pct = float(latest["price_change_pct"]) if "price_change_pct" in latest else 0.0
            vol_chg_pct = float(latest["volume_change_pct"]) if "volume_change_pct" in latest else 0.0
            prob = float(latest["prob"])
            threshold = THRESHOLDS.get(ticker, 0.65)
            status = "HYPE RISK" if prob > threshold else "NORMAL"

            eval_t     = df_t[df_t["prob"].notna()]
            n_signals  = int(eval_t["is_euphoric"].fillna(0).sum()) if "is_euphoric" in eval_t else 0
            
            rows.append({
                "Ticker": ticker, 
                "Company": COMPANY_INFO[ticker]["name"],
                "Open": round(float(latest["Open"]), 2), 
                "High": round(float(latest["High"]), 2),
                "Low": round(float(latest["Low"]), 2), 
                "Close": round(close, 2),
                "Volume": float(latest["Volume"]), 
                "Change%": round(chg_pct, 2),
                "VolumeChange%": round(vol_chg_pct, 2),
                "Sentiment": round(float(latest["sentiment"]), 3), 
                "EuphoriaProb": round(prob, 3), 
                "Signals": n_signals,
                "Status": status,
                "SnapDate": latest["Date"].strftime("%d %b %Y"),
                "EvalSpan": (f'{eval_t["Date"].min().strftime("%d %b %Y")} to {eval_t["Date"].max().strftime("%d %b %Y")}'
                             if not eval_t.empty else "the held-out period"),
            })
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error building screener data: {e}")
        return pd.DataFrame()

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def fmt_volume(v: float) -> str:
    if v >= 1e9: return f"{v/1e9:.2f}B"
    if v >= 1e6: return f"{v/1e6:.2f}M"
    if v >= 1e3: return f"{v/1e3:.2f}K"
    return str(int(v))

def color_prob(p: float, ticker: str = None) -> str:
    threshold = THRESHOLDS.get(ticker, 0.65) if ticker else 0.65
    if p >= threshold: return "#f85149"
    if p >= threshold * 0.7: return "#d29922"
    return "#3fb950"

def get_xrange(df: pd.DataFrame, tf: str):
    if df.empty:
        return None, None
    end   = df["Date"].max()
    deltas = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "1Y": 365}
    if tf == "All" or tf not in deltas:
        return None, None
    days  = deltas[tf]
    start = end - timedelta(days=days)
    x_end   = (end + timedelta(days=2)).strftime("%Y-%m-%d")
    x_start = start.strftime("%Y-%m-%d")
    return x_start, x_end

PLOTLY_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(family="Inter", color="#c9d1d9", size=13),
    hoverlabel=dict(bgcolor="#161b22", bordercolor="#30363d", font_size=12, font_family="Inter"),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
)

# ──────────────────────────────────────────────────────────────
# PAGE: STOCK ANALYSIS
# ──────────────────────────────────────────────────────────────
def page_stock_analysis(ticker: str, screener_df: pd.DataFrame, drill_date: str = ""):
    with st.spinner("Loading market data and model outputs..."):
        df = fetch_stock_data(ticker)

    if df.empty:
        st.error(f"No data available for {ticker}.")
        return

    info         = COMPANY_INFO.get(ticker, {})
    company_name = info.get("name", ticker)
    latest       = df.iloc[-1]
    prev         = df.iloc[-2] if len(df) > 1 else latest
    last_price   = latest["Close"]
    chg_abs      = last_price - prev["Close"]
    chg_pct      = chg_abs / prev["Close"] * 100 if prev["Close"] else 0
    chg_color    = COLORS["green"] if chg_abs >= 0 else COLORS["red"]
    chg_arrow    = "+" if chg_abs >= 0 else ""
    rsi_val      = float(latest["RSI14"]) if not np.isnan(latest["RSI14"]) else 50.0
    sent_val     = float(latest["sentiment"])

    st.markdown(f"""
    <div class="fade-in" style="margin-bottom:18px;">
        <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;">
            <span style="font-size:26px;font-weight:700;color:#c9d1d9;">{ticker}</span>
            <span style="font-size:13px;color:#8b949e;">{company_name}</span>
            <span style="
                font-size:13px;font-weight:600;color:#58a6ff;
                background:rgba(88,166,255,0.1);border:1px solid rgba(88,166,255,0.3);
                border-radius:4px;padding:2px 8px;letter-spacing:0.06em;
            ">{info.get('sector','')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, _ = st.columns([1, 1, 1, 1, 3])
    with m1:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="label">Latest Close</div>
            <div class="value" style="color:#c9d1d9;">{last_price:,.0f}</div>
            <div class="sub" style="color:{chg_color};">{chg_arrow}{chg_abs:,.0f} ({chg_pct:.2f}%)</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="label">Volume</div>
            <div class="value">{fmt_volume(latest["Volume"])}</div>
            <div class="sub" style="color:#8b949e;">shares, latest day</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        rc = COLORS["red"] if rsi_val > 70 else (COLORS["cyan"] if rsi_val < 30 else COLORS["text"])
        rl = "Overbought" if rsi_val > 70 else ("Oversold" if rsi_val < 30 else "Neutral")
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="label">RSI 14D</div>
            <div class="value" style="color:{rc};">{rsi_val:.1f}</div>
            <div class="sub" style="color:{rc};">{rl}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        tw_latest = int(latest["tweet_count"]) if not pd.isna(latest.get("tweet_count")) else 0
        if tw_latest == 0:
            sc, sl = "#8b949e", "No data"
        else:
            sc = COLORS["green"] if sent_val > 0.05 else (COLORS["red"] if sent_val < -0.05 else COLORS["yellow"])
            sl = "Positive" if sent_val > 0.05 else ("Negative" if sent_val < -0.05 else "Neutral")
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="label">Sentiment</div>
            <div class="value" style="color:{sc};">{sent_val:+.3f}</div>
            <div class="sub" style="color:{sc};">{sl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Chart & Model Output", "Euphoria Drill-Through", "Company Profile"])

    with tab1:
        col_chart, col_ai = st.columns([7, 3])
        with col_chart:
            ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1.5, 1.5, 2])
            with ctrl1:
                chart_type = st.radio("Chart Type", ["Line", "Candlestick"], horizontal=True, key=f"ct_{ticker}")
            with ctrl2:
                show_ema = st.checkbox("EMA 20", value=True, key=f"ema_{ticker}")
            with ctrl3:
                show_rsi = st.checkbox("RSI", value=True, key=f"rsi_{ticker}")
            with ctrl4:
                timeframe = st.selectbox(
                    "Timeframe",
                    ["1D", "1W", "1M", "3M", "1Y", "All"],
                    index=5,
                    key=f"tf_{ticker}"
                )

            dff = df.copy()
            x_start, x_end = get_xrange(df, timeframe)

            row_heights = [0.55, 0.20, 0.25] if show_rsi else [0.65, 0.35]
            n_rows = 3 if show_rsi else 2
            specs  = [[{"secondary_y": True}], [{}], [{}]] if show_rsi else [[{"secondary_y": True}], [{}]]

            fig = make_subplots(
                rows=n_rows, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=row_heights,
                specs=specs,
            )

            if chart_type == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=dff["Date"], open=dff["Open"], high=dff["High"],
                    low=dff["Low"], close=dff["Close"], name="Price",
                    increasing_line_color="#3fb950", decreasing_line_color="#f85149",
                    increasing_fillcolor="#3fb950", decreasing_fillcolor="#f85149",
                ), row=1, col=1, secondary_y=False)
            else:
                fig.add_trace(go.Scatter(
                    x=dff["Date"], y=dff["Close"], name="Close",
                    line=dict(color="#58a6ff", width=1.8),
                    fill="tozeroy", fillcolor="rgba(88,166,255,0.05)",
                ), row=1, col=1, secondary_y=False)

            if show_ema:
                fig.add_trace(go.Scatter(
                    x=dff["Date"], y=dff["EMA20"], name="EMA 20",
                    line=dict(color="#d29922", width=1.3, dash="dot"),
                ), row=1, col=1, secondary_y=False)

            vol_colors = ["#3fb950" if c >= o else "#f85149" for c, o in zip(dff["Close"], dff["Open"])]
            max_vol    = dff["Volume"].max()
            vol_scaled = dff["Volume"] / max_vol if max_vol > 0 else dff["Volume"]
            fig.add_trace(go.Bar(
                x=dff["Date"], y=vol_scaled, name="Volume",
                marker_color=vol_colors, opacity=0.35,
            ), row=1, col=1, secondary_y=True)

            eu_df = dff[dff["is_euphoric"] == 1]
            if not eu_df.empty:
                fig.add_trace(go.Scatter(
                    x=eu_df["Date"], y=eu_df["High"] * 1.02,
                    mode="markers", name="Euphoria",
                    marker=dict(symbol="triangle-down", color="#d29922", size=12,
                                line=dict(width=1, color="#f85149")),
                    hovertemplate="<b>Euphoria Alert</b><br>Date: %{x}<br>High: %{customdata:,.0f}<extra></extra>",
                    customdata=eu_df["High"],
                ), row=1, col=1, secondary_y=False)

            fig.add_trace(go.Bar(
                x=dff["Date"], y=dff["tweet_count"], name="Tweet Count",
                marker_color="#a371f7", opacity=0.7,
            ), row=2, col=1)

            if show_rsi:
                fig.add_trace(go.Scatter(
                    x=dff["Date"], y=dff["RSI14"], name="RSI 14",
                    line=dict(color="#58a6ff", width=1.5),
                ), row=3, col=1)
                fig.add_hline(y=70, line=dict(color="#f85149", dash="dash", width=1), row=3, col=1)
                fig.add_hline(y=30, line=dict(color="#3fb950", dash="dash", width=1), row=3, col=1)
                fig.add_hrect(y0=70, y1=100, fillcolor="rgba(248,81,73,0.05)", line_width=0, row=3, col=1)
                fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(63,185,80,0.05)", line_width=0, row=3, col=1)

            xaxis_range = [x_start, x_end] if x_start else None
            fig.update_layout(
                **PLOTLY_BASE,
                height=620,
                hovermode="x unified",
                xaxis_rangeslider_visible=False,
                showlegend=True,
            )
            fig.update_yaxes(secondary_y=True, showticklabels=False, showgrid=False, range=[0, 4])
            fig.update_yaxes(row=1, col=1, secondary_y=False,
                             gridcolor="#21262d", tickfont=dict(family="JetBrains Mono", size=12))
            fig.update_yaxes(row=2, col=1, title_text="Tweets", gridcolor="#21262d",
                             tickfont=dict(family="JetBrains Mono", size=12))
            if show_rsi:
                fig.update_yaxes(row=3, col=1, title_text="RSI", gridcolor="#21262d",
                                 range=[0, 100], tickfont=dict(family="JetBrains Mono", size=12))
            fig.update_xaxes(
                gridcolor="#21262d", showspikes=True,
                spikecolor="#30363d", spikethickness=1,
                rangeslider_visible=False,
                **(dict(range=xaxis_range) if xaxis_range else {}),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_ai:
            st.markdown('<div class="section-title">MODEL OUTPUT</div>', unsafe_allow_html=True)
            prob_val = float(latest["prob"])
            p_color  = color_prob(prob_val, ticker)

            st.markdown(f"""
            <div class="ai-card fade-in">
                <div style="font-size:13px;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px;">
                    Euphoria Probability
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:700;color:{p_color};">
                    {prob_val*100:.1f}%
                </div>
                <div style="height:4px;background:#21262d;border-radius:2px;margin-top:10px;">
                    <div style="height:4px;width:{prob_val*100:.0f}%;background:{p_color};border-radius:2px;"></div>
                </div>
                <div style="font-size:13px;color:#8b949e;margin-top:6px;">Euphoria classifier, most recent day in the dataset</div>
                <div style="font-size:11px;color:#8b949e;margin-top:8px;line-height:1.6;">
                    Produced by the euphoria classifier, which reads the previous 30 days of 11 features
                    (open, high, low, close, volume, RSI, price change, volume change, tweet count,
                    daily sentiment, event flag). Sentiment is one input among many, so this value does
                    not follow the IndoBERT score on its own.
                </div>
            </div>
            """, unsafe_allow_html=True)

            sent_color = COLORS["green"] if sent_val > 0.1 else (COLORS["red"] if sent_val < -0.1 else COLORS["yellow"])
            sent_label = "Bullish" if sent_val > 0.1 else ("Bearish" if sent_val < -0.1 else "Neutral")
            st.markdown(f"""
            <div class="ai-card fade-in">
                <div style="font-size:13px;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px;">
                    IndoBERT Score
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;color:{sent_color};">
                        {sent_val:+.3f}
                    </div>
                    <span style="font-size:11px;font-weight:600;color:{sent_color};
                        background:rgba(88,166,255,0.1);border:1px solid {sent_color}44;
                        border-radius:4px;padding:2px 8px;">{sent_label}</span>
                </div>
                <div style="font-size:13px;color:#8b949e;margin-top:6px;">Average tweet sentiment, most recent day in the dataset</div>
            </div>
            """, unsafe_allow_html=True)

            if latest["is_euphoric"] == 1:
                st.markdown("""
                <div class="euphoria-banner fade-in">
                    <div class="pulse" style="width:10px;height:10px;border-radius:50%;background:#f85149;flex-shrink:0;"></div>
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#f85149;">EUPHORIA SIGNAL</div>
                        <div style="font-size:13px;color:#8b949e;">The most recent day in the dataset was flagged as a euphoria signal.</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            eval_df    = df[df["in_eval"]] if "in_eval" in df.columns else df
            eval_start = eval_df["Date"].min().strftime("%d %b %Y") if not eval_df.empty else "-"
            eval_end   = eval_df["Date"].max().strftime("%d %b %Y") if not eval_df.empty else "-"
            hist_start = df["Date"].min().strftime("%d %b %Y")
            st.markdown('<div class="section-title" style="margin-top:16px;">DAILY MODEL OUTPUT (10 MOST RECENT DAYS)</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-size:11px;color:#8b949e;margin:-6px 0 10px 0;line-height:1.6;">
                Price history runs from <strong style="color:#c9d1d9;">{hist_start}</strong> to
                <strong style="color:#c9d1d9;">{eval_end}</strong>. The data is split by time, with the earlier
                80 percent used to fit the model and the later 20 percent
                (<strong style="color:#c9d1d9;">{eval_start} to {eval_end}</strong>) held out for testing.
                The model produces an output for every held-out day; this table shows only the 10 most recent
                of them so the panel stays readable. The full list of flagged days is in Euphoria Signals below.
                Nothing runs past {eval_end} because the dataset ends there.
                <strong style="color:#c9d1d9;">Close</strong> is the actual closing price and
                <strong style="color:#c9d1d9;">Prob</strong> is the model's euphoria probability for that day.
            </div>
            """, unsafe_allow_html=True)
            log_df  = df.tail(10)[["Date", "Close", "prob"]].copy()
            log_rows = ""
            for _, r in log_df.iterrows():
                pc  = color_prob(r["prob"], ticker)
                log_rows += f"""
                <tr>
                    <td style="color:#8b949e;">{r['Date'].strftime('%d %b %y')}</td>
                    <td>{r['Close']:,.0f}</td>
                    <td style="color:{pc};">{r['prob']*100:.1f}%</td>
                </tr>"""
            st.markdown(f"""
            <div style="overflow-x:auto;max-height:240px;overflow-y:auto;">
            <table class="styled-table">
                <thead><tr><th>Date</th><th>Close</th><th>Prob</th></tr></thead>
                <tbody>{log_rows}</tbody>
            </table></div>
            """, unsafe_allow_html=True)

            eu_src = df[df["in_eval"]] if "in_eval" in df.columns else df
            eu_all = eu_src[eu_src["is_euphoric"] == 1][["Date", "Close", "prob"]].copy()
            if not eu_all.empty:
                st.markdown('<div class="section-title" style="margin-top:16px;">EUPHORIA SIGNALS</div>', unsafe_allow_html=True)
                st.markdown("""
                <div style="font-size:11px;color:#8b949e;margin:-6px 0 10px 0;line-height:1.6;">
                    Every day flagged as a euphoria signal in the held-out period.
                    Open the Euphoria Drill-Through tab to inspect any of these dates.
                </div>
                """, unsafe_allow_html=True)
                eu_rows = ""
                for _, r in eu_all.iterrows():
                    d_str = r["Date"].strftime("%Y-%m-%d")
                    eu_rows += f"""
                    <tr>
                        <td style="color:#c9d1d9;">{d_str}</td>
                        <td>{r['Close']:,.0f}</td>
                        <td style="color:#f85149;">{r['prob']*100:.1f}%</td>
                    </tr>"""
                st.markdown(f"""
                <div style="overflow-x:auto;max-height:200px;overflow-y:auto;">
                <table class="styled-table">
                    <thead><tr><th>Date</th><th>Close</th><th>Prob</th></tr></thead>
                    <tbody>{eu_rows}</tbody>
                </table></div>
                """, unsafe_allow_html=True)

    with tab2:
        drill_src = df[df["in_eval"]] if "in_eval" in df.columns else df
        eu_dates = drill_src[drill_src["is_euphoric"] == 1]["Date"].dt.strftime("%Y-%m-%d").tolist()
        if not eu_dates:
            st.info("No euphoria events detected for this ticker in the evaluation set.")
        else:
            default_idx = eu_dates.index(drill_date) if drill_date in eu_dates else 0
            selected_date = st.selectbox("Select Euphoria Event Date", eu_dates, index=default_idx, key=f"drill_{ticker}")
            row = df[df["Date"] == pd.Timestamp(selected_date)]
            if row.empty:
                st.warning("Date not found in data.")
            else:
                r = row.iloc[0]
                st.markdown('<div class="section-title">EVENT ANALYSIS</div>', unsafe_allow_html=True)

                def _ratio_row(label, value_str, avg_str, ratio):
                    if ratio is None:
                        bar_pct, rc = 0, "#8b949e"
                        ratio_str = "n/a"
                    else:
                        bar_pct = min(ratio / 2 * 100, 100)
                        rc = "#3fb950" if ratio >= 1 else "#8b949e"
                        ratio_str = f"{ratio:.2f}x"
                    return (
                        '<div style="padding:10px 0;border-bottom:1px solid #21262d;">'
                        '<div style="display:flex;justify-content:space-between;align-items:baseline;">'
                        f'<div style="font-size:14px;color:#c9d1d9;">{label}</div>'
                        '<div style="text-align:right;">'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:14px;color:#c9d1d9;">{value_str}</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#8b949e;"> vs {avg_str}</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:14px;font-weight:700;color:{rc};margin-left:10px;">{ratio_str}</span>'
                        '</div></div>'
                        '<div style="height:4px;background:#21262d;border-radius:2px;margin-top:6px;">'
                        f'<div style="height:4px;width:{bar_pct:.0f}%;background:{rc};border-radius:2px;"></div>'
                        '</div></div>'
                    )

                p_avg  = float(r.get("price_avg", 0) or 0)
                v_avg  = float(r.get("vol_avg", 0) or 0)
                t_avg  = float(r.get("tweet_avg", 0) or 0)
                ctx_rows = (
                    _ratio_row("Close Price", f"{r['Close']:,.0f}", f"{p_avg:,.0f}",
                               (float(r["Close"]) / p_avg) if p_avg > 0 else None)
                    + _ratio_row("Volume", fmt_volume(r["Volume"]), fmt_volume(v_avg),
                                 (float(r["Volume"]) / v_avg) if v_avg > 0 else None)
                    + _ratio_row("Tweet Count", f"{int(r['tweet_count'])}", f"{t_avg:.1f}",
                                 (float(r["tweet_count"]) / t_avg) if t_avg > 0 else None)
                )
                st.markdown(f"""
                <div class="drill-card fade-in" style="border-left-color:#d29922;">
                    <div style="font-size:13px;font-weight:700;color:#d29922;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px;">Market Context vs 30-Day Average</div>
                    <div style="font-size:11px;color:#8b949e;margin-bottom:8px;">
                        How this day compares to its own trailing 30-day average.
                    </div>
                    {ctx_rows}
                </div>
                """, unsafe_allow_html=True)

                prev_row   = df[df["Date"] < pd.Timestamp(selected_date)].tail(1)
                prev_close = prev_row.iloc[0]["Close"] if not prev_row.empty else r["Close"]
                day_chg    = (r["Close"] - prev_close) / prev_close * 100
                five_ago   = df[df["Date"] < pd.Timestamp(selected_date)].tail(5)
                five_ret   = (r["Close"] - five_ago.iloc[0]["Close"]) / five_ago.iloc[0]["Close"] * 100 if not five_ago.empty else 0

                st.markdown(f"""
                <div class="drill-card fade-in" style="border-left-color:#f85149;">
                    <div style="font-size:13px;font-weight:700;color:#f85149;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">Price Movement</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                        <div><div style="font-size:13px;color:#8b949e;">Day Change</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:600;color:{"#3fb950" if day_chg >= 0 else "#f85149"};">{day_chg:+.2f}%</div></div>
                        <div><div style="font-size:13px;color:#8b949e;">5-Day Return</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:600;color:{"#3fb950" if five_ret >= 0 else "#f85149"};">{five_ret:+.2f}%</div></div>
                    </div>
                    <div style="font-size:11px;color:#8b949e;margin-top:10px;">
                        Change against the previous trading day and against five trading days earlier.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="drill-card fade-in" style="border-left-color:#f85149;">
                    <div style="font-size:13px;font-weight:700;color:#f85149;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">Classifier Output</div>
                    <div><div style="font-size:13px;color:#8b949e;">Euphoria Probability</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;color:#f85149;">{r['prob']*100:.1f}%</div></div>
                    <div style="margin-top:10px;font-size:11px;color:#8b949e;line-height:1.6;">
                        Output of the BiLSTM classifier for this date. It reads the previous 30 days of all
                        11 features at once, so it responds to the sequence leading up to this day rather
                        than to any single value shown on this page.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                sc2 = COLORS["green"] if r["sentiment"] > 0.1 else (COLORS["red"] if r["sentiment"] < -0.1 else COLORS["yellow"])
                sent_label_txt = ("Positive" if r["sentiment"] > 0.1
                                  else ("Negative" if r["sentiment"] < -0.1 else "Neutral"))
                n_tw = int(r["tweet_count"])
                sent_note = ("No tweets were collected for this date, so the score defaults to 0.000."
                             if n_tw == 0 else
                             f"Average IndoBERT score across the {n_tw} tweet(s) collected on this date, "
                             f"on a scale of -1 to +1.")
                st.markdown(f"""
                <div class="drill-card fade-in" style="border-left-color:#39d353;">
                    <div style="font-size:13px;font-weight:700;color:#39d353;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">Same-Day Sentiment</div>
                    <div style="display:flex;align-items:center;gap:16px;">
                        <div><div style="font-size:13px;color:#8b949e;">Sentiment Score</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;color:{sc2};">{r['sentiment']:+.3f}</div></div>
                        <div><div style="font-size:13px;color:#8b949e;">Label</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;color:{sc2};">{sent_label_txt}</div></div>
                    </div>
                    <div style="margin-top:10px;font-size:11px;color:#8b949e;line-height:1.6;">
                        {sent_note}
                        This is one day of one feature. It is not the classifier's input on its own and
                        will not always align with the probability above.
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-title">COMPANY PROFILE</div>', unsafe_allow_html=True)
        p = COMPANY_INFO.get(ticker, {})
        pc1, pc2, pc3, pc4 = st.columns(4)
        for col, title, val in [
            (pc1, "Company Name",  p.get("name", "-")),
            (pc2, "Sector",        p.get("sector", "-")),
            (pc3, "Founded Year",  str(p.get("founded", "-"))),
            (pc4, "Key Director",  p.get("director", "-")),
        ]:
            with col:
                st.markdown(f"""
                <div class="profile-card fade-in">
                    <div style="font-size:13px;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">{title}</div>
                    <div style="font-size:15px;font-weight:600;color:#c9d1d9;line-height:1.5;">{val}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="margin-top:24px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px;" class="fade-in">
            <div class="section-title">ABOUT</div>
            <p style="color:#8b949e;font-size:13px;line-height:1.8;">
                <strong style="color:#c9d1d9;">{p.get("name", ticker)}</strong> ({ticker}) is listed on the Indonesia Stock Exchange (IDX).
                Operating in the <strong style="color:#58a6ff;">{p.get("sector","")}</strong> sector, the company was established in
                <strong style="color:#c9d1d9;">{p.get("founded","")}</strong> and is currently led by
                <strong style="color:#c9d1d9;">{p.get("director","")}</strong>.
            </p>
            <p style="color:#484f58;font-size:11px;margin-top:8px;">
                Company details are static reference information entered manually and are not part of the model.
                Data is for informational purposes only and does not constitute financial advice.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# PAGE: MARKET SCREENER
# ──────────────────────────────────────────────────────────────
def page_screener(screener_df: pd.DataFrame):
    st.markdown("""
    <div class="fade-in" style="margin-bottom:20px;">
        <h2 style="font-size:22px;font-weight:700;color:#c9d1d9;margin:0;">Global Market Screener</h2>
        <p style="color:#8b949e;font-size:13px;margin:4px 0 0 0;">
            Latest evaluation-window snapshot of 15 Indonesian equities with model outputs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    total_signals = int(screener_df["Signals"].sum()) if "Signals" in screener_df.columns else 0
    eval_span     = screener_df["EvalSpan"].iloc[0] if "EvalSpan" in screener_df.columns and not screener_df.empty else "the held-out period"
    snap_date = screener_df["SnapDate"].iloc[0] if "SnapDate" in screener_df.columns and not screener_df.empty else "the final trading day"
    rows_html = ""
    for _, r in screener_df.iterrows():
        t         = r["Ticker"]
        chg       = r["Change%"]
        chg_color = "#3fb950" if chg >= 0 else "#f85149"
        chg_str   = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        sc        = "#3fb950" if r["Sentiment"] > 0.1 else ("#f85149" if r["Sentiment"] < -0.1 else "#d29922")
        ep_color  = "#f85149" if r["EuphoriaProb"] > THRESHOLDS.get(t, 0.65) else "#3fb950"
        href      = f"?page=Stock+Analysis&ticker={t}"
        rows_html += f"""
        <tr>
            <td><a href="{href}" target="_self">{t}</a></td>
            <td style="color:#8b949e;">{r['Company'][:30]}</td>
            <td>{r['Open']:,.2f}</td>
            <td>{r['High']:,.2f}</td>
            <td>{r['Low']:,.2f}</td>
            <td style="font-weight:600;">{r['Close']:,.2f}</td>
            <td>{fmt_volume(r['Volume'])}</td>
            <td style="color:{chg_color};">{chg_str}</td>
            <td style="color:{sc};">{r['Sentiment']:+.3f}</td>
            <td style="color:{ep_color};">{r['EuphoriaProb']*100:.1f}%</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid #30363d;border-radius:10px;background:#161b22;" class="fade-in">
    <table class="styled-table">
        <thead><tr>
            <th>Ticker</th><th>Company</th><th>Open</th><th>High</th><th>Low</th>
            <th>Close</th><th>Volume</th><th>Chg%</th><th>IndoBERT</th><th>Euphoria Prob</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>
    <div style="font-size:11px;color:#8b949e;margin-top:8px;line-height:1.6;">
        Every row is a snapshot of <strong style="color:#c9d1d9;">{snap_date}</strong>, the final trading day in the
        dataset. <strong style="color:#c9d1d9;">Open, High, Low, Close and Volume</strong> are that day's actual values.
        <strong style="color:#c9d1d9;">Chg%</strong> is the change in closing price against the previous trading day.
        <strong style="color:#c9d1d9;">IndoBERT</strong> is the average tweet sentiment for that day, and
        <strong style="color:#c9d1d9;">Euphoria Prob</strong> is the model's euphoria probability for that day.
        This was a calm session across all 15 stocks, so the probabilities are low. The chart below counts the
        euphoria signals each stock recorded across the whole held-out period.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">EUPHORIA SIGNALS PER STOCK</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:11px;color:#8b949e;margin:-6px 0 10px 0;line-height:1.6;">
        Number of days each stock was flagged as a euphoria signal across the held-out period
        ({eval_span}). Totals {total_signals} signals across all 15 stocks.
    </div>
    """, unsafe_allow_html=True)
    sig_df  = screener_df.sort_values("Signals", ascending=False)
    max_sig = int(sig_df["Signals"].max()) if not sig_df.empty else 1
    fig_bar = go.Figure(go.Bar(
        x=sig_df["Ticker"],
        y=sig_df["Signals"],
        marker_color="#d29922",
        text=[str(int(v)) for v in sig_df["Signals"]],
        textposition="outside",
        textfont=dict(size=11, family="JetBrains Mono"),
        hovertemplate="%{x}: %{y} signal days<extra></extra>",
    ))
    fig_bar.update_layout(
        **PLOTLY_BASE,
        height=280,
        yaxis=dict(range=[0, max_sig + 2], title="Signal days", gridcolor="#21262d",
                   dtick=1 if max_sig <= 10 else 2),
        xaxis=dict(gridcolor="#21262d"),
        bargap=0.35,
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# PAGE: METHODOLOGY
# ──────────────────────────────────────────────────────────────
def page_methodology():
    st.markdown("""
    <div class="fade-in" style="margin-bottom:20px;">
        <h2 style="font-size:22px;font-weight:700;color:#c9d1d9;margin:0;">Methodology & Model Architecture</h2>
        <p style="color:#8b949e;font-size:13px;margin:4px 0 0 0;">Scientific foundation of the Euphoria Predictor Engine.</p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="ai-card fade-in" style="border-top:3px solid #58a6ff;">
            <div style="font-size:13px;font-weight:700;color:#58a6ff;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">IndoBERT NLP</div>
            <p style="font-size:14px;color:#8b949e;line-height:1.8;">
                Sentiment is scored with <strong style="color:#c9d1d9;">IndoBERT (indobert-base-p1)</strong>,
                fine-tuned on the SmSA Indonesian sentiment dataset. Each tweet receives a score of
                P(positive) minus P(negative), giving a value between -1 and +1.
                Scores are averaged per ticker per day to produce the daily sentiment feature.
                Working in Indonesian matters here because the corpus is full of local market slang
                that a general multilingual model handles poorly.
            </p>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="ai-card fade-in" style="border-top:3px solid #a371f7;">
            <div style="font-size:13px;font-weight:700;color:#a371f7;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">BiLSTM Architecture</div>
            <p style="font-size:14px;color:#8b949e;line-height:1.8;">
                A <strong style="color:#c9d1d9;">Bidirectional LSTM</strong> processes sequences in both forward
                and backward temporal directions, capturing long-range momentum and mean-reversion simultaneously.
                Inputs: 30-day lookback windows of 11 features (OHLCV, RSI, price and volume change,
                tweet count, daily sentiment, event flag).
                Architecture: 128 hidden units x 2 stacked BiLSTM layers with 25% dropout.
            </p>
        </div>""", unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="ai-card fade-in" style="border-top:3px solid #39d353;">
            <div style="font-size:13px;font-weight:700;color:#39d353;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Bahdanau Attention</div>
            <p style="font-size:14px;color:#8b949e;line-height:1.8;">
                The <strong style="color:#c9d1d9;">Bahdanau (Additive) Attention</strong> mechanism enables the model
                to dynamically focus on the most relevant timesteps rather than compressing all history into one vector.
                This produces interpretable <em>attention weight distributions</em> showing which historical days drove
                the euphoria prediction, which matters for explaining the model's decisions.
            </p>
        </div>""", unsafe_allow_html=True)

    try:
        with open("Streamlit_Methodology_Data.json", "r") as f:
            m_data = json.load(f)
    except Exception as e:
        st.error(f"Failed to load methodology JSON artifact: {e}")
        return

    g_ours = m_data["global_performance"]["ours"]
    g_base = m_data["global_performance"]["baseline"]
    stat_t = m_data["statistical_test"]["t_stat"]
    stat_p = m_data["statistical_test"]["p_value"]
    ticker_perf = m_data["ticker_performance"]
    global_attn = m_data["attention_weights"]
    baseline_weights = m_data.get("baseline_weights")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">GLOBAL PERFORMANCE COMPARISON</div>', unsafe_allow_html=True)

    global_perf = [
        (1,
         "IndoBERT, BiLSTM, Attention<br><span style='color:#8b949e;font-size:13px;'>(Ours)</span>",
         f"<strong style='color:#3fb950;'>{g_ours['R2']:.4f}</strong>",
         f"<strong style='color:#3fb950;'>{g_ours['MAE']:.4f}</strong>",
         f"<strong style='color:#3fb950;'>{g_ours['RMSE']:.4f}</strong>",
         f"<strong style='color:#3fb950;'>{g_ours['MAPE']:.2f}%</strong>"),
        (2,
         "IndoBERT, LSTM<br><span style='color:#8b949e;font-size:13px;'>(Yadav et al.)</span>",
         f"{g_base['R2']:.4f}", f"{g_base['MAE']:.4f}", f"{g_base['RMSE']:.4f}", f"{g_base['MAPE']:.2f}%"),
    ]
    gp_rows = ""
    for row in global_perf:
        gp_rows += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"

    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid #30363d;border-radius:10px;background:#161b22;" class="fade-in">
    <table class="styled-table">
        <thead><tr>
            <th>No</th><th>Model</th><th>R2 (↑)</th><th>MAE (↓)</th><th>RMSE (↓)</th><th>MAPE (↓)</th>
        </tr></thead>
        <tbody>{gp_rows}</tbody>
    </table></div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">STATISTICAL SIGNIFICANCE TEST</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid #30363d;border-radius:10px;background:#161b22;" class="fade-in">
    <table class="styled-table">
        <thead><tr>
            <th>Metric Comparison</th>
            <th>T-Statistic</th>
            <th>P-Value</th>
            <th>Significant? (alpha &le; 0.05)</th>
        </tr></thead>
        <tbody>
        <tr>
            <td style="color:#8b949e;font-size:11px;">
                IndoBERT, BiLSTM, Attention (Ours)<br>compared to<br>IndoBERT, LSTM (Yadav et al.)
            </td>
            <td style="color:#58a6ff;font-weight:600;">{stat_t:.4f}</td>
            <td style="color:#3fb950;font-weight:600;">{stat_p:.4e}</td>
            <td style="color:#3fb950;font-weight:700;">Yes</td>
        </tr>
        </tbody>
    </table></div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">PER-TICKER PERFORMANCE COMPARISON</div>', unsafe_allow_html=True)

    pt_rows = ""
    for i, row in enumerate(ticker_perf, 1):
        tkr = row.get("Ticker", row.get("ticker", ""))
        r2_y = row.get("R2_base", row.get("r2_base", 0.0))
        mae_y = row.get("MAE_base", row.get("mae_base", 0.0))
        rmse_y = row.get("RMSE_base", row.get("rmse_base", 0.0))
        mape_y = row.get("MAPE_base", row.get("mape_base", 0.0))
        r2_o = row.get("R2_prop", row.get("r2_prop", 0.0))
        mae_o = row.get("MAE_prop", row.get("mae_prop", 0.0))
        rmse_o = row.get("RMSE_prop", row.get("rmse_prop", 0.0))
        mape_o = row.get("MAPE_prop", row.get("mape_prop", 0.0))

        def better(a, b, higher=True, suffix=""):
            is_better = a > b if higher else a < b
            if is_better:
                return f"<strong style='color:#3fb950;'>{a:,.3f}{suffix}</strong>"
            return f"{a:,.3f}{suffix}"

        pt_rows += f"""
        <tr>
            <td style="color:#8b949e;">{i}</td>
            <td style="color:#58a6ff;font-weight:600;">{tkr}</td>
            <td>{r2_y:.3f}</td>
            <td>{mae_y:,.3f}</td>
            <td>{rmse_y:,.3f}</td>
            <td>{mape_y:.3f}%</td>
            <td>{better(r2_o, r2_y, higher=True)}</td>
            <td>{better(mae_o, mae_y, higher=False)}</td>
            <td>{better(rmse_o, rmse_y, higher=False)}</td>
            <td>{better(mape_o, mape_y, higher=False, suffix="%")}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid #30363d;border-radius:10px;background:#161b22;" class="fade-in">
    <table class="styled-table">
        <thead>
            <tr>
                <th rowspan="2">No</th>
                <th rowspan="2">Ticker</th>
                <th colspan="4" style="text-align:center;color:#8b949e;border-right:1px solid #30363d;">IndoBERT, LSTM (Yadav et al.)</th>
                <th colspan="4" style="text-align:center;color:#58a6ff;">IndoBERT, BiLSTM, Attention (Ours)</th>
            </tr>
            <tr>
                <th>R2</th><th>MAE (IDR)</th><th>RMSE (IDR)</th><th style="border-right:1px solid #30363d;">MAPE (%)</th>
                <th>R2</th><th>MAE (IDR)</th><th>RMSE (IDR)</th><th>MAPE (%)</th>
            </tr>
        </thead>
        <tbody>{pt_rows}</tbody>
    </table></div>
    <div style="font-size:11px;color:#8b949e;margin-top:8px;line-height:1.6;">
        Values in <strong style="color:#3fb950;">green</strong> mark where the proposed model performs better than
        the baseline on that metric for that stock. Higher is better for R2; lower is better for MAE, RMSE and MAPE.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">TEMPORAL ALIGNMENT OF ATTENTION WEIGHTS</div>', unsafe_allow_html=True)

    # Both arrays are chronological (oldest to newest); reverse so Lag 0 (most recent) is on the left
    global_attn_reversed = list(reversed(global_attn))
    y_base = list(reversed(baseline_weights)) if baseline_weights else None

    x_vals  = list(range(len(global_attn_reversed)))
    x_ticks = list(range(0, len(global_attn_reversed), 5))
    x_tick_labels = [f"Lag {idx}" for idx in x_ticks]

    fig_att = go.Figure()
    fig_att.add_trace(go.Scatter(
        x=x_vals, y=global_attn_reversed,
        name="IndoBERT, BiLSTM, Attention (Ours)",
        line=dict(color="#58a6ff", width=2.5),
        fill="tozeroy", fillcolor="rgba(88,166,255,0.07)",
        hovertemplate="Lag %{x}: <b>%{y:.4f}</b><extra>Ours</extra>",
    ))
    if y_base is not None:
        fig_att.add_trace(go.Scatter(
            x=x_vals, y=y_base,
            name="IndoBERT, LSTM (Baseline, gradient saliency)",
            line=dict(color="#8b949e", width=1.8, dash="dash"),
            hovertemplate="Lag %{x}: <b>%{y:.4f}</b><extra>Baseline</extra>",
        ))

    fig_att.update_layout(
        **PLOTLY_BASE,
        hovermode="x unified",
        height=360,
        xaxis=dict(
            title="Lag (0 = most recent day)",
            gridcolor="#21262d",
            tickmode="array",
            tickvals=x_ticks,
            ticktext=x_tick_labels,
            tickfont=dict(family="JetBrains Mono", size=12),
        ),
        yaxis=dict(
            title="Average Attention Weight",
            gridcolor="#21262d",
            tickformat=".3f",
        ),
    )
    st.plotly_chart(fig_att, use_container_width=True)

    st.markdown("""
    <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px 20px;margin-top:8px;" class="fade-in">
        <div class="section-title">INTERPRETATION</div>
        <p style="font-size:14px;color:#8b949e;line-height:1.8;margin:0;">
            The attention layer learns a weight for each of the 30 days in the input window, so we can read
            afterwards which days the model relied on. The weights concentrate sharply on the
            <strong style="color:#58a6ff;">most recent lags</strong> and fall off quickly for older days.
            This is consistent with next-day price prediction, where the latest close carries most of the signal.
            The baseline curve is not an attention distribution. It is a gradient saliency score, which measures
            how sensitive the baseline LSTM's output is to each input day. The two are plotted together for
            comparison of temporal focus, but they are computed differently and are not on the same scale.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
def render_sidebar(qp_page: str = "", qp_ticker: str = "") -> tuple[str, str]:
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom:24px;">
            <div style="font-size:18px;font-weight:800;color:#c9d1d9;letter-spacing:-0.02em;line-height:1.2;">
                EUPHORIA<br>PREDICTOR
            </div>
            <div style="font-size:9px;color:#58a6ff;text-transform:uppercase;letter-spacing:0.15em;margin-top:4px;">
                TERMINAL v1
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#21262d;margin-bottom:18px;"></div>', unsafe_allow_html=True)

        if "nav_page" not in st.session_state and qp_page:
            page_options = ["Stock Analysis", "Market Screener", "Methodology"]
            if qp_page in page_options:
                st.session_state["nav_page"] = qp_page
        if "nav_ticker" not in st.session_state and qp_ticker in TICKERS:
            st.session_state["nav_ticker"] = qp_ticker

        page = st.selectbox(
            "TERMINAL MENU",
            ["Stock Analysis", "Market Screener", "Methodology"],
            key="nav_page",
        )
        ticker = st.radio(
            "SELECT TICKER",
            TICKERS,
            key="nav_ticker",
            horizontal=True,
            label_visibility="visible",
        )

        binus_b64 = load_logo_b64("binus")
        unpad_b64 = load_logo_b64("unpad")
        logo_imgs = ""
        for b64, alt in ((binus_b64, "BINUS"), (unpad_b64, "UNPAD")):
            if b64:
                logo_imgs += (
                    f'<img src="data:image/png;base64,{b64}" alt="{alt}" '
                    f'style="height:40px;width:auto;object-fit:contain;'
                    f'background:transparent;" />'
                )
        logo_block = (
            f'<div style="display:flex;align-items:center;justify-content:center;'
            f'gap:16px;margin-bottom:14px;flex-wrap:wrap;">{logo_imgs}</div>'
            if logo_imgs else ""
        )

        st.markdown(f"""
        <div style="margin-top:32px;">
            <div style="height:1px;background:#21262d;margin-bottom:14px;"></div>
            {logo_block}
            <div style="font-size:10px;color:#8b949e;text-align:center;line-height:1.7;">
                Developed by <strong style="color:#c9d1d9;">Michael Sanjaya</strong>
            </div>
            <div style="font-size:9px;color:#484f58;text-align:center;line-height:1.6;margin-top:6px;">
                IndoBERT + BiLSTM + Attention<br>Research prototype
            </div>
        </div>
        """, unsafe_allow_html=True)
    return page, ticker

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    inject_global_css()

    params    = st.query_params
    qp_page   = params.get("page", "")
    qp_ticker = params.get("ticker", "")
    qp_drill  = params.get("drill_date", "")

    sidebar_page, sidebar_ticker = render_sidebar(qp_page.replace("+", " ") if qp_page else "", qp_ticker)

    active_page   = sidebar_page
    active_ticker = sidebar_ticker

    with st.spinner("Loading market data and model outputs..."):
        screener_df = build_screener_df()

    if not screener_df.empty:
        render_top_bar(screener_df)

    if active_page == "Stock Analysis":
        page_stock_analysis(active_ticker, screener_df, drill_date=qp_drill)
    elif active_page == "Market Screener":
        page_screener(screener_df)
    elif active_page == "Methodology":
        page_methodology()
    else:
        page_stock_analysis(active_ticker, screener_df, drill_date=qp_drill)

if __name__ == "__main__":
    main()
