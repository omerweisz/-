import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT - 24/7", layout="wide")

# אתחול
if 'current_risk' not in st.session_state:
    st.session_state.current_risk = 12.0

# משיכת סודות
try:
    TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    TOKEN, CHAT_ID = None, None

def send_alert(msg):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try: requests.post(url, json=payload, timeout=5)
    except: pass

def get_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- לוגיקת ניתוח עם "דלת אחורית" לטסט ---
def analyze_real_risk(test_mode=False):
    if test_mode:
        return 98.5  # אם הטסט פעיל, ישר קופץ לסיכון גבוה
    
    try:
        response = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=5)
        content = response.text
        critical_keywords = ["צבע אדום", "אזעקה עכשיו", "חדירת מחבלים", "ירי רקטי", "נפילה בגזרה"]
        warning_keywords = ["חריג", "דיווח ראשוני", "פיצוץ", "כוחות ביטחון", "יירוט"]
        
        c_matches = sum(1 for word in critical_keywords if word in content)
        w_matches = sum(1 for word in warning_keywords if word in content)
        
        return min(12.0 + (c_matches * 40.0) + (w_matches * 5.0), 100.0)
    except:
        return 12.0

# --- תפריט צד סודי לטסט ---
st.sidebar.header("⚙️ ניהול מערכת")
test_trigger = st.sidebar.text_input("קוד טסט (סודי):", placeholder="הכנס קוד להפעלת התראה")
is_test = (test_trigger == "test123") # שנה את "test123" למה שבא לך

st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT מבצעי - 35 מקורות</h1>", unsafe_allow_html=True)

# קביעת מצב וצבע
current_risk = analyze_real_risk(test_mode=is_test)
alert_active = True if current_risk > 40 else False
status_color = "#ff0000" if alert_active else "#00ff00"

# תצוגת ה"עיניים"
SOURCES = {"12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet", "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר", "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס", "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC", "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS", "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare", "natbag": "נתב\"ג", "fr24": "FlightRadar24", "radio": "סורק רדיו", "field": "דיווחי שטח", "intel": "Intel Sky"}

keys = list(SOURCES.keys())
for i in range(0, len(keys), 5):
    cols = st.columns(5)
    for j, key in enumerate(keys[i:i+5]):
        cols[j].markdown(f"<div style='text-align:center; border:1px solid {status_color}; border-radius:4px; padding:2px; background-color: {status_color}10;'><b style='font-size:8px;'>{SOURCES[key]}</b><br><span style='color:{status_color};'>●</span></div>", unsafe_allow_html=True)

st.divider()

if st.button("סנכרן נתונים ידנית 🔄", use_container_width=True):
    with st.spinner("סורק..."):
        time.sleep(0.5)
        if alert_active:
            send_alert(f"⚠️ **ניסוי מערכת פעיל**\nסיכון: {current_risk}%")
        st.rerun()

# גרף (העכבר עובד!)
col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית סיכון")
    times = [get_time() + timedelta(minutes=10*i) for i in range(144)]
    values = [max(current_risk + np.sin(i/10)*2 + np.random.normal(0,0.2), 0) for i in range(144)]
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=status_color, width=2), hovertemplate='סיכון: %{y:.1f}%<extra></extra>'))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    st.metric("רמת סיכון", f"{current_risk:.1f}%", delta="חריג" if alert_active else "תקין", delta_color="inverse" if alert_active else "normal")
    if is_test: st.warning("🛠️ מצב טסט פעיל")
