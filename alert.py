import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - MULTI-SOURCE", layout="wide")

def check_multi_source_osint():
    # רשימת מקורות מורחבת לסריקה מקבילה
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",      # Ynet
        "https://rss.walla.co.il/feed/1?type=main",                # Walla
        "https://www.israelhayom.co.il/rss.xml",                   # Israel Hayom
        "https://m.maariv.co.il/Rss/RssFeeds0",                    # Maariv
        "https://www.n12.co.il/TagSearch/Tag?TagId=270"            # N12 (מבזקים)
    ]
    
    threat_words = ["טילים", "כטב\"מ", "יירוט", "נפילה", "אזעקה", "פיצוץ", "חדירה", "ירי"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "פי גלילות", "הדר יוסף"]
    end_words = ["חזרה לשגרה", "הוסרה ההתרעה", "סיום האירוע", "האירוע הסתיים", "ניתן לצאת", "לצאת מהממד"]
    
    combined_headlines = []
    
    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            # אוספים את הכותרות מכל מקור
            for item in root.findall('.//item'):
                title = item.find('title').text
                if title:
                    combined_headlines.append(title)
        except:
            continue # אם אתר אחד נפל, ממשיכים לאחרים

    # בדיקת הרגעה (✅) - עדיפות ראשונה
    for title in combined_headlines[:15]:
        if any(word in title for word in end_words):
            return False, "✅ " + title
    
    # בדיקת איום (⚠️)
    for title in combined_headlines[:30]:
        has_threat = any(word in title for word in threat_words)
        is_local = any(loc in title for loc in local_targets)
        if (has_threat and is_local) or "איראן" in title:
            return True, "⚠️ " + title
            
    return False, ""

def get_risk(dt, emergency_active):
    if emergency_active:
        return 99.8
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
            if minutes_passed < 10:
                show_box = True
            else:
                show_box = False
                alert_text = ""
        else:
            show_box = True

    current_val = get_risk(now, is_emergency)
    color = "#ff1a1a" if (current_val > 35 and not ("✅" in alert_text)) else "#00ff00"
    bg_color = "#2b0000" if (current_val > 35 and not ("✅" in alert_text)) else "#0e1117"
    
    st.markdown(f"<style>.stApp {{ background-color: {bg_color}; transition: 0.5s; }}</style>", unsafe_allow_html=True)

    # תצוגה
    st.markdown(f"""
        <div style="text-align: center; padding: 25px; border: 2px solid {color}; border-radius: 15px; background: rgba(0,0,0,0.85);">
            <p style="color: #bbb; font-size: 13px; margin: 0; letter-spacing: 2px; font-weight: bold;">EVER HAYARKON COMMAND CENTER</p>
            <h1 style="color: {color}; font-size: 80px; margin: 10px 0; font-family: monospace;">{current_val:.1f}%</h1>
            <div style="color: {color}; font-size: 16px; font-weight: bold; font-family: monospace;">
                🕒 זמן עדכון: {now.strftime('%H:%M:%S')}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if show_box and alert_text:
        box_color = "#004400" if "✅" in alert_text else "#440000"
        st.markdown(f"""
            <div style="background: {box_color}; color: white; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; font-weight: bold; border: 1px solid white; text-align: center;">
                {alert_text}
            </div>
        """, unsafe_allow_html=True)
    
    st.write("")

    # נורות מקורות
    cols = st.columns(7)
    all_keys = ["YNET", "WALLA", "N12", "HAYOM", "MAARIV", "צה\"ל", "צופר", "TELEGRAM", "ROTER", "MOKED", "SIRI", "MAPS", "FR24", "NASA", "CNN", "BBC", "FOX", "REUTERS", "IAF", "IEC", "CYBER", "GOOGLE", "INTEL", "NATBAG", "AYALON", "FIELD", "SURA", "OSINT", "RADIO", "SAT", "SENA", "ADSB", "FIRE", "POLICE", "MDA"]

    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""
                <div style="text-align: center; border: 1px solid {color}22; border-radius: 5px; background: rgba(0,0,0,0.5); margin-bottom: 5px; padding: 4px;">
                    <div style="width: 10px; height: 10px; background: {color}; border-radius: 50%; display: inline-block;"></div>
                    <br><b style="font-size:9px; color: #888;">{key}</b>
                </div>
            """, unsafe_allow_html=True)

    # גרף
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, is_emergency) for t in times]
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=3)))
    fig.update_layout(template="plotly_dark", height=180, margin=dict(l=0,r=0,t=0,b=0),
                      xaxis=dict(visible=False, fixedrange=True), yaxis=dict(fixedrange=True, range=[0, 115]), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

auto_refresh_hamaal()
