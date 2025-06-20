
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Evaluation Scorecard", layout="wide")

st.title("Stock Evaluation Scorecard")

# Initialize session state for ticker tracking
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = ""

# Ticker input
ticker = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, NVDA):", "")

# If ticker has changed, reset sliders
if ticker != st.session_state.last_ticker:
    st.session_state.moat = 0
    st.session_state.ceo = 0
    st.session_state.recession = 0
    st.session_state.trend = 0
    st.session_state.culture = 0
    st.session_state.talent = 0
    st.session_state.relative_returns = 0
    st.session_state.last_ticker = ticker

if ticker:
    # Fetch objective data from yfinance
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        st.subheader(f"{info['shortName']} ({ticker.upper()})")
        st.write(f"Market Cap: {info.get('marketCap', 'N/A')}")
        st.write(f"Sector: {info.get('sector', 'N/A')}")
    except:
        st.error("Invalid Ticker or Data not available.")

    # Subjective sliders
    st.subheader("Subjective Inputs")

    moat = st.slider("Moat", 0, 10, st.session_state.moat)
    st.session_state.moat = moat

    ceo = st.slider("CEO", 0, 10, st.session_state.ceo)
    st.session_state.ceo = ceo

    recession = st.slider("Recession Resistance", 0, 10, st.session_state.recession)
    st.session_state.recession = recession

    trend = st.slider("Trend Alignment", 0, 10, st.session_state.trend)
    st.session_state.trend = trend

    culture = st.slider("Culture Fit", 0, 10, st.session_state.culture)
    st.session_state.culture = culture

    talent = st.slider("Talent Quality", 0, 10, st.session_state.talent)
    st.session_state.talent = talent

    relative_returns = st.slider("5-Year Relative Returns vs S&P500 (%)", -50, 50, st.session_state.relative_returns)
    st.session_state.relative_returns = relative_returns

    # Convert relative returns to score
    if relative_returns >= 20:
        returns_score = 10
    elif 10 <= relative_returns < 20:
        returns_score = 5
    else:
        returns_score = 0

    total_score = sum([
        moat, ceo, recession, trend, culture, talent, returns_score
    ])

    # Assign action based on total score
    if total_score >= 75:
        action = "BUY"
    elif 50 <= total_score < 75:
        action = "WATCH"
    else:
        action = "DROP"

    st.subheader("Evaluation Result")
    st.write(f"Total Score: {total_score}/100")
    st.write(f"Action: **{action}**")
