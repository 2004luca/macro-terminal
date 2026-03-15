# pages/6_sentiment.py
# Sentiment & Risk page

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from fredapi import Fred


# --- DATA FUNCTIONS ---

@st.cache_data(ttl=3600)
def get_vix():
    """
    Fetches VIX index history via Yahoo Finance.
    
    VIX = CBOE Volatility Index
    Measures the market's expectation of S&P 500 volatility 
    over the next 30 days, derived from options prices.
    
    Ticker: ^VIX
    """
    df = yf.download("^VIX", start="2000-01-01", progress=False)
    return df["Close"].squeeze().dropna()


# --- PAGE LAYOUT ---

st.title("🌡️ Sentiment & Risk")
st.markdown("""
Markets are driven by two forces: **fundamentals** and **sentiment**. 
Even when the economic data is strong, fear can cause prices to collapse. 
Even when fundamentals are weak, euphoria can push prices higher.

This page tracks the mood of the market — are investors fearful or complacent? 
Are they taking risk or hiding from it?
""")
st.divider()

with st.spinner("Loading sentiment data..."):
    vix = get_vix()

# Calculate VIX signal
current_vix = round(vix.iloc[-1], 1)
vix_52w_high = round(vix[vix.index >= vix.index[-1] - pd.DateOffset(years=1)].max(), 1)

if current_vix < 15:
    vix_signal = "🟢 Calm — market is complacent"
elif current_vix < 25:
    vix_signal = "🟡 Normal — healthy uncertainty"
elif current_vix < 35:
    vix_signal = "🟠 Elevated — market stress"
else:
    vix_signal = "🔴 Panic — crisis mode"

# Quick VIX snapshot at the top
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current VIX", current_vix)
with col2:
    st.metric("52w High", vix_52w_high)
with col3:
    st.metric("Regime", vix_signal.split("—")[0].strip())

st.info(f"**Current Signal:** {vix_signal}")

st.divider()

# --- SECTION 1: VIX ---

st.subheader("😨 VIX — The Fear Index")
st.markdown("""
The **VIX (CBOE Volatility Index)** is the most widely watched measure of market fear. 
It is often called the **"fear gauge"** of Wall Street.

### What exactly is the VIX?

The VIX measures the market's expectation of how much the S&P 500 will move 
over the **next 30 days**, expressed as an annualized percentage.

It is calculated from the prices of **S&P 500 options** — specifically, 
how much investors are willing to pay for protection (put options) 
against a market decline. When fear rises, demand for protection rises, 
option prices increase, and the VIX goes up.

**Important distinction:**
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **📊 Implied Volatility (VIX)**  
    What the *market expects* volatility to be.  
    Forward-looking — derived from option prices.  
    Reflects fear and uncertainty.  
    *"How much does the market think it will move?"*
    """)
with col2:
    st.markdown("""
    **📈 Realized Volatility**  
    What volatility *actually was*.  
    Backward-looking — calculated from price history.  
    Reflects what actually happened.  
    *"How much did the market actually move?"*
    """)

st.markdown("""
**VIX regimes:**
- **VIX < 15** → Calm, complacent market. Investors are not worried. 
  Historically, this is when risk builds up quietly.
- **VIX 15-25** → Normal uncertainty. Healthy level of caution.
- **VIX 25-35** → Elevated fear. Market stress, significant uncertainty.
- **VIX > 35** → Panic. Crisis mode. Major macro event or systemic risk.

**The VIX paradox:** The VIX tends to be lowest right before major crashes — 
because investors are most complacent at market peaks. This is why 
*low VIX is not necessarily good news* — it can signal excessive risk-taking.
""")

# VIX historical chart
vix_events = [
    ("2008-09-15", "Lehman collapse"),
    ("2010-05-06", "Flash Crash"),
    ("2011-08-08", "US debt downgrade"),
    ("2018-02-05", "Volmageddon"),
    ("2020-03-16", "COVID panic"),
    ("2022-03-07", "Ukraine invasion"),
]

fig_vix = go.Figure()

fig_vix.add_hrect(y0=0,   y1=15,  fillcolor="green",  opacity=0.05, line_width=0)
fig_vix.add_hrect(y0=15,  y1=25,  fillcolor="yellow", opacity=0.05, line_width=0)
fig_vix.add_hrect(y0=25,  y1=35,  fillcolor="orange", opacity=0.05, line_width=0)
fig_vix.add_hrect(y0=35,  y1=100, fillcolor="red",    opacity=0.05, line_width=0)

fig_vix.add_trace(go.Scatter(
    x=vix.index,
    y=vix.values,
    mode="lines",
    line=dict(color="#00d4ff", width=1.5),
    name="VIX"
))

for date, label in vix_events:
    ts = pd.Timestamp(date)
    price = vix.asof(ts)
    fig_vix.add_annotation(
        x=ts, y=price,
        text=label,
        showarrow=True,
        arrowhead=2,
        arrowcolor="white",
        font=dict(color="white", size=9),
        bgcolor="rgba(0,0,0,0.6)",
        bordercolor="white",
        borderwidth=1,
    )

fig_vix.add_hline(y=15, line_dash="dash", line_color="green",
                  annotation_text="15 — calm", annotation_position="right")
fig_vix.add_hline(y=25, line_dash="dash", line_color="yellow",
                  annotation_text="25 — stress", annotation_position="right")
fig_vix.add_hline(y=35, line_dash="dash", line_color="red",
                  annotation_text="35 — panic", annotation_position="right")

fig_vix.update_layout(
    yaxis_title="VIX",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=400,
)

st.plotly_chart(fig_vix, use_container_width=True)

st.markdown("""
> **What to look for:** Extended periods of low VIX followed by sudden spikes. 
> The 2017-2018 period is a perfect example — VIX stayed below 12 for months 
> (extreme complacency) before the February 2018 "Volmageddon" event 
> where volatility exploded in a single day, wiping out billions in short-vol strategies.
""")

st.divider()

# --- SECTION 2: CREDIT SPREADS ---

st.subheader("📊 Credit Spreads — The Bond Market's Fear Gauge")
st.markdown("""
While the VIX measures fear in the **equity** market, credit spreads measure fear in the **bond** market. 
They are often considered a more reliable leading indicator of economic stress than the VIX.
""")

@st.cache_data(ttl=3600)
def get_credit_spreads():
    """
    Fetches credit spread data from FRED.
    
    Series:
        BAMLH0A0HYM2  → US High Yield spread (OAS) — junk bonds vs Treasuries
        BAMLC0A0CM    → US Investment Grade spread (OAS) — IG bonds vs Treasuries
    
    OAS = Option-Adjusted Spread — the extra yield investors demand 
    above the risk-free Treasury rate to hold corporate bonds.
    """
    fred = Fred(api_key=st.secrets["FRED_API_KEY"])
    start = "2000-01-01"

    hy = fred.get_series("BAMLH0A0HYM2", observation_start=start).dropna()
    ig = fred.get_series("BAMLC0A0CM",   observation_start=start).dropna()

    return hy, ig

with st.spinner("Loading credit spread data..."):
    hy, ig = get_credit_spreads()

st.markdown("""
### What is a Credit Spread?

When a company wants to borrow money, it issues **bonds**. But unlike the US government, 
companies can go bankrupt — so investors demand a higher interest rate to compensate for that risk.

The **credit spread** is the *extra yield* a company pays above the risk-free Treasury rate. 
It reflects the market's assessment of **default risk**.

**Two main categories:**
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **🟢 Investment Grade (IG)**  
    Companies with strong balance sheets and low default risk.  
    Rated BBB- or above by S&P/Moody's.  
    Examples: Apple, Microsoft, Johnson & Johnson  
    
    IG spreads are typically **0.5% - 2%** above Treasuries.  
    When they widen above 2%, it signals significant stress.
    """)
with col2:
    st.markdown("""
    **🔴 High Yield (HY) — "Junk Bonds"**  
    Companies with higher debt loads and higher default risk.  
    Rated BB+ or below — below investment grade.  
    Examples: Highly leveraged buyouts, distressed companies  
    
    HY spreads are typically **3% - 5%** above Treasuries.  
    When they widen above 8-10%, recession/crisis is usually imminent.
    """)

st.markdown("""
### Why credit spreads are leading indicators

Credit spreads widen **before** unemployment rises and **before** GDP falls — 
because bond investors see corporate stress before it shows up in economic data.

The mechanism:
1. Economy starts slowing → corporate revenues fall
2. Companies have trouble servicing debt → default risk rises
3. Bond investors demand higher spreads → borrowing costs rise
4. Higher borrowing costs → companies cut investment and hiring
5. Unemployment rises → recession confirmed

By the time unemployment is rising, credit spreads already told you 6-12 months earlier.
""")

# Current spread values
current_hy = round(hy.iloc[-1], 2)
current_ig = round(ig.iloc[-1], 2)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("HY Spread", f"{current_hy}%")
with col2:
    st.metric("IG Spread", f"{current_ig}%")
with col3:
    st.metric("HY Signal", "Normal" if current_hy < 5 else "Elevated" if current_hy < 8 else "Crisis")
with col4:
    st.metric("IG Signal", "Normal" if current_ig < 1.5 else "Elevated" if current_ig < 2.5 else "Crisis")
# Credit spreads chart
fig_cs = go.Figure()

fig_cs.add_trace(go.Scatter(
    x=hy.index,
    y=hy.values,
    mode="lines",
    line=dict(color="#ff6b6b", width=1.5),
    name="High Yield Spread"
))

fig_cs.add_trace(go.Scatter(
    x=ig.index,
    y=ig.values,
    mode="lines",
    line=dict(color="#00d4ff", width=1.5),
    name="Investment Grade Spread"
))

fig_cs.add_hline(y=5, line_dash="dash", line_color="orange",
                 annotation_text="HY warning (5%)", annotation_position="right")
fig_cs.add_hline(y=10, line_dash="dash", line_color="red",
                 annotation_text="HY crisis (10%)", annotation_position="right")

fig_cs.update_layout(
    yaxis_title="Spread (%)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_cs, use_container_width=True)

st.markdown("""
> **Key events visible:** The 2008 financial crisis sent HY spreads above 20% — 
> an unprecedented level reflecting genuine fear of systemic collapse. 
> COVID briefly spiked spreads in March 2020 before the Fed's intervention 
> compressed them back rapidly. 
> The current level gives you a real-time read on how stressed credit markets are.
""")

st.divider()

# --- SECTION 3: RISK-ON VS RISK-OFF ---

st.subheader("⚖️ Risk-On vs Risk-Off")
st.markdown("""
One of the most fundamental concepts in macro trading is the **risk-on / risk-off** framework.
It describes the two modes the market oscillates between depending on investor sentiment.
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    ### 🟢 Risk-On
    Investors are confident. They seek higher returns by taking more risk.
    
    **What performs well:**
    - Equities (S&P 500, Nasdaq, Ibovespa)
    - High Yield bonds
    - Emerging market currencies (BRL, MXN, ZAR)
    - Commodities (copper, oil)
    - Crypto
    
    **Macro conditions:**
    - Strong GDP growth
    - Low/falling unemployment
    - Central banks cutting rates
    - Low VIX, tight credit spreads
    """)

with col2:
    st.markdown("""
    ### 🔴 Risk-Off
    Investors are fearful. They flee to safety, accepting lower returns.
    
    **What performs well:**
    - US Treasuries (bonds rally, yields fall)
    - Gold
    - Japanese Yen (JPY)
    - Swiss Franc (CHF)
    - US Dollar (DXY)
    
    **Macro conditions:**
    - Recession fears
    - Rising unemployment
    - Central banks hiking or on hold
    - High VIX, wide credit spreads
    """)

@st.cache_data(ttl=3600)
def get_risk_assets():
    """
    Fetches risk-on and risk-off assets for comparison.
    
    Risk-on:  S&P 500, Ibovespa, Copper
    Risk-off: Gold, 10Y Treasury yield (inverted), DXY
    """
    tickers = {
        "S&P 500 (risk-on)":   "^GSPC",
        "Ibovespa (risk-on)":  "^BVSP",
        "Copper (risk-on)":    "HG=F",
        "Gold (risk-off)":     "GC=F",
        "DXY (risk-off)":      "DX-Y.NYB",
    }

    data = {}
    for name, ticker in tickers.items():
        df = yf.download(ticker, start="2015-01-01", progress=False)
        data[name] = df["Close"].squeeze().dropna()

    return data

with st.spinner("Loading risk assets..."):
    risk_data = get_risk_assets()

# Interactive comparison
selected_risk = st.multiselect(
    "Select assets to compare:",
    options=list(risk_data.keys()),
    default=["S&P 500 (risk-on)", "Gold (risk-off)", "DXY (risk-off)"],
    key="risk_select"
)

start_risk = st.date_input(
    "Start date:",
    value=pd.Timestamp("2018-01-01"),
    min_value=pd.Timestamp("2015-01-01"),
    max_value=pd.Timestamp.today(),
    key="risk_date"
)

fig_risk = go.Figure()
colors = {
    "S&P 500 (risk-on)":  "#00ff88",
    "Ibovespa (risk-on)": "#00d4ff",
    "Copper (risk-on)":   "#ffaa00",
    "Gold (risk-off)":    "#ffd700",
    "DXY (risk-off)":     "#ff6b6b",
}

for name in selected_risk:
    series = risk_data[name]
    series = series[series.index >= pd.Timestamp(start_risk)]
    normalized = (series / series.iloc[0]) * 100

    fig_risk.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized.values,
        mode="lines",
        line=dict(color=colors.get(name, "#ffffff"), width=1.5),
        name=name
    ))

fig_risk.update_layout(
    yaxis_title="Indexed to 100",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("""
> **How to use this chart:** Set the start date to a known risk-off event 
> (e.g. March 2020 COVID crash, September 2022 rate shock) and observe how 
> risk-on assets fell while risk-off assets rallied — or didn't. 
> During the most severe crises, even gold and DXY can correlate temporarily 
> as investors rush to pure cash.
""")
st.divider()

# --- SECTION 4: BRAZIL RISK ---

st.subheader("🇧🇷 Brazil Sovereign Risk")
st.markdown("""
Beyond global sentiment, Brazil has its own specific risk premium — 
reflecting fiscal concerns, political uncertainty, and EM vulnerability.
""")

@st.cache_data(ttl=3600)
def get_brazil_risk():
    fred = Fred(api_key=st.secrets["FRED_API_KEY"])

    us_10y = fred.get_series("DGS10", observation_start="2010-01-01").dropna()

    brl_raw  = yf.download("USDBRL=X", start="2010-01-01", progress=False)
    ibov_raw = yf.download("^BVSP",    start="2010-01-01", progress=False)
    sp_raw   = yf.download("^GSPC",    start="2010-01-01", progress=False)

    brl  = brl_raw["Close"].squeeze().dropna()
    ibov = ibov_raw["Close"].squeeze().dropna()
    sp   = sp_raw["Close"].squeeze().dropna()

    ratio = (ibov / sp.reindex(ibov.index, method="ffill")).dropna()

    return us_10y, brl, ratio

with st.spinner("Loading Brazil risk data..."):
    us_10y, brl, ibov_sp_ratio = get_brazil_risk()

current_us  = round(us_10y.iloc[-1], 2)
current_brl = round(brl.iloc[-1], 4)

st.markdown("""
### What is Sovereign Risk?

**Sovereign risk** is the risk that a country's government will default on its debt. 
It is typically measured by **CDS spreads** or **sovereign bond spreads** vs US Treasuries.

Since Brazil bond data is not reliably available via free APIs, we use two proxies:
- **USD/BRL** — currency weakness signals rising risk perception
- **Ibovespa/S&P ratio** — when Brazil underperforms the US, it signals capital outflows and rising risk

### What drives Brazil's risk premium?
- **Fiscal deficit** — Brazil runs large budget deficits, raising default concerns
- **Political risk** — policy uncertainty and changes in fiscal framework
- **Global risk appetite** — in risk-off periods, EM spreads widen indiscriminately
- **Currency** — BRL weakness increases the real debt burden for foreign investors
""")

col1, col2 = st.columns(2)
with col1:
    st.metric("US 10Y Yield", f"{current_us}%")
with col2:
    st.metric("USD/BRL", current_brl)

# BRL/USD chart
st.markdown("#### USD/BRL — Currency Risk Proxy")
st.markdown("A weaker BRL (higher USD/BRL) signals rising risk perception and capital outflows from Brazil.")

fig_brl = go.Figure()
fig_brl.add_trace(go.Scatter(
    x=brl.index,
    y=brl.values,
    mode="lines",
    line=dict(color="#00ff88", width=1.5),
    name="USD/BRL"
))
fig_brl.update_layout(
    yaxis_title="USD/BRL",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=300,
)
st.plotly_chart(fig_brl, use_container_width=True)

# Ibovespa/S&P ratio
st.markdown("#### Ibovespa / S&P 500 Ratio — Brazil vs US Relative Performance")
st.markdown("""
When this ratio falls, Brazil is underperforming the US — 
typically driven by rising risk perception, capital outflows, or commodity weakness.
When it rises, Brazil is outperforming — often driven by commodity rallies or improving fiscal outlook.
""")

fig_ratio = go.Figure()
fig_ratio.add_trace(go.Scatter(
    x=ibov_sp_ratio.index,
    y=ibov_sp_ratio.values,
    mode="lines",
    line=dict(color="#ffaa00", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(255, 170, 0, 0.1)",
    name="Ibovespa/S&P Ratio"
))
fig_ratio.update_layout(
    yaxis_title="Ratio",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=300,
)
st.plotly_chart(fig_ratio, use_container_width=True)

st.markdown("""
> **What to look for:** BRL weakening while the Ibovespa/S&P ratio falls simultaneously 
> is a strong signal of Brazil-specific stress — capital is leaving both the currency 
> and the equity market at the same time.
""")