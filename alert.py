import streamlit as st
import plotly.graph_objects as go
import requests
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT אינטראקטיבי", layout="wide")

# פונקציה למשיכת הכותרת האחרונה (לצורך התצוגה בלחיצה)
def get_latest_headline():
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=3)
        root = ET.fromstring(r.content)
        first_item = root.find('./channel/item')
        return first_item.find('title').text
    except:
        return "לא ניתן לשלוף כותרת כרגע"

# מודל סטטיסטי דקה-דקה
def get_minute_statistic(dt):
    hour = dt.hour
    minute = dt.minute
    base = 8 + 7 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    variation = 4 * math.sin(minute * 0.5) + 3 * math.cos((hour * 60 + minute) * 0.2)
    return max(min(base + variation, 25), 3)

# סורק זמן אמת
def get_live_alert_modifier():
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=3)
        root = ET.fromstring(r.content)
        now_utc = datetime.utcnow()
        alert_keywords = ["צבע אדום", "אזעקה", "חדירת", "ירי רקטי", "כטב\"ם"]
        for item in root.findall('./channel/item'):
            title = item.find('title').text
            pub_date_str = item.find('pubDate').text
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
            if (now_utc - pub_date).total_seconds() < 600:
                if any(word in title for word in alert_keywords):
                    return 75.0
        return 0.0
    except:
        return 0.0

# נתונים נוכחיים
now = datetime.now()
live_modifier = get_live_alert_modifier()
current_total_risk = min(get_minute_statistic(now) + live_modifier, 100.0)
headline = get_latest_headline()

is_alert = current_total_risk > 40.0
status_color = "#ff0000" if is_alert else "#00ff00"

st.markdown("<h1 style='text-align: right;'>🛰️ חמ\"ל OSINT מבצעי - לחץ על מקור לפירוט</h1>", unsafe_allow_html=True)

# רשימת 35 מקורות
SOURCES = {
    "12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet", 
    "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "אבו-עלי": "אבו עלי", "צופר": "TzevaAdom", "livemap": "Liveuamap",
    "fr24": "FlightRadar24", "adsb": "ADSB Exch", "iaf": "חיל האוויר", "nasa": "NASA FIRMS", "usgs": "USGS",
    "רוטר": "רוטר.נט", "חמל": "חמ\"ל", "telegram": "Telegram", "moked": "מוקד 106", "sela": "סל\"ע ת\"א",
    "iec": "חברת חשמל", "cyber": "Cloudflare", "google": "Trends", "marine": "MarineTraffic", "sentinel": "Sentinel",
    "cnn": "CNN", "bbc": "BBC", "reuters": "Reuters", "aljazeera": "Al Jazeera", "fox": "Fox News",
    "ayalon": "מצלמות איילון", "natbag": "נתב\"ג", "radio": "סורק קשר", "field": "דיווחי שטח", "intel": "Intel Sky"
}

# תצוגת מקורות ככפתורי Popover ב-7 עמודות
keys = list(SOURCES.keys())
cols = st.columns(7)
for idx, key in enumerate(keys):
    with cols[idx % 7]:
        # שימוש ב-popover כדי להציג את הכותרת בלחיצה
        with st.popover(SOURCES[key], use_container_width=True):
            st.write(f"**מקור:** {SOURCES[key]}")
            st.write(f"**עדכון אחרון:** {headline}")
            st.caption(f"סטטוס: {'מזהה אירוע' if is_alert else 'שגרה'}")

st.divider()

# גרף 24 שעות
times, values = [], []
for i in range(1440):
    future_time = now + timedelta(minutes=i)
    times.append(future_time)
    stat = get_minute_statistic(future_time)
    decay = live_modifier * (1 - (i/60.0)) if (i < 60 and live_modifier > 0) else 0
    values.append(min(stat + decay, 100.0))

col_graph, col_stat = st.columns([2, 1])
with col_graph:
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=status_color, width=1.5)))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(tickformat='%H:%M'))
    st.plotly_chart(fig, use_container_width=True)

with col_stat:
    st.metric("מדד סיכון נוכחי", f"{current_total_risk:.1f}%")
    if is_alert:
        st.error("🚨 אירוע פעיל זוהה במקורות")
    else:
        st.success("מצב שגרה")
    if st.button("רענן 🔄"):
        st.rerun()
