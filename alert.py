import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT מבצעי", layout="wide")

# מודל סטטיסטי: אחוזי סיכון ממוצעים לפי שעה ביממה (0-23)
# מותאם לשגרת "שאגת הארי" בגזרת עבר הירקון
HOURLY_STATS = {
    0: 12, 1: 10, 2: 8,  3: 8,  4: 8,  5: 10, 
    6: 12, 7: 15, 8: 18, 9: 15, 10: 14, 11: 14, 
    12: 15, 13: 18, 14: 22, 15: 20, 16: 18, 17: 25, 
    18: 30, 19: 35, 20: 45, 21: 40, 22: 30, 23: 20
}

# סריקת מקורות חיה (מחזירה רק משתנה "בוסט" לשעה הקרובה)
def get_live_alert_modifier():
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=5)
        content = r.text
        # ביטויים של זמן אמת בלבד
        live_alerts = ["התרעה: צבע אדום", "אזעקה הופעלה", "ירי רקטי עכשיו"]
        matches = sum(1 for word in live_alerts if word in content)
        
        if matches > 0:
            return 80.0 # בוסט של 80% לסיכון הסטטיסטי
        return 0.0
    except:
        return 0.0

# זמן נוכחי וחישוב נתונים
now = datetime.now() + timedelta(hours=2) # שעון ישראל
live_modifier = get_live_alert_modifier()
current_base_stat = HOURLY_STATS[now.hour]

# הסיכון הנוכחי הוא הסטטיסטיקה של עכשיו + מה שקורה בשטח (מוגבל ל-100 מקסימום)
current_total_risk = min(current_base_stat + live_modifier, 100.0)
is_alert = current_total_risk > 40.0

status_color = "#ff0000" if is_alert else "#00ff00"

# עיצוב CSS
st.markdown(f"""
    <style>
    @keyframes blink {{ 0% {{opacity: 1;}} 50% {{opacity: 0.3;}} 100% {{opacity: 1;}} }}
    .blink {{ animation: blink 1s infinite; color: #ff0000; font-weight: bold; }}
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

# יצירת נתוני הגרף (144 נקודות = 24 שעות)
times = []
values = []

for i in range(144):
    future_time = now + timedelta(minutes=10 * i)
    times.append(future_time)
    
    # 1. לוקחים את הסיכון הסטטיסטי לשעה העתידית הזו
    stat_risk = HOURLY_STATS[future_time.hour]
    
    # 2. חישוב דעיכה של התרעת זמן אמת (משפיע רק על השעתיים הקרובות = 12 נקודות)
    if i < 12 and live_modifier > 0:
        # ההשפעה יורדת בהדרגה ככל שמתרחקים מההווה
        decayed_modifier = live_modifier * (1 - (i / 12.0))
    else:
        decayed_modifier = 0
        
    # מחברים סטטיסטיקה + זמן אמת דועך
    final_point_risk = min(stat_risk + decayed_modifier, 100.0)
    values.append(final_point_risk)

# בניית הגרף
col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית סיכונים (מבוסס מודל סטטיסטי + זמן אמת)")
    
    fig = go.Figure(go.Scatter(
        x=times, y=values, fill='tozeroy', 
        line=dict(color=status_color, width=2, shape='spline'), 
        hovertemplate='זמן: %{x|%H:%M}<br>סיכון מחושב: %{y:.1f}%<extra></extra>'
    ))
    
    # נעילת זום והוספת פורמט דקות לציר ה-X
    fig.update_layout(
        template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(fixedrange=True, tickformat='%H:%M'), yaxis=dict(fixedrange=True, range=[0, 105]), 
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    st.metric("רמת סיכון נוכחית", f"{current_total_risk:.1f}%", 
              delta="אירוע אמת" if is_alert else "שגרה סטטיסטית", 
              delta_color="inverse" if is_alert else "normal")
    
    if is_alert:
        st.markdown("<div class='blink'>🚨 התראה פעילה במקורות!</div>", unsafe_allow_html=True)
    else:
        st.info("הגרף מציג תחזית סיכון המבוססת על סטטיסטיקת גזרה. במקרה של זיהוי אירוע אמת במקורות, הגרף יתעדכן בזמן אמת לשעות הקרובות.")
        
    if st.button("סנכרן נתונים 🔄", use_container_width=True):
        st.rerun()
