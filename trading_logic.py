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

st.set_page_config(page_title="Trading Oracle - Final V2.3", layout="wide")

# --- CSS FOR STYLING (පරණ ලස්සන ගන්න) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { color: #ff4b4b; }
    </style>
    """, unsafe_allow_index=True)

# --- DATA FUNCTIONS ---
def load_data(file):
    try: return pd.read_csv(file)
    except: return pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Allocation %", "Currency", "Type"])

def save_data(df, file):
    df.to_csv(file, index=False)

# --- UI START ---
st.title("🔮 Trading Oracle - Final v2.3")

tab1, tab2, tab3 = st.tabs(["📋 Portfolio Planner", "🔐 Real Account", "📈 Intelligence"])

# --- TAB 1: PORTFOLIO PLANNER (The Old Look) ---
with tab1:
    st.header("➕ Add New Asset (Practice)")
    
    col1, col2 = st.columns(2)
    with col1:
        p_asset = st.text_input("Asset Symbol (eg: TSLA, AAPL, BTC-USD)")
        p_price = st.number_input("Buy Price", min_value=0.0, value=298.21)
    with col2:
        p_qty = st.number_input("Quantity", min_value=0.0, value=2.0)
        p_curr = st.selectbox("Currency", ["USD ($)", "LKR (Rs)"])
    
    p_alloc = st.slider("මෙයට යොදවන මුදල (%)", 0, 100, 92)
    
    if st.button("💾 Save to Memory"):
        df = load_data("practice.csv")
        new_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": p_asset, "BuyPrice": p_price, "Qty": p_qty, "Allocation %": p_alloc, "Currency": p_curr, "Type": "Demo"}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df, "practice.csv")
        st.success("Saved to Memory! 🚀")

    st.subheader("📋 Saved Memory")
    st.table(load_data("practice.csv"))
    
    if st.button("🗑️ Full System Reset"):
        save_data(pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Allocation %", "Currency", "Type"]), "practice.csv")
        st.experimental_rerun()

# --- TAB 2: REAL ACCOUNT (Secure) ---
with tab2:
    st.header("🔐 Secure Portfolio")
    pass_input = st.text_input("Enter Admin Password", type="password")
    
    if pass_input == MY_SECRET_PASSWORD:
        st.info("Verified. Accessing Real Data...")
        with st.expander("Add Real Transaction"):
            r_asset = st.text_input("Real Symbol (eg: BTC-USD)")
            r_price = st.number_input("Real Price", min_value=0.0)
            r_qty = st.number_input("Real Qty", min_value=0.0)
            if st.button("✅ Log Real Trade"):
                df = load_data("real.csv")
                new = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": r_asset, "BuyPrice": r_price, "Qty": r_qty, "Type": "Real"}
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                save_data(df, "real.csv")
                st.success("Logged!")
        
        st.write("### Current Holdings")
        st.dataframe(load_data("real.csv"), use_container_width=True)
    else:
        st.warning("Locked. Enter Password to View.")

# --- TAB 3: INTELLIGENCE ---
with tab3:
    st.header("🧠 AI Intelligence & Charts")
    target = st.text_input("Analyze Symbol", "BTC-USD")
    
    if st.button("🔍 Deep Scan"):
        try:
            data = yf.download(target, period="1mo", interval="1h", progress=False)
            if not data.empty:
                # RSI Calculation
                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain/loss)))
                last_rsi = rsi.iloc[-1]
                
                st.metric("Current RSI", f"{last_rsi:.2f}")
                if last_rsi > 70: st.error("Advice: Take Profit (Overbought)")
                elif last_rsi < 30: st.success("Advice: Buy/Hold (Oversold)")
                else: st.info("Advice: Neutral / Hold")

                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
                fig.update_layout(template="plotly_dark", title=f"{target} Live Chart")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No Data Found.")
        except:
            st.error("Error fetching data.")

st.markdown("---")
st.caption("Developed by JARVIS | Professional Trading Oracle")
