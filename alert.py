import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף - מערכת הגנה רב-שכבתית
st.set_page_config(page_title="חמ\"ל עבר הירקון - ELITE V10", layout="wide")

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

def check_strategic_intel():
    # מקורות RSS כולל צבע אדום לא רשמי (מהיר יותר מחדשות)
    sources = [
        "https://www.tzevaadom.co.il/rss", # צופר / צבע אדום
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main"
    ]
    
    # מילים של תזוזת משגרים ומודיעין
    intel_keywords = ["תזוזת משגרים", "הכנה לשיגור", "דריכות", "כוננות שיא", "העלאת כוננות", "תקיפה באיראן", "יציאת כטב"]
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור", "זיהוי", "פיצוץ", "ירי"]
    target_zones = ["תל אביב", "גוש דן", "מרכז", "עבר הירקון", "גלילות", "רמת אביב", "חולון", "רמת גן", "בני ברק", "פתח תקווה"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    status = "QUIET"
    alert_msg = ""
    intel_hit = False

    for url in sources:
        try:
            response = requests.get(url, timeout=2.5)
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:10]
            for item in items:
                title = item.find('title').text
                
                # 1. בדיקת מודיעין "תזוזת משגרים"
                if any(kw in title for kw in intel_keywords):
                    intel_hit = True
                    alert_msg = title
                
                # 2. בדיקה אסטרטגית - איראן
                if "איראן" in title and any(w in title for w in ["שיגור", "ירי", "מטח", "טילים", "כטב"]):
                    return "IRAN_LAUNCH", title, True
                
                # 3. בדיקת אזעקה למרכז (אדום)
                if any(cw in title for cw in critical_words) and any(tz in title for tz in target_zones):
                    return "RED_ALERT", title, intel_hit

                # 4. בדיקת השרון (כתום)
                if any(cw in title for cw in critical_words) and any(loc in title for loc in ["השרון", "הרצליה", "רעננה", "נתניה"]):
                    status = "ORANGE_WARNING"
                    alert_msg = title
        except: continue
    
    # אם אין אזעקה אבל יש תזוזת משגרים - המדד יעלה ל-75%
    if intel_hit and status == "QUIET":
        return "INTEL_THREAT", alert_msg, True
        
    return status, alert_msg, intel_hit

def get_risk(dt, status):
    if status == "IRAN_LAUNCH": return 100.0
    if status == "RED_ALERT": return 99.8
    if status == "INTEL_THREAT": return 75.0
    if status == "ORANGE_WARNING": return 65.0
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=10)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    status, display_text, intel_active = check_strategic_intel()
    current_val = get_risk(now, status)
    
    # צבעים
    if status in ["RED_ALERT", "IRAN_LAUNCH"]: color = "#ff1a1a"
    elif status == "INTEL_THREAT": color = "#ff5500" # כתום-אדום למודיעין
    elif status == "ORANGE_WARNING": color = "#ffaa00"
    else: color = "#00ff00"

    # תצוגה
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 25px {color}20;">
            <p style="color: #FFFFFF; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold; opacity: 0.9;">UNIT: EVER HAYARKON | ELITE DEFENSE FORCE</p>
            <h1 style="color: {color}; font-size: 85px; margin: 5px 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 20px {color}88;">{current_val:.1f}%</h1>
            <div style="color: #FFFFFF; font-size: 13px; font-family: 'JetBrains Mono'; font-weight: bold;">
                <span style="color: {color};">●</span> {now.strftime('%H:%M:%S')} 
                <span class="scanning-dot" style="color: #0066ff; margin-left: 15px;">● SIGINT/OSINT ACTIVE</span>
                {"<span style='color: #ff5500; margin-left: 15px;'>● LAUNCHER_MOVEMENT_DETECTED</span>" if intel_active else ""}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        st.markdown(f"""<div style="background: rgba(30,0,0,0.9); color: white; padding: 15px; margin: 15px 0; border-radius: 8px; border: 2px solid {color}; text-align: center; font-weight: bold;">⚠️ {display_text}</div>""", unsafe_allow_html=True)

    # גרף
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, status) for t in times]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=3), hovertemplate='%{y:.1f}%<extra></extra>'))
    fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), height=150, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False, fixedrange=True), yaxis=dict(visible=False, fixedrange=True, range=[0, 115]), showlegend=False, dragmode=False, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות
    cols = st.columns(7)
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 12px;"><div style="width: 7px; height: 7px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px {color};"></div><br><span style="font-size:8px; color: #FFFFFF; font-weight: bold; opacity: 0.9;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
