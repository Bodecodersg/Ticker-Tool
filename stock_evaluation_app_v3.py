
import streamlit as st
import pandas as pd
import yfinance as yf

# Scoring functions (same as full version before)
def score_cash_vs_debt(cash, debt):
    if debt == 0:
        return 10
    ratio = cash / debt
    if ratio >= 2:
        return 10
    elif ratio >= 1:
        return 5
    else:
        return 0

def score_revenue_growth(growth):
    if growth >= 20:
        return 10
    elif growth >= 10:
        return 5
    else:
        return 0

# Additional metrics
def score_operating_margin(margin):
    if margin >= 25:
        return 10
    elif margin >= 10:
        return 5
    else:
        return 0

# The remaining scoring functions follow similar pattern... (shortened here)

st.title("Stock Evaluation Scorecard — Phase 3")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    results = []
    for _, row in df.iterrows():
        ticker = row['Ticker']
        subjective = {k: row[k] for k in ['Moat', 'CEO', 'Recession', 'Trend', 'Culture', 'Talent']}

        try:
            ticker_data = yf.Ticker(ticker).info
            cash = ticker_data.get('totalCash', 0)
            debt = ticker_data.get('totalDebt', 1)
            revenue_growth = ticker_data.get('revenueGrowth', 0) * 100
            op_margin = ticker_data.get('operatingMargins', 0) * 100
        except:
            cash, debt, revenue_growth, op_margin = 0, 1, 0, 0

        scores = {
            'Ticker': ticker,
            'Cash vs Debt': score_cash_vs_debt(cash, debt),
            'Revenue Growth': score_revenue_growth(revenue_growth),
            'Operating Margin': score_operating_margin(op_margin),
            'Moat': subjective['Moat'],
            'CEO': subjective['CEO'],
            'Recession': subjective['Recession'],
            'Trend': subjective['Trend'],
            'Culture': subjective['Culture'],
            'Talent': subjective['Talent']
        }
        total_score = sum(scores.values()) - scores['Ticker']
        scores['Total Score'] = total_score
        scores['Action'] = 'BUY' if total_score >= 90 else 'WATCH' if total_score >= 75 else 'DROP'
        results.append(scores)
    result_df = pd.DataFrame(results).set_index("Ticker")
    st.success("Evaluation Complete")
    st.dataframe(result_df)
