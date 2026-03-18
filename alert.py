import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - STRATEGIC V7", layout="wide")

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

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml"
    ]
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור", "זיהוי", "פיצוץ"]
    
    # מעגל 1: פגיעה ישירה או סביבה קרובה מאוד
    core_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "הדר יוסף"]
    
    # מעגל 2: סביבה קרובה (השרון והמרכז הכללי)
    perimeter_targets = ["השרון", "מרכז", "גוש דן", "הרצליה", "רעננה", "נתניה", "כפר סבא", "פתח תקווה", "חולון", "ראשון לציון"]
    
    # מילים שמעידות על אירוע כלל-ארצי או מכוון למרכז (לסינון ירי לצפון בלבד)
    strategic_context = ["מרכז", "גוש דן", "ישראל", "נרחב", "עומק", "תל אביב"]
    strategic_threats = ["איראן", "תימן", "חיזבאללה", "לבנון"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    status = "QUIET"
    alert_msg = ""

    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                pub_date = parser.parse(item.find('pubDate').text)
                if 0 <= (now - pub_date).total_seconds() / 60 <= 15:
                    
                    # 1. בדיקת מעגל 1 (אדום)
                    if any(word in title for word in critical_words) and any(loc in title for loc in core_targets):
                        return "RED_ALERT", title
                    
                    # 2. בדיקת איום אסטרטגי (אדום) - רק אם יש הקשר למרכז/ישראל
                    is_threat_source = any(threat in title for threat in strategic_threats)
                    has_critical_action = any(w in title for w in ["מטח", "שיגור", "תקיפה", "ירי"])
                    has_strategic_context = any(ctx in title for ctx in strategic_context)
                    
                    if is_threat_source and has_critical_action and has_strategic_context:
                        return "RED_ALERT", title

                    # 3. בדיקת מעגל 2 (כתום - השרון/מרכז)
                    if any(word in title for word in critical_words) and any(loc in title for loc in perimeter_targets):
                        status = "ORANGE_WARNING"
                        alert_msg = title
        except: continue
    
    return status, alert_msg

def get_risk(dt, status):
    if status == "RED_ALERT": return 99.8
    if status == "ORANGE_WARNING": return 65.0
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    status, display_text = check_multi_source_osint()
    current_val = get_risk(now, status)
    
    # בחירת צבע
    color = "#ff1a1a" if status == "RED_ALERT" else "#ffaa00" if status == "ORANGE_WARNING" else "#00ff00"

    # תצוגה עליונה
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 20px {color}15;">
            <p style="color: #FFFFFF; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold;">UNIT: EVER HAYARKON | STRATEGIC DEFENSE</p>
            <h1 style="color: {color}; font-size: 75px; margin: 5px 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 15px {color}66;">{current_val:.1f}%</h1>
            <div style="color: #FFFFFF; font-size: 13px; font-family: 'JetBrains Mono'; font-weight: bold;">
                <span style="color: {color};">●</span> {now.strftime('%H:%M:%S')} 
                <span class="scanning-dot" style="color: #0066ff; margin-left: 15px;">● RADAR_ACTIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        label = "סכנה מיידית" if status == "RED_ALERT" else "פעילות בגזרה שכנה"
        st.markdown(f"""<div style="background: rgba(26,0,0,0.9); color: white; padding: 12px; margin: 15px 0; border-radius: 8px; font-size: 14px; border: 1px solid {color}; text-align: center; font-weight: bold; box-shadow: 0 0 15px {color}44;"><b>[{label}]</b> ⚠️ {display_text}</div>""", unsafe_allow_html=True)

    # גרף עם Hover וביטול זום
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, status) for t in times]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=values, fill='tozeroy', 
        line=dict(color=color, width=3), 
        fillcolor=f"rgba({255 if status!='QUIET' else 0}, {170 if status=='ORANGE_WARNING' else 255}, 0, 0.1)",
        hovertemplate='%{y:.1f}%<extra></extra>'
    ))
    fig.add_vline(x=now, line_width=2, line_dash="solid", line_color="rgba(255,255,255,0.5)")
    fig.update_layout(
        margin=dict(l=0, r=0, t=5, b=0), height=150,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True, range=[0, 110]),
        showlegend=False, dragmode=False, hovermode='x unified',
        hoverlabel=dict(bgcolor="black", font_size=12, font_family="JetBrains Mono", font_color="white")
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות בקרה
    cols = st.columns(7)
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 10px;"><div style="width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {color};"></div><br><span style="font-size:8px; color: #FFFFFF; font-weight: bold; opacity: 0.8; text-transform: uppercase;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
