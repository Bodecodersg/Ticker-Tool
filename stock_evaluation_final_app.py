
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time

st.set_page_config(page_title="Stock Evaluation Tool", layout="wide")
st.title("📊 Stock Evaluation Scorecard")

api_key = st.sidebar.text_input("Enter your FMP API Key:", type="password")

def score_cash_vs_debt(cash, debt):
    if debt == 0:
        return 10
    ratio = cash / debt
    if ratio >= 2:
        return 10
    elif ratio > 1:
        return 5
    else:
        return 0

def score_revenue_growth(growth_pct):
    if growth_pct >= 20:
        return 10
    elif 10 <= growth_pct < 20:
        return 5
    else:
        return 0

def score_operating_margin(margin_pct):
    if margin_pct >= 25:
        return 10
    elif 10 <= margin_pct < 25:
        return 5
    else:
        return 0

def score_shareholder_returns(relative_returns_pct):
    if relative_returns_pct >= 20:
        return 10
    elif 10 <= relative_returns_pct < 20:
        return 5
    else:
        return 0

def score_scalability(rev_growth, opex_growth):
    if rev_growth > opex_growth:
        return 10
    else:
        return 0

def score_subjective(option, weights):
    return weights.get(option, 0)

def get_fmp_financials(ticker, api_key):
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            cash = data[0].get("cashAndShortTermInvestmentsTTM", 0)
            debt = data[0].get("totalDebtTTM", 0)
            op_margin = data[0].get("operatingMarginTTM", 0) * 100
            revenue_growth = data[0].get("revenueGrowthTTM", 0) * 100
            return cash, debt, op_margin, revenue_growth
    return 0, 0, 0, 0

def get_shareholder_returns(ticker):
    try:
        sp500 = yf.Ticker("^GSPC")
        sp500_hist = sp500.history(period="5y")
        stock = yf.Ticker(ticker)
        stock_hist = stock.history(period="5y")
        sp500_return = (sp500_hist['Close'][-1] - sp500_hist['Close'][0]) / sp500_hist['Close'][0] * 100
        stock_return = (stock_hist['Close'][-1] - stock_hist['Close'][0]) / stock_hist['Close'][0] * 100
        relative = stock_return - sp500_return
        return relative
    except:
        return 0

def evaluate_stock(ticker, subjective_inputs, opex_growth, api_key):
    cash, debt, op_margin, rev_growth = get_fmp_financials(ticker, api_key)
    shareholder_returns = get_shareholder_returns(ticker)

    scores = {
        'Cash vs Debt': score_cash_vs_debt(cash, debt),
        'Revenue Growth': score_revenue_growth(rev_growth),
        'Operating Margin': score_operating_margin(op_margin),
        'Scalability': score_scalability(rev_growth, opex_growth),
        'Shareholder Returns': score_shareholder_returns(shareholder_returns)
    }

    subjective_weights = {
        'Moat': {"Strong": 10, "Average": 5, "None": 0},
        'CEO': {"Top-tier": 10, "Good": 5, "Weak": 0},
        'Recession': {"Somewhat Resistant": 5, "No Resistance": 0},
        'Trend': {"Strong": 10, "Some": 5, "None": 0},
        'Culture': {"Fully Aligned": 10, "Partial": 5, "None": 0},
        'Talent': {"Top-tier": 10, "Some": 5, "None": 0}
    }

    for category, choice in subjective_inputs.items():
        scores[category] = score_subjective(choice, subjective_weights[category])

    total_score = sum(scores.values())
    action = 'BUY' if total_score > 100 else 'WATCH' if total_score >= 75 else 'DROP'

    result = {
        'Ticker': ticker,
        **scores,
        'Total Score': total_score,
        'Action': action
    }
    return result

if api_key:
    uploaded_file = st.sidebar.file_uploader("Upload CSV with Tickers", type=["csv"])
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file)
        tickers = df_input['Ticker'].tolist()
        results = []

        for ticker in tickers:
            with st.spinner(f"Evaluating {ticker}..."):
                subjective_inputs = {
                    'Moat': st.sidebar.selectbox(f"Moat for {ticker}", ["Strong", "Average", "None"]),
                    'CEO': st.sidebar.selectbox(f"CEO for {ticker}", ["Top-tier", "Good", "Weak"]),
                    'Recession': st.sidebar.selectbox(f"Recession Resistance for {ticker}", ["Somewhat Resistant", "No Resistance"]),
                    'Trend': st.sidebar.selectbox(f"Trend for {ticker}", ["Strong", "Some", "None"]),
                    'Culture': st.sidebar.selectbox(f"Culture for {ticker}", ["Fully Aligned", "Partial", "None"]),
                    'Talent': st.sidebar.selectbox(f"Talent for {ticker}", ["Top-tier", "Some", "None"])
                }
                result = evaluate_stock(ticker, subjective_inputs, opex_growth=5, api_key=api_key)
                results.append(result)
                time.sleep(1)
        st.success("✅ Evaluation Complete")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results)
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results", csv, "stock_eval_results.csv", "text/csv")
else:
    st.warning("Please enter your FMP API Key in the sidebar to proceed.")
