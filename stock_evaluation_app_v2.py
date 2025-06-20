import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

INFO = {
    "Cash vs Debt": "Double cash vs debt = 10; More cash than debt = 5; Less cash than debt = 0",
    "Revenue Growth": "20%+ = 10; 10–20% = 5; Below 10% = 0",
    "Operating Margin": "25%+ = 10; 10–25% = 5; Below 10% = 0",
    "Scalability": "Revenue growth > OpEx growth = 10; Otherwise = 0",
    "Shareholder Returns": "20%+ over S&P500 = 10; 10–20% = 5; Underperforms S&P500 = 0",
    "Moat": "Strong moat = 10; Average moat = 5; No moat = 0",
    "CEO": "Top-tier CEO = 10; Good CEO = 5; Weak CEO = 0",
    "Recession": "Somewhat recession resistant = 5; No resistance = 0",
    "Trend": "Strong trend = 10; Some trend = 5; No trend = 0",
    "Culture": "Fully aligned = 10; Partial = 5; None = 0",
    "Talent": "Top-tier talent = 10; Some talent = 5; No talent = 0",
}

def score_cash_vs_debt(cash, debt):
    if cash >= 2 * debt:
        return 10
    elif cash > debt:
        return 5
    return 0

def score_growth(val, high, mid):
    if val >= high:
        return 10
    elif val >= mid:
        return 5
    return 0

def evaluate_ticker(ticker, qualitative):
    try:
        stock = yf.Ticker(ticker)
        fin = stock.financials
        bal = stock.balance_sheet
        cash = bal.loc["Cash", :].iloc[0]
        debt = bal.loc["Total Debt", :].iloc[0]
        rev = fin.loc["Total Revenue", :].iloc[0]
        op_margin = stock.info.get("operatingMargins", 0)
        revenue_growth = stock.info.get("revenueGrowth", 0)
        opex_growth = stock.info.get("operatingExpenses", 0)

        scores = {
            "Cash vs Debt": score_cash_vs_debt(cash, debt),
            "Revenue Growth": score_growth(revenue_growth, 0.2, 0.1),
            "Operating Margin": score_growth(op_margin, 0.25, 0.1),
            "Scalability": 10 if revenue_growth > opex_growth else 0,
            "Shareholder Returns": 10,
        }

        for factor in ["Moat", "CEO", "Recession", "Trend", "Culture", "Talent"]:
            val = qualitative.get(factor, "None").lower()
            if val == "strong" or val == "top-tier" or val == "fully aligned":
                scores[factor] = 10
            elif val in ["average", "some", "partial", "good", "somewhat"]:
                scores[factor] = 5
            else:
                scores[factor] = 0

        total = sum(scores.values())
        action = "BUY" if total > 85 else "WATCH" if total > 65 else "DROP"

        return {**scores, "Total Score": total, "Action": action}
    except:
        return None

def display_chart(ticker):
    hist = yf.Ticker(ticker).history(period="6mo")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode='lines', name='Close Price'))
    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(layout="wide")
st.title("📊 Stock Evaluation Scorecard — Phase 3")

with st.sidebar:
    st.subheader("Add a Ticker")
    ticker_input = st.text_input("Enter Ticker Symbol (e.g., AAPL)")
    if ticker_input:
        st.markdown("#### Qualitative Factors")
        q_inputs = {
            "Moat": st.selectbox("Moat", ["Strong", "Average", "None"]),
            "CEO": st.selectbox("CEO", ["Top-tier", "Good", "Weak"]),
            "Recession": st.selectbox("Recession", ["Somewhat", "None"]),
            "Trend": st.selectbox("Trend", ["Strong", "Some", "None"]),
            "Culture": st.selectbox("Culture", ["Fully aligned", "Partial", "None"]),
            "Talent": st.selectbox("Talent", ["Top-tier", "Some", "None"]),
        }
        if st.button("Evaluate"):
            result = evaluate_ticker(ticker_input.upper(), q_inputs)
            if result:
                st.success("Evaluation Complete")
                df = pd.DataFrame([result], index=[ticker_input.upper()])
                st.dataframe(df)
                display_chart(ticker_input.upper())
            else:
                st.error("Unable to retrieve data for this ticker.")

st.markdown("### Upload CSV with Tickers & Subjective Inputs")
uploaded = st.file_uploader("Drag and drop file here", type=["csv"])

if uploaded:
    df_input = pd.read_csv(uploaded)
    output = []

    for _, row in df_input.iterrows():
        tkr = row["Ticker"]
        qvals = {
            "Moat": row.get("Moat", "None"),
            "CEO": row.get("CEO", "None"),
            "Recession": row.get("Recession", "None"),
            "Trend": row.get("Trend", "None"),
            "Culture": row.get("Culture", "None"),
            "Talent": row.get("Talent", "None"),
        }
        res = evaluate_ticker(tkr, qvals)
        if res:
            res["Ticker"] = tkr
            output.append(res)

    df_out = pd.DataFrame(output).set_index("Ticker")
    st.success("Evaluation Complete")
    st.dataframe(df_out)

    csv = df_out.reset_index().to_csv(index=False).encode()
    st.download_button("Download Results", csv, file_name="stock_scores.csv", mime="text/csv")
