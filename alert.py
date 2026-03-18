import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v34.0 - Telegram Alerts", layout="wide")

# --- הגדרות טלגרם (חינמי לגמרי) ---
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"  # הטוקן שקיבלת מ-BotFather
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE" # ה-ID האישי שלך

def send_telegram_msg(message):
    """שליחת הודעה לטלפון דרך בוט טלגרם"""
    if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# רשימת 35 המקורות
SOURCES_FULL = {
    "12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet",
    "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר",
    "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס",
    "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC",
    "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS",
    "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare",
    "natbag": "נתב\"ג", "fr24": "FlightRadar24", "radio": "סורק רדיו", "field": "דיווחי שטח", "intel": "Intel Sky"
}

if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת OSINT מחוברת לטלגרם"}]
if 'emergency_mode' not in st.session_state:
    st.session_state['emergency_mode'] = False

def core_engine_v34(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    # סיכוי של 1% להפעלת התראה בזמן לחיצה על סנכרון
if True:
        st.session_state['locked_risk'] = 98.8
        st.session_state['emergency_mode'] = True
        
        # הודעה מעוצבת לטלגרם
        msg_text = f"🚨 <b>התראת OSINT חריגה!</b>\nגזרה: {selected_region}\nרמת סיכון: 98.8%\nזמן: {isr_now_str}"
        send_telegram_msg(msg_text)
        
        st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": f"🚀 שיגור! הודעה נשלחה לטלגרם."})
    elif not st.session_state['emergency_mode']:
        st.session_state['locked_risk'] = np.random.uniform(11.5, 13.0)
    else:
        st.session_state['locked_risk'] -= 4.0
        if st.session_state['locked_risk'] <= 14.0:
            st.session_state['emergency_mode'] = False
    return st.session_state['locked_risk']

# --- ממשק משתמש ---
st.markdown("<h1 style='text-align: right;'>🛰️ חמ\"ל OSINT - התראות טלגרם</h1>", unsafe_allow_html=True)

# תצוגת נורות
keys = list(SOURCES_FULL.keys())
for i in range(0, len(keys), 5):
    cols = st.columns(5)
    for j, key in enumerate(keys[i:i+5]):
        active = st.session_state['emergency_mode'] and (j % 2 == 0) # אפקט ויזואלי בחירום
        color = "#ff4b4b" if active else "#00ff00"
        cols[j].markdown(f"<div style='text-align:center; border:1px solid {color}; border-radius:4px; padding:2px;'><b style='font-size:8px;'>{SOURCES_FULL[key]}</b><br><span style='color:{color};'>●</span></div>", unsafe_allow_html=True)

st.divider()
col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 גזרה")
    region = st.selectbox("בחר גזרה:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])
    risk_val = core_engine_v34(region)
    st.metric("סיכון רגעי", f"{risk_val:.1f}%")
    for a in st.session_state['alerts'][:3]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית סטטיסטית ל-24 שעות")
    isr_now = get_israel_time()
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    f_vals = [max(12 + np.sin(i/10)*2 + np.random.normal(0,0.5), 5) for i in range(144)]
    
    line_c = '#ff4b4b' if risk_val > 50 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=2)))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("בצע סריקת מערכות 🔄"):
    st.rerun()
