import streamlit as st
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stVerticalBlock"] { gap: 0.2rem; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml"
    ]
    # החמרת מילות המפתח - רק אירוע חי באזורנו
    critical_words = ["אזעקה", "חדירה", "נפילה", "יירוט", "מטח", "שיגור"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "הדר יוסף"]
    
    combined_headlines = []
    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                if title: combined_headlines.append(title)
        except: continue

    for title in combined_headlines[:20]:
        # קופץ רק אם יש מילת התקפה קריטית וזה קשור אלינו או מטח איראני מוכח
        has_attack = any(word in title for word in critical_words)
        is_local = any(loc in title for loc in local_targets)
        is_active_iran = ("איראן" in title and any(w in title for w in ["מטח", "שיגור", "תקיפה"]))
        
        if (has_attack and is_local) or is_active_iran:
            return True, title
            
    return False, ""

def get_risk(dt, emergency_active):
    if emergency_active: return 99.8
    hour = dt.hour
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.utcnow() + timedelta(hours=2) 
    
    if 'alert_start_time' not in st.session_state: st.session_state.alert_start_time = None
    if 'current_msg' not in st.session_state: st.session_state.current_msg = ""

    is_emergency, raw_text = check_multi_source_osint()
    
    if raw_text != st.session_state.current_msg:
        st.session_state.current_msg = raw_text
        st.session_state.alert_start_time = now if raw_text else None

    # מנקה התראות ישנות אחרי 10 דקות
    display_text = raw_text
    if st.session_state.alert_start_time:
        if (now - st.session_state.alert_start_time).total_seconds() / 60 >= 10:
            display_text = ""; is_emergency = False

    current_val = get_risk(now, is_emergency)
    color = "#ff1a1a" if is_emergency else "#00ff00"
    
    # תצוגה
    st.markdown(f"""
        <div style="text-align: center; padding: 15px; border: 1px solid {color}33; border-radius: 10px; background: #000;">
            <p style="color: #444; font-size: 10px; margin: 0; letter-spacing: 2px;">SECTOR: EVER HAYARKON</p>
            <h1 style="color: {color}; font-size: 55px; margin: 0; font-family: monospace;">{current_val:.1f}%</h1>
            <p style="color: #222; font-size: 8px;">🕒 {now.strftime('%H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        st.markdown(f"""<div style="background: #1a0000; color: white; padding: 8px; margin: 10px 0; border-radius: 5px; font-size: 11px; border: 1px solid {color}88; text-align: center;">⚠️ {display_text}</div>""", unsafe_allow_html=True)

    # גרף Matplotlib
    times = [i for i in range(50)]
    values = [get_risk(now + timedelta(minutes=i*20), is_emergency) for i in times]
    fig, ax = plt.subplots(figsize=(6, 1))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.plot(times, values, color=color, linewidth=1.5)
    ax.fill_between(times, values, color=color, alpha=0.05)
    ax.set_ylim(0, 110)
    ax.axis('off')
    st.pyplot(fig, clear_figure=True)

    # החזרת 35 הנורות בדיוק כפי שהיו
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    
    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 5px;">
                    <div style="width: 5px; height: 5px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px {color}77;"></div>
                    <br><span style="font-size:7px; color: #222;">{key}</span>
                </div>
            """, unsafe_allow_html=True)

auto_refresh_hamaal()
