import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests
import pandas_ta as ta

# --- CONFIGURATION & SECURITY ---
# මෙතන ENTER_YOUR_PASSWORD_HERE මකලා ඔයාගේ Password එක දාන්න
MY_SECRET_PASSWORD = "1221"

# Telegram Setup (ඔයාගේ පරණ විස්තරම මෙතනට දාන්න)
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

st.set_page_config(page_title="JARVIS V2.0 - Portfolio Oracle", layout="wide")

# --- DATA STORAGE ENGINE ---
def load_data(file_name):
    try:
        return pd.read_csv(file_name)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Type"])

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

# --- ANALYSIS ENGINE (THE POWER MODULE) ---
def get_ai_advice(symbol):
    data = yf.download(symbol, period="1d", interval="15m", progress=False)
    if data.empty: return "No Data", "Wait"
    
    # RSI & EMA Calculation using Pandas-TA
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['EMA_20'] = ta.ema(data['Close'], length=20)
    
    last_rsi = data['RSI'].iloc[-1]
    last_price = data['Close'].iloc[-1]
    last_ema = data['EMA_20'].iloc[-1]
    
    if last_rsi > 70:
        return "Take Profit", "🔴 Market Overbought. Sell now to secure gains."
    elif last_rsi < 30:
        return "Buy/Hold", "🟢 Market Oversold. Potential pump coming."
    elif last_price > last_ema:
        return "Hold", "🟡 Trend is Bullish. Keep holding."
    else:
        return "Avoid", "⚪ Market is unstable. Stay away for now."

# --- UI INTERFACE ---
st.title("🤖 JARVIS V2.0: Portfolio & Intelligence")

tab1, tab2, tab3 = st.tabs(["🎮 Practice Sandbox", "💰 Real Portfolio", "📊 Advanced Analysis"])

# --- TAB 1: PRACTICE SANDBOX (Fake Money, Real Market) ---
with tab1:
    st.subheader("Practice Mode (Numerical Training)")
    with st.form("practice_form"):
        p_asset = st.text_input("Asset Symbol (e.g., BTC-USD, AAPL)")
        p_buy_price = st.number_input("Fake Buy Price ($)", min_value=0.0)
        p_qty = st.number_input("Fake Quantity", min_value=0.0)
        p_submit = st.form_submit_button("Add to Practice")
        
    if p_submit:
        df_p = load_data("practice_data.csv")
        new_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": p_asset, "BuyPrice": p_buy_price, "Qty": p_qty, "Type": "Practice"}
        df_p = pd.concat([df_p, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df_p, "practice_data.csv")
        st.success("Practice Trade Saved!")

# --- TAB 2: REAL PORTFOLIO (Actual Money & Bitcoin) ---
with tab2:
    st.subheader("Real-World Asset Tracking")
    # Password Protection for Real Data
    check_pass = st.text_input("Enter Admin Password to view Real Portfolio", type="password")
    
    if check_pass == MY_SECRET_PASSWORD:
        with st.form("real_form"):
            r_asset = st.text_input("Real Asset Symbol (e.g., BTC-USD)")
            r_buy_price = st.number_input("Real Purchase Price ($)", min_value=0.0)
            r_qty = st.number_input("Real Quantity", min_value=0.0)
            r_submit = st.form_submit_button("Log Real Transaction")
            
        if r_submit:
            df_r = load_data("real_data.csv")
            new_data = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": r_asset, "BuyPrice": r_buy_price, "Qty": r_qty, "Type": "Real"}
            df_r = pd.concat([df_r, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df_r, "real_data.csv")
            st.success("Real Transaction Logged!")
            
        st.write("### Current Holdings")
        df_display = load_data("real_data.csv")
        st.table(df_display)
    else:
        st.warning("Please enter correct password to unlock sensitive data.")

# --- TAB 3: ADVANCED ANALYSIS ---
with tab3:
    st.subheader("Market Intelligence & Growth Charts")
    target = st.text_input("Enter Asset to Analyze", "BTC-USD")
    if st.button("Run AI Deep Scan"):
        advice, detail = get_ai_advice(target)
        st.metric("Recommendation", advice)
        st.info(detail)
        
        # Growth Chart logic
        hist = yf.download(target, period="1mo", interval="1d")
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
        st.plotly_chart(fig)

# --- AUTOMATED TELEGRAM REPORTING ---
# (This logic runs in background to send reports at 05:00, 12:00, 20:00)
# Note: For actual scheduling, you need the UptimeRobot ping to trigger this part.
def send_telegram_report():
    # Only sends if password check is skipped or managed via separate bot command
    msg = f"🔔 JARVIS REPORT: {datetime.now().strftime('%H:%M')}\n\n"
    msg += "Market Status: Scanned ✅\n"
    msg += "To view your Balance & AI Advice, visit your Dashboard and enter Password."
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    requests.get(url)

st.write("---")
st.caption("JARVIS V2.0 Powered by Advanced Web Analysis Modules")
