import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - LIVE", layout="wide")

# CSS מיוחד כדי להעלים את הלבן בגרף ובדף בטלפון
st.markdown("""
    <style>
    .stPlotlyChart { background-color: transparent !important; }
    div[data-testid="stPlotlyChart"] { background-color: transparent !important; }
    .main { background-color: #0a0a0a; }
    </style>
""", unsafe_allow_html=True)

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml",
        "https://m.maariv.co.il/Rss/RssFeeds0",
        "https://www.n12.co.il/TagSearch/Tag?TagId=270"
    ]
    threat_words = ["טילים", "כטב\"מ", "יירוט", "נפילה", "אזעקה", "פיצוץ", "חדירה", "ירי"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "פי גלילות", "הדר יוסף"]
    end_words = ["חזרה לשגרה", "הוסרה ההתרעה", "סיום האירוע", "האירוע הסתיים", "ניתן לצאת", "לצאת מהממד"]
    
    combined_headlines = []
    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                if title: combined_headlines.append(title)
        except: continue

    for title in combined_headlines[:15]:
        if any(word in title for word in end_words):
            return False, "✅ " + title
    
    for title in combined_headlines[:30]:
        if any(word in title for word in threat_words) and any(loc in title for loc in local_targets):
            return True, "⚠️ " + title
        if "איראן" in title:
            return True, "⚠️ " + title
            
    return False, ""

def get_risk(dt, emergency_active):
    if emergency_active: return 99.8
    hour = dt.hour
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.utcnow() + timedelta(hours=2) 
    
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = {}

    is_emergency, alert_text = check_multi_source_osint()
    
    show_box = False
    if alert_text:
        if alert_text not in st.session_state.alert_history:
            st.session_state.alert_history[alert_text] = now
        first_seen = st.session_state.alert_history[alert_text]
        minutes_passed = (now - first_seen).total_seconds() / 60
        
        if "✅" in alert_text:
            if minutes_passed < 10: show_box = True
            else: alert_text = ""
        else: show_box = True

    current_val = get_risk(now, is_emergency)
    is_red = (current_val > 35 and not ("✅" in alert_text))
    color = "#ff1a1a" if is_red else "#00ff00"
    
    # תצוגה עליונה נקייה
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 10px; background: #000;">
            <p style="color: #666; font-size: 10px; margin: 0; letter-spacing: 2px;">SECTOR: EVER HAYARKON</p>
            <h1 style="color: {color}; font-size: 65px; margin: 5px 0; font-family: monospace;">{current_val:.1f}%</h1>
            <p style="color: {color}aa; font-size: 12px; font-family: monospace;">🕒 {now.strftime('%H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)

    if show_box and alert_text:
        box_color = "#002200" if "✅" in alert_text else "#220000"
        st.markdown(f"""<div style="background: {box_color}; color: white; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 13px; font-weight: bold; border: 1px solid {color}; text-align: center;">{alert_text}</div>""", unsafe_allow_html=True)

    # --- הגרף האולטימטיבי למובייל ---
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, is_emergency) for t in times]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=values, 
        fill='tozeroy', 
        line=dict(color=color, width=2),
        fillcolor=f"rgba({255 if is_red else 0}, {26 if is_red else 255}, 0, 0.1)"
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True, range=[0, 110]),
        showlegend=False,
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות (35) - קטנות יותר למובייל
    cols = st.columns(7)
    all_keys = ["YNET", "WALLA", "N12", "HAYOM", "MAARIV", "צה\"ל", "צופר", "TG", "ROTER", "MOKED", "SIRI", "MAPS", "FR24", "NASA", "CNN", "BBC", "FOX", "IAF", "IEC", "GOOGLE", "AYALON", "FIELD", "SURA", "OSINT", "RADIO", "SAT", "SENA", "ADSB", "FIRE", "POLICE", "MDA", "IDF", "ISR", "USA", "UK"]

    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 5px;"><div style="width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px {color}aa;"></div><br><span style="font-size:7px; color: #444;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
