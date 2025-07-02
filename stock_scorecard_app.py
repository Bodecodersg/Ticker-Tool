import streamlit as st
import requests
import pandas as pd

# Constants and API key (replace with your actual FMP API key)
FMP_API_KEY = "your_fmp_api_key"
BASE_URL = "https://financialmodelingprep.com/api/v3"

def get_profile(ticker):
    url = f"{BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}"
    r = requests.get(url)
    return r.json()[0] if r.ok and r.json() else None

def get_key_metrics(ticker):
    url = f"{BASE_URL}/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}"
    r = requests.get(url)
    return r.json()[0] if r.ok and r.json() else None

def score_cash_vs_debt(cash, debt):
    if debt == 0:
        return 10
    ratio = cash / debt
    return min(int(ratio * 10), 10)

def score_revenue_growth(growth_pct):
    if growth_pct >= 30:
        return 10
    elif growth_pct <= 0:
        return 0
    return int(growth_pct / 3)

def score_op_margin(margin_pct):
    return min(int(margin_pct / 5), 10)

def score_ownership(ownership_pct):
    return min(int(ownership_pct / 10), 10)

def score_relative_return(rr_pct):
    return min(max(int((rr_pct + 50) / 10), 0), 10)

def score_scalability(rev_growth, opex_growth):
    if opex_growth == 0:
        return 10
    ratio = rev_growth / opex_growth
    return min(int(ratio * 2), 10)

st.title("📊 Stock Evaluation Scorecard")

ticker = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):", value="NVDA").upper()

if ticker:
    profile = get_profile(ticker)
    metrics = get_key_metrics(ticker)

    if profile and metrics:
        st.subheader(f"{profile['companyName']} ({ticker})")
        st.markdown(f"**Market Cap:** {profile['mktCap']:,}")
        st.markdown(f"**Sector:** {profile['sector']}")

        st.markdown("## Objective Metrics (Auto-Fetched)")

        cash = float(metrics.get("cashAndShortTermInvestments", 0))
        debt = float(metrics.get("totalDebt", 1))
        revenue_growth = float(metrics.get("revenueGrowth", 0)) * 100
        op_margin = float(metrics.get("operatingProfitMargin", 0)) * 100
        ownership = float(metrics.get("institutionalOwnership", 0)) * 100

        st.markdown(f"**Cash vs Debt Score:** {score_cash_vs_debt(cash, debt)} (Cash: {cash:,.0f}, Debt: {debt:,.0f})")
        st.markdown(f"**Revenue Growth Score:** {score_revenue_growth(revenue_growth)} (Growth: {revenue_growth:.2f}%)")
        st.markdown(f"**Operating Margin Score:** {score_op_margin(op_margin)} (Operating Margin: {op_margin:.2f}%)")
        st.markdown(f"**Institutional Ownership Score:** {score_ownership(ownership)} (Ownership: {ownership:.1f}%)")

        st.markdown(f"**Short Interest Score:** Not Available (Requires external source)")

        st.markdown("### 5-Year Relative Returns vs S&P500")
        rr_pct = st.slider("Input manually (% over/under S&P500)", -50, 50, 0)
        st.markdown(f"**Relative Return Score:** {score_relative_return(rr_pct)} (User input: {rr_pct}%)")

        st.markdown("### Scalability Score (Revenue vs OpEx)")
        rev_input = st.slider("Revenue Growth (%)", 0, 100, 20)
        opex_input = st.slider("OpEx Growth (%)", 0, 100, 20)
        st.markdown(f"**Scalability Score:** {score_scalability(rev_input, opex_input)} (Revenue: {rev_input}%, OpEx: {opex_input}%)")

    else:
        st.error("Ticker not found or data not available.")
