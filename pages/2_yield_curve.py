# pages/2_yield_curve.py
# Yield Curve page — interactive US Treasury yield curve

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fredapi import Fred


# --- DATA ---

@st.cache_data(ttl=3600)
def get_yield_curve():
    """
    Fetches US Treasury yields from FRED.
    
    @st.cache_data → caches the result for 1 hour (3600 seconds)
    This avoids hitting the API every time the page reloads.
    
    Maturities fetched:
        DGS1MO → 1M | DGS3MO → 3M | DGS6MO → 6M
        DGS1 → 1Y   | DGS2 → 2Y   | DGS5 → 5Y
        DGS7 → 7Y   | DGS10 → 10Y | DGS20 → 20Y | DGS30 → 30Y
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
        series = fred.get_series(series_id).dropna()
        yields[label] = series

    df = pd.DataFrame(yields)
    df.index = pd.to_datetime(df.index)
    df = df.dropna()

    return df


def get_spread_2y10y(df):
    """
    Calculates the 2y-10y spread over time.
    Negative = inverted curve = recession signal.
    """
    return df["10Y"] - df["2Y"]


# --- PAGE LAYOUT ---

st.title("📉 Yield Curve")
st.markdown("US Treasury yield curve — the most important macro indicator.")
st.divider()

with st.spinner("Loading yield curve data..."):
    df = get_yield_curve()
    spread = get_spread_2y10y(df)

# --- SECTION 1: CURRENT CURVE ---

latest = df.iloc[-1]
latest_date = df.index[-1].strftime("%B %d, %Y")

st.subheader(f"Current Yield Curve — {latest_date}")

# Date picker for historical comparison
compare_date = st.date_input(
    "📅 Compare with historical date:",
    value=pd.Timestamp("2020-01-01"),
    min_value=df.index[0].date(),
    max_value=df.index[-1].date(),
)

# Find the closest available date in the dataset
compare_ts = pd.Timestamp(compare_date)
closest_idx = df.index.get_indexer([compare_ts], method="nearest")[0]
compare_row = df.iloc[closest_idx]
compare_label = df.index[closest_idx].strftime("%B %d, %Y")

# Build comparison chart
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=list(latest.index),
    y=list(latest.values),
    mode="lines+markers",
    line=dict(color="#00d4ff", width=2),
    marker=dict(size=8),
    name=f"Current ({latest_date})"
))

fig.add_trace(go.Scatter(
    x=list(compare_row.index),
    y=list(compare_row.values),
    mode="lines+markers",
    line=dict(color="#ff6b6b", width=2, dash="dash"),
    marker=dict(size=8),
    name=f"Historical ({compare_label})"
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

st.subheader("📊 2Y-10Y Spread — Recession Indicator")
st.markdown("""
The **2Y-10Y spread** is the difference between the 10-year and 2-year Treasury yields.  
- **Positive** → normal curve, healthy economy  
- **Negative** → inverted curve, recession signal ⚠️  

Every US recession in the last 50 years was preceded by an inversion.
""")

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

# Zero line — the inversion threshold
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

# Current spread value
current_spread = round(spread.iloc[-1], 2)
if current_spread < 0:
    st.error(f"⚠️ Current 2Y-10Y Spread: **{current_spread}%** — Curve is INVERTED")
else:
    st.success(f"✅ Current 2Y-10Y Spread: **{current_spread}%** — Curve is normal")