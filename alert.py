import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - ELITE V5", layout="wide")

# CSS מתקדם לאפקטים ויזואליים ומעברים
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000;
        font-family: 'JetBrains+Mono', monospace;
    }
    
    .stPlotlyChart { background-color: transparent !important; transition: all 1s ease; }
    
    /* אנימציית הבהוב לסריקה */
    @keyframes blinker { 50% { opacity: 0.3; } }
    .scanning-dot { animation: blinker 1.5s linear infinite; }
    
    /* מעברים חלקים לכל הממשק */
    div, h1, p, span { transition: color 1s ease, border-color 1s ease, box-shadow 1s ease; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def check_sources_health():
    # בדיקה מהירה אם המקורות זמינים
    try:
        r = requests.get("https://www.ynet.co.il/Integration/StoryRss1854.xml", timeout=1)
        return "OK" if r.status_code == 200 else "DB_ERR"
    except:
        return "OFFLINE"

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml"
    ]
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור", "זיהוי", "נפץ"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "הדר יוסף", "המרכז", "גוש דן"]
    strategic_threats = ["איראן", "לבנון", "חיזבאללה", "תימן"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    
    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                pub_date_str = item.find('pubDate').text
                pub_date = parser.parse(pub_date_str)
                diff = (now - pub_date).total_seconds() / 60
                
                if 0 <= diff <= 15:
                    has_attack = any(word in title for word in critical_words)
                    is_local = any(loc in title for loc in local_targets)
                    is_strategic_attack = any(threat in title for threat in strategic_threats) and \
                                         any(w in title for w in ["מטח", "שיגור", "תקיפה", "ירי", "לעבר המרכז", "לעבר ישראל"])
                    
                    if (has_attack and is_local) or is_strategic_attack:
                        return True, title
        except: continue
    return False, ""

def get_risk(dt, emergency_active):
    if emergency_active: return 99.8
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    health_status = check_sources_health()
    is_emergency, display_text = check_multi_source_osint()
    current_val = get_risk(now, is_emergency)
    color = "#ff1a1a" if is_emergency else "#00ff00"
    health_color = "#00ff00" if health_status == "OK" else "#ffaa00"

    # תצוגה עליונה משופרת
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 20px {color}15;">
            <p style="color: #666; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold;">UNIT: EVER HAYARKON | SECTOR 7</p>
            <h1 style="color: {color}; font-size: 70px; margin: 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 15px {color}66;">{current_val:.1f}%</h1>
            <div style="color: white; font-size: 12px; font-family: 'JetBrains Mono'; margin-top: 10px;">
                <span style="color: {color};">●</span> {now.strftime('%H:%M:%S')} 
                <span class="scanning-dot" style="color: #0066ff; margin-left: 15px;">● SCANNING</span>
                <span style="color: {health_color}; margin-left: 15px; font-size: 10px;">[SYS_{health_status}]</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        st.markdown(f"""<div style="background: rgba(26,0,0,0.8); color: white; padding: 12px; margin: 15px 0; border-radius: 8px; font-size: 13px; border: 1px solid {color}; text-align: center; font-weight: bold; box-shadow: 0 0 10px {color}33;">⚠️ {display_text}</div>""", unsafe_allow_html=True)

    # גרף עם פס סריקה (Radar Line)
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, is_emergency) for t in times]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=3), fillcolor=f"rgba({255 if is_emergency else 0}, {255 if not is_emergency else 26}, 0, 0.1)"))
    
    # הוספת קו הסריקה (הזמן הנוכחי)
    fig.add_vline(x=now, line_width=2, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=5, b=0), height=160,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True, range=[0, 110 if is_emergency else 45]),
        showlegend=False, dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות (35) עם אפקט Glow
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 10px;">
                    <div style="width: 7px; height: 7px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {color}, 0 0 12px {color}88;"></div>
                    <br><span style="font-size:8px; color: #555; font-weight: bold; text-transform: uppercase;">{key}</span>
                </div>
            """, unsafe_allow_html=True)

auto_refresh_hamaal()
