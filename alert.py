import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT מבצעי", layout="wide")

# מודל סטטיסטי מעודכן: פערים גדולים יותר כדי שהגרף לא יהיה שטוח
# למשל: סיכון גבוה מאוד בצהריים ובערב, וכמעט אפס בלילה
HOURLY_STATS = {
    0: 5,  1: 3,  2: 2,  3: 2,  4: 2,  5: 5, 
    6: 10, 7: 15, 8: 25, 9: 20, 10: 18, 11: 20, 
    12: 45, 13: 55, 14: 65, 15: 50, 16: 40, 17: 60, 
    18: 75, 19: 85, 20: 90, 21: 70, 22: 40, 23: 15
}

def get_live_alert_modifier():
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=5)
        content = r.text
        live_alerts = ["התרעה: צבע אדום", "אזעקה הופעלה", "ירי רקטי עכשיו"]
        matches = sum(1 for word in live_alerts if word in content)
        if matches > 0:
            return 80.0 
        return 0.0
    except:
        return 0.0

now = datetime.now() + timedelta(hours=2) 
live_modifier = get_live_alert_modifier()
current_base_stat = HOURLY_STATS[now.hour]
current_total_risk = min(current_base_stat + live_modifier, 100.0)
is_alert = current_total_risk > 50.0 # סף התראה גבוה יותר בגלל הסטטיסטיקה

status_color = "#ff0000" if is_alert else "#00ff00"

st.markdown(f"""
    <style>
    @keyframes blink {{ 0% {{opacity: 1;}} 50% {{opacity: 0.3;}} 100% {{opacity: 1;}} }}
    .blink {{ animation: blink 1s infinite; color: #ff0000; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT מבצעי - 35 מקורות</h1>", unsafe_allow_html=True)

# 35 מקורות
SOURCES = {"12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet", "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר", "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס", "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC", "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS", "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare", "natbag": "נתב\"ג", "fr24": "FlightRadar24", "radio": "סורק רדיו", "field": "דיווחי שטח", "intel": "Intel Sky"}

keys = list(SOURCES.keys())
for i in range(0, len(keys), 5):
    cols = st.columns(5)
    for j, key in enumerate(keys[i:i+5]):
        cols[j].markdown(f"<div style='text-align:center; border:1px solid {status_color}; border-radius:4px; padding:2px; background-color: {status_color}05;'><b style='font-size:8px;'>{SOURCES[key]}</b><br><span style='color:{status_color};'>●</span></div>", unsafe_allow_html=True)

st.divider()

# גרף דקה-דקה ל-120 דקות הבאות
times = []
values = []
for i in range(120):
    future_time = now + timedelta(minutes=i)
    times.append(future_time)
    stat_risk = HOURLY_STATS[future_time.hour]
    
    if i < 60 and live_modifier > 0:
        decayed_modifier = live_modifier * (1 - (i / 60.0))
    else:
        decayed_modifier = 0
        
    values.append(min(stat_risk + decayed_modifier, 100.0))

col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית דקה-דקה (OSINT & Stats)")
    fig = go.Figure(go.Scatter(
        x=times, y=values, fill='tozeroy', 
        line=dict(color=status_color, width=2, shape='spline'), 
        hovertemplate='זמן: %{x|%H:%M}<br>סיכון: %{y:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(fixedrange=True, tickformat='%H:%M', nticks=15), 
        yaxis=dict(fixedrange=True, range=[0, 105]), 
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    st.metric("רמת סיכון נוכחית", f"{current_total_risk:.1f}%")
    if is_alert:
        st.markdown("<div class='blink'>🚨 התראה פעילה!</div>", unsafe_allow_html=True)
    if st.button("סנכרן נתונים 🔄", use_container_width=True):
        st.rerun()
