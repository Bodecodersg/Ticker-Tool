
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Evaluation Scorecard", layout="wide")
st.title("📊 Stock Evaluation Scorecard")

ticker_input = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):", "NVDA")

if ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        info = ticker.info
        name = info.get('longName', 'N/A')
        sector = info.get('sector', 'N/A')
        market_cap = info.get('marketCap', 'N/A')

        st.subheader(f"{name} ({ticker_input.upper()})")
        st.write(f"**Market Cap:** {market_cap:,}")
        st.write(f"**Sector:** {sector}")

        # Objective Metrics
        st.subheader("Objective Metrics (Auto-Fetched)")
        bs = ticker.balance_sheet
        cash = bs.loc['Cash'][0] if 'Cash' in bs.index else 0
        debt = bs.loc['Long Term Debt'][0] if 'Long Term Debt' in bs.index else 1
        cash_vs_debt_score = 10 if cash > 2 * debt else 5 if cash > debt else 0
        st.write(f"**Cash vs Debt Score:** {cash_vs_debt_score} (Cash: {cash:,}, Debt: {debt:,})")

        fin = ticker.financials
        revenue = fin.loc['Total Revenue'][:2].values if 'Total Revenue' in fin.index else [0, 0]
        rev_growth_score = 0
        if len(revenue) >= 2 and revenue[1] > 0:
            growth = ((revenue[0] - revenue[1]) / revenue[1]) * 100
            rev_growth_score = 10 if growth > 20 else 5 if growth > 10 else 0
        st.write(f"**Revenue Growth Score:** {rev_growth_score}")

        op_margin_score = 0
        op_income = fin.loc['Operating Income'][0] if 'Operating Income' in fin.index else 0
        if revenue[0] > 0:
            margin = (op_income / revenue[0]) * 100
            op_margin_score = 10 if margin > 25 else 5 if margin > 10 else 0
        st.write(f"**Operating Margin Score:** {op_margin_score}")

        # Subjective Sliders
        st.subheader("Subjective Inputs")
        moat = st.slider("Moat", 0, 10, 0)
        ceo = st.slider("CEO", 0, 10, 0)
        recession = st.slider("Recession Resistance", 0, 10, 0)
        trend = st.slider("Trend Alignment", 0, 10, 0)
        culture = st.slider("Culture Fit", 0, 10, 0)
        talent = st.slider("Talent Quality", 0, 10, 0)

        total_score = sum([
            cash_vs_debt_score, rev_growth_score, op_margin_score,
            moat, ceo, recession, trend, culture, talent
        ])
        st.metric("📈 Total Score", total_score)

    except Exception as e:
        st.error(f"Failed to retrieve data for ticker: {ticker_input.upper()}")
        st.exception(e)
