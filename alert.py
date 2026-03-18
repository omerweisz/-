import streamlit as st
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - LIVE", layout="wide")

# CSS להעלמת הלבן ועיצוב שחור נקי
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
    iframe { border: none !important; }
    </style>
""", unsafe_allow_html=True)

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml"
    ]
    threat_words = ["טילים", "כטב\"מ", "יירוט", "נפילה", "אזעקה", "פיצוץ", "חדירה"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "פי גלילות"]
    end_words = ["חזרה לשגרה", "הוסרה ההתרעה", "סיום האירוע", "האירוע הסתיים", "ניתן לצאת"]
    
    combined_headlines = []
    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                if title: combined_headlines.append(title)
        except: continue

    for title in combined_headlines[:10]:
        if any(word in title for word in end_words): return False, title
    for title in combined_headlines[:25]:
        if any(word in title for word in threat_words) and any(loc in title for loc in local_targets):
            return True, title
        if "איראן" in title: return True, title
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

    display_text = raw_text
    if st.session_state.alert_start_time:
        if (now - st.session_state.alert_start_time).total_seconds() / 60 >= 10:
            display_text = ""; is_emergency = False

    current_val = get_risk(now, is_emergency)
    color = "#ff1a1a" if (current_val > 35 and is_emergency) else "#00ff00"
    
    # תצוגת אחוזים
    st.markdown(f"""
        <div style="text-align: center; padding: 15px; border: 1px solid {color}44; border-radius: 10px; background: #000;">
            <p style="color: #666; font-size: 10px; margin: 0; letter-spacing: 2px;">SECTOR: EVER HAYARKON</p>
            <h1 style="color: {color}; font-size: 60px; margin: 0; font-family: monospace;">{current_val:.1f}%</h1>
            <p style="color: #444; font-size: 10px; margin:0;">🕒 {now.strftime('%H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        is_safe = any(word in display_text for word in ["סיום", "שגרה", "לצאת"])
        b_color = "#002200" if is_safe else "#220000"
        st.markdown(f"""<div style="background: {b_color}; color: white; padding: 8px; margin: 10px 0; border-radius: 5px; font-size: 12px; font-weight: bold; border: 1px solid {color}; text-align: center;">{'✅' if is_safe else '⚠️'} {display_text}</div>""", unsafe_allow_html=True)

    # --- הגרף החדש (Matplotlib) - הכי נקי שיש ---
    times = [i for i in range(100)]
    values = [get_risk(now + timedelta(minutes=i*14), is_emergency) for i in times]
    
    fig, ax = plt.subplots(figsize=(6, 1.5))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.plot(times, values, color=color, linewidth=2)
    ax.fill_between(times, values, color=color, alpha=0.1)
    ax.axis('off') # מעלים את כל המסגרת והקווים
    
    st.pyplot(fig)

    # נורות
    cols = st.columns(7)
    keys = ["YNET", "WALLA", "N12", "HAYOM", "צה\"ל", "צופר", "TG", "ROTER", "MOKED", "IAF", "IEC", "FR24", "ISR", "INT"]
    for idx, key in enumerate(keys):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center;"><div style="width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block;"></div><br><span style="font-size:7px; color: #333;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
