import streamlit as st
import yfinance as yf
import pandas as pd
import os
import requests
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION & DATABASE ---
# ඔයා එවපු රූපයේ තිබූ දත්ත මෙහි ඇතුළත් කර ඇත
DB_FILE = "oracle_final_database.csv"
TELEGRAM_TOKEN = "7508933256:AAEv1p7W-u_E8F9lX7i_E6I7r8o" 
CHAT_ID = "7154215286"

st.set_page_config(page_title="JARVIS Trading Oracle v23", layout="wide")

# 1. ස්තීර මතකය (CSV Persistence)
def load_db():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Asset", "BuyPrice", "Qty", "Currency", "Date"])

def save_db(df): df.to_csv(DB_FILE, index=False)

# 2. මුදල් පරිවර්තන මොඩියුලය (LKR to USD Math)
@st.cache_data(ttl=3600)
def get_lkr_rate():
    try:
        data = yf.Ticker("USDLKR=X").history(period="1d")
        return float(data['Close'].iloc[-1])
    except: return 325.0 

# 3. ප්‍රධාන ගණිත මොළය (RSI & Prediction Engine)
def get_market_insight(symbol):
    try:
        s = symbol.strip().upper()
        if s == "DJI": s = "^DJI"
        ticker = yf.Ticker(s)
        hist = ticker.history(period='1mo')
        if hist.empty: return None, None, None, None
        
        curr_p = float(hist['Close'].iloc[-1])
        
        # RSI Math
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Time Window Prediction Logic
        prev_rsi = 100 - (100 / (1 + (gain / loss).iloc[-2]))
        momentum = rsi - prev_rsi
        
        if rsi > 70:
            window = "වහාම විකුණන්න (පැය කිහිපයකින් මිල බැසීමට ඉඩ ඇත)" if momentum > 0 else "මිල දැනටමත් බැසීමට පටන් ගෙන ඇත"
        elif rsi < 30:
            window = "මිලදී ගැනීමට සුපිරි අවස්ථාවක් (දින 1-2ක් පවතිනු ඇත)"
        else:
            window = "වෙළඳපොළ ස්ථාවරයි (දින කිහිපයක් පවතිනු ඇත)"
            
        return curr_p, rsi, window, hist
    except: return None, None, None, None

# 4. Mobile Alert System
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    try: requests.get(url)
    except: pass

# --- UI INTERFACE ---
st.title("🏆 JARVIS AI Trading Oracle - Final v23.0")

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_db()

# SIDEBAR: Wallet & Currency Settings
st.sidebar.header("💰 Wallet & Exchange")
currency_type = st.sidebar.selectbox("මුදල් වර්ගය තෝරන්න", ["USD ($)", "LKR (Rs.)"])
raw_balance = st.sidebar.number_input(f"මුළු මුදල ({currency_type})", value=1000.0)

# Currency Logic
current_rate = get_lkr_rate()
usd_balance = raw_balance / current_rate if "LKR" in currency_type else raw_balance

st.sidebar.write(f"**USD අගය:** ${usd_balance:,.2f}")
if "LKR" in currency_type: st.sidebar.caption(f"අද දින අනුපාතය: $1 = Rs.{current_rate:.2f}")

enable_alerts = st.sidebar.toggle("Enable Phone Alerts")

tab1, tab2 = st.tabs(["📋 Portfolio Planner", "🔮 Intelligence & Live Charts"])

# TAB 1: SMART ALLOCATION
with tab1:
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.subheader("✚ Add New Asset")
        asset = st.text_input("Asset Symbol (eg: TSLA, AAPL, ^DJI)").upper()
        risk_pct = st.slider("මෙයට යොදවන මුදල (%)", 1, 100, 20)
        
        if asset:
            price, rsi, win, _ = get_market_insight(asset)
            if price:
                max_to_spend = usd_balance * (risk_pct / 100)
                qty = int(max_to_spend / price)
                
                st.info(f"වත්මන් මිල: ${price:,.2f}")
                st.success(f"ඔබට ගත හැකි ප්‍රමාණය: {qty} Shares")
                
                if st.button("Confirm Purchase"):
                    new_data = pd.DataFrame({
                        "Asset": [asset], "BuyPrice": [price], "Qty": [qty], 
                        "Currency": [currency_type], "Date": [datetime.now().strftime("%Y-%m-%d")]
                    })
                    st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_data], ignore_index=True)
                    save_db(st.session_state.portfolio)
                    st.rerun()

    with col2:
        st.subheader("Saved Memory")
        st.dataframe(st.session_state.portfolio, use_container_width=True)

# TAB 2: MONITORING, PREDICTION & CHARTS
with tab2:
    if not st.session_state.portfolio.empty:
        for i, row in st.session_state.portfolio.iterrows():
            price, rsi, win, history = get_market_insight(row['Asset'])
            if price:
                profit = (price - row['BuyPrice']) * row['Qty']
                
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.markdown(f"### {row['Asset']}")
                        st.metric("Live Profit", f"${profit:,.2f}", delta=f"{rsi:.1f} RSI")
                        
                        if rsi > 68:
                            st.error(f"🚨 SELL SIGNAL: {win}")
                            if enable_alerts:
                                send_telegram(f"🔮 JARVIS Alert: {row['Asset']}\nProfit: ${profit:,.2f}\nTime: {win}")
                        else:
                            st.write(f"💡 Prediction: {win}")
                    
                    with c2:
                        fig = go.Figure(data=[go.Candlestick(x=history.index, open=history['Open'], 
                                        high=history['High'], low=history['Low'], close=history['Close'])])
                        fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("පළමුව Portfolio එකට Asset එකක් එකතු කරන්න.")

if st.button("🗑️ Full System Reset"):
    st.session_state.portfolio = pd.DataFrame(columns=["Asset", "BuyPrice", "Qty", "Currency", "Date"])
    save_db(st.session_state.portfolio)
    st.rerun()