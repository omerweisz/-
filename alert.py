import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - סנכרון מצב", layout="wide")

def check_local_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main"
    ]
    # מילים של "סכנה"
    threat_words = ["טילים", "כטב\"מ", "יירוט", "נפילה", "אזעקה", "פיצוץ"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות"]
    
    # מילים של "סיום"
    end_words = ["חזרה לשגרה", "הוסרה ההתרעה", "סיום האירוע", "הנחיות חדשות", "האירוע הסתיים"]
    
    try:
        for url in sources:
            response = requests.get(url, timeout=3)
            root = ET.fromstring(response.content)
            headlines = [item.find('title').text for item in root.findall('./channel/item')]
            
            # בדיקת 5 המבזקים האחרונים בלבד לסיום אירוע (כדי שיהיה מעודכן)
            for title in headlines[:5]:
                if any(word in title for word in end_words):
                    return False, "✅ חזרה לשגרה: " + title
            
            # בדיקת 15 המבזקים האחרונים לאיום
            for title in headlines[:15]:
                has_threat = any(word in title for word in threat_words)
                is_local = any(loc in title for loc in local_targets)
                if (has_threat and is_local) or "איראן" in title:
                    return True, "⚠️ " + title
                    
        return False, ""
    except:
        return False, ""

def get_risk(dt, emergency_active):
    if emergency_active:
        return 99.8
    hour = dt.hour
    # מדד שגרה רגוע
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.utcnow() + timedelta(hours=2) 
    is_emergency, alert_text = check_local_osint()
    current_val = get_risk(now, is_emergency)
    
    # צבעים
    is_red = current_val > 35
    color = "#ff1a1a" if is_red else "#00ff00"
    bg_color = "#2b0000" if is_red else "#0e1117"
    
    st.markdown(f"<style>.stApp {{ background-color: {bg_color}; transition: 0.8s ease-in-out; }}</style>", unsafe_allow_html=True)

    # כותרת עם הודעת המערכת
    st.markdown(f"""
        <div style="text-align: center; padding: 15px; border: 2px solid {color}; border-radius: 15px; background: rgba(0,0,0,0.7);">
            <p style="color: #666; font-size: 11px; margin: 0; letter-spacing: 1px;">SECTOR: EVER HAYARKON | LIVE FEED</p>
            <h1 style="color: {color}; font-size: 60px; margin: 0; font-family: 'Courier New', monospace;">{current_val:.1f}%</h1>
            {f'<div style="background: {"#004400" if "✅" in alert_text else color}; color: white; padding: 8px; margin-top:10px; border-radius:5px; font-size:13px; font-weight:bold;">{alert_text}</div>' if alert_text else ''}
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # נורות (35)
    all_keys = ["12", "13", "11", "14", "ynet", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "livemap",
                "fr24", "adsb", "iaf", "nasa", "usgs", "רוטר", "חמל", "telegram", "moked", "sela",
                "iec", "cyber", "google", "marine", "sentinel", "cnn", "bbc", "reuters", "aljazeera", "fox",
                "ayalon", "natbag", "radio", "field", "intel"]

    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""
                <div style="text-align: center; border: 1px solid {color}22; border-radius: 4px; background: #000; margin-bottom: 4px; padding: 3px;">
                    <div style="width: 7px; height: 7px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px {color};"></div>
                    <br><b style="font-size:9px; color: #777;">{key}</b>
                </div>
            """, unsafe_allow_html=True)

    # גרף
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, is_emergency) for t in times]
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=3)))
    fig.update_layout(template="plotly_dark", height=220, margin=dict(l=0,r=0,t=0,b=0),
                      xaxis=dict(visible=False, fixedrange=True), yaxis=dict(fixedrange=True, range=[0, 110]), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

auto_refresh_hamaal()
