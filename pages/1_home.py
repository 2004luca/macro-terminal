# pages/1_home.py
# Home page — global snapshot of markets and macro indicators

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import xml.etree.ElementTree as ET
from fredapi import Fred


# --- DATA FUNCTIONS ---
@st.cache_data(ttl=3600)
def get_brazil_indicators():
    """
    Fetches key Brazilian macro indicators from the BCB (Banco Central do Brasil).
    
    Series used:
        432  → SELIC rate (% per year)
        433  → IPCA (monthly inflation)
        1    → BRL/USD exchange rate
    """
    from bcb import sgs
    import datetime

    end = datetime.date.today()
    start = datetime.date(2024, 1, 1)

    selic = sgs.get({"SELIC": 432}, start=start, end=end).dropna()
    ipca  = sgs.get({"IPCA": 433},  start=start, end=end).dropna()

    selic_value = round(selic["SELIC"].iloc[-1], 2)
    ipca_12m    = round(ipca["IPCA"].tail(12).sum(), 2)  # last 12 months accumulated

    rows = []

    low, high = 8.0, 12.0
    signal = "🟢" if selic_value < low else "🟡" if selic_value < high else "🔴"
    rows.append({"Indicator": f"{signal} SELIC Rate", "Value": f"{selic_value}%"})

    low, high = 3.0, 5.0
    signal = "🟢" if ipca_12m < low else "🟡" if ipca_12m < high else "🔴"
    rows.append({"Indicator": f"{signal} IPCA (12m)", "Value": f"{ipca_12m}%"})

    return pd.DataFrame(rows)

def get_market_snapshot():
    """
    Fetches current price and daily change for major assets.
    Data source: Yahoo Finance (no API key required)
    """
    tickers = {
        "S&P 500":   "^GSPC",
        "Ibovespa":  "^BVSP",
        "DXY":       "DX-Y.NYB",
        "BRL/USD":   "USDBRL=X",
        "EUR/USD":   "EURUSD=X",
        "Gold":      "GC=F",
        "Oil (WTI)": "CL=F",
    }

    rows = []
    for name, ticker in tickers.items():
        data = yf.Ticker(ticker)
        info = data.fast_info

        price = round(info.last_price, 2)
        prev = round(info.previous_close, 2)
        change_pct = round((price - prev) / prev * 100, 2)

        rows.append({
            "Asset":      name,
            "Price":      f"{price:,.2f}",
            "Prev Close": f"{prev:,.2f}",
            "Change %":   f"{change_pct:+.2f}%",
        })

    return pd.DataFrame(rows)


def get_macro_indicators():
    """
    Fetches key macro indicators from FRED.
    Returns a DataFrame with name, value and a traffic light signal.
    """
    fred = Fred(api_key=st.secrets["FRED_API_KEY"])

    indicators = [
        {"name": "Fed Funds Rate", "id": "FEDFUNDS", "unit": "%", "thresholds": (3.0, 5.0)},
        {"name": "CPI (US Inflation)", "id": "CPIAUCSL", "unit": "%", "thresholds": (2.5, 4.0), "yoy": True},
        {"name": "Unemployment (US)", "id": "UNRATE", "unit": "%", "thresholds": (4.5, 6.0)},
    ]

    rows = []
    for ind in indicators:
        series = fred.get_series(ind["id"]).dropna()

        if ind.get("yoy"):
            value = round((series.iloc[-1] / series.iloc[-13] - 1) * 100, 2)
        else:
            value = round(series.iloc[-1], 2)

        low, high = ind["thresholds"]
        if value < low:
            signal = "🟢"
        elif value < high:
            signal = "🟡"
        else:
            signal = "🔴"

        rows.append({
            "Indicator": f"{signal} {ind['name']}",
            "Value": f"{value}{ind['unit']}",
        })

    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def get_current_yield_curve():
    """
    Fetches only the most recent yield for each maturity.
    Only fetches data from 2026 onwards — very fast to load.
    """
    fred = Fred(api_key=st.secrets["FRED_API_KEY"])

    maturities = {
        "1M":  "DGS1MO",
        "3M":  "DGS3MO",
        "6M":  "DGS6MO",
        "1Y":  "DGS1",
        "2Y":  "DGS2",
        "5Y":  "DGS5",
        "7Y":  "DGS7",
        "10Y": "DGS10",
        "20Y": "DGS20",
        "30Y": "DGS30",
    }

    latest = {}
    for label, series_id in maturities.items():
        series = fred.get_series(series_id, observation_start="2026-01-01").dropna()
        latest[label] = series.iloc[-1]

    return latest


# --- PAGE LAYOUT ---

st.title("🌍 Market Overview")
st.markdown("Real-time snapshot of global markets and macro indicators.")
st.divider()

# Two columns: left = market snapshot, right = macro indicators
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📈 Market Snapshot")
    with st.spinner("Loading market data..."):
        df = get_market_snapshot()

    def color_change(val):
        if "+" in str(val):
            return "color: green"
        elif "-" in str(val):
            return "color: red"
        return ""

    styled_df = df.style.applymap(color_change, subset=["Change %"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("🚦 Macro Indicators")
    with st.spinner("Loading macro data..."):
        macro_df = get_macro_indicators()
    st.dataframe(macro_df, use_container_width=True, hide_index=True)
    st.markdown("**🇧🇷 Brazil**")
    with st.spinner("Loading Brazil data..."):
        brazil_df = get_brazil_indicators()
    st.dataframe(brazil_df, use_container_width=True, hide_index=True)

st.divider()

# --- YIELD CURVE TODAY ---

st.subheader("📉 Yield Curve — Today")
st.markdown("""
The yield curve shows the interest rate the US government pays to borrow money 
for different time periods — from 1 month to 30 years.  
Its shape is one of the most powerful signals in macroeconomics.
""")

with st.spinner("Loading yield curve..."):
    current_curve = get_current_yield_curve()

maturities = list(current_curve.keys())
yields = list(current_curve.values())

spread = round(current_curve["10Y"] - current_curve["2Y"], 2)
if spread < 0:
    curve_shape = "🔴 Inverted"
    curve_note = "Short-term yields are higher than long-term — the market is pricing in an economic slowdown ahead."
elif spread < 0.5:
    curve_shape = "🟡 Flat"
    curve_note = "Short and long-term yields are close together — the market is uncertain about the direction of the economy."
else:
    curve_shape = "🟢 Normal"
    curve_note = "Long-term yields are higher than short-term — the economy is expected to keep growing."

fig_curve = go.Figure()

fig_curve.add_trace(go.Scatter(
    x=maturities,
    y=yields,
    mode="lines+markers",
    line=dict(color="#00d4ff", width=2),
    marker=dict(size=8),
    name="Current Yield Curve"
))

fig_curve.update_layout(
    xaxis_title="Maturity",
    yaxis_title="Yield (%)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=300,
)

st.plotly_chart(fig_curve, use_container_width=True)

st.markdown(f"""
**Current curve shape: {curve_shape}**  
{curve_note}  
→ For a deeper analysis, visit the **Yield Curve** page.
""")

st.divider()

# --- HOW EVERYTHING CONNECTS ---

st.subheader("🔗 How Everything Connects")
st.markdown("""
Markets don't move in isolation. Every indicator affects others — 
understanding these relationships is the foundation of macro thinking.
""")

with st.expander("💵 Dollar (DXY) → Brazilian Real (BRL/USD)"):
    st.markdown("""
    **The relationship:** When the DXY strengthens, the BRL typically weakens — meaning more reais per dollar.

    **Why it happens:**  
    Brazil is an emerging market and commodity exporter. When the dollar strengthens globally, 
    two things happen simultaneously:
    
    1. **Capital flight** — investors sell emerging market assets (including Brazilian stocks and bonds) 
    and move money back to US dollar assets, which are seen as safer. This selling pressure weakens the BRL.
    
    2. **Commodity channel** — commodities like oil, iron ore and soybeans are priced in dollars. 
    A stronger dollar makes commodities cheaper in dollar terms, which reduces Brazil's export revenues 
    and puts further pressure on the real.

    **Who gets affected:**  
    - Brazilian importers pay more in reais for goods priced in dollars
    - Inflation rises as import costs increase
    - The BCB (Brazil's central bank) may need to raise the SELIC rate to attract foreign capital and defend the currency
    - Brazilian companies with dollar-denominated debt see their liabilities increase in local currency terms
    """)

with st.expander("🛢️ Oil Price → Inflation → Interest Rates → Stock Market"):
    st.markdown("""
    **The relationship:** Rising oil prices trigger a chain reaction across the entire economy.

    **Why it happens:**  
    Oil is an input cost for almost everything — transportation, manufacturing, agriculture, plastics. 
    When oil becomes more expensive, production costs rise across the board, and companies pass those 
    costs to consumers through higher prices.

    **The chain:**
    
    1. **Oil rises** → energy costs increase for businesses and consumers
    2. **Inflation rises** → CPI and PPI move up as costs are passed through
    3. **Central banks react** → Fed and BCB raise interest rates to cool inflation
    4. **Higher rates hurt stocks** → future earnings are discounted at a higher rate, 
    making stocks less attractive relative to bonds. Growth stocks (tech) are hit hardest.
    5. **Economy slows** → higher borrowing costs reduce consumer spending and business investment

    **The exception:** Oil-exporting countries (like Brazil, Saudi Arabia, Norway) can benefit 
    from higher oil prices through increased export revenues — which is why Petrobras and the 
    Ibovespa sometimes rally when oil spikes, while the S&P 500 falls.
    """)

with st.expander("📈 Fed Interest Rates → Global Markets"):
    st.markdown("""
    **The relationship:** When the Fed raises rates, it doesn't just affect the US — 
    it moves markets around the entire world.

    **Why it happens:**  
    The US dollar is the world's reserve currency. US Treasury bonds are the global 
    risk-free benchmark. When the Fed raises rates, Treasuries become more attractive, 
    pulling capital from everywhere else.

    **The chain:**
    
    1. **Fed raises rates** → US Treasuries offer higher yield
    2. **Global capital flows to USD** → dollar strengthens (DXY rises)
    3. **Emerging markets suffer** → capital leaves Brazil, India, Mexico etc. 
    Their currencies weaken and their stock markets fall
    4. **Gold falls** → gold pays no yield, so it becomes less attractive when 
    risk-free rates rise
    5. **Tech stocks fall** → high-growth companies are valued on future cash flows. 
    Higher discount rates reduce the present value of those future earnings

    **The reverse is also true:** When the Fed cuts rates, capital flows back into 
    emerging markets, gold rallies, and growth stocks outperform.
    """)

with st.expander("📊 Yield Curve Inversion → Recession"):
    st.markdown("""
    **The relationship:** When short-term Treasury yields exceed long-term yields, 
    a recession typically follows within 12-18 months.

    **Why it happens:**  
    Banks borrow at short-term rates (from deposits and money markets) and lend at 
    long-term rates (mortgages, business loans). When the curve inverts, this model 
    breaks down — banks can't profit from lending, so they lend less.

    **The chain:**
    
    1. **Curve inverts** → bank lending margins turn negative
    2. **Credit tightens** → banks become more selective, loan conditions worsen
    3. **Investment falls** → businesses can't borrow cheaply to expand
    4. **Consumer spending slows** → mortgages and car loans become more expensive
    5. **Economy contracts** → GDP growth slows, unemployment rises, recession begins

    **Important caveat:** The inversion predicts recession but not the timing. 
    The lag between inversion and recession has historically been 6 to 24 months. 
    The curve can also stay inverted for extended periods before the recession materializes.
    """)

with st.expander("🇧🇷 SELIC Rate → Ibovespa"):
    st.markdown("""
    **The relationship:** When Brazil's central bank (BCB) raises the SELIC rate, 
    the Ibovespa tends to fall — and vice versa.

    **Why it happens:**  
    In Brazil, the SELIC rate competes directly with equity returns. 
    Brazilian fixed income instruments (like Tesouro Direto) are indexed to SELIC 
    and are seen as virtually risk-free. When SELIC is high, investors ask: 
    *why take equity risk when I can earn 13%+ risk-free?*

    **The mechanism:**
    
    1. **BCB raises SELIC** → fixed income yields become very attractive
    2. **Capital rotates out of equities** → investors sell stocks and buy bonds
    3. **Ibovespa falls** → reduced demand for Brazilian stocks
    4. **Valuations compress** → higher discount rates reduce the present value of company earnings
    5. **Credit becomes expensive** → Brazilian companies pay more to borrow, reducing profits

    **The Brazilian context:**  
    Brazil has historically had one of the highest real interest rates in the world. 
    This makes the SELIC-equity tradeoff especially pronounced compared to developed markets, 
    where rates are typically much lower and the competition between bonds and stocks is less intense.
    """)