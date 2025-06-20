
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Scoring functions (simplified version)

def score_cash_vs_debt(cash, debt):
    if debt == 0 and cash > 0:
        return 10
    ratio = cash / debt if debt else 0
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

# UI

st.title("Stock Evaluation Scorecard — Phase 3")
st.write("Upload CSV with Tickers & Subjective Inputs")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    tickers = df["Ticker"].tolist()
    output = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info

        try:
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 1)
            growth = info.get("revenueGrowth", 0) * 100  # revenueGrowth is usually a decimal

            cash_vs_debt_score = score_cash_vs_debt(cash, debt)
            revenue_growth_score = score_revenue_growth(growth)

            result = {
                "Ticker": ticker,
                "Cash vs Debt": cash_vs_debt_score,
                "Revenue Growth": revenue_growth_score
            }

            output.append(result)
        except Exception as e:
            st.error(f"Error processing {ticker}: {e}")

    df_out = pd.DataFrame(output).set_index("Ticker")
    st.success("Evaluation Complete")
    st.dataframe(df_out)
