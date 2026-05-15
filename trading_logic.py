import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- CONFIGURATION ---
MY_SECRET_PASSWORD = "1221"  # ඔයාගේ Password එක
CHAT_ID = "7657159021"      # ඔයාගේ Telegram ID එක
TELEGRAM_TOKEN = "මෙතනට_ඔයාගේ_BOT_TOKEN_එක_දාන්න" 

st.set_page_config(page_title="JARVIS V2.5 PRO", layout="wide")

# --- DATA FUNCTIONS ---
def load_data(file):
    try:
        return pd.read_csv(file)
    except:
        return pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Allocation %", "Currency"])

def save_data(df, file):
    df.to_csv(file, index=False)

# --- TELEGRAM FUNCTION ---
def send_msg(text):
    if "මෙතනට" not in TELEGRAM_TOKEN:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
        requests.get(url)

# --- UI START ---
st.title("🤖 JARVIS V2.5 PRO")

tab1, tab2, tab3 = st.tabs(["📋 Portfolio Planner", "🔐 Real Account", "📈 Analysis & Bot"])

# --- TAB 1: PLANNER ---
with tab1:
    st.header("➕ Add New Asset")
    col1, col2 = st.columns(2)
    with col1:
        p_asset = st.text_input("Asset Symbol (eg: BTC-USD, AAPL)")
    with col2:
        p_curr = st.selectbox("Currency", ["USD ($)", "LKR (Rs)"])
    
    p_price = st.number_input("Buy Price", min_value=0.0, value=298.21)
    p_qty = st.number_input("Quantity", min_value=0.0, value=2.0)
    p_alloc = st.slider("Allocation (%)", 0, 100, 92)
    
    if st.button("💾 Save Asset"):
        df = load_data("practice.csv")
        new = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": p_asset, "BuyPrice": p_price, "Qty": p_qty, "Allocation %": p_alloc, "Currency": p_curr}
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        save_data(df, "practice.csv")
        st.success("Saved!")
        send_msg(f"✅ JARVIS: New asset added - {p_asset}")

    st.subheader("📋 Saved History")
    st.dataframe(load_data("practice.csv"), use_container_width=True)
    
    if st.button("🗑️ Reset All"):
        save_data(pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Allocation %", "Currency"]), "practice.csv")
        st.rerun()

# --- TAB 2: REAL ACCOUNT ---
with tab2:
    st.header("🔐 Secure Vault")
    lock = st.text_input("Password එක ඇතුලත් කරන්න", type="password")
    if lock == MY_SECRET_PASSWORD:
        st.success("Access Granted!")
        st.dataframe(load_data("real.csv"), use_container_width=True)
    else:
        st.warning("Locked. Enter 1221.")

# --- TAB 3: ANALYSIS & BOT (දැන් මේක වැඩ!) ---
with tab3:
    st.header("📈 AI Analysis Engine")
    target = st.text_input("Analyze Symbol", "BTC-USD")
    
    if st.button("🔍 Run Deep Scan"):
        with st.spinner("Analyzing Market..."):
            data = yf.download(target, period="1mo", interval="1h", progress=False)
            if not data.empty:
                # RSI Calculation (Manual for safety)
                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain/loss)))
                last_rsi = rsi.iloc[-1]
                
                st.metric(f"{target} RSI", f"{last_rsi:.2f}")
                
                if last_rsi > 70:
                    advice = "🔴 Take Profit (Sell)"
                elif last_rsi < 30:
                    advice = "🟢 Buy / Long"
                else:
                    advice = "🟡 Neutral / Hold"
                
                st.subheader(f"Advice: {advice}")
                send_msg(f"📊 JARVIS Scan: {target} | RSI: {last_rsi:.2f} | Advice: {advice}")

                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
                fig.update_layout(template="plotly_dark", title=f"{target} Chart")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("දත්ත ලබාගත නොහැක. Symbol එක නිවැරදිද බලන්න.")

st.divider()
st.caption("JARVIS V2.5 PRO | Stabilized & Secure")
