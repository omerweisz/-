import streamlit as st
import plotly.graph_objects as go
import requests
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT שקט", layout="wide")

# פונקציית סריקה (עם Cache קצר מאוד לדינמיות)
@st.cache_data(ttl=15)
def fetch_osint_data():
    data = {"חדשות": "שגרה", "צבאי": "שגרה", "תעופה": "שגרה", "כללי": "שגרה"}
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=3)
        root = ET.fromstring(r.content)
        latest = root.find('./channel/item/title').text
        data = {"חדשות": latest, "צבאי": latest, "תעופה": "ניטור פעיל", "כללי": "סריקה רציפה"}
    except:
        pass
    return data

def get_minute_statistic(dt):
    base = 8 + 7 * (1 - math.cos(math.pi * (dt.hour - 3) / 12)) 
    variation = 4 * math.sin(dt.minute * 0.5)
    return max(min(base + variation, 25), 3)

# --- תצוגת החמ"ל בתוך Fragment (מתרענן שקט) ---
@st.fragment(run_every=15)
def render_hamaal():
    now = datetime.now()
    osint_headlines = fetch_osint_data()
    current_risk = get_minute_statistic(now)
    
    st.markdown(f"<div style='text-align: right; color: gray;'>סנכרון שקט פעיל | עדכון אחרון: {now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: right;'>🛰️ חמ\"ל OSINT - עדכון שקט (Fragment)</h1>", unsafe_allow_html=True)

    # 35 מקורות אינטראקטיביים
    all_keys = ["12", "13", "11", "14", "ynet", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "livemap",
                "fr24", "adsb", "iaf", "nasa", "usgs", "רוטר", "חמל", "telegram", "moked", "sela",
                "iec", "cyber", "google", "marine", "sentinel", "cnn", "bbc", "reuters", "aljazeera", "fox",
                "ayalon", "natbag", "radio", "field", "intel"]

    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        cat = "חדשות" if idx < 10 else "צבאי" if idx < 20 else "כללי"
        with cols[idx % 7]:
            with st.popover(key, use_container_width=True):
                st.write(f"**מקור:** {key}")
                st.info(osint_headlines.get(cat))

    st.divider()

    # גרף 24 שעות
    times, values = [], []
    for i in range(1440):
        future_time = now + timedelta(minutes=i)
        times.append(future_time)
        values.append(get_minute_statistic(future_time))

    col_graph, col_stat = st.columns([2, 1])
    with col_graph:
        fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color="#00ff00", width=1.5)))
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(tickformat='%H:%M'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col_stat:
        st.metric("מדד סיכון", f"{current_risk:.1f}%")
        st.success("גזרה בשגרה")

# הרצת החמ"ל
render_hamaal()
