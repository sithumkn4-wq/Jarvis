import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- ⚙️ JARVIS CONFIGURATION ---
MY_PASSWORD = "1221"
MY_CHAT_ID = "7657159021"
BOT_TOKEN = "8878579463:AAGfwmj-jmUCBab5VwXjxWpYsrW9z3VyK3o"

st.set_page_config(page_title="JARVIS PRO v3.5", layout="wide")

# --- 📱 TELEGRAM FUNCTION ---
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={MY_CHAT_ID}&text={message}"
        requests.get(url)
        return True
    except:
        return False

# --- 📊 ADVANCED MATH MODULE (RSI & CHANGES) ---
def get_market_analysis(symbol):
    try:
        df = yf.download(symbol, period="1mo", interval="1h", progress=False)
        if df.empty: return None
        
        # 1. RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 2. Price Stats
        current_price = df['Close'].iloc[-1]
        open_price = df['Open'].iloc[0]
        price_change = ((current_price - open_price) / open_price) * 100
        
        return {
            "rsi": rsi.iloc[-1],
            "price": current_price,
            "change": price_change,
            "df": df
        }
    except:
        return None

# --- 🎨 UI DESIGN ---
st.title("🤖 JARVIS PRO - Advanced Trading Engine")

# --- 🚀 TELEGRAM TEST ---
with st.expander("📡 System Connectivity"):
    if st.button("🚀 Test Bot Connection"):
        if send_telegram("✅ JARVIS Intelligence System: Online & Synchronized."):
            st.success("Telegram Connection: ACTIVE")
        else:
            st.error("Telegram Connection: FAILED")

st.divider()

# --- ⏰ SCHEDULED ALERTS ---
now = datetime.now().strftime("%H:%M")
if now in ["05:00", "12:00", "20:00"]:
    analysis = get_market_analysis("BTC-USD")
    if analysis:
        msg = f"⏰ JARVIS SCHEDULED CHECK ({now})\nAsset: BTC-USD\nPrice: ${analysis['price']:.2f}\nRSI: {analysis['rsi']:.2f}\nChange: {analysis['change']:.2f}%"
        send_telegram(msg)

# --- 🗂️ MAIN MODULES ---
tab1, tab2, tab3 = st.tabs(["📋 Portfolio Management", "🔐 Secure Vault", "📈 Market Intelligence"])

with tab1:
    st.header("➕ Asset Planner")
    col1, col2, col3 = st.columns(3)
    with col1:
        asset = st.text_input("Asset Symbol", "BTC-USD")
    with col2:
        buy_p = st.number_input("Target Buy Price", value=65000.0)
    with col3:
        qty = st.number_input("Quantity", value=0.01)
    
    alloc = st.slider("Allocation Percentage (%)", 0, 100, 92)
    
    if st.button("💾 Save to Memory"):
        st.success(f"Successfully planned {asset} at {alloc}% allocation.")
        send_telegram(f"📝 Planning Update:\nAsset: {asset}\nAllocation: {alloc}%")

with tab2:
    st.header("🔐 Secure Private Vault")
    pw = st.text_input("Enter Access Key", type="password")
    if pw == MY_PASSWORD:
        st.success("Identity Verified.")
        st.info("ඔබේ සියලුම පෞද්ගලික ගනුදෙනු විස්තර මෙහි සුරක්ෂිතව පවතී.")
        # මෙතනට ඔයාගේ table එක දාන්න පුළුවන්
    elif pw != "":
        st.error("Access Denied: Invalid Password.")

with tab3:
    st.header("📈 Deep Market Analysis")
    target = st.text_input("Enter Symbol (BTC-USD, TSLA, AAPL)", "BTC-USD")
    if st.button("🔍 Run Advanced Scan"):
        with st.spinner("Calculating Mathematical Models..."):
            res = get_market_analysis(target)
            if res:
                c1, c2, c3 = st.columns(3)
                c1.metric("Live Price", f"${res['price']:.2f}", f"{res['change']:.2f}%")
                c2.metric("RSI (14h)", f"{res['rsi']:.2f}")
                
                advice = "HOLD 🟡"
                if res['rsi'] > 70: advice = "SELL 🔴 (Overbought)"
                elif res['rsi'] < 30: advice = "BUY 🟢 (Oversold)"
                c3.metric("AI Advice", advice)

                # Charting
                fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
                fig.update_layout(template="plotly_dark", title=f"{target} Analysis Chart")
                st.plotly_chart(fig, use_container_width=True)
                
                send_telegram(f"🔍 Scan Report: {target}\nPrice: ${res['price']:.2f}\nRSI: {res['rsi']:.2f}\nAdvice: {advice}")
            else:
                st.error("Error retrieving market data.")

st.divider()
st.caption("JARVIS PRO v3.5 | Mathematical Trading Module Active")
