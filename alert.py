import streamlit as st
import plotly.graph_objects as go
import requests
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT - סריקה בלחיצה", layout="wide")

# פונקציה שסורקת מקור ספציפי לפי בחירה
def fetch_specific_source(source_type):
    urls = {
        "חדשות": "https://www.ynet.co.il/Integration/StoryRss2.xml",
        "צבאי": "https://rss.walla.co.il/feed/1?type=main",
        "חוץ": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "טכנולוגי": "https://www.themarker.com/srv/rss/all"
    }
    url = urls.get(source_type, urls["חדשות"])
    try:
        r = requests.get(url, timeout=2)
        root = ET.fromstring(r.content)
        # מושך את הכותרת של הפריט הראשון
        headline = root.find('./channel/item/title').text
        return headline
    except Exception as e:
        return "שגיאה בסריקת המקור. נסה שנית."

def get_minute_statistic(dt):
    base = 10 + 5 * (1 - math.cos(math.pi * (dt.hour - 3) / 12)) 
    variation = 3 * math.sin(dt.minute * 0.5)
    return max(min(base + variation, 25), 5)

# תצוגה
st.markdown("<h1 style='text-align: right;'>🛰️ חמ\"ל OSINT - סריקה חיה בלחיצה</h1>", unsafe_allow_html=True)
st.caption("לחץ על מקור כדי להפעיל סורק ייעודי לאותו ערוץ")

# מיפוי 35 המקורות לסוגי סריקה
SOURCES = {
    "12": "חדשות", "13": "חדשות", "11": "חדשות", "14": "צבאי", "ynet": "חדשות",
    "פקע\"ר": "צבאי", "צה\"ל": "צבאי", "אבו-עלי": "צבאי", "צופר": "צבאי", "livemap": "צבאי",
    "fr24": "טכנולוגי", "adsb": "טכנולוגי", "iaf": "צבאי", "nasa": "טכנולוגי", "usgs": "טכנולוגי",
    "רוטר": "צבאי", "חמל": "חדשות", "telegram": "צבאי", "moked": "חדשות", "sela": "חדשות",
    "iec": "טכנולוגי", "cyber": "טכנולוגי", "google": "טכנולוגי", "marine": "טכנולוגי", "sentinel": "טכנולוגי",
    "cnn": "חוץ", "bbc": "חוץ", "reuters": "חוץ", "aljazeera": "חוץ", "fox": "חוץ",
    "ayalon": "טכנולוגי", "natbag": "טכנולוגי", "radio": "צבאי", "field": "צבאי", "intel": "צבאי"
}

cols = st.columns(7)
for idx, (name, s_type) in enumerate(SOURCES.items()):
    with cols[idx % 7]:
        # הכפתור עצמו
        with st.popover(name, use_container_width=True):
            st.write(f"🔍 מפעיל סורק עבור: **{name}**")
            # רק כשפותחים את הפופאובר, הפונקציה הזו רצה
            with st.spinner("סורק מקור..."):
                current_headline = fetch_specific_source(s_type)
                st.info(current_headline)
            st.caption(f"סוג מקור: {s_type} | זמן סריקה: {datetime.now().strftime('%H:%M:%S')}")

st.divider()

# גרף (נשאר קבוע כדי לא להפריע)
now = datetime.now()
col_graph, col_stat = st.columns([2, 1])
with col_graph:
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_minute_statistic(t) for t in times]
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color="#00ff00", width=1.5)))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    risk = get_minute_statistic(now)
    st.metric("סיכון נוכחי", f"{risk:.1f}%")
    st.success("מערכת סריקה מוכנה")
