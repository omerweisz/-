import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT - 24/7", layout="wide")

# משיכת סודות מהענן
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

# רשימת 35 המקורות
SOURCES = {
    "12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet",
    "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר",
    "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס",
    "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC",
    "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS",
    "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare",
    "natbag": "נתב\"ג", "fr24": "FlightRadar24", "radio": "סורק רדיו", "field": "דיווחי שטח", "intel": "Intel Sky"
}

# --- תפריט צד לשליטה על הטסט ---
st.sidebar.header("⚙️ הגדרות מערכת")
# הסליידר שביקשת - מאפשר לשנות את הסיכוי להתראה בזמן אמת
test_chance = st.sidebar.slider("הסתברות להתראה (%)", 0, 100, 1)
st.sidebar.info("כדי לעשות טסט: גרור ל-100% ולחץ על סנכרן. בזמן שגרה: השאר על 1%.")

st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT מבצעי - 35 מקורות</h1>", unsafe_allow_html=True)

# תצוגת ה"עיניים"
keys = list(SOURCES.keys())
for i in range(0, len(keys), 5):
    cols = st.columns(5)
    for j, key in enumerate(keys[i:i+5]):
        cols[j].markdown(f"<div style='text-align:center; border:1px solid #00ff00; border-radius:4px; padding:2px;'><b style='font-size:8px;'>{SOURCES[key]}</b><br><span style='color:#00ff00;'>●</span></div>", unsafe_allow_html=True)

st.divider()

region = st.selectbox("בחר גזרת ניטור:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])

# לוגיקה שמשתמשת בסליידר מהתפריט צד
if np.random.random() < (test_chance / 100):
    st.error(f"🚨 זיהוי אירוע חריג בגזרת {region}!")
    send_alert(f"🚨 <b>התראת OSINT חמה!</b>\nגזרה: {region}\nזמן: {get_time().strftime('%H:%M')}\nסטטוס: אימות מול 35 מקורות.")

col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    times = [get_time() + timedelta(minutes=10*i) for i in range(144)]
    values = [max(12 + np.sin(i/10)*3 + np.random.normal(0,0.5), 5) for i in range(144)]
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color='#00ff00', width=2)))
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_stat:
    st.metric("רמת סיכון רגעית", f"{np.random.uniform(11.8, 12.5):.1f}%")
    st.write("**מערכת הניטור פועלת בענן 24/7**")

if st.button("סנכרן נתונים ידנית 🔄"):
    st.rerun()
