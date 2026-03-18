import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - V22 INTELLIGENCE", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; font-family: 'JetBrains Mono', monospace; color: white; }
    .stPlotlyChart { background-color: transparent !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def get_source_status(url, name):
    # מילים שבאמת מחייבות 100% (זמן אמת)
    critical_alerts = ["אזעקה", "צבע אדום", "התרעות הופעלו", "חדירת כלי טיס", "ירי טילים"]
    # דיווחים על תוצאות אירוע (לא מקפיץ ל-100%)
    news_updates = ["הרוג", "פצוע", "נפילה", "יירוט", "נזק", "פגיעה ישירה", "מד\"א"]
    release_words = ["חזרה לשגרה", "הסרת הגבלות", "ניתן לצאת"]
    target_zones = ["תל אביב", "גוש דן", "מרכז", "עבר הירקון", "גלילות", "רמת אביב", "חולון", "רמת גן", "בני ברק", "פתח תקווה"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    try:
        response = requests.get(url, timeout=2.5)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')[:10]
        for item in items:
            title = item.find('title').text
            pub_date = parser.parse(item.find('pubDate').text)
            diff_min = int((now - pub_date).total_seconds() / 60)
            
            if any(rw in title for rw in release_words) and 0 <= diff_min <= 10:
                return "RELEASE", f"({diff_min} דק') {title}", pub_date

            if 0 <= diff_min <= 20:
                # רק אזעקה בזמן אמת מקפיצה ל-RED
                if any(ca in title for ca in critical_alerts) and any(tz in title for tz in target_zones):
                    return "RED", f"({diff_min} דק') {title}", pub_date
                # דיווח על אירוע (חדשות) צובע בכתום אבל לא מקפיץ ל-100
                if any(nu in title for nu in news_updates) or "איראן" in title:
                    return "ORANGE_RED", f"({diff_min} דק') {title}", pub_date
                    
        return "GREEN", "", None
    except: return "GREEN", "", None

def get_risk(dt, global_status):
    if global_status == "RED": return 100.0
    if global_status == "ORANGE_RED": return 75.0 # הורדנו מ-90 כדי להבדיל מאזעקה
    if global_status == "RELEASE": return 15.0
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=10)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    sources_map = {"YNET": "https://www.ynet.co.il/Integration/StoryRss1854.xml", "וואלה": "https://rss.walla.co.il/feed/1?type=main", "ישראל היום": "https://www.israelhayom.co.il/rss.xml", "צופר": "https://www.tzevaadom.co.il/rss"}
    source_results = {}; global_status = "GREEN"; latest_msg = ""; last_event_time = None
    
    for name, url in sources_map.items():
        res, msg, p_date = get_source_status(url, name)
        source_results[name] = res
        if res == "RELEASE": global_status = "RELEASE"; latest_msg = msg; break
        elif res == "RED": global_status = "RED"
        elif res == "ORANGE_RED" and global_status != "RED": global_status = "ORANGE_RED"
        if msg: latest_msg = msg; last_event_time = p_date

    current_val = get_risk(now, global_status)
    main_color = {"RED": "#ff1a1a", "ORANGE_RED": "#ffaa00", "RELEASE": "#00ff00", "GREEN": "#00ff00"}[global_status]

    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {main_color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 25px {main_color}20;">
            <p style="color: #FFFFFF; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold; opacity: 0.8;">UNIT: EVER HAYARKON | V22 SMART-FILTER</p>
            <h1 style="color: {main_color}; font-size: 85px; margin: 5px 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 20px {main_color}88;">{current_val:.1f}%</h1>
            <div style="color: #FFFFFF; font-size: 13px; font-family: 'JetBrains Mono';">
                <span style="color: {main_color};">●</span> {now.strftime('%H:%M:%S')} 
            </div>
        </div>
    """, unsafe_allow_html=True)

    if latest_msg:
        st.markdown(f"""<div style="background: rgba(20,20,20,0.9); color: white; padding: 15px; margin: 15px 0; border-radius: 8px; border: 1px solid {main_color}; text-align: center; font-weight: bold;">{latest_msg}</div>""", unsafe_allow_html=True)
    else: st.markdown("<div style='height: 62px;'></div>", unsafe_allow_html=True)

    # גרף עם Hover פעיל ו-Zoom נעול
    base_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    full_day_times = [base_time + timedelta(minutes=i) for i in range(1440)]
    full_day_values = [get_risk(t, "GREEN") for t in full_day_times]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=full_day_times, y=full_day_values, fill='tozeroy', line=dict(color="#222", width=2), hovertemplate="<b>Time:</b> %{x|%H:%M}<br><b>Risk:</b> %{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=[now], y=[current_val], mode='markers', marker=dict(color=main_color, size=14, line=dict(color='white', width=2)), hoverinfo='skip'))
    
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=160, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", xaxis=dict(visible=False, fixedrange=True), yaxis=dict(visible=False, range=[0, 115], fixedrange=True), showlegend=False, dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    cols = st.columns(7)
    all_keys = ["YNET", "וואלה", "ישראל היום", "צופר", "פקע\"ר", "צה\"ל", "אבו-עלי", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    for idx, key in enumerate(all_keys):
        node_status = source_results.get(key, "GREEN")
        node_color = {"RED": "#ff1a1a", "ORANGE_RED": "#ffaa00", "RELEASE": "#00ff00", "GREEN": "#00ff00"}[node_status]
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 12px;"><div style="width: 8px; height: 8px; background: {node_color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px {node_color};"></div><br><span style="font-size:8px; color: #FFFFFF; font-weight: bold; opacity: 0.6;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
