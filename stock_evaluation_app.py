
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Stock Evaluation Scorecard — Phase 3")

st.title("Stock Evaluation Scorecard — Phase 3")
st.write("Upload CSV with Tickers & Subjective Inputs")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df_input = pd.read_csv(uploaded_file)
    st.success("Evaluation Complete")
    
    output = []
    for idx, row in df_input.iterrows():
        ticker = row['Ticker']
        
        try:
            ticker_data = yf.Ticker(ticker).balance_sheet
            cash = ticker_data.loc['Cash'][0]
            debt = ticker_data.loc['Total Debt'][0]
            if debt == 0:
                cash_vs_debt = 10
            elif cash >= 2 * debt:
                cash_vs_debt = 10
            elif cash > debt:
                cash_vs_debt = 5
            else:
                cash_vs_debt = 0
        except:
            cash_vs_debt = 0

        revenue_growth = row['Revenue Growth']
        operating_margin = row['Operating Margin']
        scalability = row['Scalability']
        shareholder_returns = row['Shareholder Returns']
        moat = row['Moat']
        ceo = row['CEO']
        recession = row['Recession']
        trend = row['Trend']
        culture = row['Culture']
        talent = row['Talent']

        scores = {
            'Cash vs Debt': cash_vs_debt,
            'Revenue Growth': revenue_growth,
            'Operating Margin': operating_margin,
            'Scalability': scalability,
            'Shareholder Returns': shareholder_returns,
            'Moat': moat,
            'CEO': ceo,
            'Recession': recession,
            'Trend': trend,
            'Culture': culture,
            'Talent': talent
        }
        
        total_score = sum([v for v in scores.values() if isinstance(v, (int, float))])
        action = "BUY" if total_score >= 90 else ("WATCH" if total_score >= 75 else "DROP")

        output.append({
            'Ticker': ticker,
            **scores,
            'Total Score': total_score,
            'Action': action
        })

    df_out = pd.DataFrame(output).set_index("Ticker")
    st.dataframe(df_out)
    st.download_button("Download Results", data=df_out.to_csv(), file_name="results.csv")
