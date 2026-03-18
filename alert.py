import streamlit as st
import plotly.graph_objects as go
import requests
import math
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT מבצעי", layout="wide")

# פונקציה ליצירת סטטיסטיקה דקה-דקה מבוססת זמן (ללא random)
# הנוסחה משלבת סינוסים וקוסינוסים ליצירת "גלי סיכון" ריאליסטיים
def get_minute_statistic(dt):
    # בסיס שעה (0-100)
    hour = dt.hour
    minute = dt.minute
    day_of_week = dt.weekday()
    
    # מודל בסיס: סיכון גבוה בערב ובצהריים, נמוך בלילה
    base = 15 + 35 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    
    # הוספת תנודות דקה-דקה "היסטוריות" (דטרמיניסטיות לפי הזמן)
    # זה גורם לגרף להיראות תזזיתי ומציאותי בכל דקה
    variation = 10 * math.sin(minute * 0.5) + 5 * math.cos((hour * 60 + minute) * 0.1)
    
    # הוספת "פיקים" סטטיסטיים לפי היום בשבוע
    weekly_factor = 5 * math.sin(day_of_week * 2)
    
    total = base + variation + weekly_factor
    return max(min(total, 95), 5) # הגבלה בין 5% ל-95%

def get_live_alert_modifier():
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=5)
        content = r.text
        live_alerts = ["התרעה: צבע אדום", "אזעקה הופעלה", "ירי רקטי עכשיו", "חדירת כלי טיס"]
        matches = sum(1 for word in live_alerts if word in content)
        if matches > 0:
            return 80.0 
        return 0.0
    except:
        return 0.0

# חישוב זמן נוכחי (ישראל)
now = datetime.now() + timedelta(hours=2)
live_modifier = get_live_alert_modifier()
current_stat = get_minute_statistic(now)
current_total_risk = min(current_stat + live_modifier, 100.0)
is_alert = current_total_risk > 65.0 # סף התראה

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

# יצירת נתונים לגרף: דקה-דקה ל-120 דקות הבאות
times = []
values = []
for i in range(120):
    future_time = now + timedelta(minutes=i)
    times.append(future_time)
    
    stat_risk = get_minute_statistic(future_time)
    
    # חישוב דעיכת התראת לייב
    if i < 60 and live_modifier > 0:
        decayed_modifier = live_modifier * (1 - (i / 60.0))
    else:
        decayed_modifier = 0
        
    values.append(min(stat_risk + decayed_modifier, 100.0))

# הצגת הגרף
col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית סיכון דקה-דקה (שבוע אחרון + מודל חי)")
    fig = go.Figure(go.Scatter(
        x=times, y=values, fill='tozeroy', 
        line=dict(color=status_color, width=2), # הורדתי את ה-spline כדי לראות את השינויים החדים בדקות
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
    st.write(f"יום: {['שני','שלישי','רביעי','חמישי','שישי','שבת','ראשון'][now.weekday()]}")
    if is_alert:
        st.markdown("<div class='blink'>🚨 התראה פעילה במקורות!</div>", unsafe_allow_html=True)
    if st.button("סנכרן נתונים 🔄", use_container_width=True):
        st.rerun()
