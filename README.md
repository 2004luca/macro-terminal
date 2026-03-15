# 📊 Macro Terminal

A personal Bloomberg-inspired macro economics dashboard built with Python and Streamlit.
Real-time data from the Federal Reserve (FRED), Yahoo Finance, and Banco Central do Brasil (BCB).

---

## 🖥️ Overview

Macro Terminal is an **educational and analytical dashboard** that aggregates global macroeconomic 
data into a single interactive interface. It was built to learn both Python and macroeconomics 
simultaneously — every chart comes with explanations of what the indicator means, why it matters, 
and how it affects other markets.

---

## 📄 Pages

| Page | Description |
|------|-------------|
| 🌍 **Home** | Real-time market snapshot, macro indicators (US + Brazil), yield curve shape, and how all indicators connect |
| 📉 **Yield Curve** | Interactive US Treasury yield curve with historical comparison, 2Y-10Y spread, and educational guide to curve shapes |
| 🌐 **Global Macro** | Deep dive into macro indicators for US, Brazil, Europe, UK, Japan, and China — with real interest rates and global comparison |
| 📈 **Markets** | Global equity indices, S&P 500 deep dive with volatility, sector ETF performance, and correlation matrix |
| 💱 **FX & Commodities** | DXY analysis, FX majors, WTI vs Brent oil, commodities dashboard, and quant tools (Z-score, rolling correlations, commodity ratios) |
| 🌡️ **Sentiment & Risk** | VIX fear index, credit spreads (HY vs IG), risk-on vs risk-off framework, and Brazil sovereign risk |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Core language |
| **Streamlit** | Dashboard framework |
| **Plotly** | Interactive charts |
| **Pandas** | Data manipulation |
| **yfinance** | Market data (Yahoo Finance) |
| **fredapi** | Macroeconomic data (Federal Reserve) |
| **python-bcb** | Brazilian economic data (Banco Central do Brasil) |

---

## 📡 Data Sources

- **FRED (Federal Reserve Economic Data)** — Fed Funds Rate, CPI, GDP, unemployment, Treasury yields, credit spreads
- **Yahoo Finance** — Equity indices, FX pairs, commodities, VIX, sector ETFs
- **BCB (Banco Central do Brasil)** — SELIC rate, IPCA inflation, Brazilian GDP

---

## 🚀 Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/2004luca/macro-terminal.git
cd macro-terminal
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your FRED API key

Create a free account at [fred.stlouisfed.org](https://fred.stlouisfed.org) and request an API key.

Create the file `.streamlit/secrets.toml`:
```toml
FRED_API_KEY = "your_api_key_here"
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 📚 What I Learned

### Python
- Fetching and processing data from REST APIs (`requests`, `fredapi`, `yfinance`, `python-bcb`)
- Time series manipulation with `pandas` — resampling, rolling windows, YoY calculations
- Interactive data visualization with `plotly`
- Building multi-page web applications with `Streamlit`
- Caching strategies for performance (`@st.cache_data`)
- Project structure and best practices — separation of concerns, environment variables, `.gitignore`

### Macroeconomics
- How the **yield curve** signals recessions and economic cycles
- The relationship between **Fed policy, inflation, and asset prices**
- How **real interest rates** (nominal rate minus inflation) drive global capital flows
- The mechanics of **credit spreads** as leading indicators of economic stress
- **Cross-asset correlations** — how DXY, gold, oil, equities, and EM currencies interact
- **Sector rotation** and what it signals about the economic cycle
- Japan's **deflation trap** and the Yen carry trade
- Brazil's **risk premium** and its sensitivity to global risk appetite
- Quantitative concepts: **Z-scores**, **rolling correlations**, **commodity ratios**

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Nothing in this dashboard constitutes 
financial advice. All data is sourced from public APIs and may have delays or inaccuracies.

---

## 👤 Author

**Luca Santucci** — built as a learning project to combine Python development with macroeconomics.  
Feel free to fork, contribute, or reach out with suggestions.