import streamlit as st
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - V3", layout="wide")

# CSS לעיצוב שחור נקי והעלמת שוליים
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stVerticalBlock"] { gap: 0.3rem; }
    iframe { border: none !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml",
        "https://m.maariv.co.il/Rss/RssFeeds0"
    ]
    # מילים שמעידות על תקיפה נגדנו (לא תקיפה של צה"ל שם)
    attack_words = ["שיגור", "מטח", "ירי", "כטב\"ם", "אזעקה", "חדירה", "נפילה", "יירוט"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "פי גלילות", "הדר יוסף"]
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

    # בדיקת הרגעה
    for title in combined_headlines[:10]:
        if any(word in title for word in end_words): return False, title
    
    # לוגיקה חדשה: קופץ רק אם יש איום עלינו (מילת תקיפה + יעד מקומי/איראן)
    for title in combined_headlines[:30]:
        has_attack = any(word in title for word in attack_words)
        is_local = any(loc in title for loc in local_targets)
        # קופץ רק אם איראן מבצעת ירי/שיגור, לא אם צה"ל תוקף שם
        is_iran_attack = ("איראן" in title and any(w in title for w in ["שיגר", "מטח", "לעבר ישראל", "תקיפה נגד"]))
        
        if (has_attack and is_local) or is_iran_attack:
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

    display_text = raw_text
    if st.session_state.alert_start_time:
        if (now - st.session_state.alert_start_time).total_seconds() / 60 >= 10:
            display_text = ""; is_emergency = False

    current_val = get_risk(now, is_emergency)
    color = "#ff1a1a" if (current_val > 35 and is_emergency) else "#00ff00"
    
    # תצוגה ראשית
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 12px; background: #000; box-shadow: 0 0 15px {color}11;">
            <p style="color: #555; font-size: 10px; margin: 0; letter-spacing: 2.5px; font-weight: bold;">SECTOR: EVER HAYARKON</p>
            <h1 style="color: {color}; font-size: 65px; margin: 5px 0; font-family: monospace; text-shadow: 0 0 10px {color}33;">{current_val:.1f}%</h1>
            <p style="color: #333; font-size: 9px; margin:0; font-family: monospace;">🕒 {now.strftime('%H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        is_safe = any(word in display_text for word in ["סיום", "שגרה", "לצאת"])
        b_color = "#001a00" if is_safe else "#1a0000"
        st.markdown(f"""<div style="background: {b_color}; color: white; padding: 10px; margin: 10px 0; border-radius: 6px; font-size: 12px; font-weight: bold; border: 1px solid {color}66; text-align: center;">{'✅' if is_safe else '⚠️'} {display_text}</div>""", unsafe_allow_html=True)

    # גרף Matplotlib נקי
    times = [i for i in range(100)]
    values = [get_risk(now + timedelta(minutes=i*14), is_emergency) for i in times]
    fig, ax = plt.subplots(figsize=(6, 1.2))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.plot(times, values, color=color, linewidth=2, alpha=0.8)
    ax.fill_between(times, values, color=color, alpha=0.08)
    ax.set_ylim(0, 110)
    ax.axis('off')
    st.pyplot(fig, clear_figure=True)

    # החזרת 35 הנורות
    all_keys = ["12", "13", "11", "14", "YNET", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    
    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 8px;">
                    <div style="width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px {color}aa;"></div>
                    <br><span style="font-size:7px; color: #333; font-weight: bold;">{key}</span>
                </div>
            """, unsafe_allow_html=True)

auto_refresh_hamaal()
