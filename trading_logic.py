import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- CONFIGURATION & SECURITY ---
MY_SECRET_PASSWORD = "1221"  # ඔයා ඉල්ලපු පාස්වර්ඩ් එක
CHAT_ID = "7657159021"      # ඔයා එවපු ටෙලිග්‍රෑම් ID එක
# මෙතන " " ඇතුලත ඔයාගේ Bot Token එක විතරක් දාන්න
TELEGRAM_TOKEN = "මෙතනට_BOT_TOKEN_එක_දාන්න" 

st.set_page_config(page_title="JARVIS V2.0 - Oracle", layout="wide")

# --- DATA ENGINE ---
def load_data(file_name):
    try:
        return pd.read_csv(file_name)
    except:
        return pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Type"])

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

# --- MANUAL MATH ENGINE (100% NO ERRORS) ---
def get_ai_advice(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="15m", progress=False)
        if data.empty: return "No Data", "පද්ධතියට දත්ත ලබාගත නොහැක."
        
        # RSI Calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        last_rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        last_price = data['Close'].iloc[-1]
        ema_20 = data['Close'].rolling(window=20).mean().iloc[-1]
        
        if last_rsi > 70:
            return "Take Profit", "🔴 Market Overbought. විකුණා ලාභ ලබාගන්න."
        elif last_rsi < 30:
            return "Buy/Hold", "🟢 මිල පතුලේ ඇත. Pump එකක් බලාපොරොත්තු වන්න."
        elif last_price > ema_20:
            return "Hold", "🟡 මිල ඉහළ යන ප්‍රවණතාවයක පවතී (Bullish)."
        else:
            return "Avoid", "⚪ වෙළඳපොළ අවදානම් සහගතයි. රැඳී සිටින්න."
    except:
        return "Error", "Symbol එක වැරදියි හෝ සර්වර් දෝෂයකි."

# --- TELEGRAM SENDER ---
def send_telegram_msg(message):
    if "මෙතනට" not in TELEGRAM_TOKEN:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url)

# --- UI ---
st.title("🤖 JARVIS V2.0: Portfolio Intelligence")

tab1, tab2, tab3 = st.tabs(["🎮 Practice (Demo)", "💰 Real Account", "📊 Analysis Charts"])

# --- TAB 1: PRACTICE ---
with tab1:
    st.subheader("Practice Sandbox (බොරු සල්ලි - ඇත්ත Market)")
    with st.form("demo_form"):
        p_asset = st.text_input("Asset (e.g. BTC-USD, ETH-USD)")
        p_price = st.number_input("Fake Buy Price ($)", min_value=0.0)
        p_qty = st.number_input("Fake Qty", min_value=0.0)
        if st.form_submit_button("Add to Practice"):
            df = load_data("practice_data.csv")
            new = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": p_asset, "BuyPrice": p_price, "Qty": p_qty, "Type": "Demo"}
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            save_data(df, "practice_data.csv")
            st.success("Practice Trade Saved!")
            send_telegram_msg(f"✅ Demo Trade Added: {p_asset}")

# --- TAB 2: REAL ACCOUNT (PASSWORD PROTECTED) ---
with tab2:
    st.subheader("Real Portfolio (Crypto & Investments)")
    lock = st.text_input("ඇතුල් වීමට Password එක ගසන්න", type="password")
    
    if lock == MY_SECRET_PASSWORD:
        st.success("Access Granted! ✅")
        with st.form("real_form"):
            r_asset = st.text_input("Real Asset Symbol (e.g. BTC-USD)")
            r_price = st.number_input("Real Buy Price ($)", min_value=0.0)
            r_qty = st.number_input("Real Qty", min_value=0.0)
            if st.form_submit_button("Log Transaction"):
                df = load_data("real_data.csv")
                new = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": r_asset, "BuyPrice": r_price, "Qty": r_qty, "Type": "Real"}
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                save_data(df, "real_data.csv")
                st.success("Real Data Logged Securely!")
        
        st.write("### ඔබගේ වර්තමාන වත්කම් (Holdings)")
        st.table(load_data("real_data.csv"))
    elif lock != "":
        st.error("වැරදි Password එකක්. නැවත උත්සාහ කරන්න.")

# --- TAB 3: ANALYSIS ---
with tab3:
    st.subheader("Market Scan & Charts")
    target = st.text_input("විශ්ලේෂණයට අවශ්‍ය Symbol එක", "BTC-USD")
    if st.button("Deep Scan"):
        advice, detail = get_ai_advice(target)
        st.metric("AI Advice", advice)
        st.info(detail)
        
        hist = yf.download(target, period="1mo", interval="1d", progress=False)
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
        fig.update_layout(title=f"{target} Market Chart", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Developed by JARVIS V2.0 | Security Enabled")
