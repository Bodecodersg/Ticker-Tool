import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Evaluation Scorecard", layout="wide")

st.title("📊 Stock Evaluation Scorecard")

ticker = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        st.subheader(f"{info.get('longName', 'N/A')} ({ticker.upper()})")
        st.markdown(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")

        st.header("Objective Metrics (Auto-Fetched)")

        # Cash vs Debt
        total_cash = info.get("totalCash", 0)
        total_debt = info.get("totalDebt", 0)
        cash_debt_ratio = total_cash / total_debt if total_debt else 0
        cash_debt_score = min(round(cash_debt_ratio * 10), 10)
        st.markdown(f"**Cash vs Debt Score:** {cash_debt_score} (Cash: {total_cash:,}, Debt: {total_debt:,})")

        # Revenue Growth
        try:
            hist = stock.history(period="5y")
            revenue_growth = ((hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]) * 100
        except:
            revenue_growth = 0
        rev_score = min(round(revenue_growth / 5), 10)
        st.markdown(f"**Revenue Growth Score:** {rev_score} (Growth: {revenue_growth:.2f}%)")

        # Operating Margin
        op_margin = info.get("operatingMargins", 0)
        op_margin_score = min(round(op_margin * 100 / 10), 10)
        st.markdown(f"**Operating Margin Score:** {op_margin_score} (Operating Margin: {op_margin * 100:.2f}%)")

        # Ownership
        ownership = info.get("heldPercentInstitutions", 0)
        own_score = min(round(ownership * 10), 10)
        st.markdown(f"**Institutional Ownership Score:** {own_score} (Ownership: {ownership * 100:.1f}%)")

        # Short Interest (requires additional data source)
        st.markdown("**Short Interest Score:** Not Available (Requires external source)")

        # Relative Returns (manual for now)
        rel_return = st.slider("5-Year Relative Returns vs S&P500 (%)", -50, 50, 0)
        rel_score = min(max(int((rel_return + 50) / 10), 0), 10)
        st.markdown(f"**Relative Return Score:** {rel_score} (User input: {rel_return}%)")

        # Scalability (manual for now)
        rev_growth_input = st.slider("Revenue Growth (%)", 0, 100, 20)
        opex_growth_input = st.slider("OpEx Growth (%)", 0, 100, 20)
        scale_ratio = (rev_growth_input - opex_growth_input) / max(opex_growth_input, 1)
        scale_score = min(max(int(scale_ratio * 10), 0), 10)
        st.markdown(f"**Scalability Score:** {scale_score} (Revenue: {rev_growth_input}%, OpEx: {opex_growth_input}%)")

    except Exception as e:
        st.error("Failed to fetch data. Please check the ticker or try again later.")