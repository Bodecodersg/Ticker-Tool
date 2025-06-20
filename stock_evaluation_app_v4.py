
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Stock Evaluation Scorecard — Phase 4", layout="wide")

st.title("📊 Stock Evaluation Scorecard — Phase 4")
st.markdown("Upload CSV with Tickers & Subjective Inputs")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("✅ Evaluation Complete")
    output = []

    for idx, row in df.iterrows():
        ticker = row['Ticker']

        try:
            stock = yf.Ticker(ticker)
            balance_sheet = stock.balance_sheet

            if not balance_sheet.empty:
                cash = balance_sheet.loc['Cash'][0] if 'Cash' in balance_sheet.index else 0
                debt = balance_sheet.loc['Long Term Debt'][0] if 'Long Term Debt' in balance_sheet.index else 0
            else:
                cash, debt = 0, 0

            if debt == 0 and cash > 0:
                cash_vs_debt_score = 10
            elif cash > debt:
                cash_vs_debt_score = 5
            else:
                cash_vs_debt_score = 0

        except Exception:
            cash_vs_debt_score = 0

        # Subjective Metrics from CSV input (assumed in CSV)
        revenue_growth_score = row.get('Revenue Growth', 0)
        operating_margin_score = row.get('Operating Margin', 0)
        scalability_score = row.get('Scalability', 0)
        shareholder_returns_score = row.get('Shareholder Returns', 0)
        moat_score = row.get('Moat', 0)
        ceo_score = row.get('CEO', 0)
        recession_score = row.get('Recession', 0)
        trend_score = row.get('Trend', 0)
        culture_score = row.get('Culture', 0)
        talent_score = row.get('Talent', 0)

        scores = {
            "Cash vs Debt": cash_vs_debt_score,
            "Revenue Growth": revenue_growth_score,
            "Operating Margin": operating_margin_score,
            "Scalability": scalability_score,
            "Shareholder Returns": shareholder_returns_score,
            "Moat": moat_score,
            "CEO": ceo_score,
            "Recession": recession_score,
            "Trend": trend_score,
            "Culture": culture_score,
            "Talent": talent_score
        }

        total_score = sum(scores.values())
        action = "BUY" if total_score >= 85 else ("WATCH" if total_score >= 60 else "DROP")

        scores['Ticker'] = ticker
        scores['Total Score'] = total_score
        scores['Action'] = action

        output.append(scores)

    df_out = pd.DataFrame(output)
    df_out.set_index("Ticker", inplace=True)
    st.dataframe(df_out)

    csv_download = df_out.reset_index().to_csv(index=False).encode('utf-8')
    st.download_button("Download Results", csv_download, "evaluation_results.csv", "text/csv")
