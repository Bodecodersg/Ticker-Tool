
import streamlit as st
import pandas as pd
import yfinance as yf

# Scoring functions
def score_cash_vs_debt(cash, debt):
    if debt == 0:
        return 10
    ratio = cash / debt
    if ratio >= 1: return 10
    elif ratio >= 0.5: return 5
    else: return 0

def score_revenue_growth(rev_growth_pct):
    if rev_growth_pct >= 15: return 10
    elif rev_growth_pct >= 5: return 5
    else: return 0

def score_operating_margin(op_margin_pct):
    if op_margin_pct >= 25: return 10
    elif op_margin_pct >= 10: return 5
    else: return 0

def score_scalability(op_margin_pct, rev_growth_pct):
    if op_margin_pct >= 25 and rev_growth_pct >= 15: return 10
    elif op_margin_pct >= 10 and rev_growth_pct >= 5: return 5
    else: return 0

def score_shareholder_returns(return_vs_sp500):
    if return_vs_sp500 >= 10: return 10
    elif return_vs_sp500 >= 0: return 5
    else: return 0

def evaluate_ticker(ticker, subjective_inputs):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        cash = info.get('totalCash', 0)
        debt = info.get('totalDebt', 1)
        op_margin_pct = info.get('operatingMargins', 0) * 100
        rev_growth_pct = info.get('revenueGrowth', 0) * 100

        cash_vs_debt_score = score_cash_vs_debt(cash, debt)
        rev_growth_score = score_revenue_growth(rev_growth_pct)
        op_margin_score = score_operating_margin(op_margin_pct)
        scalability_score = score_scalability(op_margin_pct, rev_growth_pct)
        shareholder_returns_score = score_shareholder_returns(subjective_inputs['Shareholder Returns'])

        total = (
            cash_vs_debt_score + rev_growth_score + op_margin_score +
            scalability_score + shareholder_returns_score +
            subjective_inputs['Moat'] + subjective_inputs['CEO'] +
            subjective_inputs['Recession'] + subjective_inputs['Trend'] +
            subjective_inputs['Culture'] + subjective_inputs['Talent']
        )
        action = "BUY" if total >= 85 else "WATCH" if total >= 70 else "DROP"

        return {
            'Ticker': ticker,
            'Cash vs Debt': cash_vs_debt_score,
            'Revenue Growth': rev_growth_score,
            'Operating Margin': op_margin_score,
            'Scalability': scalability_score,
            'Shareholder Returns': shareholder_returns_score,
            'Moat': subjective_inputs['Moat'],
            'CEO': subjective_inputs['CEO'],
            'Recession': subjective_inputs['Recession'],
            'Trend': subjective_inputs['Trend'],
            'Culture': subjective_inputs['Culture'],
            'Talent': subjective_inputs['Talent'],
            'Total Score': total,
            'Action': action
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Streamlit UI
st.title("📊 Stock Evaluation Scorecard — Live Mode")

ticker_input = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):").upper()

if ticker_input:
    st.subheader("Subjective Inputs")
    moat = st.slider("Moat", 0, 10, 10)
    ceo = st.slider("CEO", 0, 10, 10)
    recession = st.slider("Recession Resistance", 0, 10, 5)
    trend = st.slider("Trend Alignment", 0, 10, 10)
    culture = st.slider("Culture Fit", 0, 10, 10)
    talent = st.slider("Talent Quality", 0, 10, 10)
    shareholder_returns = st.slider("5-Year Relative Returns vs S&P500 (%)", -50, 50, 10)

    subjective_inputs = {
        'Moat': moat,
        'CEO': ceo,
        'Recession': recession,
        'Trend': trend,
        'Culture': culture,
        'Talent': talent,
        'Shareholder Returns': shareholder_returns
    }

    if st.button("Evaluate"):
        result = evaluate_ticker(ticker_input, subjective_inputs)
        if result:
            df = pd.DataFrame([result])
            df.set_index("Ticker", inplace=True)
            st.success("Evaluation Complete")
            st.dataframe(df)
