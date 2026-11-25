import numpy as np
import json
import time

import pandas as pd
import streamlit as st


from atms.engine import prepare_data, run_backtest, optimize
from atms.reports import build_excel


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ATMS - Automated Trading Model Search",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL NAVY + WHITE + GOLD THEME
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* 1. Pitch-Dark Obsidian Canvas (TradingView Style) */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: radial-gradient(circle at 75% 20%, rgba(255, 107, 0, 0.10), transparent 45%),
                radial-gradient(circle at 20% 80%, rgba(255, 59, 92, 0.08), transparent 45%),
                #07090E !important;
    color: #F3F4F6 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stHeader"] {
    background-color: rgba(7, 9, 14, 0.85) !important;
    backdrop-filter: blur(10px) !important;
}

/* 2. Sidebar: Sleek Glass Dark Panel */
section[data-testid="stSidebar"] {
    background-color: #0B0E16 !important;
    border-right: 1px solid #1E2433 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #E5E7EB !important;
}

/* 3. Sidebar & Main Inputs (Dark Glass Cards with Crisp White Text) */
input, textarea, [data-baseweb="select"] > div,
div[data-testid="stNumberInput"] > div {
    background-color: #131824 !important;
    color: #FFFFFF !important;
    border: 1px solid #2A3244 !important;
    border-radius: 10px !important;
}
input:focus, [data-baseweb="select"] > div:focus-within {
    border-color: #FF6B2B !important;
    box-shadow: 0 0 0 1px #FF6B2B !important;
}
[data-baseweb="select"] *,
div[data-testid="stNumberInput"] input {
    color: #FFFFFF !important;
}
div[data-testid="stNumberInput"] button {
    background-color: #1C2333 !important;
    color: #F9FAFB !important;
    border-left: 1px solid #2A3244 !important;
}
div[data-testid="stNumberInput"] button:hover {
    background-color: #FF5A36 !important;
    color: #FFFFFF !important;
}

/* Dropdown Popup Menu */
ul[role="listbox"], [data-baseweb="popover"] > div {
    background-color: #131824 !important;
    border: 1px solid #2A3244 !important;
}
ul[role="listbox"] li, [data-baseweb="popover"] * {
    color: #F3F4F6 !important;
}
ul[role="listbox"] li:hover {
    background-color: #1F2937 !important;
}

/* 4. Sidebar File Uploader & Uploaded File Box */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: #121722 !important;
    border: 1.5px dashed #FF6B2B !important;
    border-radius: 12px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: linear-gradient(90deg, #FF3B5C 0%, #FF7A1A 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button *,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* 5. Main Title Gradient (TradingView Coral -> Orange) */
h1 {
    background: linear-gradient(90deg, #FF3B5C 0%, #FF8A00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}
h2, h3 {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
p, label, [data-testid="stCaptionContainer"] {
    color: #CBD5E1 !important;
}

/* 6. Tabs Bar: Dark Glass Pill Container + Coral-Orange Active Tab */
div[data-baseweb="tab-list"] {
    gap: 8px !important;
    background-color: #111622 !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid #222938 !important;
}
button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #9CA3AF !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    border: none !important;
}
button[data-baseweb="tab"] * {
    color: #9CA3AF !important;
}
button[data-baseweb="tab"]:hover * {
    color: #FFFFFF !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, #FF3B5C 0%, #FF7A1A 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(255, 90, 54, 0.35) !important;
}
button[data-baseweb="tab"][aria-selected="true"] * {
    color: #FFFFFF !important;
}

/* 7. Action & Download Buttons */
.stButton > button {
    background: linear-gradient(90deg, #FF3B5C 0%, #FF7A1A 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(255, 75, 75, 0.28) !important;
}
.stButton > button:hover {
    filter: brightness(1.08) !important;
    color: #FFFFFF !important;
}
.stDownloadButton > button {
    background-color: #161D2C !important;
    color: #FF8A00 !important;
    border: 1px solid #FF7A1A !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(90deg, #FF3B5C 0%, #FF7A1A 100%) !important;
    color: #FFFFFF !important;
}

/* 8. Alert / Dataset Status Banner */
div[data-testid="stAlert"] {
    background-color: #111723 !important;
    border: 1px solid #2A3447 !important;
    border-left: 4px solid #FF6B2B !important;
    border-radius: 10px !important;
}
div[data-testid="stAlert"] * {
    color: #F3F4F6 !important;
}

/* 9. Metrics & Dataframes */
div[data-testid="stMetric"] {
    background-color: #111622 !important;
    border: 1px solid #222938 !important;
    padding: 14px 18px !important;
    border-radius: 12px !important;
}
div[data-testid="stMetricValue"] * {
    color: #FFFFFF !important;
}
div[data-testid="stMetricLabel"] * {
    color: #9CA3AF !important;
}

/* Larger & bolder text for Run Manual Backtest and action buttons */
.stButton > button,
.stButton > button * {
    font-size: 18px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: 0.02em !important;
}
.stButton > button {
    padding: 14px 28px !important;
    min-height: 50px !important;
}


/* Fix Data & Method alert / info / warning boxes contrast */
div[data-testid="stAlert"],
div[data-testid="stNotification"],
[data-baseweb="notification"],
.stAlert {
    background-color: #121826 !important;
    background: #121826 !important;
    border: 1px solid #2A354B !important;
    border-left: 4px solid #FF7A1A !important;
    border-radius: 10px !important;
}
div[data-testid="stAlert"] *,
div[data-testid="stNotification"] *,
[data-baseweb="notification"] *,
.stAlert * {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.title("ATMS Strategy Lab")

st.caption(
    "AUTOMATED TRADING MODEL SEARCH | "
    "Strategy Research | Backtesting | Optimization"
)

st.markdown("---")


# ============================================================
# SIDEBAR SETTINGS
# ============================================================

with st.sidebar:

    st.header("ATMS CONTROL PANEL")

    st.markdown("### 1. Historical Market Data")

    uploaded = st.file_uploader(
        "Upload OHLC CSV",
        type=["csv"]
    )

    st.caption(
        "Required: datetime, open, high, low, close. "
        "Optional: volume."
    )

    st.divider()

    st.markdown("### 2. Market Settings")

    symbol = st.text_input(
        "Trading Symbol",
        "XAUUSD"
    )

    timeframe = st.selectbox(
        "Timeframe",
        ["M15", "H1"],
        index=0
    )

    st.divider()

    st.markdown("### 3. Account Settings")

    initial_balance = st.number_input(
        "Starting Balance ($)",
        min_value=100.0,
        value=10000.0,
        step=500.0
    )

    risk_pct = st.number_input(
        "Risk Per Trade (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1
    )

    st.divider()

    st.markdown("### 4. Trading Costs")

    spread = st.number_input(
        "Spread (price units)",
        min_value=0.0,
        value=0.30,
        step=0.05
    )

    slippage = st.number_input(
        "Slippage (price units)",
        min_value=0.0,
        value=0.05,
        step=0.01
    )

    commission = st.number_input(
        "Commission ($ per lot, round turn)",
        min_value=0.0,
        value=0.0,
        step=0.5
    )

    st.caption(
        "Trading costs are configurable assumptions, "
        "not live broker quotes."
    )


# ============================================================
# DATA UPLOAD AND PREPARATION
# ============================================================

from pathlib import Path
_builtin_csv_path = Path(__file__).resolve().parent / "data" / "builtin_XAUUSD.csv"
_using_builtin_csv = False

if uploaded is None and _builtin_csv_path.exists():
    _using_builtin_csv = True
    try:
        raw = pd.read_csv(_builtin_csv_path)
    except Exception:
        raw = pd.read_csv(_builtin_csv_path)
    st.caption(f"Auto-loaded built-in dataset: {_builtin_csv_path.name} ({len(raw):,} rows)")

elif uploaded is None:

    st.markdown(
        '<div style="background: linear-gradient(95deg, rgba(153, 27, 27, 0.45) 0%, rgba(24, 12, 18, 0.97) 100%); '
        'border: 1px solid rgba(239, 68, 68, 0.65); border-left: 4px solid #EF4444; '
        'border-radius: 10px; padding: 14px 18px; margin: 10px 0 16px 0; '
        'color: #FFF1F2 !important; -webkit-text-fill-color: #FFF1F2 !important; '
        'font-weight: 600; font-size: 15px; opacity: 1 !important;">'
        'Welcome to ATMS Strategy Lab. Upload your historical market data to begin.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Getting Started")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Historical Data")
        st.write(
            "Import your Forex or Gold historical OHLC data."
        )

    with c2:
        st.markdown("#### Strategy Research")
        st.write(
            "Run manual backtests and automatic optimization."
        )

    st.markdown("### Supported CSV Format")

    st.code(
        "datetime,open,high,low,close,volume",
        language="text"
    )

    st.stop()


try:

    if not _using_builtin_csv:
        raw = pd.read_csv(uploaded)

    data = prepare_data(raw, timeframe)

    if data.empty:
        st.error("No valid market data was found.")
        st.stop()

except Exception as e:

    st.error(f"Could not read this file: {e}")
    st.stop()


# ============================================================
# DATA INFORMATION
# ============================================================

if len(data) < 300:

    st.warning(
        f"Only {len(data):,} candles available. "
        "For reliable research, several thousand candles are recommended."
    )

else:

    st.success(
        f"{symbol} | {timeframe} | "
        f"{len(data):,} candles | "
        f"{data.index.min()} to {data.index.max()}"
    )


# ============================================================
# NAVIGATION TABS
# ============================================================
tab_manual, tab_opt, tab_info, tab_4, tab_selected, tab_auto_filtered = st.tabs(["Manual Backtest",
    "Automatic Optimizer",
    "Data & Method", "Autonomous Lab (24/7)", "Selected Strategies", "Auto Filtered"])


# ============================================================
# MANUAL BACKTEST
# ============================================================

with tab_manual:

    st.header("Manual Strategy Backtesting")

    st.write(
        "Configure your trading strategy and test it "
        "against historical market data."
    )

    st.markdown("### EMA & RSI Settings")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        ema_fast = st.number_input(
            "Fast EMA", 2, 300, 20
        )

    with c2:
        ema_mid = st.number_input(
            "Middle EMA", 3, 500, 50
        )

    with c3:
        ema_slow = st.number_input(
            "Slow EMA", 5, 1000, 200
        )

    with c4:
        rsi_len = st.number_input(
            "RSI Length", 2, 100, 14
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        buy_level = st.number_input(
            "BUY RSI Cross Above",
            1.0, 99.0, 40.0, 1.0
        )

    with c2:
        sell_level = st.number_input(
            "SELL RSI Cross Below",
            1.0, 99.0, 60.0, 1.0
        )

    with c3:
        atr_len = st.number_input(
            "ATR Length", 2, 100, 14
        )

    with c4:
        atr_mult = st.number_input(
            "Stop Loss ATR Multiple",
            0.1, 10.0, 1.5, 0.1
        )

    st.markdown("### Risk & Trade Settings")

    c1, c2 = st.columns(2)

    with c1:
        rr = st.number_input(
            "Take Profit (R)",
            0.1, 10.0, 1.5, 0.1
        )

    with c2:
        allow_side = st.selectbox(
            "Trade Direction",
            ["Both", "Long only", "Short only"]
        )

    st.markdown("### Backtest Date Range")

    c1, c2 = st.columns(2)

    with c1:
        start_date = st.date_input(
            "Start Date",
            value=data.index.min().date(),
            key="manual_start"
        )

    with c2:
        end_date = st.date_input(
            "End Date",
            value=data.index.max().date(),
            key="manual_end"
        )

    if st.button(
        "Run Manual Backtest",
        type="primary",
        use_container_width=True
    ):

        if not (ema_fast < ema_mid < ema_slow):

            st.error(
                "EMA periods must be in ascending order: "
                "Fast < Middle < Slow."
            )

        elif buy_level >= sell_level:

            st.error(
                "BUY RSI level must be lower than SELL RSI level."
            )

        elif start_date > end_date:

            st.error(
                "Start date must be before end date."
            )

        else:

            subset = data.loc[
                str(start_date):str(end_date)
            ]

            if subset.empty:

                st.error("No candles found in the selected date range.")

            else:

                params = dict(
                    ema_fast=int(ema_fast),
                    ema_mid=int(ema_mid),
                    ema_slow=int(ema_slow),
                    rsi_len=int(rsi_len),
                    buy_level=float(buy_level),
                    sell_level=float(sell_level),
                    atr_len=int(atr_len),
                    atr_mult=float(atr_mult),
                    rr=float(rr),
                    allow_side=allow_side
                )

                with st.spinner("Running manual backtest..."):

                    summary, trades, curve = run_backtest(
                        subset,
                        params,
                        initial_balance,
                        risk_pct,
                        spread,
                        slippage,
                        commission
                    )

                    st.session_state["last_result"] = (
                        summary,
                        trades,
                        curve,
                        params,
                        symbol,
                        timeframe
                    )


    # DISPLAY MANUAL RESULTS

    if "last_result" in st.session_state:

        summary, trades, curve, params, sym, tf = (
            st.session_state["last_result"]
        )

        st.markdown("---")

        st.subheader("Backtest Performance")

        cols = st.columns(5)

        metrics = [
            ("Total Trades", "trades", "{:,.0f}"),
            ("Win Rate", "win_rate", "{:.1f}%"),
            ("Net Profit/Loss", "net_profit", "${:,.2f}"),
            ("Profit Factor", "profit_factor", "{:.2f}"),
            ("Maximum Drawdown", "max_drawdown", "{:.2f}%")
        ]

        for col, (label, key, fmt) in zip(cols, metrics):

            col.metric(
                label,
                fmt.format(summary.get(key, 0))
            )

        st.markdown("### Equity Curve")

        if not curve.empty:

            st.line_chart(
                curve.set_index("datetime")["balance"]
            )

        st.markdown("### Trade History")

        st.dataframe(
            trades.tail(100),
            use_container_width=True
        )

        xlsx = build_excel(
            summary,
            trades,
            curve,
            params,
            sym,
            tf
        )

        st.download_button(
            "Download Excel Report",
            xlsx,
            file_name=f"{sym}_{tf}_manual_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# ============================================================
# AUTOMATIC OPTIMIZER
# ============================================================

with tab_opt:

    st.header("Automatic Strategy Optimizer")

    st.write(
        "Test multiple predefined parameter combinations "
        "and compare their historical performance."
    )

    st.markdown("### Select Strategy Combinations")

    a, b, c = st.columns(3)

    with a:

        ema_sets = st.multiselect(
            "EMA Combinations",
            ["20/50/200", "20/100/200", "50/100/200"],
            default=["20/50/200", "20/100/200"]
        )

        rsi_sets = st.multiselect(
            "RSI Levels",
            ["35/65", "40/60", "45/55"],
            default=["40/60", "45/55"]
        )

    with b:

        atr_sets = st.multiselect(
            "ATR Stop Multiples",
            [1.0, 1.5, 2.0],
            default=[1.5, 2.0]
        )

        rr_sets = st.multiselect(
            "Take Profit R",
            [1.0, 1.5, 2.0, 2.5],
            default=[1.5, 2.0]
        )

    with c:

        opt_start = st.date_input(
            "Optimization Start",
            value=data.index.min().date(),
            key="os"
        )

        opt_end = st.date_input(
            "Optimization End",
            value=data.index.max().date(),
            key="oe"
        )

        min_trades = st.number_input(
            "Minimum Trades to Rank",
            min_value=1,
            value=30
        )

    st.markdown("---")

    if st.button(
        "Run Automatic Optimization",
        type="primary",
        use_container_width=True
    ):

        if not all([
            ema_sets,
            rsi_sets,
            atr_sets,
            rr_sets
        ]):

            st.error(
                "Select at least one option in every parameter group."
            )

        elif opt_start > opt_end:

            st.error(
                "Optimization start date must be before end date."
            )

        else:

            subset = data.loc[
                str(opt_start):str(opt_end)
            ]

            if subset.empty:

                st.error(
                    "No candles found in the selected date range."
                )

            else:

                with st.spinner(
                    "Testing strategy combinations. Please wait..."
                ):

                    results, details = optimize(
                        subset,
                        ema_sets,
                        rsi_sets,
                        atr_sets,
                        rr_sets,
                        initial_balance,
                        risk_pct,
                        spread,
                        slippage,
                        commission,
                        int(min_trades)
                    )

                    st.session_state["opt_results"] = (
                        results,
                        details,
                        symbol,
                        timeframe
                    )


    # DISPLAY OPTIMIZATION RESULTS

    if "opt_results" in st.session_state:

        results, details, sym, tf = (
            st.session_state["opt_results"]
        )

        st.markdown("---")

        st.subheader("Optimization Results")

        st.metric(
            "Combinations Tested",
            len(results)
        )

        st.dataframe(
            results,
            use_container_width=True
        )

        if len(results) > 0:

            best = results.iloc[0]

            st.success(
                f"Top Ranked Strategy: {best['strategy']} | "
                f"Profit Factor: {best['profit_factor']:.2f} | "
                f"Net Profit: ${best['net_profit']:.2f} | "
                f"Max Drawdown: {best['max_drawdown']:.2f}% | "
                f"Trades: {int(best['trades'])}"
            )

            opt_bytes = build_excel(
                {"optimizer_rows": len(results)},
                pd.DataFrame(),
                pd.DataFrame(),
                {},
                sym,
                tf,
                results
            )

            st.download_button(
                "Download Optimization Excel Report",
                opt_bytes,
                file_name=f"{sym}_{tf}_optimization.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:

            st.warning(
                "No strategies met the minimum trade requirement."
            )


# ============================================================
# DATA & BACKTEST METHOD
# ============================================================

with tab_info:

    st.header("Data & Backtest Method")

    st.subheader("Historical Data")

    st.markdown("""
    - Supports OHLC CSV historical market data.
    - Required columns: datetime, open, high, low, close.
    - Optional column: volume.
    - M15 and H1 timeframes are available.
    """)

    st.subheader("Backtest Assumptions")

    st.markdown("""
    - Signals are evaluated at candle close.
    - Entries are attempted at the next candle open.
    - Position size is calculated from current balance and configured risk.
    - If stop-loss and take-profit are both touched in one candle,
      the conservative assumption is that stop-loss happens first.
    - Spread and slippage are applied as configurable price-unit costs.
    - H1 data is resampled from uploaded lower-timeframe OHLC data
      when supported by the data engine.
    - Historical results cannot guarantee future performance.
    - Validate strategies on separate unseen data before live trading.
    """)

    st.subheader("Current Software Limitations")

    st.warning("""
    Initial release limitations:

    - Single-symbol OHLC backtesting.
    - Broker-specific lot sizing is not yet implemented.
    - Swaps and partial fills are not modeled.
    - Tick-level execution is not modeled.
    - Automatic optimizer currently tests predefined parameter combinations.
    - Autonomous strategy generation and continuous research
      are planned for future development.
    """)

    st.info(
        "ATMS - Automated Trading Model Search | "
        "Strategy Research Platform"
    )


with tab_selected:
    st.markdown("### Selected Strategies Dashboard")
    st.caption("Autonomous Lab (24/7) ki chuni hui strategies, unke performance results, aur parameters ka view.")

    _sel_engine = locals().get("engine") or globals().get("engine")
    if _sel_engine is None or not hasattr(_sel_engine, "db"):
        st.warning("Autonomous DB engine abhi active nahi hai. Pehle Autonomous Lab (24/7) initialize ya run karein.")
    else:
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])
        with col_f1:
            top_n = st.selectbox("Show Top Strategies", [10, 20, 50, 100], index=1, key="sel_strat_top_n")
        with col_f2:
            min_score = st.number_input("Min Composite Score", min_value=0.0, value=0.0, step=0.25, key="sel_strat_min_score")
        with col_f3:
            search_txt = st.text_input("Filter by Name / Symbol / TF", value="", placeholder="e.g. XAUUSD, M15, EMA...", key="sel_strat_search")
        with col_f4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh", key="sel_strat_refresh"):
                st.rerun()

        try:
            raw_df = _sel_engine.db.get_top_strategies(limit=int(top_n))
        except TypeError:
            raw_df = _sel_engine.db.get_top_strategies(limit=int(top_n), symbol=None)
        except Exception as exc:
            st.error(f"Selected strategies load karne mein masla aaya: {exc}")
            raw_df = None

        if raw_df is None or getattr(raw_df, "empty", True):
            st.info("Abhi tak koi selected strategy database mein save nahi hui. Autonomous Lab chalayein to results yahan aa jayenge.")
        else:
            df_view = raw_df.copy()
            import json as _json
            import pandas as _pd

            # Normalize composite_score filter if column exists
            score_col = next((c for c in ["composite_score", "score", "fitness"] if c in df_view.columns), None)
            if score_col and min_score > 0:
                df_view = df_view[_pd.to_numeric(df_view[score_col], errors="coerce").fillna(0) >= float(min_score)]

            # Text filter across string columns
            if search_txt.strip():
                q = search_txt.strip().lower()
                mask = _pd.Series(False, index=df_view.index)
                for col in df_view.columns:
                    mask = mask | df_view[col].astype(str).str.lower().str.contains(q, na=False)
                df_view = df_view[mask]

            if df_view.empty:
                st.warning("Is filter ke mutabiq koi strategy nahi mili.")
            else:
                # Top summary cards
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Selected Strategies", str(len(df_view)))
                with m2:
                    if score_col:
                        best_val = _pd.to_numeric(df_view[score_col], errors="coerce").max()
                        st.metric("Top Score", f"{best_val:.4f}" if _pd.notna(best_val) else "N/A")
                    else:
                        st.metric("Top Score", "N/A")
                wr_col = next((c for c in ["win_rate", "winrate", "win_pct"] if c in df_view.columns), None)
                with m3:
                    if wr_col:
                        avg_wr = _pd.to_numeric(df_view[wr_col], errors="coerce").mean()
                        st.metric("Avg Win Rate", f"{avg_wr:.2f}%" if _pd.notna(avg_wr) else "N/A")
                    else:
                        st.metric("Columns Tracked", str(len(df_view.columns)))
                pf_col = next((c for c in ["profit_factor", "pf", "net_profit"] if c in df_view.columns), None)
                with m4:
                    if pf_col:
                        best_pf = _pd.to_numeric(df_view[pf_col], errors="coerce").max()
                        st.metric(f"Best {pf_col}", f"{best_pf:.2f}" if _pd.notna(best_pf) else "N/A")
                    else:
                        st.metric("Engine Status", "Ready")

                st.markdown("#### Ranked Selected Strategies")
                st.dataframe(df_view, use_container_width=True, hide_index=True)

                # Strategy selector for detailed parameter & result inspection
                st.markdown("#### Strategy Parameters & Result Inspector")
                label_col = next((c for c in ["strategy_name", "name", "strategy_type", "strategy_hash", "id"] if c in df_view.columns), None)
                options = list(df_view.index)

                def _fmt_option(idx):
                    row = df_view.loc[idx]
                    base_lbl = str(row[label_col]) if label_col else f"Row #{idx}"
                    sym_lbl = f" | {row['symbol']}" if "symbol" in df_view.columns and _pd.notna(row["symbol"]) else ""
                    tf_lbl = f" ({row['timeframe']})" if "timeframe" in df_view.columns and _pd.notna(row["timeframe"]) else ""
                    sc_lbl = f" | Score: {row[score_col]}" if score_col and _pd.notna(row[score_col]) else ""
                    return f"{base_lbl}{sym_lbl}{tf_lbl}{sc_lbl}"

                selected_idx = st.selectbox(
                    "Detail dekhne ke liye strategy chunein",
                    options=options,
                    format_func=_fmt_option,
                    key="sel_strat_inspector_idx",
                )
                chosen_row = df_view.loc[selected_idx]

                # Separate parameters vs performance/meta fields
                param_candidates = [c for c in df_view.columns if any(k in c.lower() for k in ["param", "genome", "config", "setting"])]
                parsed_params = {}
                for pc in param_candidates:
                    val = chosen_row[pc]
                    if isinstance(val, dict):
                        parsed_params.update(val)
                    elif isinstance(val, str) and val.strip():
                        try:
                            loaded = _json.loads(val)
                            if isinstance(loaded, dict):
                                parsed_params.update(loaded)
                            else:
                                parsed_params[pc] = loaded
                        except Exception:
                            parsed_params[pc] = val

                det_c1, det_c2 = st.columns([1.2, 1])
                with det_c1:
                    st.markdown("**Parameters**")
                    if parsed_params:
                        p_df = _pd.DataFrame(
                            [{"Parameter": str(k), "Value": str(v)} for k, v in parsed_params.items()]
                        )
                        st.dataframe(p_df, use_container_width=True, hide_index=True)
                    else:
                        # Fallback: show non-metric columns if no dedicated JSON param column exists
                        fallback_cols = [c for c in df_view.columns if c not in param_candidates]
                        f_df = _pd.DataFrame(
                            [{"Field": str(c), "Value": str(chosen_row[c])} for c in fallback_cols]
                        )
                        st.dataframe(f_df, use_container_width=True, hide_index=True)

                with det_c2:
                    st.markdown("**Full Strategy Record**")
                    record_dict = {}
                    for col in df_view.columns:
                        v = chosen_row[col]
                        if isinstance(v, str):
                            try:
                                record_dict[col] = _json.loads(v)
                            except Exception:
                                record_dict[col] = v
                        else:
                            record_dict[col] = v.item() if hasattr(v, "item") else v
                    st.json(record_dict)

                    st.download_button(
                        "Download Filtered CSV",
                        data=df_view.to_csv(index=False).encode("utf-8"),
                        file_name="selected_strategies.csv",
                        mime="text/csv",
                        key="sel_strat_dl_csv",
                    )
                    st.download_button(
                        "Download Selected Strategy JSON",
                        data=_json.dumps(record_dict, indent=2, default=str).encode("utf-8"),
                        file_name="selected_strategy_detail.json",
                        mime="application/json",
                        key="sel_strat_dl_json",
                    )

# === ATMS STRATEGY & INDICATOR PARAMETER LIBRARY START ===
with tab_selected:
    st.markdown("---")
    st.markdown("### Strategy Catalog & Indicator Parameter Library")
    st.caption("Engine parameters (EMA, RSI, ATR, RR, Side) aur mukhtalif strategy presets ka catalog.")

    _strat_catalog = [
        {
            "Strategy Name": "Triple EMA Trend Momentum",
            "Category": "Trend Following",
            "Best Timeframes": "M15, H1, H4",
            "Indicators Used": "EMA (Fast/Mid/Slow), RSI, ATR",
            "Signal Logic": "EMA Fast > Mid > Slow + Price above Fast EMA + RSI momentum confirmation",
            "Default Params": {
                "strategy_type": "triple_ema_trend",
                "ema_fast": 9,
                "ema_mid": 21,
                "ema_slow": 55,
                "rsi_len": 14,
                "buy_level": 55.0,
                "sell_level": 45.0,
                "atr_len": 14,
                "atr_mult": 1.5,
                "rr": 2.0,
                "allow_side": "Both",
            },
        },
        {
            "Strategy Name": "RSI Pullback in Trend",
            "Category": "Trend Pullback",
            "Best Timeframes": "M15, H1",
            "Indicators Used": "EMA Trend Filter, RSI Pullback, ATR SL",
            "Signal Logic": "Trend direction ke mutabiq pullback par RSI entry aur ATR stop loss",
            "Default Params": {
                "strategy_type": "rsi_pullback",
                "ema_fast": 12,
                "ema_mid": 34,
                "ema_slow": 100,
                "rsi_len": 14,
                "buy_level": 40.0,
                "sell_level": 60.0,
                "atr_len": 14,
                "atr_mult": 1.4,
                "rr": 2.2,
                "allow_side": "Both",
            },
        },
        {
            "Strategy Name": "RSI Overbought / Oversold Reversal",
            "Category": "Mean Reversion",
            "Best Timeframes": "M5, M15, H1",
            "Indicators Used": "RSI Extremes, Fast/Slow EMA, ATR",
            "Signal Logic": "Extreme oversold/overbought zones se reversal jab slow EMA flat/range mein ho",
            "Default Params": {
                "strategy_type": "rsi_reversal",
                "ema_fast": 8,
                "ema_mid": 21,
                "ema_slow": 50,
                "rsi_len": 7,
                "buy_level": 28.0,
                "sell_level": 72.0,
                "atr_len": 14,
                "atr_mult": 1.2,
                "rr": 1.5,
                "allow_side": "Both",
            },
        },
        {
            "Strategy Name": "ATR Volatility Breakout",
            "Category": "Breakout / Volatility",
            "Best Timeframes": "M15, H1, H4",
            "Indicators Used": "ATR Expansion, EMA Structure, RSI Filter",
            "Signal Logic": "Volatility expansion aur trend alignment ke saath breakout continuation",
            "Default Params": {
                "strategy_type": "atr_breakout",
                "ema_fast": 10,
                "ema_mid": 25,
                "ema_slow": 80,
                "rsi_len": 14,
                "buy_level": 52.0,
                "sell_level": 48.0,
                "atr_len": 21,
                "atr_mult": 2.0,
                "rr": 2.5,
                "allow_side": "Both",
            },
        },
        {
            "Strategy Name": "Intraday Scalper (Fast EMA + Tight ATR)",
            "Category": "Scalping",
            "Best Timeframes": "M1, M5, M15",
            "Indicators Used": "Fast EMA Ribbon, Short RSI, Tight ATR",
            "Signal Logic": "Chhotay timeframes par tez EMA cross/alignment aur tight risk control",
            "Default Params": {
                "strategy_type": "fast_scalper",
                "ema_fast": 5,
                "ema_mid": 13,
                "ema_slow": 34,
                "rsi_len": 9,
                "buy_level": 54.0,
                "sell_level": 46.0,
                "atr_len": 10,
                "atr_mult": 1.0,
                "rr": 1.6,
                "allow_side": "Both",
            },
        },
        {
            "Strategy Name": "Swing Trend Runner (High RR)",
            "Category": "Swing Trading",
            "Best Timeframes": "H1, H4, D1",
            "Indicators Used": "Slow EMA Trend, RSI (14/21), Wide ATR",
            "Signal Logic": "Baray trend waves ko pakarne ke liye wider ATR stop aur higher R:R target",
            "Default Params": {
                "strategy_type": "swing_runner",
                "ema_fast": 20,
                "ema_mid": 50,
                "ema_slow": 200,
                "rsi_len": 21,
                "buy_level": 50.0,
                "sell_level": 50.0,
                "atr_len": 21,
                "atr_mult": 2.5,
                "rr": 3.0,
                "allow_side": "Both",
            },
        },
    ]

    import json as _lib_json
    import pandas as _lib_pd

    cat_options = ["All"] + sorted({item["Category"] for item in _strat_catalog})
    chosen_cat = st.selectbox("Filter by Strategy Category", cat_options, key="lib_cat_filter")

    filtered_catalog = [
        item for item in _strat_catalog
        if chosen_cat == "All" or item["Category"] == chosen_cat
    ]

    cat_table_df = _lib_pd.DataFrame([
        {
            "Strategy Name": it["Strategy Name"],
            "Category": it["Category"],
            "Best Timeframes": it["Best Timeframes"],
            "Indicators Used": it["Indicators Used"],
            "Signal Logic": it["Signal Logic"],
        }
        for it in filtered_catalog
    ])
    st.dataframe(cat_table_df, use_container_width=True, hide_index=True)

    st.markdown("#### Indicator Parameter Builder & Preset Exporter")
    preset_names = [it["Strategy Name"] for it in filtered_catalog]
    selected_preset_name = st.selectbox("Preset chunein aur parameters customize karein", preset_names, key="lib_preset_select")
    active_preset = next(it for it in filtered_catalog if it["Strategy Name"] == selected_preset_name)
    dp = active_preset["Default Params"]

    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        st.markdown("**EMA Parameters**")
        ema_fast = st.number_input("ema_fast", min_value=2, max_value=200, value=int(dp["ema_fast"]), step=1, key="lib_ema_fast")
        ema_mid = st.number_input("ema_mid", min_value=3, max_value=300, value=int(dp["ema_mid"]), step=1, key="lib_ema_mid")
        ema_slow = st.number_input("ema_slow", min_value=5, max_value=500, value=int(dp["ema_slow"]), step=1, key="lib_ema_slow")

    with p_col2:
        st.markdown("**RSI Parameters**")
        rsi_len = st.number_input("rsi_len", min_value=2, max_value=100, value=int(dp["rsi_len"]), step=1, key="lib_rsi_len")
        buy_level = st.number_input("buy_level", min_value=1.0, max_value=99.0, value=float(dp["buy_level"]), step=1.0, key="lib_buy_level")
        sell_level = st.number_input("sell_level", min_value=1.0, max_value=99.0, value=float(dp["sell_level"]), step=1.0, key="lib_sell_level")

    with p_col3:
        st.markdown("**ATR & Risk Parameters**")
        atr_len = st.number_input("atr_len", min_value=2, max_value=100, value=int(dp["atr_len"]), step=1, key="lib_atr_len")
        atr_mult = st.number_input("atr_mult", min_value=0.1, max_value=20.0, value=float(dp["atr_mult"]), step=0.1, key="lib_atr_mult")
        rr_val = st.number_input("rr (Risk:Reward)", min_value=0.2, max_value=20.0, value=float(dp["rr"]), step=0.1, key="lib_rr")

    with p_col4:
        st.markdown("**Execution / Side**")
        allow_side = st.selectbox("allow_side", ["Both", "Long Only", "Short Only"], index=["Both", "Long Only", "Short Only"].index(dp["allow_side"]) if dp["allow_side"] in ["Both", "Long Only", "Short Only"] else 0, key="lib_allow_side")
        custom_params_dict = {
            "strategy_name": selected_preset_name,
            "category": active_preset["Category"],
            "strategy_type": dp["strategy_type"],
            "ema_fast": int(ema_fast),
            "ema_mid": int(ema_mid),
            "ema_slow": int(ema_slow),
            "rsi_len": int(rsi_len),
            "buy_level": float(buy_level),
            "sell_level": float(sell_level),
            "atr_len": int(atr_len),
            "atr_mult": float(atr_mult),
            "rr": float(rr_val),
            "allow_side": allow_side,
        }
        st.json(custom_params_dict)
        st.download_button(
            "Download Parameter Set (JSON)",
            data=_lib_json.dumps(custom_params_dict, indent=2).encode("utf-8"),
            file_name=f"{dp['strategy_type']}_params.json",
            mime="application/json",
            key="lib_dl_params_json",
        )
# === ATMS STRATEGY & INDICATOR PARAMETER LIBRARY END ===

# === ATMS AUTO FILTERED STRATEGIES TAB START ===
with tab_auto_filtered:
    st.markdown("### Auto Filtered Strategies (Autonomous Picks)")
    st.caption("`atms_research.db` ke `experiments` table se automatic quality rules ke mutabiq chuni hui strategies, unke results, aur `genome_json` parameters.")

    import json as _af_json
    import sqlite3 as _af_sql
    import pandas as _af_pd
    from pathlib import Path as _af_Path

    def _load_auto_experiments_df(limit_n: int):
        # 1. Try engine/session_state if already initialized
        _eng = st.session_state.get("atms_auto_engine") or globals().get("engine") or locals().get("engine")
        if _eng is not None and hasattr(_eng, "db"):
            try:
                df_e = _eng.db.get_top_strategies(limit=int(limit_n))
                if df_e is not None and not getattr(df_e, "empty", True):
                    return df_e
            except Exception:
                pass

        # 2. Direct fallback to atms_research.db
        db_candidates = [_af_Path("atms_research.db")] + list(_af_Path(".").rglob("atms_research.db"))
        for db_p in db_candidates:
            if db_p.exists():
                try:
                    conn = _af_sql.connect(str(db_p))
                    cols_info = [r[1] for r in conn.execute("PRAGMA table_info(experiments)").fetchall()]
                    if cols_info:
                        order_col = "composite_score" if "composite_score" in cols_info else ("id" if "id" in cols_info else cols_info[0])
                        q_sql = f"SELECT * FROM experiments ORDER BY {order_col} DESC LIMIT ?"
                        df_s = _af_pd.read_sql_query(q_sql, conn, params=(int(limit_n),))
                        conn.close()
                        return df_s
                    conn.close()
                except Exception:
                    pass
        return None

    with st.expander("Automatic Qualification Rules (Kis Base Par Filter Hoti Hain)", expanded=True):
        r_top1, r_top2, r_top3 = st.columns([1.5, 1.5, 1])
        with r_top1:
            auto_rules_on = st.toggle("Auto-Qualify Rules Active", value=True, key="af_rules_toggle")
        with r_top2:
            af_scan_limit = st.selectbox("Scan Pool Size", [100, 250, 500, 1000], index=2, key="af_scan_limit")
        with r_top3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh DB", key="af_refresh_db_btn"):
                st.rerun()

        rc1, rc2, rc3, rc4, rc5, rc6 = st.columns(6)
        with rc1:
            min_pf = st.number_input("Min Profit Factor", min_value=1.15, value=1.15, step=0.05, key="af_rule_pf")
        with rc2:
            min_oos_pf = st.number_input("Min OOS PF", min_value=1.00, value=1.00, step=0.05, key="af_rule_oos_pf")
        with rc3:
            min_wr = st.number_input("Min Win Rate (%)", min_value=30.0, max_value=100.0, value=40.0, step=1.0, key="af_rule_wr")
        with rc4:
            max_dd = st.number_input("Max Drawdown (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="af_rule_dd")
        with rc5:
                min_trades = st.number_input("Min Trades", min_value=0, max_value=5000, value=80, step=5, key="af_rule_trades")
        with rc6:
            min_comp_score = st.number_input("Min Score", min_value=1.00, value=1.00, step=0.10, key="af_rule_score")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        af_sym_filter = st.text_input("Symbol Filter", value="", placeholder="e.g. XAUUSD", key="af_sym_txt")
    with f_col2:
        af_tf_filter = st.text_input("Timeframe Filter", value="", placeholder="e.g. M15, H1", key="af_tf_txt")
    with f_col3:
        af_gen_filter = st.text_input("Generation Type / Param Search", value="", placeholder="e.g. evo, random, ema_fast", key="af_gen_txt")

    base_df = _load_auto_experiments_df(int(af_scan_limit))

    if base_df is None or getattr(base_df, "empty", True):
        st.info("Abhi `atms_research.db` (`experiments` table) mein koi strategy record nahi mila.")
    else:
        work_df = base_df.copy()

        if af_sym_filter.strip() and "symbol" in work_df.columns:
            work_df = work_df[work_df["symbol"].astype(str).str.lower().str.contains(af_sym_filter.strip().lower(), na=False)]
        if af_tf_filter.strip() and "timeframe" in work_df.columns:
            work_df = work_df[work_df["timeframe"].astype(str).str.lower().str.contains(af_tf_filter.strip().lower(), na=False)]
        if af_gen_filter.strip():
            q_low = af_gen_filter.strip().lower()
            mask_q = _af_pd.Series(False, index=work_df.index)
            for c_chk in ["generation_type", "genome_json", "strategy_hash"]:
                if c_chk in work_df.columns:
                    mask_q = mask_q | work_df[c_chk].astype(str).str.lower().str.contains(q_low, na=False)
            work_df = work_df[mask_q]

        if auto_rules_on:
            qual_mask = _af_pd.Series(True, index=work_df.index)

            if "profit_factor" in work_df.columns and float(min_pf) > 0:
                pf_s = _af_pd.to_numeric(work_df["profit_factor"], errors="coerce")
                qual_mask = qual_mask & pf_s.notna() & (pf_s >= float(min_pf))

            if "oos_profit_factor" in work_df.columns and float(min_oos_pf) > 0:
                oos_s = _af_pd.to_numeric(work_df["oos_profit_factor"], errors="coerce")
                qual_mask = qual_mask & oos_s.notna() & (oos_s >= float(min_oos_pf))

            if "win_rate" in work_df.columns and float(min_wr) > 0:
                wr_s = _af_pd.to_numeric(work_df["win_rate"], errors="coerce")
                qual_mask = qual_mask & wr_s.notna() & (wr_s >= float(min_wr))

            if "max_drawdown" in work_df.columns and float(max_dd) > 0:
                dd_s = _af_pd.to_numeric(work_df["max_drawdown"], errors="coerce").abs()
                qual_mask = qual_mask & dd_s.notna() & (dd_s <= float(max_dd))

            if "trade_count" in work_df.columns and int(min_trades) > 0:
                tc_s = _af_pd.to_numeric(work_df["trade_count"], errors="coerce")
                qual_mask = qual_mask & tc_s.notna() & (tc_s >= int(min_trades))

            if "composite_score" in work_df.columns and float(min_comp_score) > 0:
                cs_s = _af_pd.to_numeric(work_df["composite_score"], errors="coerce")
                qual_mask = qual_mask & cs_s.notna() & (cs_s >= float(min_comp_score))

            shown_df = work_df[qual_mask].copy()
        else:
            shown_df = work_df.copy()

        if shown_df.empty:
            st.warning(
                f"Total {len(work_df)} scanned records mein se kisi ne bhi maujooda qualification rules pass nahi kiye. "
                "Thresholds kam karein ya 'Auto-Qualify Rules Active' OFF kar ke saare records dekhein."
            )
        else:
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Qualified Strategies", f"{len(shown_df)} / {len(work_df)}")
            with k2:
                best_cs = _af_pd.to_numeric(shown_df["composite_score"], errors="coerce").max() if "composite_score" in shown_df.columns else None
                st.metric("Best Score", f"{best_cs:.4f}" if best_cs is not None and _af_pd.notna(best_cs) else "N/A")
            with k3:
                best_pf_val = _af_pd.to_numeric(shown_df["profit_factor"], errors="coerce").max() if "profit_factor" in shown_df.columns else None
                st.metric("Best Profit Factor", f"{best_pf_val:.2f}" if best_pf_val is not None and _af_pd.notna(best_pf_val) else "N/A")
            with k4:
                avg_wr_val = _af_pd.to_numeric(shown_df["win_rate"], errors="coerce").mean() if "win_rate" in shown_df.columns else None
                st.metric("Avg Win Rate", f"{avg_wr_val:.2f}%" if avg_wr_val is not None and _af_pd.notna(avg_wr_val) else "N/A")

            st.markdown("#### Filtered Strategies Results Table")
            st.dataframe(shown_df, use_container_width=True, hide_index=True)

            st.markdown("#### Strategy Parameters (`genome_json`) & Performance Breakdown")
            sel_row_idx = st.selectbox(
                "Detail dekhne ke liye strategy chunein",
                options=list(shown_df.index),
                format_func=lambda idx: (
                    f"#{shown_df.loc[idx, 'id'] if 'id' in shown_df.columns else idx} | "
                    f"{shown_df.loc[idx, 'symbol'] if 'symbol' in shown_df.columns else ''} "
                    f"({shown_df.loc[idx, 'timeframe'] if 'timeframe' in shown_df.columns else ''}) | "
                    f"Score: {shown_df.loc[idx, 'composite_score'] if 'composite_score' in shown_df.columns else ''} | "
                    f"PF: {shown_df.loc[idx, 'profit_factor'] if 'profit_factor' in shown_df.columns else ''}"
                ),
                key="af_detail_row_idx",
            )
            chosen = shown_df.loc[sel_row_idx]

            genome_dict = {}
            if "genome_json" in shown_df.columns and _af_pd.notna(chosen["genome_json"]):
                raw_g = chosen["genome_json"]
                if isinstance(raw_g, dict):
                    genome_dict = raw_g
                elif isinstance(raw_g, str) and raw_g.strip():
                    try:
                        parsed_g = _af_json.loads(raw_g)
                        if isinstance(parsed_g, dict):
                            genome_dict = parsed_g
                    except Exception:
                        genome_dict = {"raw_genome": raw_g}

            d_left, d_right = st.columns([1.15, 1])
            with d_left:
                st.markdown("**Strategy Parameters (`genome_json`)**")
                if genome_dict:
                    st.dataframe(
                        _af_pd.DataFrame([{"Parameter": str(k), "Value": str(v)} for k, v in genome_dict.items()]),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("Is strategy ke `genome_json` mein koi parameter dictionary nahi mila.")

                st.markdown("**Performance Metrics**")
                metric_cols = [
                    c for c in [
                        "profit_factor", "oos_profit_factor", "win_rate",
                        "max_drawdown", "expectancy", "trade_count",
                        "composite_score", "generation_type", "strategy_hash", "created_at"
                    ] if c in shown_df.columns
                ]
                st.dataframe(
                    _af_pd.DataFrame([{"Metric": c, "Value": str(chosen[c])} for c in metric_cols]),
                    use_container_width=True,
                    hide_index=True,
                )

            with d_right:
                st.markdown("**Full Database Record**")
                rec_out = {}
                for col_i in shown_df.columns:
                    val_i = chosen[col_i]
                    if col_i == "genome_json" and genome_dict:
                        rec_out[col_i] = genome_dict
                    else:
                        rec_out[col_i] = val_i.item() if hasattr(val_i, "item") else val_i
                st.json(rec_out)

                st.download_button(
                    "Export Qualified Strategies CSV",
                    data=shown_df.to_csv(index=False).encode("utf-8"),
                    file_name="auto_qualified_strategies.csv",
                    mime="text/csv",
                    key="af_export_csv",
                )
                st.download_button(
                    "Export Selected Strategy JSON",
                    data=_af_json.dumps(rec_out, indent=2, default=str).encode("utf-8"),
                    file_name="auto_qualified_strategy.json",
                    mime="application/json",
                    key="af_export_json",
                )
# === ATMS AUTO FILTERED STRATEGIES TAB END ===

st.markdown('''<style>
/* 1. Sidebar ka background aur general text */
[data-testid="stSidebar"] {
    background-color: #0F172A !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p {
    color: #F8FAFC !important;
}

/* 2. Sidebar File Uploader box aur uploaded file ka naam saaf dikhane ke liye */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: #1E293B !important;
    border: 1px dashed #64748B !important;
    color: #F8FAFC !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
[data-testid="stSidebar"] small {
    color: #F8FAFC !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button svg {
    fill: #F8FAFC !important;
}

/* 3. Sidebar Inputs (Trading Symbol, Timeframe) */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

/* 4. Main Area Tabs (Manual Backtest, Automatic Optimizer, Data & Method) */
button[data-baseweb="tab"] {
    background-color: #E2E8F0 !important;
    color: #0F172A !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
}
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #FFFFFF !important;
}

</style>''', unsafe_allow_html=True)

st.markdown('''
<style>
div[data-testid="stAlert"],
div[data-testid="stAlert"] > div,
div[data-testid="stAlertContainer"],
div[data-testid="stNotification"],
[data-baseweb="notification"],
.stAlert,
.stAlert > div {
    background-color: #141B29 !important;
    background: #141B29 !important;
    color: #FFFFFF !important;
    border-color: #2D3A54 !important;
    border-left: 4px solid #FF7A1A !important;
}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] li,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] strong,
div[data-testid="stNotification"] *,
[data-baseweb="notification"] *,
.stAlert * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}
</style>
''', unsafe_allow_html=True)


st.markdown('''<style id="atms-spinner-ring-style">
@keyframes atmsSpinRing {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Style Streamlit spinner & running status as a sleek coral-amber spinning ring */
div[data-testid="stSpinner"] > div,
div[data-testid="stStatusWidget"] {
    background: #111724 !important;
    border: 1px solid #2A354B !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
}

div[data-testid="stSpinner"] svg,
div[data-testid="stStatusWidget"] svg {
    display: none !important;
}

div[data-testid="stSpinner"] > div::before,
div[data-testid="stStatusWidget"] > div::before {
    content: "";
    display: inline-block;
    width: 22px;
    height: 22px;
    margin-right: 10px;
    border-radius: 50%;
    border: 3px solid rgba(255, 138, 0, 0.22);
    border-top-color: #FF3B5C;
    border-right-color: #FF8A00;
    animation: atmsSpinRing 0.75s linear infinite;
    vertical-align: middle;
}

div[data-testid="stSpinner"] *,
div[data-testid="stStatusWidget"] * {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
</style>''', unsafe_allow_html=True)

# ============================================================
# AUTONOMOUS LAB (24/7) INTEGRATION
# ============================================================
try:
    from atms.autonomous.engine import AutonomousResearchEngine as _ATMSAutoEngine
except Exception as _auto_import_err:
    _ATMSAutoEngine = None
    _ATMS_IMPORT_ERR = str(_auto_import_err)


@st.cache_resource
def _get_atms_auto_engine():
    if _ATMSAutoEngine is None:
        return None
    return _ATMSAutoEngine(db_path="atms_research.db", export_dir="research_exports")


def _build_scheduled_datasets(base_df, selected_tfs):
    datasets = {}
    if base_df is None or len(base_df) == 0:
        return datasets

    df_work = base_df.copy()
    dt_col = None
    for cand in ["datetime", "timestamp", "time", "date"]:
        if cand in df_work.columns:
            dt_col = cand
            break

    if dt_col is not None:
        df_work[dt_col] = pd.to_datetime(df_work[dt_col], errors="coerce")
        df_work = df_work.dropna(subset=[dt_col]).sort_values(dt_col)
        df_work = df_work.set_index(dt_col)

    for tf in selected_tfs:
        if isinstance(df_work.index, pd.DatetimeIndex) and tf in ("H1", "H4", "1D"):
            rule_map = {"H1": "1h", "H4": "4h", "1D": "1d"}
            agg = {}
            for col, how in [("open", "first"), ("high", "max"), ("low", "min"), ("close", "last"), ("volume", "sum")]:
                if col in df_work.columns:
                    agg[col] = how
            if agg:
                resampled = df_work.resample(rule_map[tf]).agg(agg).dropna().reset_index()
                if len(resampled) >= 120:
                    datasets[tf] = resampled
                    continue
        datasets[tf] = base_df.reset_index(drop=True)

    return datasets


def _format_genome_rules(genome_str):
    try:
        g = json.loads(genome_str) if isinstance(genome_str, str) else (genome_str or {})
        mods = " + ".join(g.get("modules", [])) or "CUSTOM"
        sl_m = g.get("sl_atr_mult", "-")
        tp_r = g.get("tp_r_mult", "-")
        rsi_b = g.get("rsi_buy", "-")
        rsi_s = g.get("rsi_sell", "-")
        return f"{mods} | RSI({rsi_b}/{rsi_s}) | SL:{sl_m}x ATR | TP:{tp_r}R"
    except Exception:
        return str(genome_str)


def _simulate_r_curve(df, g, spread_pts=0.20, slip_pts=0.10):
    if df is None or len(df) < 80:
        return pd.Series(dtype=float)
    close = df["close"]
    high = df["high"]
    low = df["low"]

    ema_f = close.ewm(span=g.get("fast_ema", 20), adjust=False).mean()
    ema_m = close.ewm(span=g.get("mid_ema", 50), adjust=False).mean()
    ema_s = close.ewm(span=g.get("slow_ema", 200), adjust=False).mean()

    delta = close.diff()
    rsi_p = g.get("rsi_period", 14)
    gain = delta.clip(lower=0).rolling(rsi_p).mean()
    loss = (-delta.clip(upper=0)).rolling(rsi_p).mean().replace(0, np.nan)
    rsi = 100 - (100 / (1 + (gain / loss)))

    buy_c = pd.Series(True, index=df.index)
    sell_c = pd.Series(True, index=df.index)
    mods = g.get("modules", [])
    if "EMA_CROSS" in mods:
        buy_c &= (ema_f > ema_m) & (close > ema_s)
        sell_c &= (ema_f < ema_m) & (close < ema_s)
    if "RSI_FILTER" in mods:
        buy_c &= rsi > g.get("rsi_buy", 45)
        sell_c &= rsi < g.get("rsi_sell", 55)
    if "MACD_TREND" in mods:
        macd = close.ewm(span=g.get("macd_fast", 12)).mean() - close.ewm(span=g.get("macd_slow", 26)).mean()
        sig = macd.ewm(span=g.get("macd_signal", 9)).mean()
        buy_c &= macd > sig
        sell_c &= macd < sig
    if "BB_BREAKOUT" in mods:
        ma = close.rolling(g.get("bb_period", 20)).mean()
        std = close.rolling(g.get("bb_period", 20)).std()
        buy_c &= close > (ma + g.get("bb_std", 2.0) * std)
        sell_c &= close < (ma - g.get("bb_std", 2.0) * std)
    if "DONCHIAN_BREAKOUT" in mods:
        lb = g.get("breakout_lookback", 20)
        buy_c &= close > high.shift(1).rolling(lb).max()
        sell_c &= close < low.shift(1).rolling(lb).min()

    sig = pd.Series(0, index=df.index)
    sig[buy_c] = 1
    sig[sell_c] = -1

    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(g.get("atr_period", 14)).mean().bfill()

    closes = close.to_numpy()
    highs = high.to_numpy()
    lows = low.to_numpy()
    atrs = atr.to_numpy()
    sigs = sig.to_numpy()

    eq = [0.0]
    i = 50
    n = len(df) - 1
    cost_total = float(spread_pts + slip_pts)
    tp_mult = float(g.get("tp_r_mult", 2.0))
    sl_mult = float(g.get("sl_atr_mult", 1.5))

    while i < n:
        if sigs[i] == 0 or np.isnan(atrs[i]) or atrs[i] <= 0:
            i += 1
            continue
        direction = sigs[i]
        entry = closes[i]
        sl_dist = atrs[i] * sl_mult
        tp_dist = sl_dist * tp_mult
        sl = entry - direction * sl_dist
        tp = entry + direction * tp_dist
        outcome = 0.0
        for j in range(i + 1, min(i + 96, n)):
            if direction == 1:
                if lows[j] <= sl:
                    outcome = -1.0
                    i = j
                    break
                if highs[j] >= tp:
                    outcome = tp_mult
                    i = j
                    break
            else:
                if highs[j] >= sl:
                    outcome = -1.0
                    i = j
                    break
                if lows[j] <= tp:
                    outcome = tp_mult
                    i = j
                    break
        if outcome != 0.0:
            net_r = outcome - (cost_total / max(sl_dist, 1e-9))
            eq.append(round(eq[-1] + net_r, 3))
        i += 1
    return pd.Series(eq, name="Cumulative R")


def _render_autonomous_lab_tab(active_df=None, symbol="XAUUSD"):
    st.markdown("### ATMS Autonomous Strategy Lab")
    st.caption("24/7 Continuous Strategy Discovery, Walk-Forward Validation, Evolution & Auto Excel Reporting")

    if _ATMSAutoEngine is None:
        st.error(f"Autonomous module load nahi ho saka: {_ATMS_IMPORT_ERR}")
        return

    engine = _get_atms_auto_engine()
    db_stats = engine.db.get_stats()

    # 4 Proposed Dashboard KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Research Mode", f"AUTO ({engine.status})")
    with c2:
        st.metric("Strategy Generation", "24/7", delta=f"+{engine.session_tested} tested")
    with c3:
        st.metric("Best Strategy Leaderboard", "TOP 20", delta=f"Best Score: {db_stats['best_score']}")
    with c4:
        st.metric("Excel Reporting", "AUTO", delta=f"Skipped Dupes: {engine.duplicates_skipped}")

    st.markdown("")

    # Scheduled Timeframes & Controls
    ctrl_col1, ctrl_col2 = st.columns([2, 3])
    with ctrl_col1:
        sched_tfs = st.multiselect(
            "Scheduled Timeframes",
            options=["M15", "H1", "H4", "1D"],
            default=["M15", "H1"],
            key="atms_auto_sched_tfs",
        )
        auto_refresh = st.toggle("Live Auto-Refresh (every 3s while running)", value=True, key="atms_auto_refresh")

    with ctrl_col2:
        st.write("Research Controls")
        b1, b2, b3, b4, b5 = st.columns(5)
        start_clicked = b1.button("Start 24/7", key="atms_auto_start")
        pause_clicked = b2.button("Pause", key="atms_auto_pause")
        resume_clicked = b3.button("Resume", key="atms_auto_resume")
        stop_clicked = b4.button("Stop", key="atms_auto_stop")
        export_clicked = b5.button("Export Excel", key="atms_auto_export")

    # Resolve dataset (uploaded df or fallback sample data)
    run_df = active_df
    if run_df is None or len(run_df) == 0:
        for var_name in ["df", "data", "ohlc_df", "market_df"]:
            if var_name in globals() and isinstance(globals()[var_name], pd.DataFrame) and len(globals()[var_name]) > 0:
                run_df = globals()[var_name]
                break

    if start_clicked:
        if run_df is None or len(run_df) < 120:
            st.warning("Pehle sidebar se kam az kam 120 candles ka OHLC CSV upload karein.")
        else:
            chosen_tfs = sched_tfs if sched_tfs else ["M15"]
            datasets = _build_scheduled_datasets(run_df, chosen_tfs)
            engine.start(datasets=datasets, symbol=symbol or "XAUUSD")
            st.success(f"24/7 Autonomous Research shuru ho gayi ({', '.join(chosen_tfs)})!")

    if pause_clicked:
        engine.pause()
        st.info("Research paused.")

    if resume_clicked:
        engine.resume()
        st.success("Research resumed.")

    if stop_clicked:
        engine.stop()
        st.warning("Research stopped.")

    if export_clicked:
        out_path = engine.export_top_excel(symbol=symbol or "XAUUSD")
        st.success(f"Excel Leaderboard export ho gaya: {out_path}")

    with st.expander("Trading Realism & Minimum Trade Filter", expanded=False):
        r1, r2, r3 = st.columns(3)
        spread_val = r1.number_input("Spread Cost (price units)", min_value=0.0, max_value=10.0, value=0.20, step=0.05, key="atms_auto_spread")
        slip_val = r2.number_input("Slippage Cost (price units)", min_value=0.0, max_value=10.0, value=0.10, step=0.05, key="atms_auto_slip")
        min_tr_val = r3.number_input("Minimum Trades Required", min_value=5, max_value=500, value=30, step=5, key="atms_auto_min_trades")
        engine.spread_points = float(spread_val)
        engine.slippage_points = float(slip_val)
        engine.min_trades = int(min_tr_val)

    st.info(f"Live Status: **{engine.status}** | Total DB Experiments: **{db_stats['total_tested']}** | Last Event: `{engine.last_message}`")

    # Top 20 Leaderboard
    st.markdown("#### Top 20 Strategy Leaderboard")
    top20_df = engine.db.get_top_strategies(limit=20)
    if top20_df is not None and len(top20_df) > 0:
        lb_view = top20_df.copy()
        if "genome_json" in lb_view.columns:
            lb_view["strategy_rules"] = lb_view["genome_json"].apply(_format_genome_rules)
        display_cols = [
            col for col in [
                "id", "symbol", "timeframe", "generation_type", "strategy_rules",
                "composite_score", "profit_factor", "oos_profit_factor",
                "win_rate", "max_drawdown", "expectancy", "trade_count", "created_at"
            ] if col in lb_view.columns
        ]
        st.dataframe(lb_view[display_cols], use_container_width=True, hide_index=True)

        if run_df is not None and len(run_df) >= 80 and "id" in top20_df.columns:
            st.markdown("##### Top Strategy Equity Curve Preview (Net R)")
            sel_id = st.selectbox("Select Strategy ID to Preview", options=top20_df["id"].tolist(), key="atms_auto_preview_id")
            chosen_row = top20_df[top20_df["id"] == sel_id].iloc[0]
            try:
                g_dict = json.loads(chosen_row["genome_json"])
                curve_s = _simulate_r_curve(
                    run_df, g_dict,
                    spread_pts=float(st.session_state.get("atms_auto_spread", 0.20)),
                    slip_pts=float(st.session_state.get("atms_auto_slip", 0.10)),
                )
                if len(curve_s) > 1:
                    st.line_chart(curve_s, use_container_width=True)
            except Exception as _prev_err:
                st.caption(f"Preview unavailable: {_prev_err}")

        excel_file = engine.export_top_excel(symbol=symbol or "XAUUSD")
        if excel_file.exists():
            with open(excel_file, "rb") as f_xlsx:
                st.download_button(
                    label="Download Top 10 / 20 / 100 Excel Report",
                    data=f_xlsx.read(),
                    file_name=excel_file.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="atms_auto_dl_xlsx",
                )
    else:
        st.caption("Abhi tak koi strategy rank nahi hui—Start 24/7 dabayein ya data upload karke shuru karein.")

    if engine.status == "RUNNING" and auto_refresh:
        time.sleep(3)
        st.rerun()

with tab_4:
    _active_df = globals().get('df', None)
    _sym = globals().get('symbol', 'XAUUSD')
    
# === ATMS BUILTIN CSV FALLBACK START ===
def _atms_load_builtin_xauusd():
    import pandas as pd
    from pathlib import Path
    bpath = Path(__file__).resolve().parent / "data" / "builtin_XAUUSD.csv"
    if not bpath.exists():
        return None
    df_in = pd.read_csv(bpath)
    dt_col = None
    for c in df_in.columns:
        if str(c).strip().lower() in ("datetime", "date", "time", "timestamp", "gmt time", "local time"):
            dt_col = c
            break
    if dt_col is not None:
        df_in[dt_col] = pd.to_datetime(df_in[dt_col], errors="coerce")
        df_in = df_in.dropna(subset=[dt_col]).sort_values(dt_col).set_index(dt_col)
    df_in.columns = [str(c).strip().lower() for c in df_in.columns]
    for req in ("open", "high", "low", "close"):
        if req not in df_in.columns:
            return None
    return df_in if len(df_in) > 0 else None

_builtin_df = _atms_load_builtin_xauusd()
if _builtin_df is not None:
    for _name in ("df", "data", "ohlc_df", "market_df", "_active_df"):
        _cur = globals().get(_name)
        if _cur is None or (hasattr(_cur, "empty") and _cur.empty):
            globals()[_name] = _builtin_df.copy()
    if "symbol" not in globals() or not globals().get("symbol"):
        symbol = "XAUUSD"
    _active_df = globals().get("_active_df", _builtin_df.copy())
# === ATMS BUILTIN CSV FALLBACK END ===
_render_autonomous_lab_tab(active_df=_active_df, symbol=_sym if isinstance(_sym, str) else 'XAUUSD')



st.markdown('''
<style id="atms-red-theme-autonomous-fix">
/* Autonomous Lab KPI Cards (stMetric) - Red/Coral TradingView Style */
div[data-testid="stMetric"],
div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #171118 0%, #101420 100%) !important;
    border: 1px solid rgba(255, 59, 92, 0.42) !important;
    border-top: 3px solid #FF3B5C !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    box-shadow: 0 6px 20px rgba(255, 59, 92, 0.14) !important;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label *,
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] label * {
    color: #FF8FA3 !important;
    -webkit-text-fill-color: #FF8FA3 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] *,
div[data-testid="metric-container"] [data-testid="stMetricValue"],
div[data-testid="metric-container"] [data-testid="stMetricValue"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 800 !important;
    opacity: 1 !important;
}

div[data-testid="stMetricDelta"],
div[data-testid="stMetricDelta"] *,
div[data-testid="metric-container"] [data-testid="stMetricDelta"],
div[data-testid="metric-container"] [data-testid="stMetricDelta"] * {
    color: #FF5C77 !important;
    -webkit-text-fill-color: #FF5C77 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/* Captions, Expander Headers & Subheadings in Autonomous Lab */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
.stCaption,
.stCaption * {
    color: #E2E8F0 !important;
    -webkit-text-fill-color: #E2E8F0 !important;
    opacity: 1 !important;
}

div[data-testid="stExpander"] {
    background-color: #131622 !important;
    border: 1px solid rgba(255, 59, 92, 0.35) !important;
    border-radius: 12px !important;
}
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}
div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background-color: #0E121B !important;
}

/* DataFrame / Leaderboard Container */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 59, 92, 0.32) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
</style>
''', unsafe_allow_html=True)

st.markdown('''
<style id="atms-uploader-welcome-fix">
/* Uploaded file name (XAUUSD_M15.csv) & file size (2.1MB) visibility */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}

[data-testid="stFileUploaderFile"] {
    background-color: #161C2C !important;
    border: 1px solid rgba(255, 59, 92, 0.45) !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
}

[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] [data-testid="stFileUploaderFileSize"],
[data-testid="stFileUploaderFile"] span:last-child {
    color: #FF8FA3 !important;
    -webkit-text-fill-color: #FF8FA3 !important;
    font-weight: 600 !important;
}

/* Welcome / Empty-state message ("Welcome to ATMS Strategy Lab...") */
div[data-testid="stAlert"],
div[data-testid="stAlert"] > div,
div[data-testid="stAlertContainer"],
[data-baseweb="notification"] {
    background: linear-gradient(135deg, #17121A 0%, #111624 100%) !important;
    border: 1px solid rgba(255, 59, 92, 0.4) !important;
    border-left: 4px solid #FF3B5C !important;
    border-radius: 12px !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] strong,
[data-baseweb="notification"] p,
[data-baseweb="notification"] span,
[data-baseweb="notification"] div {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}
</style>
''', unsafe_allow_html=True)

st.markdown('''
<style id="atms-welcome-and-uploader-contrast-fix">
/* 1. Welcome / Info / Warning Alert Box */
div[data-testid="stAlert"],
div[data-testid="stAlert"] > div,
div[data-testid="stAlertContainer"],
div[data-testid="stAlertContainer"] > div,
div[data-baseweb="notification"] {
    background: linear-gradient(135deg, #191218 0%, #101522 100%) !important;
    background-color: #141824 !important;
    border: 1px solid rgba(255, 59, 92, 0.55) !important;
    border-left: 4px solid #FF3B5C !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
}

div[data-testid="stAlert"] *,
div[data-testid="stAlertContainer"] *,
div[data-baseweb="notification"] * {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    opacity: 1 !important;
}

/* 2. Uploaded File Name & Size in File Uploader */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploaderFileSize"],
div[data-testid="stFileUploader"] ul li,
div[data-testid="stFileUploader"] ul li * {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    opacity: 1 !important;
}

div[data-testid="stFileUploaderFile"],
div[data-testid="stFileUploader"] ul li {
    background-color: #151B2B !important;
    border: 1px solid rgba(255, 59, 92, 0.45) !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploaderFileSize"] {
    color: #FF8FA3 !important;
    -webkit-text-fill-color: #FF8FA3 !important;
}

/* 3. Supported CSV Format / Code Block */
div[data-testid="stCodeBlock"],
div[data-testid="stCodeBlock"] > div,
div[data-testid="stCodeBlock"] pre,
div[data-testid="stCodeBlock"] code {
    background-color: #121722 !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    border-color: rgba(255, 59, 92, 0.35) !important;
}
</style>
''', unsafe_allow_html=True)

st.markdown('''
<style id="atms-unified-red-theme">
/* Welcome / Status / Alert Banner -> Deep Red & Crimson Border */
div[role="alert"],
div[data-testid="stAlert"],
div[data-testid="stAlert"] > div,
div[data-testid="stAlertContainer"],
[data-baseweb="notification"] {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.45) 0%, rgba(20, 14, 20, 0.96) 100%) !important;
    background-color: #1A1016 !important;
    border: 1px solid rgba(239, 68, 68, 0.55) !important;
    border-left: 4px solid #EF4444 !important;
    border-radius: 10px !important;
    color: #FFF1F2 !important;
    box-shadow: 0 4px 16px rgba(220, 38, 38, 0.16) !important;
}

div[role="alert"] *,
div[data-testid="stAlert"] *,
div[data-testid="stAlertContainer"] *,
[data-baseweb="notification"] * {
    color: #FFF1F2 !important;
    -webkit-text-fill-color: #FFF1F2 !important;
    opacity: 1 !important;
}

/* Uploaded File Card (Filename + File Size) -> Red Theme Match */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {
    background-color: #161118 !important;
    border: 1px dashed rgba(239, 68, 68, 0.55) !important;
}

[data-testid="stFileUploader"] ul,
[data-testid="stFileUploader"] li,
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div {
    background: linear-gradient(90deg, rgba(153, 27, 27, 0.35) 0%, rgba(24, 15, 22, 0.95) 100%) !important;
    background-color: #1A1118 !important;
    border: 1px solid rgba(239, 68, 68, 0.45) !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] li *,
[data-testid="stFileUploaderFile"] *,
[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploaderFileName"] * {
    color: #FFF1F2 !important;
    -webkit-text-fill-color: #FFF1F2 !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

[data-testid="stFileUploaderFileSize"],
[data-testid="stFileUploaderFileSize"] * {
    color: #FCA5A5 !important;
    -webkit-text-fill-color: #FCA5A5 !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Autonomous Lab KPI Cards -> Red Accent Match */
div[data-testid="stMetric"],
div[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(127, 29, 29, 0.32) 0%, rgba(16, 14, 22, 0.96) 100%) !important;
    border: 1px solid rgba(239, 68, 68, 0.42) !important;
    border-top: 3px solid #EF4444 !important;
    border-radius: 12px !important;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label *,
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {
    color: #FCA5A5 !important;
    -webkit-text-fill-color: #FCA5A5 !important;
    opacity: 1 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] *,
div[data-testid="stMetricDelta"],
div[data-testid="stMetricDelta"] * {
    color: #FFF1F2 !important;
    -webkit-text-fill-color: #FFF1F2 !important;
    opacity: 1 !important;
}
</style>
''', unsafe_allow_html=True)


import streamlit.components.v1 as _atms_components

_atms_components.html('''
<script>
(function() {
  function applyRedThemeNow() {
    const doc = window.parent ? window.parent.document : document;
    if (!doc) return;

    // 1. Find exact welcome/empty-state box by text and style its container + text
    const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.nodeValue && node.nodeValue.includes("Welcome to ATMS Strategy Lab")) {
        const el = node.parentElement;
        if (el) {
          el.style.setProperty("color", "#FFF1F2", "important");
          el.style.setProperty("-webkit-text-fill-color", "#FFF1F2", "important");
          el.style.setProperty("opacity", "1", "important");
          el.style.setProperty("font-weight", "600", "important");

          let box = el;
          for (let i = 0; i < 6 && box && box.parentElement; i++) {
            const rect = box.getBoundingClientRect();
            if (rect.width > 250 && rect.height >= 36 && rect.height <= 160) {
              box.style.setProperty("background", "linear-gradient(90deg, rgba(153,27,27,0.45) 0%, rgba(26,12,18,0.98) 100%)", "important");
              box.style.setProperty("background-color", "#1D0E15", "important");
              box.style.setProperty("border", "1px solid rgba(239,68,68,0.65)", "important");
              box.style.setProperty("border-left", "4px solid #EF4444", "important");
              box.style.setProperty("border-radius", "10px", "important");
              box.querySelectorAll("*").forEach(child => {
                child.style.setProperty("color", "#FFF1F2", "important");
                child.style.setProperty("-webkit-text-fill-color", "#FFF1F2", "important");
                child.style.setProperty("opacity", "1", "important");
              });
              break;
            }
            box = box.parentElement;
          }
        }
      }
    }

    // 2. Style uploaded file items (filename + size) in red/dark theme
    doc.querySelectorAll('[data-testid="stFileUploaderFile"], [data-testid="stFileUploader"] li').forEach(item => {
      item.style.setProperty("background-color", "#261018", "important");
      item.style.setProperty("border", "1px solid rgba(239,68,68,0.55)", "important");
      item.style.setProperty("border-radius", "8px", "important");
      item.querySelectorAll("*").forEach(ch => {
        ch.style.setProperty("color", "#FFF1F2", "important");
        ch.style.setProperty("-webkit-text-fill-color", "#FFF1F2", "important");
        ch.style.setProperty("opacity", "1", "important");
      });
    });
  }

  applyRedThemeNow();
  const observer = new MutationObserver(() => applyRedThemeNow());
  if (window.parent && window.parent.document && window.parent.document.body) {
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
  }
  setInterval(applyRedThemeNow, 800);
})();
</script>
''', height=0, width=0)

st.markdown('''<style id="atms-locked-red-theme">
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --primary-color: #FF3B5C !important;
    --background-color: #090A0F !important;
    --secondary-background-color: #141016 !important;
    --text-color: #F8FAFC !important;
    --font: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background: radial-gradient(circle at top left, rgba(255, 59, 92, 0.14), transparent 45%), #090A0F !important;
    color: #F8FAFC !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    -webkit-font-smoothing: antialiased !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricDelta"],
input[type="number"],
div[data-testid="stDataFrame"] {
    font-variant-numeric: tabular-nums !important;
}

::selection {
    background: #FF3B5C !important;
    color: #FFFFFF !important;
}

/* Bold, Larger, Colored Tabs */
div[data-baseweb="tab-list"] {
    gap: 18px !important;
    background: transparent !important;
    border-bottom: 1px solid rgba(148, 163, 184, 0.22) !important;
    padding-bottom: 4px !important;
}

button[data-baseweb="tab"],
button[data-baseweb="tab"] * {
    font-size: 17px !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    opacity: 1 !important;
}

button[data-baseweb="tab"] {
    padding: 10px 6px !important;
    background: transparent !important;
    color: #FDA4AF !important;
    -webkit-text-fill-color: #FDA4AF !important;
}

button[data-baseweb="tab"]:hover,
button[data-baseweb="tab"]:hover * {
    color: #FF7A90 !important;
    -webkit-text-fill-color: #FF7A90 !important;
}

button[data-baseweb="tab"][aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"] * {
    color: #FF3B5C !important;
    -webkit-text-fill-color: #FF3B5C !important;
    font-weight: 800 !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #FF3B5C !important;
    height: 3px !important;
}

/* Sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #160B10 0%, #090A0F 100%) !important;
    border-right: 1px solid rgba(255, 59, 92, 0.25) !important;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label * {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Inputs & Selectboxes */
input,
textarea,
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background-color: #140D13 !important;
    background: #140D13 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border-color: rgba(255, 59, 92, 0.35) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    opacity: 1 !important;
}

/* File Uploader: SAME consistent dark-red look before AND after upload */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {
    background: #140C11 !important;
    background-color: #140C11 !important;
    border: 1.5px dashed rgba(255, 59, 92, 0.65) !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"],
[data-testid="stFileUploader"] li {
    background: #1E1017 !important;
    background-color: #1E1017 !important;
    border-color: rgba(255, 59, 92, 0.45) !important;
    border-radius: 8px !important;
    opacity: 1 !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *,
[data-testid="stFileUploader"] li *,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    opacity: 1 !important;
}

[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button * {
    background: #FF6B1A !important;
    background-color: #FF6B1A !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}

/* Welcome / Info / Status Banner */
div[role="alert"],
div[data-testid="stAlert"],
div[data-testid="stAlertContainer"],
[data-baseweb="notification"] {
    background: linear-gradient(90deg, rgba(127, 29, 29, 0.35) 0%, rgba(20, 12, 17, 0.96) 100%) !important;
    background-color: #160D13 !important;
    border: 1px solid rgba(255, 59, 92, 0.45) !important;
    border-left: 4px solid #FF3B5C !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

div[role="alert"] > div,
div[data-testid="stAlert"] > div,
div[data-testid="stAlertContainer"] > div,
[data-baseweb="notification"] > div,
div[role="alert"] *,
div[data-testid="stAlert"] *,
div[data-testid="stAlertContainer"] *,
[data-baseweb="notification"] * {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    font-weight: 500 !important;
    opacity: 1 !important;
}

/* KPI Cards */
div[data-testid="stMetric"],
div[data-testid="metric-container"] {
    background: linear-gradient(155deg, rgba(127, 29, 29, 0.24) 0%, rgba(15, 11, 18, 0.97) 100%) !important;
    border: 1px solid rgba(255, 59, 92, 0.35) !important;
    border-top: 3px solid #FF3B5C !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label * {
    color: #FDA4AF !important;
    -webkit-text-fill-color: #FDA4AF !important;
    font-weight: 600 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 800 !important;
}

/* Buttons */
button[kind="primary"],
.stButton > button {
    background: linear-gradient(135deg, #FF3B5C 0%, #DC2626 100%) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
</style>''', unsafe_allow_html=True)

st.markdown('''<style id="atms-tabs-force-style">
/* Force large, bold, colored tabs across all nested elements */
div[data-testid="stTabs"] div[data-baseweb="tab-list"],
div[data-baseweb="tab-list"] {
    gap: 14px !important;
    padding: 8px 10px !important;
    border-bottom: 2px solid rgba(255, 107, 26, 0.35) !important;
    align-items: center !important;
}

div[data-testid="stTabs"] button[data-baseweb="tab"],
button[data-baseweb="tab"] {
    height: auto !important;
    min-height: 48px !important;
    padding: 10px 18px !important;
    border-radius: 10px 10px 0 0 !important;
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 107, 26, 0.22) !important;
    border-bottom: none !important;
    transition: all 0.15s ease !important;
}

div[data-testid="stTabs"] button[data-baseweb="tab"],
div[data-testid="stTabs"] button[data-baseweb="tab"] *,
button[data-baseweb="tab"],
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span,
button[data-baseweb="tab"] div {
    font-size: 20px !important;
    font-weight: 800 !important;
    line-height: 1.25 !important;
    letter-spacing: 0.01em !important;
    opacity: 1 !important;
}

/* Distinct vibrant colors per tab so they look colorful & bold */
button[data-baseweb="tab"]:nth-of-type(1),
button[data-baseweb="tab"]:nth-of-type(1) * {
    color: #FF8A4C !important;
    -webkit-text-fill-color: #FF8A4C !important;
}

button[data-baseweb="tab"]:nth-of-type(2),
button[data-baseweb="tab"]:nth-of-type(2) * {
    color: #38BDF8 !important;
    -webkit-text-fill-color: #38BDF8 !important;
}

button[data-baseweb="tab"]:nth-of-type(3),
button[data-baseweb="tab"]:nth-of-type(3) * {
    color: #A78BFA !important;
    -webkit-text-fill-color: #A78BFA !important;
}

button[data-baseweb="tab"]:nth-of-type(4),
button[data-baseweb="tab"]:nth-of-type(4) * {
    color: #34D399 !important;
    -webkit-text-fill-color: #34D399 !important;
}

/* Selected / Active Tab highlight */
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(180deg, rgba(255, 107, 26, 0.24) 0%, rgba(255, 59, 92, 0.12) 100%) !important;
    border-color: rgba(255, 107, 26, 0.65) !important;
}

button[data-baseweb="tab"][aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    text-shadow: 0 0 12px rgba(255, 107, 26, 0.55) !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #FF6B1A !important;
    height: 4px !important;
    border-radius: 999px !important;
}
</style>''', unsafe_allow_html=True)

# === ATMS SINGLE DARK THEME & WHITE BOX FIX START ===
st.markdown("""<style id="atms-single-dark-theme-fix">
/* Inline badges / code contrast */
code, [data-testid="stCode"], [data-testid="stCode"] * {
    background-color: rgba(255, 90, 54, 0.15) !important;
    color: #FFB29E !important;
    border: 1px solid rgba(255, 90, 54, 0.35) !important;
    border-radius: 6px !important;
}

/* Inputs, selects & file uploader contrast */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] * {
    color: #F3F4F6 !important;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    background-color: #14161F !important;
    color: #F3F4F6 !important;
    border-color: rgba(255, 90, 54, 0.35) !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="input"] input {
    color: #F3F4F6 !important;
}

/* DataFrames & JSON viewers dark surface (no white boxes) */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] > div > div,
[data-testid="stDataFrame"] iframe,
[data-testid="stJson"],
[data-testid="stJson"] > div,
[data-testid="stJson"] pre {
    background-color: #12141D !important;
    color: #F3F4F6 !important;
    border-color: rgba(255, 90, 54, 0.28) !important;
}

[data-testid="stJson"] span,
[data-testid="stJson"] div {
    color: #E5E7EB !important;
}
</style>""", unsafe_allow_html=True)
# === ATMS SINGLE DARK THEME & WHITE BOX FIX END ===

# === ATMS BIGGER TABS POLISH START ===
st.markdown("""<style id="atms-bigger-tabs-polish">
/* Bigger, cleaner tab bar & individual tabs */
[data-testid="stTabs"] [role="tablist"],
.stTabs [data-baseweb="tab-list"] {
    gap: 10px !important;
    padding-bottom: 6px !important;
    border-bottom: 1px solid rgba(255, 90, 54, 0.25) !important;
}

[data-testid="stTabs"] button[role="tab"],
.stTabs [data-baseweb="tab"] {
    height: auto !important;
    min-height: 46px !important;
    padding: 10px 18px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    border-radius: 10px 10px 0 0 !important;
    white-space: nowrap !important;
    color: #D1D5DB !important;
}

[data-testid="stTabs"] button[role="tab"] p,
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] div,
.stTabs [data-baseweb="tab"] span {
    font-size: 15px !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #FF7A59 !important;
}
</style>""", unsafe_allow_html=True)
# === ATMS BIGGER TABS POLISH END ===

# === ATMS BIG RED TABS FINAL START ===
st.markdown("""<style id="atms-big-red-tabs-final">
/* Tab list container */
[data-testid="stTabs"] [role="tablist"],
.stTabs [data-baseweb="tab-list"],
div[data-baseweb="tab-list"] {
    gap: 12px !important;
    padding: 6px 4px 10px 4px !important;
    border-bottom: 2px solid rgba(239, 68, 68, 0.45) !important;
    flex-wrap: wrap !important;
}

/* Individual tab buttons (bigger & red) */
[data-testid="stTabs"] button[role="tab"],
.stTabs [data-baseweb="tab"],
div[data-baseweb="tab"] {
    height: auto !important;
    min-height: 50px !important;
    padding: 12px 20px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    background-color: rgba(220, 38, 38, 0.14) !important;
    color: #FCA5A5 !important;
    border: 1.5px solid rgba(239, 68, 68, 0.45) !important;
    transition: all 0.18s ease !important;
}

[data-testid="stTabs"] button[role="tab"] *,
.stTabs [data-baseweb="tab"] *,
div[data-baseweb="tab"] * {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #FCA5A5 !important;
}

/* Hover state */
[data-testid="stTabs"] button[role="tab"]:hover,
.stTabs [data-baseweb="tab"]:hover,
div[data-baseweb="tab"]:hover {
    background-color: rgba(220, 38, 38, 0.28) !important;
    color: #FFFFFF !important;
    border-color: #EF4444 !important;
}

[data-testid="stTabs"] button[role="tab"]:hover *,
.stTabs [data-baseweb="tab"]:hover *,
div[data-baseweb="tab"]:hover * {
    color: #FFFFFF !important;
}

/* Active / Selected tab (bright red) */
[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"],
div[data-baseweb="tab"][aria-selected="true"] {
    background-color: #DC2626 !important;
    color: #FFFFFF !important;
    border-color: #FF4D4D !important;
    box-shadow: 0 0 14px rgba(239, 68, 68, 0.55) !important;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] *,
.stTabs [data-baseweb="tab"][aria-selected="true"] *,
div[data-baseweb="tab"][aria-selected="true"] * {
    color: #FFFFFF !important;
}

/* Hide default thin highlight bar so our red pill/tab style stays clean */
[data-testid="stTabs"] [data-testid="stTabHighlight"],
div[data-baseweb="tab-highlight"] {
    background-color: transparent !important;
    height: 0px !important;
}
</style>""", unsafe_allow_html=True)
# === ATMS BIG RED TABS FINAL END ===

# === ATMS AUTONOMOUS LIVE TELEMETRY START ===
def _atms_get_autonomous_summary():
    import sqlite3
    from pathlib import Path

    summary = {
        "db_found": False,
        "total_rows": 0,
        "unique_hashes": 0,
        "duplicates_in_db": 0,
        "best_pf": None,
        "best_win_rate": None,
        "session_evaluated": int(st.session_state.get("atms_eval_count", 0)),
        "session_skipped": int(st.session_state.get("atms_skip_count", 0)),
    }

    candidates = [
        Path("atms_research.db"),
        Path(__file__).resolve().parent / "atms_research.db",
        Path("data") / "atms_research.db",
    ]
    db_path = next((c for c in candidates if c.exists()), None)
    if db_path is None:
        return summary

    summary["db_found"] = True
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "experiments" in tables:
            cols = {r[1] for r in cur.execute("PRAGMA table_info(experiments)").fetchall()}
            row = cur.execute("SELECT COUNT(*) FROM experiments").fetchone()
            summary["total_rows"] = int(row[0] or 0) if row else 0

            if "strategy_hash" in cols:
                urow = cur.execute(
                    "SELECT COUNT(DISTINCT strategy_hash) FROM experiments WHERE strategy_hash IS NOT NULL AND strategy_hash != ''"
                ).fetchone()
                summary["unique_hashes"] = int(urow[0] or 0) if urow else summary["total_rows"]
                summary["duplicates_in_db"] = max(0, summary["total_rows"] - summary["unique_hashes"])
            else:
                summary["unique_hashes"] = summary["total_rows"]

            for cand_pf in ("profit_factor", "pf", "best_pf"):
                if cand_pf in cols:
                    r_pf = cur.execute(f"SELECT MAX({cand_pf}) FROM experiments WHERE {cand_pf} IS NOT NULL").fetchone()
                    if r_pf and r_pf[0] is not None:
                        summary["best_pf"] = float(r_pf[0])
                        break

            for cand_wr in ("win_rate", "win_rate_pct", "best_win_rate"):
                if cand_wr in cols:
                    r_wr = cur.execute(f"SELECT MAX({cand_wr}) FROM experiments WHERE {cand_wr} IS NOT NULL").fetchone()
                    if r_wr and r_wr[0] is not None:
                        summary["best_win_rate"] = float(r_wr[0])
                        break
        conn.close()
    except Exception:
        pass
    return summary

def _atms_render_auto_lab_banner():
    s = _atms_get_autonomous_summary()
    st.markdown("### Autonomous Lab — Live Status & Deduplication Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DB Experiments", f"{s['total_rows']:,}" if s["db_found"] else "0")
    c2.metric("Unique Strategy Hashes", f"{s['unique_hashes']:,}" if s["db_found"] else "0")
    dedup_total = s["duplicates_in_db"] + s["session_skipped"]
    c3.metric("Skipped Duplicates", f"{dedup_total:,}")
    best_str = f"PF {s['best_pf']:.2f}" if s["best_pf"] is not None else "—"
    if s["best_win_rate"] is not None:
        best_str += f" | WR {s['best_win_rate']:.1f}%"
    c4.metric("Best Benchmark", best_str)
    st.caption(
        f"DB Status: {'Connected (atms_research.db)' if s['db_found'] else 'Waiting for atms_research.db'} | "
        f"Session Evaluated: {s['session_evaluated']:,} | Session Skipped: {s['session_skipped']:,}"
    )
# === ATMS AUTONOMOUS LIVE TELEMETRY END ===

# === ATMS CLEAN UI CSS START ===
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input {
        background-color: #111622 !important;
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
        border-color: rgba(255, 255, 255, 0.16) !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[role="listbox"],
    div[role="option"] {
        background-color: #111622 !important;
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[role="option"]:hover {
        background-color: rgba(239, 68, 68, 0.25) !important;
        color: #FFFFFF !important;
    }
    button[kind],
    .stButton > button,
    div[data-testid="stButton"] button {
        white-space: nowrap !important;
        text-overflow: clip !important;
        overflow: visible !important;
        font-size: 0.85rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# === ATMS CLEAN UI CSS END ===
