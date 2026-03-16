# pages/5_fx_commodities.py
# FX & Commodities page

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import numpy as np


# --- DATA FUNCTIONS ---

@st.cache_data(ttl=3600)
def get_fx_data():
    """
    Fetches FX and commodity price history via Yahoo Finance.
    
    Tickers:
        DX-Y.NYB → DXY (US Dollar Index)
        USDBRL=X → USD/BRL
        EURUSD=X → EUR/USD
        USDJPY=X → USD/JPY
        GBPUSD=X → GBP/USD
    """
    tickers = {
        "DXY":     "DX-Y.NYB",
        "USD/BRL": "USDBRL=X",
        "EUR/USD": "EURUSD=X",
        "USD/JPY": "USDJPY=X",
        "GBP/USD": "GBPUSD=X",
    }

    data = {}
    for name, ticker in tickers.items():
        df = yf.download(ticker, start="2000-01-01", progress=False)
        data[name] = df["Close"].squeeze().dropna()

    return data

@st.cache_data(ttl=3600)
def get_commodity_data():
    """
    Fetches commodity price history via Yahoo Finance.
    
    Tickers:
        GC=F  → Gold (futures)
        SI=F  → Silver (futures)
        CL=F  → WTI Crude Oil (futures)
        BZ=F  → Brent Crude Oil (futures)
        HG=F  → Copper (futures)
        NG=F  → Natural Gas (futures)
    """
    tickers = {
        "Gold":        "GC=F",
        "Silver":      "SI=F",
        "WTI Oil":     "CL=F",
        "Brent Oil":   "BZ=F",
        "Copper":      "HG=F",
        "Natural Gas": "NG=F",
    }

    data = {}
    for name, ticker in tickers.items():
        df = yf.download(ticker, start="2000-01-01", progress=False)
        data[name] = df["Close"].squeeze().dropna()

    return data


# --- PAGE LAYOUT ---

st.title("💱 FX & Commodities")
st.markdown("""
Foreign exchange and commodities are the backbone of the global economy. 
They move before equities, signal inflation before CPI data, and reflect 
geopolitical risk in real time. Understanding them is essential for any macro trader.
""")
st.divider()

with st.spinner("Loading FX and commodity data..."):
    fx_data = get_fx_data()
    comm_data = get_commodity_data()

# --- SECTION 1: DXY ---

st.subheader("💵 The US Dollar (DXY)")
st.markdown("""
The **DXY (US Dollar Index)** measures the value of the US dollar against a basket 
of 6 major currencies: Euro (57.6%), Japanese Yen (13.6%), British Pound (11.9%), 
Canadian Dollar (9.1%), Swedish Krona (4.2%), and Swiss Franc (3.6%).

**Why the dollar is the most important price in the world:**

The US dollar is the world's **reserve currency** — roughly 60% of global foreign exchange 
reserves are held in dollars, and most international trade (especially commodities) is 
priced in dollars. This gives the US extraordinary power: when the Fed moves, 
the entire world feels it.

**How DXY affects everything else:**
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **🟡 Commodities**  
    DXY up → commodities down  
    Since oil and gold are priced in USD, 
    a stronger dollar makes them more expensive 
    for foreign buyers — reducing demand.
    """)
with col2:
    st.markdown("""
    **🔴 Emerging Markets**  
    DXY up → EM currencies weaken  
    Capital flows back to USD assets. 
    Countries with USD-denominated debt 
    see their debt burden increase.
    """)
with col3:
    st.markdown("""
    **🟢 US Multinationals**  
    DXY up → earnings headwind  
    US companies earn revenue abroad. 
    A strong dollar means those foreign 
    revenues are worth less when converted back.
    """)

# DXY chart with Fed events
dxy = fx_data["DXY"]

fed_events = [
    ("2004-06-30", "Fed starts hiking"),
    ("2007-09-18", "Fed starts cutting"),
    ("2015-12-16", "Fed first hike post-GFC"),
    ("2018-12-19", "Fed pauses hiking"),
    ("2022-03-16", "Fed hiking cycle 2022"),
    ("2024-09-18", "Fed starts cutting 2024"),
]

fig_dxy = go.Figure()
fig_dxy.add_trace(go.Scatter(
    x=dxy.index,
    y=dxy.values,
    mode="lines",
    line=dict(color="#00d4ff", width=1.5),
    name="DXY"
))

if len(dxy) > 0:
    for date, label in fed_events:
        try:
            ts = pd.Timestamp(date)
            if ts < dxy.index[0] or ts > dxy.index[-1]:
                continue
            price = dxy.asof(ts)
            if pd.isna(price):
                continue
            fig_dxy.add_annotation(
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
        except Exception:
            continue

fig_dxy.update_layout(
    yaxis_title="DXY",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=400,
)

st.plotly_chart(fig_dxy, use_container_width=True)
st.divider()

# --- SECTION 2: FX MAJORS ---

st.subheader("🌐 FX Majors")
st.markdown("""
Each currency pair tells a different macro story. Understanding what drives 
each pair is essential for cross-asset macro analysis.
""")

# YTD table
fx_pairs = ["USD/BRL", "EUR/USD", "USD/JPY", "GBP/USD"]

fx_rows = []
for name in fx_pairs:
    series = fx_data[name]
    current_year = series.index[-1].year
    start_price = series[series.index.year == current_year].iloc[0]
    current = series.iloc[-1]
    ytd = round((current / start_price - 1) * 100, 2)
    fx_rows.append({
        "Pair":    name,
        "Current": round(current, 4),
        "YTD (%)": f"{ytd:+.2f}%",
    })

df_fx = pd.DataFrame(fx_rows)

def color_ytd(val):
    if "+" in str(val):
        return "color: green"
    elif "-" in str(val):
        return "color: red"
    return ""

st.dataframe(
    df_fx.style.applymap(color_ytd, subset=["YTD (%)"]),
    use_container_width=True,
    hide_index=True
)

# Historical chart
selected_fx = st.multiselect(
    "Select pairs to display:",
    options=fx_pairs,
    default=["USD/BRL", "EUR/USD"],
    key="fx_select"
)

start_fx = st.date_input(
    "Start date:",
    value=pd.Timestamp("2015-01-01"),
    min_value=pd.Timestamp("2000-01-01"),
    max_value=pd.Timestamp.today(),
    key="fx_date"
)

fig_fx = go.Figure()
for name in selected_fx:
    series = fx_data[name]
    series = series[series.index >= pd.Timestamp(start_fx)]
    normalized = (series / series.iloc[0]) * 100

    fig_fx.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized.values,
        mode="lines",
        name=name
    ))

fig_fx.update_layout(
    yaxis_title="Indexed to 100",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=350,
)

st.plotly_chart(fig_fx, use_container_width=True)

# Pair explanations
st.markdown("#### What drives each pair?")

col1, col2 = st.columns(2)

with col1:
    with st.expander("🇧🇷 USD/BRL — Dollar vs Brazilian Real"):
        st.markdown("""
        The BRL is one of the most volatile EM currencies. Its key drivers:
        
        - **DXY** — a stronger dollar weakens the real almost mechanically
        - **Commodity prices** — Brazil exports iron ore, soybeans, oil. Higher commodity prices strengthen BRL
        - **SELIC vs Fed spread** — when Brazil's real rate advantage shrinks, capital flows out
        - **Fiscal risk** — Brazil's high debt and political uncertainty create a permanent risk premium
        - **Risk appetite** — in risk-off environments, investors flee EM including Brazil
        
        The BRL is often used as a **barometer of global risk appetite** — 
        when it weakens sharply, it signals broader EM stress.
        """)

    with st.expander("💶 EUR/USD — Euro vs Dollar"):
        st.markdown("""
        The most traded currency pair in the world — ~24% of all FX volume.
        
        - **Interest rate differential** — when Fed rates exceed ECB rates, USD strengthens vs EUR
        - **European growth** — weak European GDP weighs on EUR
        - **Energy dependence** — Europe imports most of its energy. Energy price spikes hurt EUR
        - **Safe haven flows** — in crises, USD strengthens as the ultimate safe haven
        
        The parity level (1.00) was breached in 2022 for the first time in 20 years — 
        driven by the energy crisis and aggressive Fed hiking vs cautious ECB.
        """)

with col2:
    with st.expander("🇯🇵 USD/JPY — Dollar vs Japanese Yen"):
        st.markdown("""
        One of the most macro-sensitive pairs in the world.
        
        - **Rate differential** — with BOJ at near-zero for decades, USD/JPY tracked US rates almost perfectly
        - **Carry trade** — investors borrowed cheap yen to buy USD assets. When this unwinds, JPY strengthens sharply
        - **Safe haven** — JPY is a safe haven currency. In crises, investors repatriate to Japan, strengthening JPY
        - **BOJ intervention** — Japan intervenes in FX markets more than any other developed nation
        
        The 2022-2024 period saw USD/JPY hit 160 — a 30-year high — 
        as the Fed hiked aggressively while BOJ stayed at zero.
        The subsequent BOJ rate hike triggered a violent yen strengthening in 2024.
        """)

    with st.expander("🇬🇧 GBP/USD — British Pound vs Dollar"):
        st.markdown("""
        Known as **"Cable"** — named after the transatlantic telegraph cable 
        that transmitted rates between London and New York in the 19th century.
        
        - **BoE vs Fed differential** — same framework as EUR/USD
        - **Brexit premium** — GBP has traded at a permanent discount since 2016 
        reflecting structural uncertainty about UK's economic relationship with Europe
        - **UK current account deficit** — the UK runs a large trade deficit, 
        requiring constant capital inflows to fund it. Weakens in risk-off environments.
        
        The Liz Truss mini-budget of September 2022 sent GBP/USD to 1.035 — 
        its lowest level ever, briefly approaching parity with the dollar.
        """)
st.divider()

# --- SECTION 3: OIL ---

st.subheader("🛢️ Oil — WTI vs Brent")
st.markdown("""
Oil is the most geopolitically sensitive commodity in the world. 
Understanding the difference between WTI and Brent — and what moves them — 
is essential macro knowledge.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🇺🇸 WTI (West Texas Intermediate)
    
    - **Origin:** Cushing, Oklahoma, USA
    - **Quality:** API gravity ~40°, sulfur ~0.24% — the lightest and sweetest of the two, easiest to refine into gasoline. Commands a quality premium in refining.
    - **Benchmark for:** North American oil market
    - **Traded on:** NYMEX (New York Mercantile Exchange)
    - **Ticker:** CL=F
    
    WTI is the primary benchmark for US oil production. 
    Its price is heavily influenced by **US inventory data** 
    (published weekly by the EIA) and **US shale production**.
    """)

with col2:
    st.markdown("""
    ### 🌍 Brent Crude
    
    - **Origin:** North Sea (UK/Norway)
    - **Quality:** API gravity ~38°, sulfur ~0.37% — slightly heavier and higher sulfur than WTI,but still classified as light sweet crude. The global pricing standard despite being slightly lower quality than WTI.
    - **Benchmark for:** ~70% of global oil trade
    - **Traded on:** ICE (Intercontinental Exchange, London)
    - **Ticker:** BZ=F
    
    Brent is the **global benchmark** — most international oil contracts 
    reference Brent. It's more sensitive to **Middle East geopolitics** 
    and **OPEC decisions** than WTI.
    """)

# WTI vs Brent chart
wti   = comm_data["WTI Oil"]
brent = comm_data["Brent Oil"]

fig_oil = go.Figure()

fig_oil.add_trace(go.Scatter(
    x=wti.index, y=wti.values,
    mode="lines",
    line=dict(color="#00d4ff", width=1.5),
    name="WTI"
))

fig_oil.add_trace(go.Scatter(
    x=brent.index, y=brent.values,
    mode="lines",
    line=dict(color="#ff6b6b", width=1.5),
    name="Brent"
))

fig_oil.update_layout(
    yaxis_title="Price (USD/barrel)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=350,
)

spread_oil = (brent - wti.reindex(brent.index, method="ffill")).dropna()
spread_oil = spread_oil[spread_oil.index >= "2007-01-01"]

# WTI-Brent spread
spread_oil = (brent - wti.reindex(brent.index, method="ffill")).dropna()

st.markdown("#### WTI-Brent Spread")
st.markdown("""
The **WTI-Brent spread** reflects the price differential between the two benchmarks.
Normally Brent trades at a small premium to WTI (~$2-5) because it has 
better access to global shipping routes.

**When the spread widens:**
- US oversupply (shale boom) → WTI falls relative to Brent
- Middle East tensions → Brent rises on geopolitical risk premium
- Pipeline/infrastructure constraints in the US → WTI gets stuck inland

**The 2011-2013 anomaly:** The US shale revolution flooded Cushing with oil 
while export restrictions prevented it leaving the US. 
WTI traded at a massive discount to Brent — up to $25/barrel.
The spread normalized after US lifted crude export restrictions in 2015.
""")

fig_spread = go.Figure()
fig_spread.add_trace(go.Scatter(
    x=spread_oil.index,
    y=spread_oil.values,
    mode="lines",
    line=dict(color="#ffaa00", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(255, 170, 0, 0.1)",
    name="Brent - WTI"
))
fig_spread.add_hline(y=0, line_dash="dash", line_color="white")
fig_spread.update_layout(
    yaxis_title="Spread (USD/barrel)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=300,
)
st.plotly_chart(fig_spread, use_container_width=True)

st.markdown("""
### 📚 How Macro Affects Oil — and How Oil Affects Macro

**Macro → Oil:**
- **Global growth** → more economic activity = more energy demand = higher oil
- **Fed rate hikes** → stronger dollar = oil more expensive for non-USD buyers = lower demand
- **OPEC decisions** → supply cuts push price up, increases push price down
- **Geopolitics** → Middle East conflicts add a risk premium to Brent especially

**Oil → Macro:**
- **Higher oil** → energy costs rise → CPI rises → central banks hike → economy slows
- **Lower oil** → deflationary pressure → gives central banks room to cut
- **Oil shock** → sudden spike in oil prices is one of the most reliable recession predictors
- **Petrodollars** → oil exporters accumulate USD → recycle into US Treasuries → keeps US rates lower
""")

st.divider()

# --- SECTION 4: COMMODITIES ---

st.subheader("🥇 Commodities")
st.markdown("""
Commodities are raw materials that drive the global economy. 
Beyond being tradeable assets, they are **leading indicators** — 
they often signal macro shifts before official economic data does.
""")

@st.cache_data(ttl=3600)
def get_commodity_ytd():
    """Calculates YTD return for each commodity."""
    rows = []
    for name, series in comm_data.items():
        if name in ["WTI Oil", "Brent Oil"]:
            continue
        current_year = series.index[-1].year
        start = series[series.index.year == current_year].iloc[0]
        current = series.iloc[-1]
        ytd = round((current / start - 1) * 100, 2)
        rows.append({
            "Commodity": name,
            "Current":   f"{round(current, 2):,.2f}",
            "YTD (%)":   f"{ytd:+.2f}%",
        })
    return pd.DataFrame(rows)

comm_ytd = get_commodity_ytd()

def color_ytd(val):
    if "+" in str(val):
        return "color: green"
    elif "-" in str(val):
        return "color: red"
    return ""

st.dataframe(
    comm_ytd.style.applymap(color_ytd, subset=["YTD (%)"]),
    use_container_width=True,
    hide_index=True
)

# Interactive chart
selected_comm = st.multiselect(
    "Select commodities:",
    options=["Gold", "Silver", "Copper", "Natural Gas"],
    default=["Gold", "Copper"],
    key="comm_select"
)

start_comm = st.date_input(
    "Start date:",
    value=pd.Timestamp("2010-01-01"),
    min_value=pd.Timestamp("2000-01-01"),
    max_value=pd.Timestamp.today(),
    key="comm_date"
)

fig_comm = go.Figure()
for name in selected_comm:
    series = comm_data[name]
    series = series[series.index >= pd.Timestamp(start_comm)]
    normalized = (series / series.iloc[0]) * 100
    fig_comm.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized.values,
        mode="lines",
        name=name
    ))

fig_comm.update_layout(
    yaxis_title="Indexed to 100",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    hovermode="x unified",
    height=350,
)
st.plotly_chart(fig_comm, use_container_width=True)

# Commodity explanations
col1, col2 = st.columns(2)

with col1:
    with st.expander("🥇 Gold — The Ultimate Safe Haven"):
        st.markdown("""
        Gold is the oldest store of value in human history. It has **no yield**, 
        no industrial use case that justifies its price, and yet it has been 
        considered valuable for 5,000 years.
        
        **What drives gold:**
        - **Real interest rates** — gold's biggest driver. When real rates fall, 
        the opportunity cost of holding gold (which pays nothing) also falls → gold rises
        - **Dollar weakness** — gold is priced in USD. Weaker dollar = gold more affordable globally
        - **Inflation fears** — gold is seen as an inflation hedge, though historically imperfect
        - **Geopolitical risk** — war, crisis, uncertainty → investors buy gold as insurance
        - **Central bank buying** — EM central banks (China, India, Russia) have been 
        accumulating gold to reduce USD dependency
        
        **Key relationship:** Gold and real rates move in opposite directions — 
        this is the most reliable relationship in commodity markets.
        """)

    with st.expander("🥈 Silver — Gold's Industrial Cousin"):
        st.markdown("""
        Silver is unique because it serves **two roles simultaneously**: 
        a precious metal (like gold) and an industrial metal (like copper).
        
        **Industrial uses:** Solar panels, electronics, electric vehicles, 
        medical equipment — silver is the best electrical conductor of all metals.
        
        **What drives silver:**
        - Everything that drives gold (safe haven, real rates, dollar)
        - **Industrial demand** — solar panel boom has been a major silver demand driver
        - **Gold/Silver ratio** — traders watch this ratio to identify relative value 
        between the two metals
        
        Silver tends to **outperform gold in bull markets** (higher beta) 
        and **underperform in bear markets** — making it a leveraged play on gold.
        """)

with col2:
    with st.expander("🟤 Copper — Dr. Copper, the Economist"):
        st.markdown("""
        Copper has a **PhD in economics** — or so the saying goes. 
        It's the most widely used industrial metal and its price is 
        considered one of the best leading indicators of global economic health.
        
        **Why copper predicts the economy:**
        Copper is in everything — wiring, plumbing, construction, electronics, 
        electric vehicles, power grids. When economic activity accelerates, 
        copper demand rises. When it slows, copper falls.
        
        **Key drivers:**
        - **China** — China consumes ~55% of global copper. Chinese growth = copper demand
        - **Green energy transition** — EVs use 4x more copper than combustion cars. 
        Solar and wind farms require massive copper wiring
        - **Supply constraints** — major mines in Chile and Peru face geopolitical and 
        environmental challenges
        
        **Trading signal:** Copper falling while stocks are rising is a **divergence warning** — 
        it suggests the equity rally may not have fundamental economic support.
        """)

    with st.expander("🔥 Natural Gas — The Volatile One"):
        st.markdown("""
        Natural gas is the most volatile major commodity — prices can move 50-100% 
        in a single season due to **weather and storage dynamics**.
        
        **What drives natural gas:**
        - **Weather** — cold winters spike heating demand, hot summers spike cooling demand
        - **Storage levels** — weekly EIA storage reports move prices significantly
        - **LNG exports** — the US became a major LNG exporter, linking US prices 
        to global prices for the first time
        - **Geopolitics** — the Russia-Ukraine war exposed Europe's dangerous dependency 
        on Russian gas, causing European gas to spike 10x in 2022
        
        **US vs European gas:** Until recently, US and European gas prices were 
        completely disconnected. LNG infrastructure is now gradually linking them — 
        a structural shift with major macro implications for European energy security.
        """)

st.divider()

# --- SECTION 5: QUANT TOOLS ---

st.subheader("🧮 Quant Tools")
st.markdown("""
These tools apply quantitative techniques to commodity and FX analysis — 
going beyond price levels to understand **relative value**, **statistical extremes**, 
and **changing relationships** between assets.
""")

# Build full commodity dataset for quant section
quant_assets = {
    "Gold":        comm_data["Gold"],
    "Silver":      comm_data["Silver"],
    "Copper":      comm_data["Copper"],
    "WTI Oil":     comm_data["WTI Oil"],
    "Natural Gas": comm_data["Natural Gas"],
    "DXY":         fx_data["DXY"],
}

tab_zscore, tab_rolling_corr, tab_ratios = st.tabs([
    "📊 Z-Score",
    "🔄 Rolling Correlations",
    "⚖️ Commodity Ratios"
])

# --- Z-SCORE TAB ---
with tab_zscore:
    st.markdown("""
    ### What is a Z-Score?
    
    A **Z-score** tells you how many standard deviations away from the historical mean 
    a price currently is. It answers the question: *"Is this asset cheap or expensive 
    relative to its own history?"*
    """)
    st.info("**Formula:** Z-Score = (Current Price − Mean) / Standard Deviation")
    st.markdown("""
    **How to interpret it:**
    - **Z > +2** → Price is unusually high (2 standard deviations above mean) — potentially overvalued
    - **Z between -1 and +1** → Price is within normal historical range
    - **Z < -2** → Price is unusually low — potentially undervalued
    
    **Important caveat:** Z-scores assume prices are normally distributed and 
    mean-reverting. Commodities in structural bull or bear markets can stay at 
    extreme Z-scores for extended periods. Z-scores are a signal, not a prediction.
    
    **How traders use it:**
    - **Mean reversion strategies** — buy when Z < -2, sell when Z > +2
    - **Pair trading** — if two correlated assets diverge in Z-score, trade the spread
    - **Risk management** — extreme Z-scores signal unusual market conditions
    """)

    # Rolling window selector
    window = st.slider(
        "Historical window (days):",
        min_value=252,
        max_value=1260,
        value=504,
        step=252,
        help="252 = 1 year, 504 = 2 years, 756 = 3 years, 1260 = 5 years"
    )

    zscore_rows = []
    for name, series in quant_assets.items():
        series = series.dropna()
        rolling_mean = series.rolling(window).mean()
        rolling_std  = series.rolling(window).std()
        zscore = ((series - rolling_mean) / rolling_std).dropna()

        current_z = round(zscore.iloc[-1], 2)
        current_p = round(series.iloc[-1], 2)

        if current_z > 2:
            signal = "🔴 Expensive"
        elif current_z < -2:
            signal = "🟢 Cheap"
        elif current_z > 1:
            signal = "🟡 Slightly high"
        elif current_z < -1:
            signal = "🟡 Slightly low"
        else:
            signal = "⚪ Normal"

        zscore_rows.append({
            "Asset":     name,
            "Price":     f"{current_p:,.2f}",
            "Z-Score":   current_z,
            "Signal":    signal,
        })

    df_zscore = pd.DataFrame(zscore_rows)
    st.dataframe(df_zscore, use_container_width=True, hide_index=True)

    # Z-score chart
    selected_z = st.selectbox(
        "View Z-score history for:",
        options=list(quant_assets.keys()),
        key="zscore_select"
    )

    series = quant_assets[selected_z].dropna()
    rolling_mean = series.rolling(window).mean()
    rolling_std  = series.rolling(window).std()
    zscore_hist  = ((series - rolling_mean) / rolling_std).dropna()
    zscore_hist  = zscore_hist[zscore_hist.index >= "2005-01-01"]

    fig_z = go.Figure()
    fig_z.add_trace(go.Scatter(
        x=zscore_hist.index,
        y=zscore_hist.values,
        mode="lines",
        line=dict(color="#00d4ff", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(0, 212, 255, 0.1)",
        name=f"{selected_z} Z-Score"
    ))
    fig_z.add_hline(y=2,  line_dash="dash", line_color="red",
                    annotation_text="+2 (expensive)", annotation_position="right")
    fig_z.add_hline(y=-2, line_dash="dash", line_color="green",
                    annotation_text="-2 (cheap)", annotation_position="right")
    fig_z.add_hline(y=0,  line_dash="dot",  line_color="white")

    fig_z.update_layout(
        yaxis_title="Z-Score",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        hovermode="x unified",
        height=350,
    )
    st.plotly_chart(fig_z, use_container_width=True)

# --- ROLLING CORRELATIONS TAB ---
with tab_rolling_corr:
    st.markdown("""
    ### Rolling Correlations — Relationships That Change Over Time
    
    A **static correlation** tells you how two assets moved together over a fixed period. 
    But correlations are not constant — they change depending on the macro regime, 
    risk appetite, and market structure.
    
    A **rolling correlation** calculates the correlation over a moving window of time, 
    showing how the relationship between two assets **evolves**.
    """)
    st.info("**Formula:** Pearson correlation of daily returns over a rolling N-day window")
    st.markdown("""
    **Why this matters for traders:**
    - A correlation that was reliable for years can break down suddenly
    - During crises, correlations often spike toward +1 (everything falls together)
    - Understanding when correlations are stable vs unstable helps size positions and manage risk
    
    **Classic example:** Gold and DXY are normally negatively correlated (-0.5 to -0.7). 
    But during severe crises (2008, March 2020), even gold sold off as investors 
    rushed to cash — the correlation temporarily broke down.
    """)

    roll_window = st.slider(
        "Rolling window (days):",
        min_value=30,
        max_value=252,
        value=90,
        step=30,
        key="roll_window"
    )

    asset_a = st.selectbox("Asset A:", options=list(quant_assets.keys()), index=0, key="corr_a")
    asset_b = st.selectbox("Asset B:", options=list(quant_assets.keys()), index=5, key="corr_b")

    returns_a = quant_assets[asset_a].pct_change().dropna()
    returns_b = quant_assets[asset_b].pct_change().dropna()

    combined = pd.DataFrame({"a": returns_a, "b": returns_b}).dropna()
    rolling_corr = combined["a"].rolling(roll_window).corr(combined["b"]).dropna()
    rolling_corr = rolling_corr[rolling_corr.index >= "2005-01-01"]

    fig_rc = go.Figure()
    fig_rc.add_trace(go.Scatter(
        x=rolling_corr.index,
        y=rolling_corr.values,
        mode="lines",
        line=dict(color="#ffaa00", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(255, 170, 0, 0.1)",
        name=f"{asset_a} vs {asset_b}"
    ))
    fig_rc.add_hline(y=0,    line_dash="dot",  line_color="white")
    fig_rc.add_hline(y=0.7,  line_dash="dash", line_color="red",
                     annotation_text="High correlation", annotation_position="right")
    fig_rc.add_hline(y=-0.7, line_dash="dash", line_color="green",
                     annotation_text="High negative correlation", annotation_position="right")

    fig_rc.update_layout(
        yaxis_title="Correlation",
        yaxis_range=[-1, 1],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        hovermode="x unified",
        height=350,
    )
    st.plotly_chart(fig_rc, use_container_width=True)

# --- RATIOS TAB ---
with tab_ratios:
    st.markdown("""
    ### Commodity Ratios — Relative Value in Action
    
    Commodity ratios compare the price of one asset relative to another. 
    They are powerful because they **remove the noise of absolute price levels** 
    and focus on relative value — how expensive one asset is compared to another.
    
    Traders use ratios to identify:
    - When an asset is cheap or expensive **relative to a related asset**
    - Macro regime shifts (growth vs recession, risk-on vs risk-off)
    - Mean reversion opportunities
    """)

    gold  = comm_data["Gold"].dropna()
    silver= comm_data["Silver"].dropna()
    wti   = comm_data["WTI Oil"].dropna()

    # Align all series
    combined_ratios = pd.DataFrame({
        "Gold":   gold,
        "Silver": silver,
        "WTI":    wti
    }).dropna()

    gold_oil    = combined_ratios["Gold"] / combined_ratios["WTI"]
    gold_silver = combined_ratios["Gold"] / combined_ratios["Silver"]

    tab_go, tab_gs = st.tabs(["Gold/Oil Ratio", "Gold/Silver Ratio"])

    with tab_go:
        st.markdown("""
        **Gold/Oil Ratio** = Price of Gold ÷ Price of WTI Oil
        
        It tells you how many barrels of oil one ounce of gold can buy.
        
        **What it signals:**
        - **High ratio (gold expensive vs oil)** → risk-off environment, recession fears, 
        low growth expectations. Investors flee to gold while oil falls on demand concerns.
        - **Low ratio (oil expensive vs gold)** → inflationary environment, strong growth, 
        geopolitical supply shocks pushing oil up.
        
        **Historical average:** roughly 15-20 barrels per ounce.  
        During COVID (April 2020), the ratio spiked above 100 as oil briefly went negative 
        while gold surged — one of the most extreme macro dislocations in history.
        """)

        current_go = round(gold_oil.iloc[-1], 1)
        hist_mean_go = round(gold_oil.mean(), 1)
        st.metric(
            label="Current Gold/Oil Ratio",
            value=f"{current_go} barrels/oz",
            delta=f"Historical avg: {hist_mean_go}"
        )

        fig_go = go.Figure()
        fig_go.add_trace(go.Scatter(
            x=gold_oil.index,
            y=gold_oil.values,
            mode="lines",
            line=dict(color="#ffaa00", width=1.5),
            name="Gold/Oil"
        ))
        fig_go.add_hline(
            y=gold_oil.mean(),
            line_dash="dash",
            line_color="white",
            annotation_text=f"Historical avg: {hist_mean_go}",
            annotation_position="right"
        )
        fig_go.update_layout(
            yaxis_title="Barrels per oz",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            hovermode="x unified",
            height=300,
        )
        st.plotly_chart(fig_go, use_container_width=True)

    with tab_gs:
        st.markdown("""
        **Gold/Silver Ratio** = Price of Gold ÷ Price of Silver
        
        It tells you how many ounces of silver are needed to buy one ounce of gold.
        
        **What it signals:**
        - **High ratio (>80)** → gold is expensive relative to silver, or silver is cheap. 
        Often seen during recessions and risk-off periods when gold's safe haven demand 
        outpaces silver's industrial demand.
        - **Low ratio (<50)** → silver is expensive relative to gold. 
        Often seen during economic expansions with strong industrial demand.
        
        **Historical average:** roughly 65-70 ounces of silver per ounce of gold.
        
        **Traders use this ratio for:**
        - **Relative value** — when ratio is very high, buy silver / sell gold
        - **Economic cycle signal** — rising ratio = deteriorating growth outlook
        """)

        current_gs = round(gold_silver.iloc[-1], 1)
        hist_mean_gs = round(gold_silver.mean(), 1)
        st.metric(
            label="Current Gold/Silver Ratio",
            value=f"{current_gs} oz silver per oz gold",
            delta=f"Historical avg: {hist_mean_gs}"
        )

        fig_gs = go.Figure()
        fig_gs.add_trace(go.Scatter(
            x=gold_silver.index,
            y=gold_silver.values,
            mode="lines",
            line=dict(color="#c0c0c0", width=1.5),
            name="Gold/Silver"
        ))
        fig_gs.add_hline(
            y=gold_silver.mean(),
            line_dash="dash",
            line_color="white",
            annotation_text=f"Historical avg: {hist_mean_gs}",
            annotation_position="right"
        )
        fig_gs.add_hline(y=80, line_dash="dot", line_color="red",
                         annotation_text="80 — historically high", annotation_position="right")
        fig_gs.add_hline(y=50, line_dash="dot", line_color="green",
                         annotation_text="50 — historically low", annotation_position="right")

        fig_gs.update_layout(
            yaxis_title="Oz silver per oz gold",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            hovermode="x unified",
            height=300,
        )
        st.plotly_chart(fig_gs, use_container_width=True)