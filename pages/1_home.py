# pages/1_home.py
# Home page — global snapshot of markets and macro indicators

import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from fredapi import Fred


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
    Returns a list of dicts with name, value and a traffic light color.

    Thresholds:
        Fed Funds Rate → green < 3%, yellow < 5%, red >= 5%
        CPI            → green < 2.5%, yellow < 4%, red >= 4%
        Unemployment   → green < 4.5%, yellow < 6%, red >= 6%
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
            # CPI is a level — we calculate year-over-year % change
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


def get_market_news():
    """
    Fetches latest financial news from Yahoo Finance RSS feed.
    RSS is a free, no-auth-required news format.
    Returns a list of dicts with title and link.
    """
    url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^BVSP&region=US&lang=en-US"
    try:
        response = requests.get(url, timeout=5)
        root = ET.fromstring(response.content)
        items = root.findall("./channel/item")

        news = []
        for item in items[:6]:  # show only 6 latest headlines
            title = item.find("title").text
            link = item.find("link").text
            news.append({"title": title, "link": link})

        return news
    except:
        return []


# --- PAGE LAYOUT ---

st.title("🌍 Market Overview")
st.markdown("Real-time snapshot of global markets and macro indicators.")
st.divider()

# Two columns: left = market snapshot, right = macro + news
col_left, col_right = st.columns([1.5, 1])

# --- LEFT COLUMN ---
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

# --- RIGHT COLUMN ---
with col_right:

    # Macro Indicators
    st.subheader("🚦 Macro Indicators")
    with st.spinner("Loading macro data..."):
        macro_df = get_macro_indicators()
    st.dataframe(macro_df, use_container_width=True, hide_index=True)

    st.divider()

    # Latest News
    st.subheader("📰 Latest News")
    with st.spinner("Loading news..."):
        news = get_market_news()

    if news:
        for item in news:
            st.markdown(f"• [{item['title']}]({item['link']})")
    else:
        st.info("News unavailable at the moment.")