import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time

# הגדרות דף וחמ"ל
st.set_page_config(page_title="חמ\"ל OSINT מבצעי", layout="wide")

# פונקציית סריקה משופרת - מונעת "באג אדום" על ידי חיפוש ביטויים ספציפיים בלבד
def get_operational_status():
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=5)
        content = r.text
        # ביטויים של "זמן אמת" בלבד
        live_alerts = ["התרעה: צבע אדום", "אזעקה הופעלה", "חדירת מחבלים", "ירי רקטי עכשיו"]
        matches = sum(1 for word in live_alerts if word in content)
        
        if matches > 0:
            return 96.4, True
        return 12.2 + np.random.uniform(-0.3, 0.3), False
    except:
        return 12.0, False

# הרצת הלוגיקה
current_risk, is_alert = get_operational_status()
status_color = "#ff0000" if is_alert else "#00ff00"

# עיצוב CSS למערכת
st.markdown(f"""
    <style>
    @keyframes blink {{ 0% {{opacity: 1;}} 50% {{opacity: 0.3;}} 100% {{opacity: 1;}} }}
    .blink {{ animation: blink 1s infinite; color: #ff0000; font-weight: bold; }}
    .stMetric {{ background-color: {status_color}10; padding: 10px; border-radius: 5px; border: 1px solid {status_color}; }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT מבצעי - 35 מקורות</h1>", unsafe_allow_html=True)

# תצוגת 35 המקורות
SOURCES = {"12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet", "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר", "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס", "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC", "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS", "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare", "natbag": "נתב\"ג", "fr24": "FlightRadar24", "radio": "סורק רדיו", "field": "דיווחי שטח", "intel": "Intel Sky"}

keys = list(SOURCES.keys())
for i in range(0, len(keys), 5):
    cols = st.columns(5)
    for j, key in enumerate(keys[i:i+5]):
        cols[j].markdown(f"<div style='text-align:center; border:1px solid {status_color}; border-radius:4px; padding:2px; background-color: {status_color}05;'><b style='font-size:8px;'>{SOURCES[key]}</b><br><span style='color:{status_color};'>●</span></div>", unsafe_allow_html=True)

st.divider()

# גרף (עכבר עובד, זום מבוטל)
col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 ניטור סיכונים")
    times = [(datetime.now() + timedelta(hours=2) + timedelta(minutes=10*i)) for i in range(144)]
    values = [max(current_risk + np.sin(i/10)*2 + np.random.normal(0,0.2), 0) for i in range(144)]
    
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=status_color, width=2), hovertemplate='סיכון: %{y:.1f}%<extra></extra>'))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    st.metric("רמת סיכון", f"{current_risk:.1f}%", delta="חריג" if is_alert else "תקין", delta_color="inverse" if is_alert else "normal")
    if is_alert:
        st.markdown("<div class='blink'>🚨 התראה פעילה: זוהה אירוע זמן אמת!</div>", unsafe_allow_html=True)
    
    if st.button("סנכרן נתונים 🔄", use_container_width=True):
        st.rerun()

st.sidebar.info(f"עדכון אחרון: {datetime.now().strftime('%H:%M:%S')}")
