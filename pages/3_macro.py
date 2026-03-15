# pages/3_macro.py
# Global Macro page — key economic indicators by country

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fredapi import Fred


# --- DATA FUNCTIONS ---

@st.cache_data(ttl=3600)
def get_us_data():
    """
    Fetches US macro indicators from FRED.
    
    Series:
        FEDFUNDS  → Fed Funds Rate (monthly)
        CPIAUCSL  → CPI All Urban Consumers (monthly, index level)
        GDP       → Gross Domestic Product (quarterly, billions USD)
        UNRATE    → Unemployment Rate (monthly)
    """
    fred = Fred(api_key=st.secrets["FRED_API_KEY"])
    start = "2000-01-01"

    fed    = fred.get_series("FEDFUNDS",  observation_start=start).dropna()
    cpi    = fred.get_series("CPIAUCSL",  observation_start=start).dropna()
    gdp    = fred.get_series("GDP",       observation_start=start).dropna()
    unrate = fred.get_series("UNRATE",    observation_start=start).dropna()

    # Calculate YoY CPI inflation from index level
    # CPI is reported as an index (e.g. 300), not a % directly
    # YoY % = (current / 12 months ago - 1) * 100
    cpi_yoy = ((cpi / cpi.shift(12)) - 1) * 100
    cpi_yoy = cpi_yoy.dropna()

    # Calculate GDP growth rate QoQ annualized
    # GDP is reported in levels — we calculate % change from previous quarter
    gdp_growth = gdp.pct_change() * 100
    gdp_growth = gdp_growth.dropna()

    # Real interest rate = Fed Funds Rate - CPI YoY
    # Align both series to same dates first
    real_rate = fed - cpi_yoy.reindex(fed.index, method="ffill")
    real_rate = real_rate.dropna()

    return {
        "fed":        fed,
        "cpi_yoy":    cpi_yoy,
        "gdp_growth": gdp_growth,
        "unrate":     unrate,
        "real_rate":  real_rate,
    }


def plot_series(series, title, ylabel, color="#00d4ff", hline=None, hline_label=""):
    """
    Generic function to plot a time series with Plotly.
    Reused for every chart on this page.
    
    Parameters:
        series      → pd.Series with datetime index
        title       → chart title
        ylabel      → y axis label
        color       → line color
        hline       → optional horizontal line (e.g. 2% inflation target)
        hline_label → label for the horizontal line
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode="lines",
        line=dict(color=color, width=1.5),
        name=title
    ))

    if hline is not None:
        fig.add_hline(
            y=hline,
            line_dash="dash",
            line_color="red",
            annotation_text=hline_label,
            annotation_position="bottom right"
        )

    fig.update_layout(
        title=title,
        yaxis_title=ylabel,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        hovermode="x unified",
        height=300,
        margin=dict(t=40, b=40)
    )

    return fig


# --- PAGE LAYOUT ---

st.title("🌐 Global Macro")
st.markdown("""
A deep dive into the key economic indicators that drive global markets.
Select a country to explore its macroeconomic data and understand 
how each indicator affects the economy and financial markets.
""")
st.divider()

# Country tabs
tab_us, tab_br, tab_eu, tab_jp, tab_cn, tab_compare = st.tabs([
    "🇺🇸 United States",
    "🇧🇷 Brazil",
    "🇪🇺 Europe",
    "🇯🇵 Japan",
    "🇨🇳 China",
    "📊 Global Comparison"
])

# --- US TAB ---
with tab_us:
    st.subheader("🇺🇸 United States — Macro Overview")

    with st.spinner("Loading US data..."):
        us = get_us_data()

    # Fed Funds Rate
    st.markdown("### 📌 Fed Funds Rate")
    st.markdown("""
    The **Fed Funds Rate** is the interest rate at which US banks lend money to each other overnight. 
    It is set by the Federal Reserve (Fed) and is the most important interest rate in the world — 
    it directly influences borrowing costs for consumers, businesses, and governments globally.
    
    - **When the Fed raises rates** → borrowing becomes more expensive, economy slows, inflation cools
    - **When the Fed cuts rates** → borrowing becomes cheaper, economy accelerates, risk assets rally
    """)
    st.plotly_chart(plot_series(us["fed"], "Fed Funds Rate", "Rate (%)"), use_container_width=True)

    # CPI
    st.markdown("### 📌 Inflation (CPI YoY)")
    st.markdown("""
    The **Consumer Price Index (CPI)** measures the average change in prices paid by consumers 
    for goods and services. We show it as **year-over-year % change** — how much more expensive 
    things are compared to the same month last year.
    
    The Fed's **inflation target is 2%**. When CPI runs above 2%, the Fed raises rates to cool demand.
    When it falls below, the Fed may cut rates to stimulate the economy.
    """)
    st.plotly_chart(
        plot_series(us["cpi_yoy"], "CPI YoY (%)", "Inflation (%)", 
                   hline=2.0, hline_label="Fed 2% target"),
        use_container_width=True
    )

    # GDP Growth
    st.markdown("### 📌 GDP Growth (QoQ)")
    st.markdown("""
    **Gross Domestic Product (GDP)** is the total value of all goods and services produced 
    in the US economy. We show it as **quarter-over-quarter % change** — the pace of growth 
    from one quarter to the next.
    
    - **Positive** → economy is expanding
    - **Negative** → economy is contracting
    - **Two consecutive negative quarters** → technical definition of recession
    """)
    st.plotly_chart(
        plot_series(us["gdp_growth"], "GDP Growth QoQ (%)", "Growth (%)", 
                   color="#00ff88", hline=0, hline_label="Recession threshold"),
        use_container_width=True
    )

    # Unemployment
    st.markdown("### 📌 Unemployment Rate")
    st.markdown("""
    The **unemployment rate** measures the percentage of the labor force that is jobless 
    and actively looking for work. It is a lagging indicator — it tends to rise *after* 
    a recession has already started, and fall *after* recovery is underway.
    
    The Fed considers **~4%** as "full employment" — the natural rate where everyone 
    who wants a job can find one without causing wage inflation.
    """)
    st.plotly_chart(
        plot_series(us["unrate"], "Unemployment Rate", "Rate (%)", 
                   color="#ffaa00", hline=4.0, hline_label="Full employment"),
        use_container_width=True
    )

    # Real Interest Rate
    st.markdown("### 📌 Real Interest Rate")
    st.markdown("""
    The **real interest rate** is arguably more important than the nominal rate. It tells you 
    the *actual* return on money after accounting for inflation.
    """)
    
    st.info("**How it's calculated:** Real Rate = Fed Funds Rate − CPI YoY")
    
    st.markdown("""
    - **Positive real rate** → money is expensive in real terms, restrictive policy
    - **Negative real rate** → even after inflation, money is cheap, stimulative policy
    
    During 2021-2022, despite rising nominal rates, real rates were deeply negative 
    because inflation was running much higher than the Fed Funds Rate — 
    this is why financial conditions remained loose for so long.
    """)
    st.plotly_chart(
        plot_series(us["real_rate"], "Real Interest Rate", "Rate (%)", 
                   color="#ff6b6b", hline=0, hline_label="Neutral"),
        use_container_width=True
    )
# --- BRAZIL TAB ---
with tab_br:
    st.subheader("🇧🇷 Brazil — Macro Overview")

    @st.cache_data(ttl=3600)
    def get_brazil_data():
        """
        Fetches Brazilian macro indicators from BCB (Banco Central do Brasil).
        
        Series:
            432  → SELIC rate (% per year)
            433  → IPCA monthly inflation
            4380 → GDP growth QoQ
            13522 → Unemployment (PNAD)
        """
        from bcb import sgs
        import datetime

        end   = datetime.date.today()
        start = datetime.date(end.year - 10, end.month, end.day)

        selic = sgs.get({"SELIC": 432},   start=start, end=end).dropna()
        ipca  = sgs.get({"IPCA": 433},    start=start, end=end).dropna()
        gdp_raw = sgs.get({"GDP": 4380}, start=start, end=end).dropna()["GDP"]
        gdp = ((gdp_raw / gdp_raw.shift(12)) - 1) * 100
        gdp = gdp.dropna()    
        unemp = sgs.get({"UNEMP": 13522}, start=start, end=end).dropna()

        # IPCA accumulated 12 months — rolling sum of monthly readings
        ipca_12m = ipca["IPCA"].rolling(12).sum().dropna()

        # Real rate Brazil = SELIC - IPCA 12m
        real_rate = selic["SELIC"] - ipca_12m.reindex(selic.index, method="ffill")
        real_rate = real_rate.dropna()

        return {
            "selic":     selic["SELIC"],
            "ipca_12m":  ipca_12m,
            "gdp": gdp,
            "unemp":     unemp["UNEMP"],
            "real_rate": real_rate,
        }

    with st.spinner("Loading Brazil data..."):
        br = get_brazil_data()

    # SELIC
    st.markdown("### 📌 SELIC Rate")
    st.markdown("""
    The **SELIC** is Brazil's benchmark interest rate, set by the BCB (Banco Central do Brasil) 
    through its COPOM committee — the Brazilian equivalent of the Fed's FOMC.
    
    Brazil has historically maintained some of the **highest real interest rates in the world**, 
    reflecting structural challenges: high inflation history, fiscal risk, and currency volatility.
    
    - **High SELIC** → fixed income becomes very attractive, capital flows into bonds, BRL strengthens, Ibovespa suffers
    - **Low SELIC** → equities become more attractive, credit expands, economy accelerates
    """)
    st.plotly_chart(
        plot_series(br["selic"], "SELIC Rate", "Rate (%)"),
        use_container_width=True
    )

    # IPCA
    st.markdown("### 📌 IPCA (12-month accumulated)")
    st.markdown("""
    The **IPCA** is Brazil's official inflation index, measured by IBGE. 
    We show it as the **accumulated reading over the last 12 months** — 
    the same way the BCB monitors it against its annual target.
    
    The BCB's inflation target system works with a **center target and tolerance bands**. 
    When IPCA consistently exceeds the upper band, the COPOM raises SELIC to cool demand.
    """)
    st.plotly_chart(
        plot_series(br["ipca_12m"], "IPCA 12m (%)", "Inflation (%)",
                   color="#ffaa00", hline=3.0, hline_label="BCB target ~3%"),
        use_container_width=True
    )

    # GDP
    st.markdown("### 📌 GDP Growth (YoY)")
    st.markdown("""
Brazil's **GDP growth** shown as year-over-year % change — 
how much the economy grew compared to the same month one year earlier.
This smooths out seasonal effects and gives a cleaner picture of the trend.
""")
    st.plotly_chart(
    plot_series(br["gdp"], "Brazil GDP Growth (YoY %)", "Growth (%)",
               color="#00ff88", hline=0, hline_label="Recession threshold"),
    use_container_width=True
)

    # Unemployment
    st.markdown("### 📌 Unemployment Rate")
    st.markdown("""
    Brazil's unemployment rate is measured by PNAD (Pesquisa Nacional por Amostra de Domicílios), 
    conducted by IBGE. It includes both formal and informal workers looking for employment.
    
    Brazil has a large **informal economy** — many workers are not captured in formal employment 
    statistics, making unemployment data harder to interpret than in developed markets.
    """)
    st.plotly_chart(
        plot_series(br["unemp"], "Unemployment Rate", "Rate (%)",
                   color="#ffaa00"),
        use_container_width=True
    )

    # Real Rate
    st.markdown("### 📌 Real Interest Rate")
    st.markdown("""
    Brazil's real interest rate is one of the most watched figures in emerging market finance.
    """)

    st.info("**How it's calculated:** Real Rate = SELIC − IPCA 12m")

    st.markdown("""
    Brazil has often had the **highest real interest rate in the world** among major economies — 
    sometimes exceeding 6-8% in real terms. This attracts foreign capital into Brazilian bonds 
    (the famous *carry trade*) but also suppresses domestic investment and growth.
    
    - High real rates → BRL tends to strengthen, foreign investors buy Brazilian bonds
    - Low or negative real rates → capital outflows, BRL weakens, inflation risk rises
    """)
    st.plotly_chart(
        plot_series(br["real_rate"], "Brazil Real Interest Rate", "Rate (%)",
                   color="#ff6b6b", hline=0, hline_label="Neutral"),
        use_container_width=True
    )    
# --- EUROPE TAB ---
with tab_eu:
    st.subheader("🇪🇺 Europe — Macro Overview")

    @st.cache_data(ttl=3600)
    def get_europe_data():
        """
        Fetches European macro indicators from FRED.
        
        Series:
            ECBDFR           → ECB Deposit Facility Rate
            CP0000EZ19M086NEST → CPI Eurozone YoY
            EUGDPNQDSMEI     → Eurozone GDP QoQ growth
            LRHUTTTTEZM156S  → Eurozone Unemployment Rate
        """
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        start = "2000-01-01"

        ecb_rate = fred.get_series("ECBDFR",             observation_start=start).dropna()
        cpi_raw = fred.get_series("CP0000EZ19M086NEST", observation_start=start).dropna()
        cpi = ((cpi_raw / cpi_raw.shift(12)) - 1) * 100
        cpi = cpi.dropna()
        gdp = fred.get_series("CLVMNACSCAB1GQEA19", observation_start=start).dropna()
        gdp = gdp.pct_change() * 100
        gdp = gdp.dropna()
        unemp    = fred.get_series("LRHUTTTTEZM156S",    observation_start=start).dropna()

        # Real rate Europe = ECB rate - CPI YoY
        real_rate = ecb_rate - cpi.reindex(ecb_rate.index, method="ffill")
        real_rate = real_rate.dropna()

        return {
            "ecb_rate":  ecb_rate,
            "cpi":       cpi,
            "gdp":       gdp,
            "unemp":     unemp,
            "real_rate": real_rate,
        }

    with st.spinner("Loading Europe data..."):
        eu = get_europe_data()

    # ECB Rate
    st.markdown("### 📌 ECB Deposit Facility Rate")
    st.markdown("""
    The **ECB Deposit Rate** is the rate the European Central Bank pays on excess reserves 
    held by commercial banks. It is the primary policy tool of the ECB — the European equivalent 
    of the Fed Funds Rate.
    
    Europe's rate cycle has historically lagged the US — the ECB tends to move more slowly 
    due to the complexity of managing monetary policy across 20 different economies with 
    different fiscal situations, growth rates, and inflation levels.
    
    - **2014-2022** → ECB held rates at zero or negative to stimulate the economy
    - **2022-2023** → Aggressive hiking cycle to fight post-COVID inflation
    - **2024 onwards** → Cutting cycle began as inflation returned toward target
    """)
    st.plotly_chart(
        plot_series(eu["ecb_rate"], "ECB Deposit Rate", "Rate (%)"),
        use_container_width=True
    )

    # CPI
    st.markdown("### 📌 Inflation (HICP YoY)")
    st.markdown("""
    Eurozone inflation is measured by the **HICP (Harmonised Index of Consumer Prices)** — 
    a standardized measure that allows comparison across all EU member states.
    
    The ECB's inflation target is **2%**, same as the Fed. However, Europe faced a unique 
    challenge in 2022: inflation was driven largely by **energy prices** (gas dependency on Russia) 
    rather than demand — making it harder to control with rate hikes alone.
    """)
    st.plotly_chart(
        plot_series(eu["cpi"], "HIPC YoY (%)", "Inflation (%)",
                   color="#ffaa00", hline=2.0, hline_label="ECB 2% target"),
        use_container_width=True
    )

    # GDP
    st.markdown("### 📌 GDP Growth (QoQ)")
    st.markdown("""
    Eurozone GDP growth is more **structurally constrained** than the US — 
    aging population, high regulation, energy dependence, and less flexible labor markets 
    tend to produce slower but more stable growth.
    
    Key events: the 2008 financial crisis, the **2011-2012 European sovereign debt crisis** 
    (Greece, Italy, Spain on the brink), the COVID crash in 2020, and the energy shock of 2022.
    """)
    st.plotly_chart(
        plot_series(eu["gdp"], "Eurozone GDP Growth QoQ (%)", "Growth (%)",
                   color="#00ff88", hline=0, hline_label="Recession threshold"),
        use_container_width=True
    )

    # Unemployment
    st.markdown("### 📌 Unemployment Rate")
    st.markdown("""
    Eurozone unemployment is structurally higher than the US — typically ranging between 
    6-12% even during expansions. This reflects more rigid labor markets, stronger 
    worker protections, and higher minimum wages in many member states.
    
    There is also **significant dispersion** within the Eurozone: Germany and the Netherlands 
    often have unemployment below 4%, while Spain and Greece have historically exceeded 15-20%.
    """)
    st.plotly_chart(
        plot_series(eu["unemp"], "Eurozone Unemployment Rate", "Rate (%)",
                   color="#ffaa00"),
        use_container_width=True
    )

    # Real Rate
    st.markdown("### 📌 Real Interest Rate")
    st.markdown("""
    Europe's real interest rate spent most of the 2010s in **deeply negative territory** — 
    a deliberate policy choice by the ECB to stimulate growth and avoid deflation after 
    the sovereign debt crisis.
    """)
    st.info("**How it's calculated:** Real Rate = ECB Deposit Rate − HICP YoY")
    st.markdown("""
    Negative real rates punish savers and encourage borrowing and investment. 
    However, they also inflate asset prices and can create financial instability — 
    exactly what happened in European real estate and bond markets during 2015-2021.
    """)
    st.plotly_chart(
        plot_series(eu["real_rate"], "Europe Real Interest Rate", "Rate (%)",
                   color="#ff6b6b", hline=0, hline_label="Neutral"),
        use_container_width=True
    )
# --- JAPAN TAB ---
with tab_jp:
    st.subheader("🇯🇵 Japan — Macro Overview")
    @st.cache_data(ttl=3600)
    def get_japan_data():
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        start = "2000-01-01"

        # BOJ rate — using more recent series
        boj = fred.get_series("IRSTCB01JPM156N", observation_start=start).dropna()

        # CPI — calculate YoY from index level
        cpi_raw = fred.get_series("JPNCPIALLMINMEI", observation_start=start).dropna()
        cpi = ((cpi_raw / cpi_raw.shift(12)) - 1) * 100
        cpi = cpi.dropna()

        # GDP — calculate YoY from level
        gdp_raw = fred.get_series("JPNRGDPEXP", observation_start=start).dropna()
        gdp = gdp_raw.pct_change() * 100
        gdp = gdp.dropna()

        # Unemployment
        unemp = fred.get_series("LRUNTTTTJPM156S", observation_start=start).dropna()

        # Real rate
        real_rate = boj - cpi.reindex(boj.index, method="ffill")
        real_rate = real_rate.dropna()

        return {
            "boj":       boj,
            "cpi":       cpi,
            "gdp":       gdp,
            "unemp":     unemp,
            "real_rate": real_rate,
        }

    with st.spinner("Loading Japan data..."):
        jp = get_japan_data()

    # BOJ Rate
    st.markdown("### 📌 BOJ Policy Rate")
    st.markdown("""
    Japan's monetary policy is one of the most unique and studied cases in modern macroeconomics.
    The **Bank of Japan (BOJ)** kept interest rates at **zero or negative for over two decades** — 
    a policy known as **ZIRP (Zero Interest Rate Policy)** and later **NIRP (Negative Interest Rate Policy)**.
    
    **Why did Japan keep rates so low for so long?**  
    Japan has been fighting **deflation** — falling prices — since the 1990s asset bubble burst. 
    When prices fall, consumers delay purchases expecting things to get cheaper, 
    which further slows the economy. The BOJ tried to break this cycle with ultra-loose policy.
    
    - **2016** → BOJ introduced negative rates (-0.1%)
    - **2024** → Historic shift — BOJ finally raised rates for the first time in 17 years
    - This rate hike triggered the **Yen carry trade unwind** in August 2024 — 
    a massive global market shock as investors who had borrowed in cheap yen rushed to repay
    """)
    st.plotly_chart(
        plot_series(jp["boj"], "BOJ Policy Rate", "Rate (%)"),
        use_container_width=True
    )

    # CPI
    st.markdown("### 📌 Inflation (CPI YoY)")
    st.markdown("""
    Japan's inflation story is the **opposite of the rest of the world**. 
    While the US and Europe fought high inflation in 2022-2023, Japan was celebrating 
    inflation finally returning after decades of deflation.
    
    **Deflation** is dangerous because it creates a self-reinforcing cycle:
    falling prices → delayed spending → less revenue → wage cuts → less spending → more deflation.
    Japan was trapped in this cycle for over 20 years.
    
    The BOJ's 2% inflation target — the same as the Fed and ECB — was seen as nearly 
    unachievable for years. Its recent return above 2% is a significant structural shift.
    """)
    st.plotly_chart(
        plot_series(jp["cpi"], "CPI YoY (%)", "Inflation (%)",
                   color="#ffaa00", hline=2.0, hline_label="BOJ 2% target"),
        use_container_width=True
    )

    # GDP
    st.markdown("### 📌 GDP Growth (QoQ)")
    st.markdown("""
    Japan's economy is the **third largest in the world** but has grown very slowly 
    for decades — a phenomenon economists call **"The Lost Decades"**.
    
    Key structural challenges:
    - **Aging population** — one of the oldest in the world, shrinking workforce
    - **Low immigration** — limited labor force replenishment
    - **Corporate conservatism** — Japanese companies historically hoarded cash rather than investing
    - **Deflationary mindset** — consumers and businesses accustomed to falling prices
    """)
    st.plotly_chart(
        plot_series(jp["gdp"], "Japan GDP Growth QoQ (%)", "Growth (%)",
                   color="#00ff88", hline=0, hline_label="Recession threshold"),
        use_container_width=True
    )

    # Unemployment
    st.markdown("### 📌 Unemployment Rate")
    st.markdown("""
    Japan has one of the **lowest unemployment rates** among developed economies — 
    typically between 2-3%. This reflects cultural factors (lifetime employment tradition), 
    demographic decline (fewer workers entering the labor force), and a very different 
    labor market structure compared to Western countries.
    
    However, Japan has high rates of **underemployment** — many workers in part-time or 
    low-productivity jobs that don't show up in unemployment statistics.
    """)
    st.plotly_chart(
        plot_series(jp["unemp"], "Japan Unemployment Rate", "Rate (%)",
                   color="#ffaa00"),
        use_container_width=True
    )

    # Real Rate
    st.markdown("### 📌 Real Interest Rate")
    st.markdown("""
    Japan's real interest rate has been **deeply negative** for most of the last two decades — 
    even more so than Europe. This made the Japanese Yen the world's favorite **funding currency** 
    for carry trades.
    """)
    st.info("**How it's calculated:** Real Rate = BOJ Policy Rate − CPI YoY")
    st.markdown("""
    **The Yen Carry Trade:**  
    Investors borrowed cheaply in yen (near-zero rates), converted to other currencies, 
    and invested in higher-yielding assets globally. When the BOJ raised rates in 2024, 
    this trade unwound rapidly — triggering a global market selloff as investors rushed 
    to repay yen loans, driving the yen sharply higher and selling risk assets worldwide.
    
    This is a perfect example of how a single central bank decision can ripple through 
    every asset class globally.
    """)
    st.plotly_chart(
        plot_series(jp["real_rate"], "Japan Real Interest Rate", "Rate (%)",
                   color="#ff6b6b", hline=0, hline_label="Neutral"),
        use_container_width=True
    )
# --- CHINA TAB ---
with tab_cn:
    st.subheader("🇨🇳 China — Macro Overview")

    @st.cache_data(ttl=3600)
    def get_china_data():
        """
        Fetches Chinese macro indicators from FRED.
        
        Series:
            INTDSRCNM193N    → PBoC Interest Rate
            CHNCPIALLMINMEI  → CPI China (index level)
            MKTGDPCNA646NWDB → GDP China (annual, current USD)
            LRUNTTTTCNM156S  → China Unemployment Rate
        """
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        start = "2000-01-01"

        pboc = fred.get_series("INTDSRCNM193N", observation_start=start).dropna()

        cpi_raw = fred.get_series("CHNCPIALLMINMEI", observation_start=start).dropna()
        cpi = ((cpi_raw / cpi_raw.shift(12)) - 1) * 100
        cpi = cpi.dropna()

        gdp_raw = fred.get_series("MKTGDPCNA646NWDB", observation_start=start).dropna()
        gdp = gdp_raw.pct_change() * 100
        gdp = gdp.dropna()
        real_rate = pboc - cpi.reindex(pboc.index, method="ffill")
        real_rate = real_rate.dropna()

        return {
            "pboc":      pboc,
            "cpi":       cpi,
            "gdp":       gdp,
            "unemp":     None,
            "real_rate": real_rate,
        }

    with st.spinner("Loading China data..."):
        cn = get_china_data()

    # PBoC Rate
    st.markdown("### 📌 PBoC Lending Rate")
    st.markdown("""
    The **People's Bank of China (PBoC)** is China's central bank. Unlike the Fed or ECB, 
    the PBoC operates within a tightly controlled financial system where the government 
    plays a direct role in credit allocation.
    
    China's monetary policy is less transparent than Western central banks — 
    the PBoC uses multiple tools simultaneously: reserve requirements, lending quotas, 
    exchange rate management, and interest rates.
    
    **Key context:**
    - China has been in a **structural easing cycle** since 2021 to combat a property sector crisis
    - The property market collapse (Evergrande, Country Garden) wiped out ~$1 trillion in wealth
    - Unlike Western countries, China's challenge post-COVID was **deflation**, not inflation
    - The PBoC has limited room to cut — already at historically low rates
    """)
    st.plotly_chart(
        plot_series(cn["pboc"], "PBoC Lending Rate", "Rate (%)"),
        use_container_width=True
    )

    # CPI
    st.markdown("### 📌 Inflation (CPI YoY)")
    st.markdown("""
    China's inflation picture is **structurally different** from Western economies. 
    While the US and Europe fought high inflation in 2022-2023, China was facing 
    **deflationary pressures** — a sign of weak domestic demand rather than overheating.
    
    **Why is China facing deflation?**
    - The property crisis destroyed household wealth (70% of Chinese savings are in real estate)
    - Consumer confidence collapsed after COVID lockdowns
    - Overcapacity in manufacturing pushes goods prices down
    - Demographics — aging population spends less
    
    This is China's biggest macro challenge today: how to stimulate domestic demand 
    when consumers are deleveraging and confidence is low.
    """)
    st.plotly_chart(
        plot_series(cn["cpi"], "CPI YoY (%)", "Inflation (%)",
                   color="#ffaa00", hline=2.0, hline_label="Target ~2%"),
        use_container_width=True
    )

    # GDP
    st.markdown("### 📌 GDP Growth (YoY)")
    st.markdown("""
    China's GDP growth has been one of the most remarkable stories in economic history — 
    averaging nearly **10% per year for three decades**, lifting 800 million people out of poverty.
    
    However, the era of double-digit growth is over. China is now in a **structural slowdown**:
    - The easy gains from urbanization and industrialization are exhausted
    - Debt levels have reached unsustainable levels (property + local government debt)
    - The US-China tech war is limiting access to semiconductors and advanced technology
    - Demographics are turning negative — workforce is shrinking
    
    The official GDP target of **~5%** is increasingly questioned by economists who 
    believe actual growth may be lower than reported figures.
    """)
    st.plotly_chart(
        plot_series(cn["gdp"], "China GDP Growth YoY (%)", "Growth (%)",
                   color="#00ff88", hline=5.0, hline_label="Official target ~5%"),
        use_container_width=True
    )

    # Unemployment
    st.markdown("### 📌 Unemployment Rate")
    st.markdown("""
    China's official unemployment data is **not reliably available** through international sources. 
    The government only publishes urban registered unemployment, which excludes the ~300 million 
    migrant workers — making it largely meaningless as a macro indicator.
    
    A more telling indicator is **youth unemployment**, which reached a record **21.3% in 2023** 
    before the government **stopped publishing the data entirely** — itself a significant signal 
    about the reliability of Chinese economic statistics.
    """)
    st.warning("⚠️ Reliable unemployment data for China is not available via public APIs.")

    # Real Rate
    st.markdown("### 📌 Real Interest Rate")
    st.markdown("""
    China's real interest rate has been oscillating around zero — 
    sometimes slightly positive, sometimes negative depending on the inflation cycle.
    """)
    st.info("**How it's calculated:** Real Rate = PBoC Lending Rate − CPI YoY")
    st.markdown("""
    With deflation returning in 2023-2024, China's real rates have actually been 
    **rising despite nominal rate cuts** — because falling prices increase the real 
    cost of debt. This is the classic deflation trap: real debt burdens increase 
    even as nominal rates fall, discouraging borrowing and investment.
    
    This is exactly what Japan experienced in the 1990s — and why economists worry 
    China could be entering its own "Lost Decade."
    """)
    st.plotly_chart(
        plot_series(cn["real_rate"], "China Real Interest Rate", "Rate (%)",
                   color="#ff6b6b", hline=0, hline_label="Neutral"),
        use_container_width=True
    )