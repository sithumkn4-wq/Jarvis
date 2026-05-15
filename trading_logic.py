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

st.set_page_config(page_title="JARVIS Trading System", layout="wide")

# --- 📱 TELEGRAM FUNCTION ---
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={MY_CHAT_ID}&text={message}"
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

# --- 📈 RSI CALCULATION (No external library needed to avoid errors) ---
def get_rsi_and_data(symbol):
    try:
        df = yf.download(symbol, period="1mo", interval="1h", progress=False)
        if df.empty: return None, None
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        return float(current_rsi), df
    except:
        return None, None

# --- 🎨 MAIN UI DESIGN ---
st.title("🤖 JARVIS Trading System")

# --- 🚀 TELEGRAM CONNECTION TEST ---
st.info("💡 මුලින්ම පල්ලෙහා තියෙන බටන් එක ඔබලා Telegram එකට මැසේජ් එනවාද බලන්න.")

if st.button("🚀 Test Telegram Message"):
    success = send_telegram("✅ JARVIS පද්ධතිය සාර්ථකව සම්බන්ධ විය! දැන් ඔබට Alerts ලැබෙනු ඇත.")
    if success:
        st.success("✅ මැසේජ් එක සාර්ථකව යැව්වා! Telegram එක පරීක්ෂා කරන්න.")
    else:
        st.error("❌ මැසේජ් එක යැවීමට නොහැකි විය. කරුණාකර අන්තර්ජාල සම්බන්ධතාවය පරීක්ෂා කරන්න.")

st.divider()

# --- ⏰ SCHEDULED ALERTS (Manual Trigger logic) ---
# සටහන: මෙය ක්‍රියාත්මක වන්නේ App එක විවෘතව පවතින විට පමණි.
now = datetime.now().strftime("%H:%M")
if now in ["05:00", "12:00", "20:00"]:
    rsi_val, _ = get_rsi_and_data("BTC-USD")
    if rsi_val:
        send_telegram(f"⏰ JARVIS TIME UPDATE ({now})\nMarket: BTC-USD\nCurrent RSI: {rsi_val:.2f}")

# --- 🗂️ FUNCTIONAL TABS ---
tab1, tab2, tab3 = st.tabs(["📋 Portfolio", "🔐 Private Vault", "📈 Live Scan"])

with tab1:
    st.header("📋 Portfolio Planner")
    col1, col2 = st.columns(2)
    with col1:
        asset = st.text_input("Asset Symbol", "AAPL")
        buy_price = st.number_input("Fake Buy Price ($)", min_value=0.0, value=0.10)
    with col2:
        qty = st.number_input("Fake Qty", min_value=0.0, value=0.07)
    
    alloc = st.slider("යොදවන මුදල (%)", 0, 100, 70)
    
    if st.button("Save to Practice"):
        st.success("Practice Trade Saved!")
        send_telegram(f"📝 New Practice Entry\nAsset: {asset}\nPrice: ${buy_price}\nAllocation: {alloc}%")

with tab2:
    st.header("🔐 Secure Vault")
    pw = st.text_input("Password", type="password")
    if pw == MY_PASSWORD:
        st.success("Access Granted!")
        st.write("### ඔබගේ වර්තමාන වත්කම් (Holdings)")
        # Mock table based on your previous designs
        data = {'Date': ['2026-05-15'], 'Asset': ['AAPL'], 'BuyPrice': [50.00], 'Qty': [5.00], 'Type': ['Real']}
        st.table(pd.DataFrame(data))
    elif pw != "":
        st.error("වැරදි මුරපදයකි.")

with tab3:
    st.header("📈 Market Intelligence")
    scan_target = st.text_input("Symbol to Analyze (e.g. BTC-USD, TSLA)", "AAPL")
    if st.button("Deep Scan"):
        rsi_val, chart_data = get_rsi_and_data(scan_target)
        if rsi_val is not None:
            # AI Advice Logic
            advice = "Neutral 🟡"
            if rsi_val > 70: advice = "SELL 🔴 (Overbought)"
            elif rsi_val < 30: advice = "BUY 🟢 (Oversold)"
            
            st.metric(f"{scan_target} Current RSI", f"{rsi_val:.2f}")
            st.subheader(f"AI Advice: {advice}")
            
            # Draw Live Candlestick Chart
            fig = go.Figure(data=[go.Candlestick(
                x=chart_data.index,
                open=chart_data['Open'],
                high=chart_data['High'],
                low=chart_data['Low'],
                close=chart_data['Close']
            )])
            fig.update_layout(title=f"{scan_target} Live Market Chart", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            # Send result to Telegram
            send_telegram(f"🔍 Scan Report: {scan_target}\nRSI: {rsi_val:.2f}\nAdvice: {advice}")
        else:
            st.error("දත්ත ලබාගත නොහැක. Symbol එක නිවැරදිදැයි බලන්න.")
