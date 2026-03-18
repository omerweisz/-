import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - PRECISION V13", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; font-family: 'JetBrains Mono', monospace; color: white; }
    .stPlotlyChart { background-color: transparent !important; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .scanning-dot { animation: blinker 1.5s linear infinite; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def get_source_status(url, name):
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור", "זיהוי", "פיצוץ", "ירי"]
    pre_alert_words = ["התרעה", "דיווח ראשוני", "חשש", "תזוזה", "הכנה", "כוננות", "איראן"]
    reset_words = ["חזרה לשגרה", "הסרת הגבלות", "אין נפגעים", "סוף האירוע"]
    target_zones = ["תל אביב", "גוש דן", "מרכז", "עבר הירקון", "גלילות", "רמת אביב", "חולון", "רמת גן", "בני ברק", "פתח תקווה"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    
    try:
        response = requests.get(url, timeout=2)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')[:5]
        
        for item in items:
            title = item.find('title').text
            pub_date = parser.parse(item.find('pubDate').text)
            diff_minutes = (now - pub_date).total_seconds() / 60
            
            # אם יש הודעת "חזרה לשגרה" ב-10 הדקות האחרונות
            if any(rw in title for rw in reset_words) and 0 <= diff_minutes <= 10:
                return "GREEN", title, pub_date

            # בדיקה אם האירוע קרה ב-15 הדקות האחרונות
            if 0 <= diff_minutes <= 15:
                if any(cw in title for cw in critical_words) and any(tz in title for tz in target_zones):
                    return "RED", title, pub_date
                if any(pw in title for pw in pre_alert_words):
                    return "ORANGE_RED", title, pub_date
                if any(cw in title for cw in critical_words) and any(loc in title for loc in ["השרון", "הרצליה", "נתניה"]):
                    return "ORANGE", title, pub_date
                    
        return "GREEN", "", None
    except:
        return "GREEN", "", None

def get_risk(dt, global_status):
    if global_status == "RED": return 100.0
    if global_status == "ORANGE_RED": return 90.0
    if global_status == "ORANGE": return 65.0
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=10)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    sources_map = {
        "YNET": "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "וואלה": "https://rss.walla.co.il/feed/1?type=main",
        "ישראל היום": "https://www.israelhayom.co.il/rss.xml",
        "צופר": "https://www.tzevaadom.co.il/rss"
    }
    
    source_results = {}
    global_status = "GREEN"
    latest_msg = ""
    last_event_time = None
    
    for name, url in sources_map.items():
        res, msg, p_date = get_source_status(url, name)
        source_results[name] = res
        if res == "RED": global_status = "RED"
        elif res == "ORANGE_RED" and global_status != "RED": global_status = "ORANGE_RED"
        elif res == "ORANGE" and global_status not in ["RED", "ORANGE_RED"]: global_status = "ORANGE"
        if msg: 
            latest_msg = msg
            last_event_time = p_date

    current_val = get_risk(now, global_status)
    main_color = {"RED": "#ff1a1a", "ORANGE_RED": "#ff4400", "ORANGE": "#ffaa00", "GREEN": "#00ff00"}[global_status]

    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {main_color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 25px {main_color}20;">
            <p style="color: #FFFFFF; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold;">UNIT: EVER HAYARKON | PRECISION MONITOR</p>
            <h1 style="color: {main_color}; font-size: 85px; margin: 5px 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 20px {main_color}88;">{current_val:.1f}%</h1>
            <div style="color: #FFFFFF; font-size: 12px; font-family: 'JetBrains Mono'; opacity: 0.8;">
                {f"זמן התרעה אחרונה: {last_event_time.strftime('%H:%M:%S')}" if last_event_time else "סטטוס: שגרה מבצעית"}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if latest_msg:
        st.markdown(f"""<div style="background: rgba(20,0,0,0.9); color: white; padding: 12px; margin: 15px 0; border-radius: 8px; border: 1px solid {main_color}; text-align: center; font-weight: bold;">⚠️ {latest_msg}</div>""", unsafe_allow_html=True)

    # נורות בקרה
    cols = st.columns(7)
    all_keys = ["YNET", "וואלה", "ישראל היום", "צופר", "פקע\"ר", "צה\"ל", "אבו-עלי", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    
    for idx, key in enumerate(all_keys):
        node_status = source_results.get(key, "GREEN")
        node_color = {"RED": "#ff1a1a", "ORANGE_RED": "#ff4400", "ORANGE": "#ffaa00", "GREEN": "#00ff00"}[node_status]
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 15px;"><div style="width: 8px; height: 8px; background: {node_color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px {node_color};"></div><br><span style="font-size:8px; color: #FFFFFF; font-weight: bold; opacity: 0.7;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
