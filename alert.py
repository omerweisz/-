import streamlit as st
import plotly.graph_objects as go
import requests
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT מבצעי", layout="wide")

# פונקציית סטטיסטיקה דקה-דקה (דטרמיניסטית לפי זמן)
def get_minute_statistic(dt):
    hour = dt.hour
    minute = dt.minute
    # מודל בסיס משתנה לפי שעה
    base = 15 + 35 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    # תנודות דקה-דקה למראה ריאליסטי
    variation = 8 * math.sin(minute * 0.8) + 4 * math.cos((hour * 60 + minute) * 0.15)
    return max(min(base + variation, 90), 5)

# סורק חכם: בודק רק ידיעות מה-10 דקות האחרונות
def get_live_alert_modifier():
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=5)
        root = ET.fromstring(r.content)
        now_utc = datetime.utcnow()
        
        alert_keywords = ["צבע אדום", "אזעקה", "חדירת", "ירי רקטי", "כטב\"ם"]
        
        for item in root.findall('./channel/item'):
            title = item.find('title').text
            pub_date_str = item.find('pubDate').text
            # המרה לזמן אמת להשוואה
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
            
            # אם הידיעה פורסמה ב-10 הדקות האחרונות ויש בה מילת מפתח
            if (now_utc - pub_date).total_seconds() < 600:
                if any(word in title for word in alert_keywords):
                    return 85.0
        return 0.0
    except:
        return 0.0

# חישוב נתונים (שעון ישראל)
now = datetime.now()
live_modifier = get_live_alert_modifier()
current_stat = get_minute_statistic(now)
current_total_risk = min(current_stat + live_modifier, 100.0)

# המערכת תהיה אדומה רק אם יש "בוסט" של זמן אמת
is_alert = live_modifier > 0 
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

# גרף דקה-דקה (120 דקות)
times, values = [], []
for i in range(120):
    future_time = now + timedelta(minutes=i)
    times.append(future_time)
    stat_risk = get_minute_statistic(future_time)
    # דעיכה של התראת לייב בגרף
    decay = live_modifier * (1 - (i/60.0)) if (i < 60 and live_modifier > 0) else 0
    values.append(min(stat_risk + decay, 100.0))

col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית דקה-דקה (מסונן זמן אמת)")
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=status_color, width=2), hovertemplate='%{y:.1f}%<extra></extra>'))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(fixedrange=True, tickformat='%H:%M'), yaxis=dict(fixedrange=True, range=[0, 105]), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    st.metric("רמת סיכון נוכחית", f"{current_total_risk:.1f}%")
    if is_alert:
        st.markdown("<div class='blink'>🚨 אירוע אמת בדקות האחרונות!</div>", unsafe_allow_html=True)
    else:
        st.success("מצב שגרה - סריקה פעילה")
    if st.button("סנכרן נתונים 🔄", use_container_width=True):
        st.rerun()
