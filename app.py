# app.py
# Entry point — Introduction page

import streamlit as st

st.set_page_config(
    page_title="Macro Terminal",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Macro Terminal")
st.markdown("*Your personal Bloomberg — powered by Python and open data*")
st.divider()

# Introduction
st.markdown("""
## Welcome to Macro Terminal

**Macro Terminal** is an open-source, educational macroeconomics dashboard 
that aggregates real-time global economic data into a single interactive interface.

It was built with one goal: to make macroeconomics **accessible, visual, and intuitive** — 
whether you're a student, a trader, or just curious about how the global economy works.

Every chart comes with explanations of what each indicator means, why it matters, 
and how it connects to other markets. This is not just a data dashboard — 
it's a learning tool.
""")

st.divider()
st.info("""
**📌 A few things to know before you start:**

- **Loading times** — this dashboard pulls a large amount of real-time data from multiple APIs. 
Some pages may take 1-2 minutes to load on first visit. Once loaded, data is cached for 1 hour and subsequent visits will be much faster.

- **Brazil data** — Brazilian economic data is sourced directly from the Banco Central do Brasil (BCB). 
Their API occasionally times out. If you see an error on the Brazil tab, simply reload the page and it should work.
""")
# Pages guide
st.subheader("🗺️ How to Navigate")
st.markdown("Use the sidebar on the left to explore each section:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🌍 Home**  
    Real-time snapshot of global markets and macro indicators. 
    Includes the current yield curve shape, US and Brazil key indicators, 
    and a guide explaining how all macro variables connect to each other.
    
    ---
    
    **📉 Yield Curve**  
    The most important indicator in macroeconomics. 
    Compare the US Treasury yield curve across different years, 
    track the 2Y-10Y spread recession indicator, and learn 
    what each curve shape signals about the economy.
    
    ---
    
    **🌐 Global Macro**  
    Deep dive into macroeconomic data for 6 major economies: 
    US, Brazil, Europe, UK, Japan, and China. 
    Includes interest rates, inflation, GDP, unemployment, 
    real interest rates, and a global comparison table.
    """)

with col2:
    st.markdown("""
    **📈 Markets & Equities**  
    Global equity indices, S&P 500 historical analysis with key events annotated, 
    realized volatility, sector ETF performance with rotation signals, 
    and an interactive correlation matrix.
    
    ---
                        
                
    **💱 FX & Commodities**  
    The US Dollar (DXY) and its impact on global markets, 
    major FX pairs with macro drivers explained, 
    WTI vs Brent oil deep dive, commodities dashboard, 
    and quantitative tools: Z-scores, rolling correlations, and commodity ratios.
    
    ---
    
    **🌡️ Sentiment & Risk**  
    How is the market feeling right now? 
    VIX fear index with regime classification, 
    High Yield and Investment Grade credit spreads, 
    risk-on vs risk-off framework with interactive asset comparison, 
    and Brazil sovereign risk indicators.
    """)

st.divider()

# Data sources
st.subheader("📡 Data Sources")
st.markdown("""
All data is fetched in real-time from free, public APIs:

- **FRED (Federal Reserve Economic Data)** — interest rates, inflation, GDP, unemployment, Treasury yields, credit spreads
- **Yahoo Finance** — equity indices, FX pairs, commodities, VIX, sector ETFs  
- **BCB (Banco Central do Brasil)** — SELIC rate, IPCA inflation, Brazilian GDP
""")

st.divider()

# Disclaimer
st.caption("""
⚠️ This dashboard is for educational purposes only. 
Nothing here constitutes financial advice. 
Data is sourced from public APIs and may have delays or inaccuracies.
""")