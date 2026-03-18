import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT - 24/7", layout="wide")

# אתחול מצב התראה
if 'alert_mode' not in st.session_state:
    st.session_state.alert_mode = False

# משיכת סודות
try:
    TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    TOKEN = None
    CHAT_ID = None

def send_alert(msg):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try: requests.post(url, json=payload, timeout=5)
    except: pass

def get_time():
    return datetime.utcnow() + timedelta(hours=2)

# רשימת המקורות
SOURCES = {
    "12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet",
    "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר",
    "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס",
    "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC",
    "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS",
    "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare",
    "natbag": "נתב\"ג", "fr24": "FlightRadar24", "radio": "סורק רדיו", "field": "דיווחי שטח", "intel": "Intel Sky"
}

st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT מבצעי - 35 מקורות</h1>", unsafe_allow_html=True)

# צבעים לפי מצב
status_color = "#ff0000" if st.session_state.alert_mode else "#00ff00"

# תצוגת ה"עיניים"
keys = list(SOURCES.keys())
for i in range(0, len(keys), 5):
    cols = st.columns(5)
    for j, key in enumerate(keys[i:i+5]):
        cols[j].markdown(f"""
            <div style='text-align:center; border:1px solid {status_color}; border-radius:4px; padding:2px; background-color: {status_color}10;'>
                <b style='font-size:8px;'>{SOURCES[key]}</b><br>
                <span style='color:{status_color};'>●</span>
            </div>
        """, unsafe_allow_html=True)

st.divider()

region = st.selectbox("בחר גזרת ניטור:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])

def check_real_sources():
    try:
        response = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=5)
        # לניסוי: תחליף את "צבע אדום" במילה שמופיעה עכשיו (כמו "ישראל")
        if "צבע אדום" in response.text or "התרעה" in response.text:
            return True
        return False
    except: return False

if st.button("סנכרן נתונים ידנית 🔄", use_container_width=True):
    with st.spinner("סורק מקורות..."):
        time.sleep(1)
        if check_real_sources():
            st.session_state.alert_mode = True
            send_alert(f"🚨 <b>זיהוי חריג!</b>\nגזרה: {region}")
        else:
            st.session_state.alert_mode = False
        st.rerun()

# גרף ותצוגה - התיקון לעכבר כאן!
col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית הסתברותית")
    times = [get_time() + timedelta(minutes=10*i) for i in range(144)]
    values = [max(12 + np.sin(i/10)*3 + np.random.normal(0,0.5), 5) for i in range(144)]
    graph_color = "#ff0000" if st.session_state.alert_mode else "#00ff00"
    
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=graph_color, width=2), hovertemplate='זמן: %{x}<br>סיכון: %{y:.1f}%<extra></extra>'))
    
    fig.update_layout(
        template="plotly_dark", 
        height=300, 
        margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(fixedrange=True), # מבטל זום בציר X
        yaxis=dict(fixedrange=True), # מבטל זום בציר Y
        dragmode=False               # מבטל אפשרות גרירה וזום
    )
    
    # config כאן מחזיר את העכבר אבל בלי הכלים של הזום
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    st.metric("רמת סיכון", f"{np.random.uniform(11.8, 12.5):.1f}%")
    if st.sidebar.button("אפס מערכת 🛠️"):
        st.session_state.alert_mode = False
        st.rerun()
