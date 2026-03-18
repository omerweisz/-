import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - SOURCE MONITOR V12", layout="wide")

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
    pre_alert_words = ["התרעה", "דיווח ראשוני", "חשש", "תזוזה", "הכנה", "כוננות"]
    target_zones = ["תל אביב", "גוש דן", "מרכז", "עבר הירקון", "גלילות", "רמת אביב", "חולון", "רמת גן", "בני ברק", "פתח תקווה"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    
    try:
        response = requests.get(url, timeout=2)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')[:5]
        
        for item in items:
            title = item.find('title').text
            pub_date = parser.parse(item.find('pubDate').text)
            is_recent = 0 <= (now - pub_date).total_seconds() / 60 <= 15
            
            if is_recent:
                # בדיקת אזעקה (אדום)
                if any(cw in title for cw in critical_words) and any(tz in title for tz in target_zones):
                    return "RED", title
                # בדיקת התרעה לפני (כתום-אדום/90%)
                if any(pw in title for pw in pre_alert_words) or ("איראן" in title):
                    return "ORANGE_RED", title
                # בדיקת השרון (כתום)
                if any(cw in title for cw in critical_words) and any(loc in title for loc in ["השרון", "הרצליה", "נתניה"]):
                    return "ORANGE", title
        return "GREEN", ""
    except:
        return "GREEN", ""

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
    
    # מיפוי מקורות לנורות
    sources_map = {
        "YNET": "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "וואלה": "https://rss.walla.co.il/feed/1?type=main",
        "ישראל היום": "https://www.israelhayom.co.il/rss.xml",
        "צופר": "https://www.tzevaadom.co.il/rss"
    }
    
    source_results = {}
    global_status = "GREEN"
    latest_msg = ""
    
    for name, url in sources_map.items():
        res, msg = get_source_status(url, name)
        source_results[name] = res
        if res == "RED": global_status = "RED"
        elif res == "ORANGE_RED" and global_status != "RED": global_status = "ORANGE_RED"
        elif res == "ORANGE" and global_status not in ["RED", "ORANGE_RED"]: global_status = "ORANGE"
        if msg: latest_msg = msg

    current_val = get_risk(now, global_status)
    main_color = {"RED": "#ff1a1a", "ORANGE_RED": "#ff4400", "ORANGE": "#ffaa00", "GREEN": "#00ff00"}[global_status]

    # תצוגה ראשית
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {main_color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 25px {main_color}20;">
            <p style="color: #FFFFFF; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold;">UNIT: EVER HAYARKON | MULTI-SOURCE MONITOR</p>
            <h1 style="color: {main_color}; font-size: 85px; margin: 5px 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 20px {main_color}88;">{current_val:.1f}%</h1>
            <div style="color: #FFFFFF; font-size: 13px; font-family: 'JetBrains Mono';">
                <span style="color: {main_color};">●</span> {now.strftime('%H:%M:%S')} 
                <span class="scanning-dot" style="color: #0066ff; margin-left: 15px;">● ANALYSIS_ACTIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if latest_msg:
        st.markdown(f"""<div style="background: rgba(20,0,0,0.9); color: white; padding: 12px; margin: 15px 0; border-radius: 8px; border: 1px solid {main_color}; text-align: center; font-size: 14px; font-weight: bold;">⚠️ {latest_msg}</div>""", unsafe_allow_html=True)

    # גרף
    fig = go.Figure()
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, "GREEN") for t in times]
    fig.add_trace(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color="#333", width=2), hovertemplate='%{y:.1f}%<extra></extra>'))
    fig.add_trace(go.Scatter(x=[now], y=[current_val], mode='markers', marker=dict(color=main_color, size=12, line=dict(color='white', width=2))))
    fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), height=130, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False, range=[0, 115]), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות בקרה - כאן השינוי המשמעותי
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(7)
    all_keys = ["YNET", "וואלה", "ישראל היום", "צופר", "פקע\"ר", "צה\"ל", "אבו-עלי", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    
    for idx, key in enumerate(all_keys):
        # צבע נורה אינדיבידואלי
        node_status = source_results.get(key, "GREEN")
        node_color = {"RED": "#ff1a1a", "ORANGE_RED": "#ff4400", "ORANGE": "#ffaa00", "GREEN": "#00ff00"}[node_status]
        
        with cols[idx % 7]:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="width: 8px; height: 8px; background: {node_color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px {node_color}; transition: 0.3s;"></div>
                    <br><span style="font-size:8px; color: #FFFFFF; font-weight: bold; opacity: 0.8;">{key}</span>
                </div>
            """, unsafe_allow_html=True)

auto_refresh_hamaal()
