
import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Stock Evaluation Tool (Phase 2)", layout="wide")
st.title("📊 Stock Evaluation Scorecard — Phase 2")

def score_cash_vs_debt(cash, debt):
    if debt == 0:
        return 10
    ratio = cash / debt
    if ratio >= 2:
        return 10
    elif ratio > 1:
        return 5
    return 0

def score_revenue_growth(growth_pct):
    if growth_pct >= 20:
        return 10
    elif 10 <= growth_pct < 20:
        return 5
    return 0

def score_operating_margin(margin_pct):
    if margin_pct >= 25:
        return 10
    elif 10 <= margin_pct < 25:
        return 5
    return 0

def score_shareholder_returns(relative_returns_pct):
    if relative_returns_pct >= 20:
        return 10
    elif 10 <= relative_returns_pct < 20:
        return 5
    return 0

def score_scalability(rev_growth, opex_growth):
    return 10 if rev_growth > opex_growth else 0

def score_subjective(option, weights):
    return weights.get(option, 0)

def evaluate_stock(ticker, subjective_inputs, opex_growth=5):
    try:
        ticker_data = yf.Ticker(ticker)
        fin = ticker_data.financials
        bs = ticker_data.balance_sheet

        cash = bs.loc['Cash'].iloc[0] if 'Cash' in bs.index else 0
        debt = bs.loc['Long Term Debt'].iloc[0] if 'Long Term Debt' in bs.index else 0

        revs = fin.loc['Total Revenue']
        growth_pct = (revs.iloc[0] - revs.iloc[1]) / revs.iloc[1] * 100 if len(revs) >= 2 else 0

        op_inc = fin.loc['Operating Income'].iloc[0] if 'Operating Income' in fin.index else 0
        revenue = revs.iloc[0] if len(revs) > 0 else 0
        op_margin = (op_inc / revenue * 100) if revenue != 0 else 0

        past = pd.Timestamp.now() - pd.DateOffset(years=5)
        hist = ticker_data.history(start=past)
        spx = yf.Ticker('^GSPC').history(start=past)
        stock_return = (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100 if len(hist) > 0 else 0
        sp500_return = (spx['Close'][-1] - spx['Close'][0]) / spx['Close'][0] * 100 if len(spx) > 0 else 0
        rel_return = stock_return - sp500_return

    except:
        cash, debt, growth_pct, op_margin, rel_return = 0, 0, 0, 0, 0

    scores = {
        'Cash vs Debt': score_cash_vs_debt(cash, debt),
        'Revenue Growth': score_revenue_growth(growth_pct),
        'Operating Margin': score_operating_margin(op_margin),
        'Scalability': score_scalability(growth_pct, opex_growth),
        'Shareholder Returns': score_shareholder_returns(rel_return)
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

    result = {'Ticker': ticker, **scores, 'Total Score': total_score, 'Action': action}
    return result

uploaded_file = st.file_uploader("Upload CSV with Tickers & Subjective Inputs", type=["csv"])
if uploaded_file:
    df_input = pd.read_csv(uploaded_file)
    results = []
    for index, row in df_input.iterrows():
        ticker = row['Ticker']
        subjective_inputs = {
            'Moat': row['Moat'],
            'CEO': row['CEO'],
            'Recession': row['Recession'],
            'Trend': row['Trend'],
            'Culture': row['Culture'],
            'Talent': row['Talent']
        }
        with st.spinner(f"Evaluating {ticker}..."):
            result = evaluate_stock(ticker, subjective_inputs)
            results.append(result)
            time.sleep(1)
    st.success("✅ Evaluation Complete")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)
    csv = df_results.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results", csv, "stock_eval_results.csv", "text/csv")
