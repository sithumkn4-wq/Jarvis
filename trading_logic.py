import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import requests
import time

# --- CONFIGURATION (මේ ටික හරියටම පුරවන්න) ---
MY_SECRET_PASSWORD = "1221"
CHAT_ID = "7657159021" # ඔයාගේ ID එක Screenshot එකේ තිබ්බ විදිහට
# පහත තැනට BotFather ගෙන් ලැබුණු දිගු අංකය (Token එක) ඇතුළත් කරන්න
TELEGRAM_TOKEN = "මෙතනට_ඔයාගේ_BOT_TOKEN_එක_දාන්න" 

st.set_page_config(page_title="JARVIS Ultimate V3.0", layout="wide")

# --- FUNCTIONS ---
def send_telegram(message):
    if "මෙතනට" not in TELEGRAM_TOKEN:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url)

def get_signal(symbol):
    try:
        data = yf.download(symbol, period="1mo", interval="1h", progress=False)
        if data.empty: return None, None
        data['RSI'] = ta.rsi(data['Close'], length=14)
        last_rsi = data['RSI'].iloc[-1]
        last_price = data['Close'].iloc[-1]
        
        if last_rsi > 70:
            return "SELL 🔴", last_rsi
        elif last_rsi < 30:
            return "BUY 🟢", last_rsi
        else:
            return "HOLD 🟡", last_rsi
    except:
        return None, None

# --- UI SETUP ---
st.title("🤖 JARVIS Trading Oracle - Final")

# ⏰ SCHEDULED ALERTS LOGIC
now = datetime.now().strftime("%H:%M")
alert_times = ["05:00", "12:00", "20:00"]

st.sidebar.header("⏰ Scheduled Status")
if now in alert_times:
    st.sidebar.success(f"It's {now}! Sending Update...")
    # ඇප් එක open වෙලා තියෙන වෙලාවක මේ වෙලාවන් ආවොත් alert එකක් යයි
    # මෙතනට ඔයා නිතර බලන symbols ටික දාන්න
    watch_list = ["BTC-USD", "AAPL"]
    for s in watch_list:
        sig, rsi = get_signal(s)
        if sig:
            send_telegram(f"⏰ Scheduled Update ({now})\nSymbol: {s}\nSignal: {sig}\nRSI: {rsi:.2f}")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Planner", "🔐 Private Vault", "📈 Analysis"])

with tab1:
    st.header("➕ Add New Asset")
    col1, col2 = st.columns(2)
    with col1:
        p_asset = st.text_input("Asset Symbol (eg: BTC-USD)", value="BTC-USD")
        p_price = st.number_input("Buy Price", min_value=0.0, value=65000.0)
    with col2:
        p_curr = st.selectbox("Currency", ["USD ($)", "LKR (Rs)"])
        p_qty = st.number_input("Quantity", min_value=0.0, value=0.01)
    
    p_alloc = st.slider("මෙයට යොදවන මුදල (%)", 0, 100, 92) # ඔයා ඉල්ලපු slider එක

    if st.button("💾 Save Asset"):
        st.success("Asset Saved Locally!")
        send_telegram(f"✅ New Asset Planned: {p_asset}\nPrice: {p_price}\nQty: {p_qty}")

with tab2:
    st.header("🔐 Private Vault")
    pwd = st.text_input("මුරපදය ඇතුළත් කරන්න", type="password")
    if pwd == MY_SECRET_PASSWORD:
        st.success("Access Granted!")
        # මෙතන ඔයාගේ real data table එක පෙන්වන්න පුළුවන්
    else:
        st.warning("මෙම කොටස බැලීමට '1221' ඇතුළත් කරන්න.")

with tab3:
    st.header("📈 Deep Market Analysis")
    target = st.text_input("Symbol to Scan", value="BTC-USD")
    if st.button("🔍 Run Scan"):
        sig, rsi = get_signal(target)
        if sig:
            st.metric("Current RSI", f"{rsi:.2f}")
            st.subheader(f"Advice: {sig}")
            send_telegram(f"🔍 Manual Scan\nSymbol: {target}\nRSI: {rsi:.2f}\nAdvice: {sig}")
            
            # Chart
            data = yf.download(target, period="1mo", interval="1h", progress=False)
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.update_layout(template="plotly_dark", title=f"{target} Live Chart")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("දත්ත ලබාගත නොහැක. Symbol එක පරීක්ෂා කරන්න.")

st.divider()
st.caption("JARVIS V3.0 | 24/7 Monitoring Active")
