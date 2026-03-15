# pages/2_yield_curve.py
# Yield Curve page — interactive US Treasury yield curve

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fredapi import Fred


# --- DATA ---

@st.cache_data(ttl=3600)
def get_yield_curve_annual():
    """
    Fetches US Treasury yields sampled once per year.
    Used for curve shape comparison — keeps loading fast.
    Note: for daily precision, a full dataset would be required.
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

    yields = {}
    for label, series_id in maturities.items():
        series = fred.get_series(series_id, observation_start="2000-01-01").dropna()
        # Take one snapshot per year — first business day of each year
        series = series.resample("YS").first().dropna()
        yields[label] = series

    df = pd.DataFrame(yields).dropna()
    df.index = pd.to_datetime(df.index)
    return df


@st.cache_data(ttl=3600)
def get_spread_data():
    """
    Fetches daily 2Y and 10Y yields for the spread chart.
    Only 2 series — loads much faster than full curve data.
    """
    fred = Fred(api_key=st.secrets["FRED_API_KEY"])
    dgs2  = fred.get_series("DGS2",  observation_start="2000-01-01").dropna()
    dgs10 = fred.get_series("DGS10", observation_start="2000-01-01").dropna()

    df = pd.DataFrame({"2Y": dgs2, "10Y": dgs10}).dropna()
    df.index = pd.to_datetime(df.index)
    df["Spread"] = df["10Y"] - df["2Y"]
    return df


# --- PAGE LAYOUT ---

st.title("📉 Yield Curve")
st.markdown("""
The yield curve is one of the most powerful tools in macroeconomics. 
It shows the interest rates on US government bonds across different maturities — 
from 1 month to 30 years — and its shape tells us a lot about where the economy is headed.
""")
st.divider()


# --- SECTION 1: CURVE COMPARISON ---

st.subheader("📊 Yield Curve Comparison")
st.markdown("""
Select two years to compare how the yield curve has shifted over time.  
Each dot represents the yield investors demanded for lending money to the US government 
for that specific period.

> ⚠️ **Note:** To keep this tool fast, we display one snapshot per year 
> (first available trading day of January). A full daily dataset would require 
> significantly longer loading times.
""")

df_annual = get_yield_curve_annual()
available_years = df_annual.index.year.tolist()

col1, col2 = st.columns(2)
with col1:
    year_a = st.selectbox("📅 Year A", options=available_years[::-1], index=0)
with col2:
    year_b = st.selectbox("📅 Year B", options=available_years[::-1], index=5)

row_a = df_annual[df_annual.index.year == year_a].iloc[0]
row_b = df_annual[df_annual.index.year == year_b].iloc[0]
date_a = df_annual[df_annual.index.year == year_a].index[0].strftime("%B %d, %Y")
date_b = df_annual[df_annual.index.year == year_b].index[0].strftime("%B %d, %Y")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=list(row_a.index),
    y=list(row_a.values),
    mode="lines+markers",
    line=dict(color="#00d4ff", width=2),
    marker=dict(size=8),
    name=f"{year_a} ({date_a})"
))

fig.add_trace(go.Scatter(
    x=list(row_b.index),
    y=list(row_b.values),
    mode="lines+markers",
    line=dict(color="#ff6b6b", width=2, dash="dash"),
    marker=dict(size=8),
    name=f"{year_b} ({date_b})"
))

fig.update_layout(
    xaxis_title="Maturity",
    yaxis_title="Yield (%)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()


# --- SECTION 2: 2Y-10Y SPREAD ---

st.subheader("📈 2Y-10Y Spread — Recession Indicator")
st.markdown("""
The **2Y-10Y spread** is the difference between the 10-year and 2-year Treasury yields.
It is the single most watched recession indicator in macroeconomics.

- **Positive spread** → normal curve, long-term yields higher than short-term
- **Negative spread (inversion)** → short-term yields higher than long-term ⚠️

**Why does inversion signal recession?**  
When short-term rates exceed long-term rates, banks become less profitable — 
they borrow short and lend long, so their margin shrinks. 
This leads to tighter credit conditions, less lending, less investment, 
and ultimately slower economic growth.

Every US recession in the last 50 years was preceded by a yield curve inversion.
""")

df_spread = get_spread_data()
spread = df_spread["Spread"]

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=spread.index,
    y=spread.values,
    mode="lines",
    line=dict(color="#00d4ff", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(0, 212, 255, 0.1)",
    name="2Y-10Y Spread"
))

fig2.add_hline(
    y=0,
    line_dash="dash",
    line_color="red",
    annotation_text="Inversion threshold",
    annotation_position="bottom right"
)

fig2.update_layout(
    xaxis_title="Date",
    yaxis_title="Spread (%)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
)

st.plotly_chart(fig2, use_container_width=True)

current_spread = round(spread.iloc[-1], 2)
if current_spread < 0:
    st.error(f"⚠️ Current 2Y-10Y Spread: **{current_spread}%** — Curve is INVERTED")
else:
    st.success(f"✅ Current 2Y-10Y Spread: **{current_spread}%** — Curve is normal")

st.divider()


# --- SECTION 3: YIELD CURVE SHAPES ---

st.subheader("📚 Understanding Yield Curve Shapes")
st.markdown("""
The yield curve doesn't always look the same. Its shape changes depending on 
what investors expect about the future of the economy and interest rates.
There are three main shapes you need to know:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🟢 Normal")
    st.markdown("""
    **Short-term yields < Long-term yields**
    
    The healthy default state. Investors demand higher return 
    for locking up money longer — this is the **term premium**.
    
    **What it signals:**
    - Economy is growing
    - Inflation is under control
    - No immediate recession expected
    
    **Example:** 2010–2021, post-crisis recovery.
    """)

with col2:
    st.markdown("### 🟡 Flat")
    st.markdown("""
    **Short-term yields ≈ Long-term yields**
    
    Flattens when the Fed raises short-term rates while 
    long-term rates stay anchored — market expects rate cuts ahead.
    
    **What it signals:**
    - Transition period
    - Uncertainty about growth
    - Often a warning before inversion
    
    **Example:** Mid-2019 and early 2022.
    """)

with col3:
    st.markdown("### 🔴 Inverted")
    st.markdown("""
    **Short-term yields > Long-term yields**
    
    Investors expect the Fed to cut rates — usually because 
    they anticipate a recession. The most watched recession signal in macro.
    
    **What it signals:**
    - Market pricing in economic slowdown
    - Fed likely to cut rates ahead
    - Preceded every US recession historically
    
    **Example:** 2006–2007, 2022–2024.
    """)