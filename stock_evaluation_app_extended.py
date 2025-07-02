
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Evaluation Scorecard", layout="wide")

st.title("📊 Stock Evaluation Scorecard")
ticker_input = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):", value="NVDA")

if ticker_input:
    ticker = yf.Ticker(ticker_input.upper())
    info = ticker.info

    name = info.get("longName", "Unknown Company")
    market_cap = info.get("marketCap", "N/A")
    sector = info.get("sector", "N/A")

    st.markdown(f"### {name} ({ticker_input.upper()})")
    st.markdown(f"**Market Cap:** {market_cap:,}" if isinstance(market_cap, int) else "**Market Cap:** N/A")
    st.markdown(f"**Sector:** {sector}")

    # Objective Metrics
    st.markdown("## Objective Metrics (Auto-Fetched)")

    # Cash vs Debt
    cash = info.get("totalCash", 0)
    debt = info.get("totalDebt", 0)
    if cash > 2 * debt:
        score_cash_debt = 10
    elif cash > debt:
        score_cash_debt = 5
    else:
        score_cash_debt = 0
    st.markdown(f"**Cash vs Debt Score:** {score_cash_debt} (Cash: {cash:,}, Debt: {debt:,})")

    # Revenue Growth
    try:
        hist = ticker.history(period="5y")
        rev_growth = (hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0] * 100
        if rev_growth > 20:
            score_growth = 10
        elif rev_growth > 10:
            score_growth = 5
        else:
            score_growth = 0
        st.markdown(f"**Revenue Growth Score:** {score_growth} (Growth: {rev_growth:.2f}%)")
    except Exception:
        score_growth = 0
        st.markdown("**Revenue Growth Score:** Not Available")

    # Operating Margin
    op_margin = info.get("operatingMargins", 0)
    if op_margin > 0.25:
        score_margin = 10
    elif op_margin > 0.10:
        score_margin = 5
    else:
        score_margin = 0
    st.markdown(f"**Operating Margin Score:** {score_margin} (Operating Margin: {op_margin*100:.2f}%)")

    # Short Interest Score (placeholder)
    st.markdown("**Short Interest Score:** Not Available (Requires external source)")

    # Institutional Ownership
    ownership = info.get("heldPercentInstitutions", 0)
    if ownership > 0.60:
        score_inst = 10
    elif ownership > 0.30:
        score_inst = 5
    else:
        score_inst = 0
    st.markdown(f"**Institutional Ownership Score:** {score_inst} (Ownership: {ownership*100:.1f}%)")

    # 5-Year Relative Returns (Manual input or API)
    st.markdown("**5-Year Relative Returns vs S&P500:**")
    rel_return = st.slider("Input manually (% over/under S&P500)", -50, 50, 0)
    if rel_return > 20:
        score_rel = 10
    elif rel_return > 10:
        score_rel = 5
    else:
        score_rel = 0
    st.markdown(f"Relative Return Score: {score_rel} (User input: {rel_return}%)")

    # Scalability: Revenue vs OpEx (Placeholder logic)
    st.markdown("**Scalability Score (Revenue vs OpEx):**")
    revenue_growth = st.slider("Revenue Growth (%)", 0, 100, 20)
    opex_growth = st.slider("OpEx Growth (%)", 0, 100, 20)
    if revenue_growth > opex_growth:
        score_scalability = 10
    else:
        score_scalability = 0
    st.markdown(f"Scalability Score: {score_scalability} (Revenue: {revenue_growth}%, OpEx: {opex_growth}%)")
