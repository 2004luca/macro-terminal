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