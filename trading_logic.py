import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- CONFIGURATION ---
MY_SECRET_PASSWORD = "1221"
CHAT_ID = "7657159021"
TELEGRAM_TOKEN = "මෙතනට_ඔයාගේ_BOT_TOKEN_එක_දාන්න"

st.set_page_config(page_title="Trading Oracle V2.4", layout="wide")

# --- DATA FUNCTIONS ---
def load_data(file):
    try:
        return pd.read_csv(file)
    except:
        return pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Allocation %", "Currency"])

def save_data(df, file):
    df.to_csv(file, index=False)

# --- UI START ---
st.title("🔮 Trading Oracle - Final v2.4")

tab1, tab2, tab3 = st.tabs(["📋 Portfolio Planner", "🔐 Real Account", "📈 Intelligence"])

# --- TAB 1: PORTFOLIO PLANNER (ඔයා කැමතිම පරණ UI එක) ---
with tab1:
    st.header("➕ Add New Asset")
    
    col1, col2 = st.columns(2)
    with col1:
        p_asset = st.text_input("Asset Symbol (eg: TSLA, AAPL, BTC-USD)", key="p_sym")
    with col2:
        p_curr = st.selectbox("Currency", ["USD ($)", "LKR (Rs)"], key="p_cur")
        
    col3, col4 = st.columns(2)
    with col3:
        p_price = st.number_input("Buy Price", min_value=0.0, value=298.21, step=0.01)
    with col4:
        p_qty = st.number_input("Quantity", min_value=0.0, value=2.0, step=0.01)
    
    p_alloc = st.slider("මෙයට යොදවන මුදල (%)", 0, 100, 92)
    
    if st.button("💾 Save to Memory"):
        df = load_data("practice.csv")
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Asset": p_asset,
            "BuyPrice": p_price,
            "Qty": p_qty,
            "Allocation %": p_alloc,
            "Currency": p_curr
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df, "practice.csv")
        st.success("Saved Successfully! 🚀")

    st.subheader("📋 Saved Memory")
    st.dataframe(load_data("practice.csv"), use_container_width=True)
    
    if st.button("🗑️ Full System Reset"):
        save_data(pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Allocation %", "Currency"]), "practice.csv")
        st.rerun()

# --- TAB 2: REAL ACCOUNT ---
with tab2:
    st.header("🔐 Secure Portfolio")
    pass_input = st.text_input("Enter Admin Password", type="password")
    
    if pass_input == MY_SECRET_PASSWORD:
        st.success("Access Granted! ✅")
        with st.form("real_trade_form"):
            r_asset = st.text_input("Asset Symbol")
            r_price = st.number_input("Price", min_value=0.0)
            r_qty = st.number_input("Qty", min_value=0.0)
            if st.form_submit_button("Log Trade"):
                df = load_data("real.csv")
                new = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": r_asset, "BuyPrice": r_price, "Qty": r_qty, "Allocation %": 100, "Currency": "USD"}
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                save_data(df, "real.csv")
                st.success("Logged!")
        st.dataframe(load_data("real.csv"), use_container_width=True)
    else:
        st.warning("Locked. Please enter 1221.")

# --- TAB 3: INTELLIGENCE ---
with tab3:
    st.header("🧠 AI Analysis")
    target = st.text_input("Symbol to Analyze", "BTC-USD")
    if st.button("🔍 Deep Scan"):
        data = yf.download(target, period="1mo", interval="1h", progress=False)
        if not data.empty:
            st.write(f"### {target} Live Chart")
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("දත්ත ලබාගත නොහැක.")

st.divider()
st.caption("JARVIS V2.4 | System Stable")
