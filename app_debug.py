
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
            st.warning(f"No data returned for {endpoint} - {ticker}")
            return {}
        return data[0]
    except Exception as e:
        st.error(f"API Error ({endpoint} - {ticker}): {e}")
        return {}

st.title("Stock Evaluation Scorecard")

ticker = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):", value="AAPL").upper()

if ticker:
    st.subheader(f"📈 Objective Metrics (Auto-Fetched) for {ticker}")

    # Fetching data from different FMP endpoints
    profile = fetch_fmp_data("profile", ticker)
    metrics = fetch_fmp_data("key-metrics", ticker)
    ratios = fetch_fmp_data("ratios-ttm", ticker)
    income = fetch_fmp_data("income-statement", ticker)

    # Extracting and displaying information
    market_cap = profile.get("mktCap", "N/A")
    st.markdown(f"**Market Cap:** {market_cap:,}" if isinstance(market_cap, (int, float)) else "**Market Cap:** N/A")

    cash = metrics.get("cashAndCashEquivalents", 0)
    debt = metrics.get("totalDebt", 1)
    cash_vs_debt_score = min(10, round((cash / debt) * 10)) if debt else 0
    st.markdown(f"**Cash vs Debt Score:** {cash_vs_debt_score} (Cash: {cash:,}, Debt: {debt:,})")

    growth = metrics.get("revenueGrowth", 0)
    growth_score = min(10, round(growth * 100 / 10)) if isinstance(growth, (int, float)) else 0
    st.markdown(f"**Revenue Growth Score:** {growth_score} (Growth: {growth * 100:.2f}%)")

    op_margin = ratios.get("operatingProfitMargin", 0)
    op_margin_score = min(10, round(op_margin * 100 / 10)) if isinstance(op_margin, (int, float)) else 0
    st.markdown(f"**Operating Margin Score:** {op_margin_score} (Operating Margin: {op_margin * 100:.2f}%)")

    ownership = metrics.get("institutionalOwnership", 0)
    ownership_score = min(10, round(ownership * 100 / 10)) if isinstance(ownership, (int, float)) else 0
    st.markdown(f"**Institutional Ownership Score:** {ownership_score} (Ownership: {ownership * 100:.1f}%)")

    st.markdown(f"**Short Interest Score:** Not Available (Requires external source)")

    st.info("For full automation of '5-Year Relative Returns' and 'Scalability', additional endpoints or providers (like Alpha Vantage) are required.")
