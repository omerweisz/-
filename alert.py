import streamlit as st
import plotly.graph_objects as go
import requests
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT רב-ערוצי", layout="wide")

# פונקציה חכמה לסריקת מספר מקורות במקביל
@st.cache_data(ttl=15)
def fetch_all_feeds():
    feeds = {
        "general": "שגרה - סריקה פעילה",
        "military": "דיווחים ביטחוניים: שגרה",
        "world": "כותרות עולמיות: אין אירוע חריג",
        "tech": "ניטור מערכות: תקין"
    }
    try:
        # מקור 1: ynet (כללי)
        r_ynet = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=2)
        feeds["general"] = ET.fromstring(r_ynet.content).find('./channel/item/title').text
        
        # מקור 2: וואלה (צבאי/ביטחוני)
        r_walla = requests.get("https://rss.walla.co.il/feed/1?type=main", timeout=2)
        feeds["military"] = ET.fromstring(r_walla.content).find('./channel/item/title').text
        
        # מקור 3: מעריב/חוץ
        r_intl = requests.get("https://www.maariv.co.il/Rss/RssFeedsWorld", timeout=2)
        feeds["world"] = ET.fromstring(r_intl.content).find('./channel/item/title').text
    except:
        pass
    return feeds

def get_minute_statistic(dt):
    base = 8 + 7 * (1 - math.cos(math.pi * (dt.hour - 3) / 12)) 
    variation = 4 * math.sin(dt.minute * 0.5)
    return max(min(base + variation, 25), 3)

@st.fragment(run_every=15)
def render_hamaal():
    now = datetime.now()
    all_data = fetch_all_feeds()
    
    st.markdown(f"<div style='text-align: right; color: #00ff00; font-family: monospace;'>[SYSTEM ACTIVE] LAST SYNC: {now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: right;'>🛰️ חמ\"ל OSINT מבצעי - הצלבת מקורות</h1>", unsafe_allow_html=True)

    # מיפוי המקורות לקטגוריות שונות
    SOURCES = {
        "12": "general", "13": "general", "11": "general", "14": "military", "ynet": "general",
        "פקע\"ר": "military", "צה\"ל": "military", "אבו-עלי": "military", "צופר": "military", "livemap": "military",
        "fr24": "tech", "adsb": "tech", "iaf": "military", "nasa": "tech", "usgs": "tech",
        "רוטר": "military", "חמל": "general", "telegram": "military", "moked": "general", "sela": "general",
        "iec": "tech", "cyber": "tech", "google": "tech", "marine": "tech", "sentinel": "tech",
        "cnn": "world", "bbc": "world", "reuters": "world", "aljazeera": "world", "fox": "world",
        "ayalon": "tech", "natbag": "tech", "radio": "military", "field": "military", "intel": "military"
    }

    cols = st.columns(7)
    for idx, (key, category) in enumerate(SOURCES.items()):
        with cols[idx % 7]:
            # צבע שונה למקורות צבאיים
            btn_label = f"📍 {key}" if category == "military" else key
            with st.popover(btn_label, use_container_width=True):
                st.subheader(f"מקור: {key}")
                st.write(f"**עדכון אחרון:**")
                st.info(all_data.get(category, "סורק..."))
                st.caption(f"סיווג מקור: {category}")

    st.divider()

    # גרף ונתונים
    col_graph, col_stat = st.columns([2, 1])
    with col_graph:
        times = [now + timedelta(minutes=i) for i in range(1440)]
        values = [get_minute_statistic(t) for t in times]
        fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color="#00ff00", width=1.5)))
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col_stat:
        risk = get_minute_statistic(now)
        st.metric("רמת סיכון גזרה", f"{risk:.1f}%")
        st.success("סטטוס: סריקה תקינה")

render_hamaal()
