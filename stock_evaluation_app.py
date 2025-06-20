
import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime, timedelta
import time

# API CONFIGURATION
st.sidebar.header("API Configuration")
FMP_API_KEY = st.sidebar.text_input("Enter your FMP API Key:", type="password")
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

if not FMP_API_KEY:
    st.warning("Please enter your FMP API Key in the sidebar to proceed.")
    st.stop()

# SCORING FUNCTIONS
def score_moat(description):
    keywords_strong = ['dominant', 'monopoly', 'patented', 'market leader', 'exclusive', 'strong brand', 'global leader']
    keywords_average = ['recognized', 'established', 'growing brand', 'differentiated']
    desc = description.lower()
    if any(kw in desc for kw in keywords_strong):
        return 10
    elif any(kw in desc for kw in keywords_average):
        return 5
    return 0

def score_trend(description):
    keywords_strong = ['artificial intelligence', 'cloud', 'saas', 'machine learning', '5g', 'cybersecurity', 'green energy', 'renewables']
    keywords_some = ['software', 'automation', 'digitization', 'e-commerce']
    desc = description.lower()
    if any(kw in desc for kw in keywords_strong):
        return 10
    elif any(kw in desc for kw in keywords_some):
        return 5
    return 0

def score_recession(description):
    keywords_resistant = ['healthcare', 'utilities', 'consumer staples', 'defense', 'insurance']
    desc = description.lower()
    if any(kw in desc for kw in keywords_resistant):
        return 5
    return 0

def score_ceo(description):
    keywords_top = ['visionary', 'pioneer', 'innovative', 'renowned']
    keywords_good = ['experienced', 'longstanding', 'proven track record']
    desc = description.lower()
    if any(kw in desc for kw in keywords_top):
        return 10
    elif any(kw in desc for kw in keywords_good):
        return 5
    return 0

def score_cash_vs_debt(cash, debt):
    if debt == 0:
        return 10
    ratio = cash / debt
    return 10 if ratio >= 2 else 5 if ratio > 1 else 0

def score_revenue_growth(growth_pct):
    return 10 if growth_pct >= 20 else 5 if growth_pct >= 10 else 0

def score_operating_margin(margin_pct):
    return 10 if margin_pct >= 25 else 5 if margin_pct >= 10 else 0

def score_shareholder_returns(relative_returns_pct):
    return 10 if relative_returns_pct >= 20 else 5 if relative_returns_pct >= 10 else 0

def safe_value(value):
    try:
        return float(value) if value not in [None, 'null'] else 0.0
    except:
        return 0.0

# API CALLS
def get_financial_data(ticker):
    try:
        url_bs = f"{FMP_BASE_URL}/balance-sheet-statement/{ticker}?limit=2&apikey={FMP_API_KEY}"
        url_is = f"{FMP_BASE_URL}/income-statement/{ticker}?limit=2&apikey={FMP_API_KEY}"
        bs_data = requests.get(url_bs).json()
        is_data = requests.get(url_is).json()
        if len(bs_data) < 2 or len(is_data) < 2:
            return 0, 0, 0, 0, 0
        cash = safe_value(bs_data[0].get('cashAndCashEquivalents'))
        debt = safe_value(bs_data[0].get('longTermDebt'))
        rev0 = safe_value(is_data[0].get('revenue'))
        rev1 = safe_value(is_data[1].get('revenue'))
        op_income = safe_value(is_data[0].get('operatingIncome'))
        operating_margin = (op_income / rev0 * 100) if rev0 else 0
        revenue_growth = ((rev0 - rev1) / rev1 * 100) if rev1 else 0
        opex_growth = 0
        return cash, debt, revenue_growth, operating_margin, opex_growth
    except:
        return 0, 0, 0, 0, 0

def get_company_description(ticker):
    try:
        url_profile = f"{FMP_BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}"
        profile_data = requests.get(url_profile).json()
        if isinstance(profile_data, list) and len(profile_data) > 0:
            description = profile_data[0].get('description', '')
            if description:
                return description
    except:
        pass
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        description = info.get('longBusinessSummary', '')
        if description:
            return description
    except:
        pass
    return ''

# EVALUATION FUNCTION
def evaluate_stock(ticker):
    cash, debt, growth, op_margin, opex_growth = get_financial_data(ticker)
    try:
        today = datetime.today()
        past = today - timedelta(days=5*365)
        hist = yf.download(ticker, start=past, end=today)
        spx = yf.download("^GSPC", start=past, end=today)
        rel_return = ((hist['Adj Close'][-1] - hist['Adj Close'][0]) / hist['Adj Close'][0]) * 100 -                      ((spx['Adj Close'][-1] - spx['Adj Close'][0]) / spx['Adj Close'][0]) * 100
    except:
        rel_return = 0

    description = get_company_description(ticker)

    scores = {
        "Cash vs Debt": score_cash_vs_debt(cash, debt),
        "Revenue Growth": score_revenue_growth(growth),
        "Operating Margin": score_operating_margin(op_margin),
        "Scalability": 10 if growth > opex_growth else 0,
        "Shareholder Returns": score_shareholder_returns(rel_return),
        "Moat": score_moat(description),
        "CEO": score_ceo(description),
        "Recession Resistance": score_recession(description),
        "Secular Trend": score_trend(description)
    }
    total = sum(scores.values())
    scores["Total Score"] = total
    scores["Action"] = "BUY" if total > 100 else "WATCH" if total >= 75 else "DROP"
    return pd.Series(scores, name=ticker)

# STREAMLIT UI
st.title("📊 Stock Evaluation Platform")

mode = st.radio("Select Input Mode:", ["Single Ticker", "Batch Mode"])

if mode == "Single Ticker":
    ticker = st.text_input("Enter Ticker Symbol:").upper()
    if ticker:
        with st.spinner(f"Evaluating {ticker}..."):
            result = evaluate_stock(ticker)
            st.subheader(f"Results for {ticker}:")
            st.write(result.to_frame())
else:
    uploaded_file = st.file_uploader("Upload CSV file with 'Ticker' column:", type=["csv"])
    if uploaded_file is not None:
        df_input = pd.read_csv(uploaded_file)
        all_results = []
        for ticker in df_input["Ticker"]:
            with st.spinner(f"Evaluating {ticker}..."):
                result = evaluate_stock(ticker)
                all_results.append(result)
                time.sleep(1)
        df_results = pd.DataFrame(all_results)
        st.write(df_results)
        st.download_button("Download Results", df_results.to_csv().encode(), "results.csv", "text/csv")
