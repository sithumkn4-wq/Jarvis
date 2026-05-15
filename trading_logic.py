import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- 1. SETUP & CONFIGURATION ---
MY_SECRET_PASSWORD = "1221"
CHAT_ID = "7657159021"
# මෙතනට ඔයාගේ Bot Token එක දාන්න (උද්ධෘත ලකුණු ඇතුලේ)
TELEGRAM_TOKEN = "මෙතනට_ඔයාගේ_BOT_TOKEN_එක_දාන්න"

st.set_page_config(page_title="JARVIS Final Setup", layout="wide")

# --- 2. TELEGRAM FUNCTION (ආරක්ෂිතව හදා ඇත) ---
def send_telegram(msg):
    if "මෙතනට" not in TELEGRAM_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except:
            return False
    return False

# --- 3. DATA FUNCTIONS ---
def load_data(file):
    try:
        return pd.read_csv(file)
    except:
        return pd.DataFrame(columns=["Date", "Asset", "BuyPrice", "Qty", "Allocation %", "Currency"])

def save_data(df, file):
    df.to_csv(file, index=False)

# --- 4. MAIN UI ---
st.title("🤖 JARVIS Trading System")

# --- TELEGRAM TEST BUTTON ---
st.info("💡 මුලින්ම පල්ලෙහා තියෙන බටන් එක ඔබලා Telegram එකට මැසේජ් එනවාද බලන්න.")
if st.button("🚀 Test Telegram Message"):
    success = send_telegram("👋 JARVIS System is Online & Working Perfectly!")
    if success:
        st.success("✅ මැසේජ් එක Telegram එකට ගියා! ෆෝන් එක චෙක් කරන්න.")
    else:
        st.error("❌ මැසේජ් එක ගියේ නෑ. Bot Token එක හරියට දැම්මාද බලන්න.")

st.divider()

# TABS Tying Everything Together
tab1, tab2, tab3 = st.tabs(["📋 Portfolio Planner", "🔐 Private Vault", "📈 Live Analysis"])

# --- TAB 1: PORTFOLIO PLANNER (පරණ ලස්සන UI එක) ---
with tab1:
    st.header("➕ Add New Asset (Practice)")
    c1, c2 = st.columns(2)
    with c1:
        p_asset = st.text_input("Asset Symbol (eg: BTC-USD)")
        p_price = st.number_input("Buy Price", min_value=0.0, value=100.0)
    with c2:
        p_curr = st.selectbox("Currency", ["USD ($)", "LKR (Rs)"])
        p_qty = st.number_input("Quantity", min_value=0.0, value=1.0)
        
    p_alloc = st.slider("මෙයට යොදවන මුදල (%)", 0, 100, 50)
    
    if st.button("💾 Save Asset"):
        df = load_data("practice.csv")
        new = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": p_asset, "BuyPrice": p_price, "Qty": p_qty, "Allocation %": p_alloc, "Currency": p_curr}
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        save_data(df, "practice.csv")
        st.success(f"{p_asset} සාර්ථකව ඇතුළත් කළා!")
        send_telegram(f"✅ JARVIS Update: New Practice Asset Added -> {p_asset}")
            
    st.subheader("📋 Saved Memory")
    st.dataframe(load_data("practice.csv"), use_container_width=True)

# --- TAB 2: PRIVATE VAULT (ආරක්ෂිත කලාපය) ---
with tab2:
    st.header("🔐 Private Vault (Real Money)")
    pwd = st.text_input("Enter Password", type="password")
    
    if pwd == MY_SECRET_PASSWORD:
        st.success("✅ Access Granted!")
        with st.form("real_data"):
            r_asset = st.text_input("Real Asset Symbol")
            r_price = st.number_input("Buy Price ($)", min_value=0.0)
            r_qty = st.number_input("Quantity", min_value=0.0)
            if st.form_submit_button("Save Real Data"):
                df = load_data("real.csv")
                new = {"Date": datetime.now().strftime("%Y-%m-%d"), "Asset": r_asset, "BuyPrice": r_price, "Qty": r_qty, "Allocation %": 100, "Currency": "USD"}
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                save_data(df, "real.csv")
                st.success("Real Data Saved Securely!")
                send_telegram(f"💰 JARVIS: Real Trade Logged -> {r_asset}")
                
        st.subheader("ඔබගේ සැබෑ වත්කම්")
        st.dataframe(load_data("real.csv"), use_container_width=True)
    elif pwd != "":
        st.error("❌ වැරදි මුරපදයකි.")

# --- TAB 3: ANALYSIS ---
with tab3:
    st.header("📈 Market Scan & Charts")
    target = st.text_input("Symbol to Scan", "BTC-USD")
    if st.button("🔍 Scan Now"):
        with st.spinner("දත්ත ලබා ගනිමින් පවතී..."):
            data = yf.download(target, period="1mo", interval="1h", progress=False)
            if not data.empty:
                st.success("Scan Complete!")
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
                fig.update_layout(template="plotly_dark", title=f"{target} Live Market")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("දත්ත ලබාගත නොහැක. Symbol එක පරීක්ෂා කරන්න.")
