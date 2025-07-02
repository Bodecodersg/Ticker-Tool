
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Evaluation Scorecard", layout="wide")
st.title("📊 Stock Evaluation Scorecard")

ticker_input = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):", "")

if ticker_input:
    ticker = ticker_input.upper()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        st.subheader(f"{info.get('longName', 'N/A')} ({ticker})")
        st.markdown(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")

        st.subheader("Objective Metrics (Auto-Fetched)")

        # Cash vs Debt
        cash = info.get("totalCash", 0) or 0
        debt = info.get("totalDebt", 0) or 1
        if cash >= 2 * debt:
            cash_score = 10
        elif cash >= debt:
            cash_score = 5
        else:
            cash_score = 0
        st.markdown(f"**Cash vs Debt Score:** {cash_score} (Cash: {cash:,}, Debt: {debt:,})")

        # Revenue Growth (TTM)
        revenue_growth = info.get("revenueGrowth", 0) or 0
        if revenue_growth >= 0.2:
            rg_score = 10
        elif revenue_growth >= 0.1:
            rg_score = 5
        else:
            rg_score = 0
        st.markdown(f"**Revenue Growth Score:** {rg_score} (Growth: {revenue_growth*100:.2f}%)")

        # Operating Margin
        op_margin = info.get("operatingMargins", 0) or 0
        if op_margin >= 0.25:
            op_score = 10
        elif op_margin >= 0.1:
            op_score = 5
        else:
            op_score = 0
        st.markdown(f"**Operating Margin Score:** {op_score} (Operating Margin: {op_margin*100:.2f}%)")

        # Short Interest (not available from yfinance directly)
        st.markdown(f"**Short Interest Score:** Not Available (Requires external source)")

        # Institutional Ownership
        inst_own = info.get("heldPercentInstitutions", 0) or 0
        if inst_own >= 0.6:
            inst_score = 10
        elif inst_own >= 0.3:
            inst_score = 5
        else:
            inst_score = 0
        st.markdown(f"**Institutional Ownership Score:** {inst_score} (Ownership: {inst_own*100:.1f}%)")

        # Shareholder Return vs S&P500 (placeholder)
        st.markdown(f"**5-Year Relative Returns vs S&P500:** Placeholder (manual input or alpha_vantage)")

        # Scalability (requires comparison between revenue and opex)
        st.markdown("**Scalability Score:** Placeholder (needs revenue vs OpEx data)")

    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
