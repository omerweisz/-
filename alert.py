import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף - חמ"ל מבצעי דינמי
st.set_page_config(page_title="חמ\"ל עבר הירקון - AUTO-RESET V11", layout="wide")

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
    sources = [
        "https://www.tzevaadom.co.il/rss", 
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main"
    ]
    
    intel_keywords = ["תזוזת משגרים", "הכנה לשיגור", "דריכות", "כוננות שיא", "העלאת כוננות", "תקיפה באיראן"]
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור", "זיהוי", "פיצוץ", "ירי"]
    target_zones = ["תל אביב", "גוש דן", "מרכז", "עבר הירקון", "גלילות", "רמת אביב", "חולון", "רמת גן", "בני ברק", "פתח תקווה"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    status = "QUIET"
    alert_msg = ""
    intel_hit = False
    last_alert_time = None

    for url in sources:
        try:
            response = requests.get(url, timeout=2.5)
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:10]
            for item in items:
                title = item.find('title').text
                try:
                    pub_date = parser.parse(item.find('pubDate').text)
                except: continue
                
                # בדיקה אם האירוע קרה ב-15 הדקות האחרונות
                is_recent = 0 <= (now - pub_date).total_seconds() / 60 <= 15
                
                if is_recent:
                    # 1. איראן
                    if "איראן" in title and any(w in title for w in ["שיגור", "ירי", "מטח", "טילים"]):
                        return "IRAN_LAUNCH", title, True, pub_date
                    
                    # 2. אזעקה במרכז
                    if any(cw in title for cw in critical_words) and any(tz in title for tz in target_zones):
                        return "RED_ALERT", title, False, pub_date

                    # 3. מודיעין
                    if any(kw in title for kw in intel_keywords):
                        intel_hit = True
                        status = "INTEL_THREAT"
                        alert_msg = title
                        last_alert_time = pub_date

                    # 4. השרון
                    if any(cw in title for cw in critical_words) and any(loc in title for loc in ["השרון", "הרצליה", "רעננה"]):
                        if status != "INTEL_THREAT":
                            status = "ORANGE_WARNING"
                            alert_msg = title
                            last_alert_time = pub_date
        except: continue
        
    return status, alert_msg, intel_hit, last_alert_time

def get_risk(dt, status):
    # אם אין אירוע פעיל ב-15 דקות האחרונות, מחזירים לשגרה
    if status == "IRAN_LAUNCH": return 100.0
    if status == "RED_ALERT": return 99.8
    if status == "INTEL_THREAT": return 75.0
    if status == "ORANGE_WARNING": return 65.0
    
    # חישוב שגרתי
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=10)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    status, display_text, intel_active, event_time = check_strategic_intel()
    current_val = get_risk(now, status)
    
    color = "#ff1a1a" if status in ["RED_ALERT", "IRAN_LAUNCH"] else "#ff5500" if status == "INTEL_THREAT" else "#ffaa00" if status == "ORANGE_WARNING" else "#00ff00"

    # תצוגה
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 25px {color}20;">
            <p style="color: #FFFFFF; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold; opacity: 0.9;">UNIT: EVER HAYARKON | ACTIVE DEFENSE</p>
            <h1 style="color: {color}; font-size: 85px; margin: 5px 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 20px {color}88;">{current_val:.1f}%</h1>
            <div style="color: #FFFFFF; font-size: 13px; font-family: 'JetBrains Mono'; font-weight: bold;">
                <span style="color: {color};">●</span> {now.strftime('%H:%M:%S')} 
                <span class="scanning-dot" style="color: #0066ff; margin-left: 15px;">● SYSTEM_READY</span>
                {f"<span style='color: {color}; margin-left: 15px;'>● EVENT_ACTIVE</span>" if status != "QUIET" else ""}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        st.markdown(f"""<div style="background: rgba(30,0,0,0.9); color: white; padding: 15px; margin: 15px 0; border-radius: 8px; border: 2px solid {color}; text-align: center; font-weight: bold;">⚠️ {display_text}</div>""", unsafe_allow_html=True)

    # גרף - מציג את השגרה הצפויה
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, "QUIET") for t in times] # הגרף תמיד מראה את קו השגרה
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color if status=="QUIET" else "#444", width=2), hovertemplate='%{y:.1f}%<extra></extra>'))
    
    # סימון המצב הנוכחי על הגרף
    fig.add_trace(go.Scatter(x=[now], y=[current_val], mode='markers', marker=dict(color=color, size=12, line=dict(color='white', width=2))))
    
    fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), height=150, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False, fixedrange=True), yaxis=dict(visible=False, fixedrange=True, range=[0, 115]), showlegend=False, dragmode=False, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות
    cols = st.columns(7)
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 12px;"><div style="width: 7px; height: 7px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px {color};"></div><br><span style="font-size:8px; color: #FFFFFF; font-weight: bold; opacity: 0.9;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
