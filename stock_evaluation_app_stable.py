
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Stock Evaluation Scorecard — Stable Version", layout="wide")

st.title("📊 Stock Evaluation Scorecard — Stable Version")

# Upload CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    results = []

    for _, row in df.iterrows():
        ticker = row['Ticker']

        # Quantitative evaluation
        try:
            stock = yf.Ticker(ticker)
            balance_sheet = stock.balance_sheet
            cash = balance_sheet.loc['Cash'][0] if 'Cash' in balance_sheet.index else 0
            debt = balance_sheet.loc['TotalDebt'][0] if 'TotalDebt' in balance_sheet.index else 0

            if debt == 0 and cash > 0:
                cash_vs_debt_score = 10
            elif cash >= 2 * debt:
                cash_vs_debt_score = 10
            elif cash > debt:
                cash_vs_debt_score = 5
            else:
                cash_vs_debt_score = 0
        except:
            cash_vs_debt_score = 0

        # Revenue Growth (dummy value for stable version)
        revenue_growth = row['Revenue Growth']
        revenue_growth_score = 10 if revenue_growth >= 20 else 5 if revenue_growth >= 10 else 0

        # Operating Margin (dummy value for stable version)
        operating_margin = row['Operating Margin']
        operating_margin_score = 10 if operating_margin >= 25 else 5 if operating_margin >= 10 else 0

        # Scalability (dummy subjective input directly from CSV)
        scalability_score = row['Scalability']
        shareholder_returns_score = row['Shareholder Returns']
        moat_score = row['Moat']
        ceo_score = row['CEO']
        recession_score = row['Recession']
        trend_score = row['Trend']
        culture_score = row['Culture']
        talent_score = row['Talent']

        total_score = (
            cash_vs_debt_score + revenue_growth_score + operating_margin_score + scalability_score +
            shareholder_returns_score + moat_score + ceo_score + recession_score +
            trend_score + culture_score + talent_score
        )

        if total_score >= 90:
            action = "BUY"
        elif total_score >= 75:
            action = "WATCH"
        else:
            action = "DROP"

        results.append({
            'Ticker': ticker,
            'Cash vs Debt': cash_vs_debt_score,
            'Revenue Growth': revenue_growth_score,
            'Operating Margin': operating_margin_score,
            'Scalability': scalability_score,
            'Shareholder Returns': shareholder_returns_score,
            'Moat': moat_score,
            'CEO': ceo_score,
            'Recession': recession_score,
            'Trend': trend_score,
            'Culture': culture_score,
            'Talent': talent_score,
            'Total Score': total_score,
            'Action': action
        })

    results_df = pd.DataFrame(results).set_index("Ticker")

    st.success("✅ Evaluation Complete")
    st.dataframe(results_df)
    st.download_button("Download Results", results_df.to_csv().encode('utf-8'), file_name="evaluation_results.csv", mime='text/csv')
