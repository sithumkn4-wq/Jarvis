import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- CONFIGURATION ---
MY_PASSWORD = "1221"
MY_CHAT_ID = "7657159021"
# BotFather ගෙන් ලැබුණු Token එක මෙතනට දාන්න
BOT_TOKEN = "මෙතනට_ඔයාගේ_BOT_TOKEN_එක_දාන්න"

st.set_page_config(page_title="JARVIS ULTIMATE", layout="wide")

# --- TELEGRAM FUNCTION ---
def send_bot_msg(text):
    if "මෙතනට" not in BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={MY_CHAT_ID}&text={text}"
            requests.get(url)
        except:
            pass

# --- RSI CALCULATION (Manual to avoid install errors) ---
def get_rsi(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1h", progress=False)
        if df.empty: return None
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except:
        return None

# --- UI ---
st.title("🤖 JARVIS Trading System V3")

# ⏰ SCHEDULED CHECK (App එක Open වෙලාවට වැඩ කරයි)
now = datetime.now().strftime("%H:%M")
scheduled_times = ["05:00", "12:00", "20:00"]

if now in scheduled_times:
    st.warning(f"⏰ Scheduled Time: {now}. Sending Alert...")
    # උදාහරණයක් ලෙස BTC බලමු
    current_rsi = get_rsi("BTC-USD")
    if current_rsi:
        msg = f"⏰ JARVIS TIME CHECK ({now})\nAsset: BTC-USD\nRSI: {current_rsi:.2f}"
        send_bot_msg(msg)

# TABS
tab1, tab2, tab3 = st.tabs(["📊 Portfolio", "🔐 Private Vault", "📈 Live Scan"])

with tab1:
    st.header("📋 Portfolio Planner")
    asset = st.text_input("Asset Symbol", "BTC-USD")
    alloc = st.slider("යොදවන මුදල (%)", 0, 100, 92)
    if st.button("Save to Practice"):
        st.success(f"{asset} Saved at {alloc}%")
        send_bot_msg(f"✅ Practice Saved: {asset} ({alloc}%)")

with tab2:
    st.header("🔐 Secure Vault")
    pw = st.text_input("Password", type="password")
    if pw == MY_PASSWORD:
        st.success("Access Granted")
        st.write("ඔබගේ රහස්‍ය තොරතුරු මෙතනට...")
    elif pw != "":
        st.error("වැරදි මුරපදයකි")

with tab3:
    st.header("📈 Market Intelligence")
    scan_target = st.text_input("Symbol to Analyze", "AAPL")
    if st.button("Deep Scan"):
        rsi_val = get_rsi(scan_target)
        if rsi_val:
            st.metric(f"{scan_target} RSI", f"{rsi_val:.2f}")
            advice = "Neutral"
            if rsi_val > 70: advice = "SELL 🔴"
            elif rsi_val < 30: advice = "BUY 🟢"
            st.subheader(f"Advice: {advice}")
            send_bot_msg(f"🔍 Scan Result: {scan_target}\nRSI: {rsi_val:.2f}\nAdvice: {advice}")
            
            # Chart
            chart_data = yf.download(scan_target, period="1mo", interval="1h", progress=False)
            fig = go.Figure(data=[go.Candlestick(x=chart_data.index, open=chart_data['Open'], high=chart_data['High'], low=chart_data['Low'], close=chart_data['Close'])])
            fig.update_layout(template="plotly_dark", title=f"{scan_target} Market View")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("දත්ත ලබාගත නොහැක. Symbol එක පරීක්ෂා කරන්න.")
