import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - STRATEGIC", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; font-family: 'JetBrains Mono', monospace; }
    .stPlotlyChart { background-color: transparent !important; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .scanning-dot { animation: blinker 1.5s linear infinite; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def check_sources_health():
    health = {"NEWS": "OK", "AIR": "OK"}
    try:
        if requests.get("https://www.ynet.co.il", timeout=1.5).status_code != 200: health["NEWS"] = "ERR"
        if requests.get("https://www.flightradar24.com", timeout=1.5).status_code != 200: health["AIR"] = "ERR"
    except: health = {"NEWS": "DOWN", "AIR": "DOWN"}
    return health

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml"
    ]
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור", "זיהוי", "נפץ", "פיצוץ"]
    negative_words = ["שגרה", "הסרת", "בדיקה", "תרגיל", "חזרה", "סיום", "שווא", "הכחשה"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "הדר יוסף", "המרכז", "גוש דן", "חולון", "רמת גן"]
    strategic_threats = ["איראן", "לבנון", "חיזבאללה", "תימן", "כטב\"ם"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    hits = [] # רשימת מקורות שזיהו אירוע
    
    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                pub_date = parser.parse(item.find('pubDate').text)
                diff = (now - pub_date).total_seconds() / 60
                
                if 0 <= diff <= 15:
                    # סינון מילים שחורות (סעיף 2)
                    if any(neg in title for neg in negative_words): continue
                    
                    is_local = any(loc in title for loc in local_targets) and any(word in title for word in critical_words)
                    is_strategic = any(threat in title for threat in strategic_threats) and any(w in title for w in ["מטח", "שיגור", "תקיפה", "ירי"])
                    
                    if is_local or is_strategic:
                        hits.append(title)
                        break # נמצא אירוע במקור הנוכחי
        except: continue
    
    # אימות צולב (סעיף 1): אם יותר ממקור אחד דיווח, האמינות עולה
    if len(hits) >= 2: return True, hits[0], "HIGH_CONFIRMATION"
    if len(hits) == 1: return True, hits[0], "SINGLE_SOURCE"
    return False, "", "QUIET"

def get_risk(dt, emergency_active, status_type):
    if emergency_active:
        return 99.8 if status_type == "HIGH_CONFIRMATION" else 85.0
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    health = check_sources_health()
    is_emergency, display_text, status_type = check_multi_source_osint()
    
    # ניהול לוג
    if 'alert_log' not in st.session_state: st.session_state.alert_log = []
    if is_emergency and (not st.session_state.alert_log or display_text != st.session_state.alert_log[0]['msg']):
        st.session_state.alert_log.insert(0, {'time': now.strftime('%H:%M'), 'msg': display_text})
        st.session_state.alert_log = st.session_state.alert_log[:3]

    current_val = get_risk(now, is_emergency, status_type)
    
    # קביעת צבע (ירוק/כתום/אדום) לפי רמת האימות
    if not is_emergency: color = "#00ff00"
    elif status_type == "SINGLE_SOURCE": color = "#ffaa00" # כתום לאימות חלקי
    else: color = "#ff1a1a" # אדום לאימות צולב

    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 20px {color}15;">
            <p style="color: #666; font-size: 10px; margin: 0; letter-spacing: 3px;">UNIT: EVER HAYARKON | STRATEGIC DEP</p>
            <h1 style="color: {color}; font-size: 70px; margin: 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 15px {color}66;">{current_val:.1f}%</h1>
            <div style="color: white; font-size: 11px; font-family: 'JetBrains Mono'; margin-top: 10px;">
                <span style="color: {color};">●</span> {now.strftime('%H:%M:%S')} 
                <span class="scanning-dot" style="color: #0066ff; margin-left: 15px;">● RADAR_ACTIVE</span>
                <span style="color: #444; margin-left: 15px;">| SYS: {health['NEWS']} | AIR: {health['AIR']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        label = "אימות צולב" if status_type == "HIGH_CONFIRMATION" else "דיווח ראשוני"
        st.markdown(f"""<div style="background: rgba(26,0,0,0.8); color: white; padding: 12px; margin: 15px 0; border-radius: 8px; font-size: 13px; border: 1px solid {color}; text-align: center;"><b>[{label}]</b> ⚠️ {display_text}</div>""", unsafe_allow_html=True)

    # גרף 24 שעות עם קו סריקה
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, is_emergency, status_type) for t in times]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=2.5), fillcolor=f"rgba({255 if is_emergency else 0}, {255 if not is_emergency else 26}, 0, 0.08)"))
    fig.add_vline(x=now, line_width=1.5, line_dash="solid", line_color="rgba(255,255,255,0.4)")
    fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), height=140, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False, range=[0, 110 if is_emergency else 45]))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות בקרה
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 8px;"><div style="width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {color};"></div><br><span style="font-size:7px; color: #444; font-weight: bold;">{key}</span></div>""", unsafe_allow_html=True)

    # היסטוריה (סעיף 4 - שקט תעשייתי)
    if st.session_state.alert_log:
        st.markdown("<div style='color: #333; font-size: 9px; margin-top: 10px; border-top: 1px solid #222; padding-top: 5px;'>RECENT LOGS:</div>", unsafe_allow_html=True)
        for entry in st.session_state.alert_log:
            st.markdown(f"<p style='color: #555; font-size: 10px; margin: 0;'>[{entry['time']}] {entry['msg']}</p>", unsafe_allow_html=True)

auto_refresh_hamaal()
