import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Evaluation Scorecard", layout="wide")

st.title("📊 Stock Evaluation Scorecard")
ticker = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        st.subheader(f"{info.get('longName', 'Unknown Company')} ({ticker.upper()})")
        st.markdown(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")

        st.header("Objective Metrics (Auto-Fetched)")

        # Cash vs Debt Score
        total_cash = info.get("totalCash", 0)
        total_debt = info.get("totalDebt", 0)
        if total_cash > 2 * total_debt:
            cash_score = 10
        elif total_cash > total_debt:
            cash_score = 5
        else:
            cash_score = 0
        st.markdown(f"**Cash vs Debt Score:** {cash_score} (Cash: {total_cash:,}, Debt: {total_debt:,})")

        # Revenue Growth Score
        try:
            rev_ttm = info.get("totalRevenue")
            prev_rev = info.get("previousRevenue") or (rev_ttm / (1 + 0.1))  # fallback
            revenue_growth = ((rev_ttm - prev_rev) / prev_rev) * 100
            if revenue_growth > 20:
                rev_score = 10
            elif revenue_growth > 10:
                rev_score = 5
            else:
                rev_score = 0
            st.markdown(f"**Revenue Growth Score:** {rev_score} (Growth: {revenue_growth:.2f}%)")
        except:
            st.markdown("**Revenue Growth Score:** Not Available")

        # Operating Margin Score
        margin = info.get("operatingMargins", 0)
        if margin > 0.25:
            margin_score = 10
        elif margin > 0.1:
            margin_score = 5
        else:
            margin_score = 0
        st.markdown(f"**Operating Margin Score:** {margin_score} (Operating Margin: {margin * 100:.2f}%)")

        # Short Interest Placeholder
        st.markdown("**Short Interest Score:** Not Available (Requires external source)")

        # Institutional Ownership
        ownership = info.get("heldPercentInstitutions", 0)
        if ownership > 0.6:
            inst_score = 10
        elif ownership > 0.3:
            inst_score = 5
        else:
            inst_score = 0
        st.markdown(f"**Institutional Ownership Score:** {inst_score} (Ownership: {ownership * 100:.1f}%)")

        # 5Y Relative Returns Placeholder
        st.markdown("**5-Year Relative Returns vs S&P500:** Placeholder (manual input or alpha_vantage)")

        # Scalability Placeholder
        st.markdown("**Scalability Score:** Placeholder (needs revenue vs OpEx data)")

        st.header("Subjective Inputs 🧠")
        moat = st.slider("Moat", 0, 10, 0)
        ceo = st.slider("CEO", 0, 10, 0)
        recession = st.slider("Recession Resistance", 0, 10, 0)
        trend = st.slider("Trend Alignment", 0, 10, 0)
        culture = st.slider("Culture Fit", 0, 10, 0)
        talent = st.slider("Talent Quality", 0, 10, 0)

        total = sum([cash_score, rev_score, margin_score, inst_score, moat, ceo, recession, trend, culture, talent])
        st.subheader(f"📈 **Total Score: {total}/100**")

    except Exception as e:
        st.error(f"Error retrieving data for {ticker}: {e}")
