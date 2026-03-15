# pages/4_markets.py
# Markets & Equities page

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf


# --- DATA FUNCTIONS ---

@st.cache_data(ttl=3600)
def get_index_data():
    """
    Fetches historical price data for major equity indices.
    
    Tickers:
        ^GSPC  → S&P 500
        ^BVSP  → Ibovespa
        ^IXIC  → Nasdaq 100
        ^FTSE  → FTSE 100 (UK)
    """
    tickers = {
        "S&P 500":  "^GSPC",
        "Ibovespa": "^BVSP",
        "Nasdaq":   "^IXIC",
        "FTSE 100": "^FTSE",
    }

    data = {}
    for name, ticker in tickers.items():
        df = yf.download(ticker, start="2000-01-01", progress=False)
        data[name] = df["Close"].squeeze()

    return data


def calc_ytd(series):
    """
    Calculates Year-To-Date return.
    Finds the last closing price of the previous year and compares to today.
    """
    current_year = series.index[-1].year
    prev_year_end = series[series.index.year == current_year - 1].iloc[-1]
    current = series.iloc[-1]
    return round((current / prev_year_end - 1) * 100, 2)


# --- PAGE LAYOUT ---

st.title("📈 Markets & Equities")
st.markdown("""
A deep dive into global equity markets — performance, valuation, sector rotation, 
and correlations. Understanding equity markets requires understanding the macro 
environment they operate in.
""")
st.divider()

# --- SECTION 1: INDICES ---

st.subheader("🌍 Global Indices")
st.markdown("""
Equity indices are the best single measure of market sentiment and economic expectations. 
They aggregate the collective view of millions of investors about the future value of companies.
""")

with st.spinner("Loading index data..."):
    indices = get_index_data()

# YTD Performance table
ytd_rows = []
for name, series in indices.items():
    ytd = calc_ytd(series)
    current = round(series.iloc[-1], 2)
    ytd_rows.append({
        "Index":   name,
        "Current": f"{current:,.2f}",
        "YTD (%)": f"{ytd:+.2f}%",
    })

df_ytd = pd.DataFrame(ytd_rows)

def color_ytd(val):
    if "+" in str(val):
        return "color: green"
    elif "-" in str(val):
        return "color: red"
    return ""

styled_ytd = df_ytd.style.applymap(color_ytd, subset=["YTD (%)"])
st.dataframe(styled_ytd, use_container_width=True, hide_index=True)

# Historical chart
st.markdown("#### Historical Performance")
st.markdown("""
Select which indices to compare. Note that indices are in their **local currency** — 
a Brazilian investor in Ibovespa and a US investor in S&P 500 have very different 
real returns when you account for currency moves.
""")

selected = st.multiselect(
    "Select indices to display:",
    options=list(indices.keys()),
    default=["S&P 500", "Ibovespa"]
)

# Normalize to 100 at start date for fair comparison
start_date = st.date_input(
    "Start date:",
    value=pd.Timestamp("2010-01-01"),
    min_value=pd.Timestamp("2000-01-01"),
    max_value=pd.Timestamp.today()
)

fig = go.Figure()
for name in selected:
    series = indices[name]
    series = series[series.index >= pd.Timestamp(start_date)]
    # Normalize to 100 at start
    normalized = (series / series.iloc[0]) * 100

    fig.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized.values,
        mode="lines",
        name=name
    ))

fig.update_layout(
    yaxis_title="Indexed to 100",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=400,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
> **Why normalize to 100?**  
> The S&P 500 trades around 5,000 and the Ibovespa around 130,000 — 
> comparing them directly is meaningless. Normalizing both to 100 at the same 
> start date lets you compare **relative performance** fairly.
""")

st.divider()

# --- SECTION 2: S&P 500 DEEP DIVE ---

st.subheader("🔍 S&P 500 — Deep Dive")
st.markdown("""
The S&P 500 is the most important equity index in the world — 
it represents the 500 largest US companies and is the benchmark 
against which virtually every fund manager is measured.
""")

@st.cache_data(ttl=3600)
def get_sp500_detail():
    """
    Fetches detailed S&P 500 data for deep dive analysis.
    Includes price history and calculates realized volatility.
    """
    df = yf.download("^GSPC", start="2000-01-01", progress=False)
    close = df["Close"].squeeze()

    # Daily returns
    returns = close.pct_change().dropna()

    # Realized volatility — rolling 30-day standard deviation annualized
    # Annualized by multiplying by sqrt(252) — trading days in a year
    vol_30d = returns.rolling(30).std() * (252 ** 0.5) * 100
    vol_30d = vol_30d.dropna()

    return close, returns, vol_30d


with st.spinner("Loading S&P 500 detail..."):
    sp_close, sp_returns, sp_vol = get_sp500_detail()

# Price chart with key events annotated
st.markdown("#### Price History with Key Events")

fig_sp = go.Figure()

fig_sp.add_trace(go.Scatter(
    x=sp_close.index,
    y=sp_close.values,
    mode="lines",
    line=dict(color="#00d4ff", width=1.5),
    name="S&P 500"
))

# Annotate key events
events = [
    ("2008-09-15", "Lehman collapse"),
    ("2020-03-23", "COVID low"),
    ("2022-01-03", "Fed hiking cycle"),
    ("2023-10-27", "2023 low"),
]

for date, label in events:
    ts = pd.Timestamp(date)
    if ts in sp_close.index:
        price = sp_close[ts]
    else:
        price = sp_close.asof(ts)

    fig_sp.add_annotation(
        x=ts,
        y=price,
        text=label,
        showarrow=True,
        arrowhead=2,
        arrowcolor="white",
        font=dict(color="white", size=10),
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="white",
        borderwidth=1,
    )

fig_sp.update_layout(
    yaxis_title="Price (USD)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=400,
)

st.plotly_chart(fig_sp, use_container_width=True)

# Realized Volatility
st.markdown("#### Realized Volatility (30-day Rolling)")
st.markdown("""
**Realized volatility** measures how much the S&P 500 actually moved over the past 30 days, 
expressed as an annualized percentage.

- **Low vol (< 15%)** → calm market, investors complacent
- **Medium vol (15-25%)** → normal uncertainty
- **High vol (> 25%)** → fear, crisis, or major macro event

**How it's calculated:**
""")
st.info("Realized Vol = Rolling 30-day Std Dev of Daily Returns × √252")
st.markdown("""
We multiply by √252 to **annualize** the volatility — 
252 is the number of trading days in a year. This lets us compare 
volatility across different time windows on the same scale.
""")

fig_vol = go.Figure()

fig_vol.add_trace(go.Scatter(
    x=sp_vol.index,
    y=sp_vol.values,
    mode="lines",
    line=dict(color="#ff6b6b", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(255, 107, 107, 0.1)",
    name="30d Realized Vol"
))

fig_vol.add_hline(y=15, line_dash="dash", line_color="yellow",
                  annotation_text="15% — calm threshold",
                  annotation_position="right")
fig_vol.add_hline(y=25, line_dash="dash", line_color="red",
                  annotation_text="25% — fear threshold",
                  annotation_position="right")

fig_vol.update_layout(
    yaxis_title="Annualized Vol (%)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=300,
)

st.plotly_chart(fig_vol, use_container_width=True)

st.divider()

st.divider()

# --- SECTION 3+4: SECTORS & CORRELATIONS ---

st.subheader("🏭 Sectors & Correlations")
st.markdown("""
The S&P 500 is divided into **11 sectors**. Understanding sector dynamics — 
what's in each sector, how they perform over time, and how they correlate — 
is fundamental to equity analysis and portfolio construction.
""")

@st.cache_data(ttl=3600)
def get_sector_data():
    """
    Fetches price history for all S&P 500 sector ETFs.
    SPDR Sector ETFs by State Street — the most liquid sector vehicles.
    """
    sectors = {
        "Technology":             "XLK",
        "Financials":             "XLF",
        "Energy":                 "XLE",
        "Health Care":            "XLV",
        "Industrials":            "XLI",
        "Consumer Discretionary": "XLY",
        "Consumer Staples":       "XLP",
        "Materials":              "XLB",
        "Utilities":              "XLU",
        "Real Estate":            "XLRE",
        "Communication Services": "XLC",
    }

    data = {}
    for name, ticker in sectors.items():
        df = yf.download(ticker, start="2000-01-01", progress=False)
        data[name] = df["Close"].squeeze().dropna()

    return data

with st.spinner("Loading sector data..."):
    sector_data = get_sector_data()

# Sector metadata
sector_info = {
    "Technology": {
        "description": "Companies that develop software, hardware, and semiconductors. The largest sector in the S&P 500.",
        "companies": "Apple, Microsoft, NVIDIA, Broadcom, Salesforce",
        "macro_sensitivity": "🔴 High — very sensitive to interest rates. Long-duration assets: valued on future earnings discounted at current rates.",
    },
    "Financials": {
        "description": "Banks, insurance companies, asset managers, and payment processors.",
        "companies": "JPMorgan, Berkshire Hathaway, Visa, Mastercard, Bank of America",
        "macro_sensitivity": "🟡 Medium — benefits from higher rates (wider lending margins) but hurt by recessions (credit losses).",
    },
    "Energy": {
        "description": "Oil & gas exploration, production, refining, and services companies.",
        "companies": "ExxonMobil, Chevron, ConocoPhillips, EOG Resources, Schlumberger",
        "macro_sensitivity": "🟡 Medium — driven by oil prices, which depend on global growth and geopolitics.",
    },
    "Health Care": {
        "description": "Pharmaceuticals, biotech, medical devices, and managed care organizations.",
        "companies": "UnitedHealth, Johnson & Johnson, Eli Lilly, AbbVie, Pfizer",
        "macro_sensitivity": "🟢 Low — defensive sector. Demand is inelastic — people need healthcare regardless of the economy.",
    },
    "Industrials": {
        "description": "Aerospace, defense, machinery, transportation, and construction companies.",
        "companies": "GE Aerospace, Caterpillar, Honeywell, Union Pacific, Boeing",
        "macro_sensitivity": "🟡 Medium — cyclical. Performs well in expansions, suffers in slowdowns.",
    },
    "Consumer Discretionary": {
        "description": "Companies selling non-essential goods and services — cars, retail, restaurants, entertainment.",
        "companies": "Amazon, Tesla, Home Depot, McDonald's, Nike",
        "macro_sensitivity": "🔴 High — very cyclical. Consumers cut discretionary spending first in downturns.",
    },
    "Consumer Staples": {
        "description": "Companies selling essential goods — food, beverages, household products, tobacco.",
        "companies": "Procter & Gamble, Coca-Cola, PepsiCo, Walmart, Costco",
        "macro_sensitivity": "🟢 Low — defensive. People buy toothpaste and food regardless of the economy.",
    },
    "Materials": {
        "description": "Mining, chemicals, paper, and packaging companies.",
        "companies": "Linde, Sherwin-Williams, Air Products, Freeport-McMoRan, Newmont",
        "macro_sensitivity": "🟡 Medium — tied to global growth and commodity prices. China demand is key.",
    },
    "Utilities": {
        "description": "Electric, gas, and water utilities. Highly regulated, capital-intensive businesses.",
        "companies": "NextEra Energy, Southern Company, Duke Energy, Dominion Energy",
        "macro_sensitivity": "🟢 Low — defensive but rate-sensitive. High debt loads make utilities vulnerable to rising rates.",
    },
    "Real Estate": {
        "description": "REITs (Real Estate Investment Trusts) — companies that own income-producing properties.",
        "companies": "Prologis, American Tower, Equinix, Crown Castle, Simon Property",
        "macro_sensitivity": "🔴 High — very sensitive to interest rates. REITs are valued like bonds — higher rates hurt valuations.",
    },
    "Communication Services": {
        "description": "Telecom, media, entertainment, and social media companies.",
        "companies": "Meta, Alphabet, Netflix, Disney, T-Mobile",
        "macro_sensitivity": "🟡 Medium — mix of defensive (telecom) and growth (social media/streaming).",
    },
}

# Tabs
tab_ytd, tab_hist, tab_info, tab_corr = st.tabs([
    "📊 YTD Performance",
    "📈 Historical Performance",
    "🏢 Sector Guide",
    "🔗 Correlation Matrix"
])

# --- YTD TAB ---
with tab_ytd:
    ytd_rows = []
    for name, series in sector_data.items():
        start_price = series[series.index.year == series.index[-1].year].iloc[0]
        current = series.iloc[-1]
        ytd = round((current / start_price - 1) * 100, 2)
        ytd_rows.append({"Sector": name, "YTD (%)": ytd})

    df_ytd = pd.DataFrame(ytd_rows).sort_values("YTD (%)", ascending=False)
    colors = ["#00ff88" if v >= 0 else "#ff6b6b" for v in df_ytd["YTD (%)"]]

    fig_ytd = go.Figure()
    fig_ytd.add_trace(go.Bar(
        x=df_ytd["Sector"],
        y=df_ytd["YTD (%)"],
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in df_ytd["YTD (%)"]],
        textposition="outside",
    ))
    fig_ytd.add_hline(y=0, line_dash="dash", line_color="white")
    fig_ytd.update_layout(
        yaxis_title="YTD Return (%)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=450,
        margin=dict(t=40, b=100)
    )
    st.plotly_chart(fig_ytd, use_container_width=True)

    st.markdown("""
    **Sector rotation signal:** Look at which sectors are leading.
    - Defensives leading (Staples, Utilities, Health Care) → late cycle, risk-off
    - Cyclicals leading (Tech, Discretionary, Financials) → early/mid cycle, risk-on
    - Energy leading → inflation concerns, commodity supercycle
    """)
    st.markdown("""
**YTD (Year-to-Date)** measures how much each sector has returned since the first trading day 
of the current year. It's the most common way to compare performance across assets 
on a level playing field — everyone starts at zero on January 1st.
""")

# --- HISTORICAL TAB ---
with tab_hist:
    st.markdown("Compare sector performance over time — normalized to 100 at your chosen start date.")

    selected_sectors = st.multiselect(
        "Select sectors:",
        options=list(sector_data.keys()),
        default=["Technology", "Energy", "Consumer Staples", "Financials"]
    )

    start_hist = st.date_input(
        "Start date:",
        value=pd.Timestamp("2015-01-01"),
        min_value=pd.Timestamp("2000-01-01"),
        max_value=pd.Timestamp.today(),
        key="sector_start"
    )

    fig_hist = go.Figure()
    for name in selected_sectors:
        series = sector_data[name]
        series = series[series.index >= pd.Timestamp(start_hist)]
        normalized = (series / series.iloc[0]) * 100

        fig_hist.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized.values,
            mode="lines",
            name=name
        ))

    fig_hist.update_layout(
        yaxis_title="Indexed to 100",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        hovermode="x unified",
        height=450,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# --- SECTOR GUIDE TAB ---
with tab_info:
    st.markdown("A guide to each S&P 500 sector — what's in it, key companies, and macro sensitivity.")

    for sector, info in sector_info.items():
        with st.expander(f"**{sector}**"):
            st.markdown(f"**What it is:** {info['description']}")
            st.markdown(f"**Key companies:** {info['companies']}")
            st.markdown(f"**Macro sensitivity:** {info['macro_sensitivity']}")

# --- CORRELATION MATRIX TAB ---
with tab_corr:
    st.markdown("""
    ### What is a Correlation Matrix?
    
    A **correlation** measures how two assets move together, on a scale from -1 to +1:
    - **+1.0** → perfect positive correlation — they always move together
    - **0.0** → no correlation — they move independently
    - **-1.0** → perfect negative correlation — when one goes up, the other goes down
    
    **Why traders use it:**
    - **Portfolio diversification** — combining low-correlation assets reduces risk
    - **Pair trading** — trading the spread between highly correlated assets
    - **Risk management** — understanding how positions interact in a portfolio
    """)
    st.info("**Rule of thumb:** Correlation > 0.7 = highly correlated. Correlation < 0.3 = low correlation.")

    # Build returns dataframe for correlation
    returns_dict = {}
    for name, series in sector_data.items():
        returns_dict[name] = series.pct_change().dropna()

    df_returns = pd.DataFrame(returns_dict).dropna()
    corr_matrix = df_returns.corr().round(2)

    import plotly.figure_factory as ff

    fig_corr = ff.create_annotated_heatmap(
        z=corr_matrix.values,
        x=list(corr_matrix.columns),
        y=list(corr_matrix.index),
        annotation_text=corr_matrix.values.round(2),
        colorscale="RdBu",
        reversescale=True,
        zmin=-1, zmax=1,
        showscale=True,
    )

    fig_corr.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=550,
        margin=dict(t=40, b=100, l=100)
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("""
    **What to look for:**
    - **Cyclicals cluster together** — Tech, Discretionary, Financials tend to be highly correlated
    - **Defensives cluster together** — Staples, Utilities, Health Care move similarly
    - **Energy is different** — driven by oil prices, often has lower correlation with the rest
    - **Real Estate is rate-sensitive** — correlates more with Utilities than Tech
    """)