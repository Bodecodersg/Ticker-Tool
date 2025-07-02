
import streamlit as st
import requests

FMP_API_KEY = "EZ9ZWlvQTeKLLnqTv4mBoZoidw1APRNi"

def fetch_fmp_data(endpoint, ticker):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?limit=1&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            st.warning(f"No data returned for {endpoint} – {ticker}")
            return {}
        return data[0]
    except Exception as e:
        st.error(f"API Error ({endpoint} – {ticker}): {e}")
        return {}

def get_objective_scores(ticker):
    profile = fetch_fmp_data("profile", ticker)
    financials = fetch_fmp_data("key-metrics-ttm", ticker)
    ratios = fetch_fmp_data("ratios-ttm", ticker)

    scores = {}
    try:
        cash = float(financials.get("cashAndCashEquivalents", 0))
        debt = float(financials.get("totalDebt", 1))  # prevent division by zero
        scores["Cash vs Debt"] = 10 if cash > debt else 0
    except:
        scores["Cash vs Debt"] = 0

    try:
        revenue_growth = float(financials.get("revenueGrowth", 0)) * 100
        scores["Revenue Growth"] = min(10, round(revenue_growth / 10))
    except:
        scores["Revenue Growth"] = 0

    try:
        op_margin = float(ratios.get("operatingProfitMargin", 0)) * 100
        scores["Operating Margin"] = min(10, round(op_margin / 10))
    except:
        scores["Operating Margin"] = 0

    try:
        inst_ownership = float(profile.get("institutionalOwnership", 0)) * 100
        scores["Institutional Ownership"] = min(10, round(inst_ownership / 10))
    except:
        scores["Institutional Ownership"] = 0

    return scores

st.title("📊 Stock Evaluation Scorecard")
ticker = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):").upper()

if ticker:
    st.subheader(f"📈 Objective Metrics (Auto-Fetched) for {ticker}")
    scores = get_objective_scores(ticker)

    for metric, score in scores.items():
        st.markdown(f"**{metric} Score:** {score}")
