
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Stock Evaluation Scorecard", layout="wide")
st.title("Stock Evaluation Scorecard — Phase 3")
fmp_api_key = st.sidebar.text_input("Enter your FMP API Key", type="password")
if not fmp_api_key:
    st.warning("Please enter your FMP API Key in the sidebar to proceed.")
    st.stop()

def fetch_fmp_financials(ticker, api_key):
    url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?limit=1&apikey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if not data:
        return None
    latest = data[0]
    cash = latest.get("cashAndCashEquivalents", 0)
    debt = latest.get("totalDebt", 0)
    return cash, debt

def fetch_fmp_income(ticker, api_key):
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=2&apikey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if len(data) < 2:
        return None
    latest, previous = data[0], data[1]
    revenue_growth = (latest["revenue"] - previous["revenue"]) / previous["revenue"] * 100
    operating_margin = latest.get("operatingIncome", 0) / latest.get("revenue", 1) * 100
    return revenue_growth, operating_margin

def score_cash_vs_debt(cash, debt):
    if debt == 0 and cash > 0:
        return 10
    ratio = cash / debt
    if ratio >= 1:
        return 10
    elif ratio >= 0.5:
        return 5
    else:
        return 0

def score_growth(value):
    if value >= 20:
        return 10
    elif value >= 10:
        return 5
    else:
        return 0

def score_margin(value):
    if value >= 20:
        return 10
    elif value >= 10:
        return 5
    else:
        return 0

def evaluate_ticker(ticker, subjective):
    cash_score = growth_score = margin_score = scalability_score = shareholder_score = 0
    financials = fetch_fmp_financials(ticker, fmp_api_key)
    income = fetch_fmp_income(ticker, fmp_api_key)

    if financials:
        cash, debt = financials
        cash_score = score_cash_vs_debt(cash, debt)
    if income:
        revenue_growth, operating_margin = income
        growth_score = score_growth(revenue_growth)
        margin_score = score_margin(operating_margin)
        scalability_score = shareholder_score = 10

    total = (cash_score + growth_score + margin_score + scalability_score + shareholder_score +
        subjective["Moat"] + subjective["CEO"] + subjective["Recession"] +
        subjective["Trend"] + subjective["Culture"] + subjective["Talent"])

    action = "BUY" if total >= 90 else "WATCH" if total >= 75 else "DROP"

    return {
        "Cash vs Debt": cash_score,
        "Revenue Growth": growth_score,
        "Operating Margin": margin_score,
        "Scalability": scalability_score,
        "Shareholder Returns": shareholder_score,
        "Moat": subjective["Moat"],
        "CEO": subjective["CEO"],
        "Recession": subjective["Recession"],
        "Trend": subjective["Trend"],
        "Culture": subjective["Culture"],
        "Talent": subjective["Talent"],
        "Total Score": total,
        "Action": action
    }

uploaded_file = st.file_uploader("Upload CSV with Tickers & Subjective Inputs", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    results = []
    for _, row in df.iterrows():
        ticker = row["Ticker"]
        subjective = {
            "Moat": row["Moat"],
            "CEO": row["CEO"],
            "Recession": row["Recession"],
            "Trend": row["Trend"],
            "Culture": row["Culture"],
            "Talent": row["Talent"]
        }
        scores = evaluate_ticker(ticker, subjective)
        scores["Ticker"] = ticker
        results.append(scores)
    result_df = pd.DataFrame(results)
    st.success("Evaluation Complete")
    st.dataframe(result_df)
    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Results", csv, "results.csv", "text/csv")
