import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - PRO", layout="wide")

# CSS להעלמת רקעים לבנים ושיפור נראות הטקסט
st.markdown("""
    <style>
    .stPlotlyChart { background-color: transparent !important; }
    div[data-testid="stPlotlyChart"] { background-color: transparent !important; }
    .main { background-color: #000000; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml"
    ]
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור", "זיהוי"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "הדר יוסף"]
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
                    if any(word in title for word in critical_words) and (any(loc in title for loc in local_targets) or "איראן" in title):
                        return True, title
        except: continue
    return False, ""

def get_risk(dt, emergency_active):
    if emergency_active: return 99.8
    hour = dt.hour
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    is_emergency, display_text = check_multi_source_osint()
    current_val = get_risk(now, is_emergency)
    color = "#ff1a1a" if is_emergency else "#00ff00"
    
    # תצוגה עליונה
    st.markdown(f"""
        <div style="text-align: center; padding: 15px; border: 1px solid {color}44; border-radius: 10px; background: #000;">
            <p style="color: #888; font-size: 11px; margin: 0; letter-spacing: 2px; font-weight: bold;">SECTOR: EVER HAYARKON</p>
            <h1 style="color: {color}; font-size: 60px; margin: 0; font-family: monospace;">{current_val:.1f}%</h1>
            <div style="color: white; font-size: 14px; font-family: monospace; font-weight: bold; margin-top: 5px;">
                <span style="color: {color};">●</span> זמן עדכון: {now.strftime('%H:%M:%S')}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        st.markdown(f"""<div style="background: #1a0000; color: white; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px; border: 1px solid {color}; text-align: center; font-weight: bold;">⚠️ {display_text}</div>""", unsafe_allow_html=True)

    # --- החזרת גרף Plotly המקורי ---
    times = [now + timedelta(minutes=i*20) for i in range(50)]
    values = [get_risk(t, is_emergency) for t in times]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=values, fill='tozeroy', 
        line=dict(color=color, width=3),
        fillcolor=f"rgba({255 if is_emergency else 0}, {26 if is_emergency else 255}, 0, 0.1)"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=150,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True, range=[0, 110]),
        showlegend=False, dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות (35)
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 5px;"><div style="width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px {color}aa;"></div><br><span style="font-size:8px; color: #666; font-weight: bold;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
