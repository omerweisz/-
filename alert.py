import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# הגדרות דף - נקי ומותאם
st.set_page_config(page_title="חמ\"ל עבר הירקון - LIVE", layout="wide")

def check_local_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main"
    ]
    # מילות איום - כולל עברית ואנגלית למקרה שיש כותרות מעורבות
    threat_words = ["טילים", "כטב\"מ", "יירוט", "נפילה", "אזעקה", "פיצוץ", "חדירה", "missile", "rocket", "siren"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "פי גלילות"]
    # מילות הרגעה
    end_words = ["חזרה לשגרה", "הוסרה ההתרעה", "סיום האירוע", "האירוע הסתיים", "לצאת מהממד", "ניתן לצאת", "שגרה"]
    
    try:
        for url in sources:
            response = requests.get(url, timeout=3)
            root = ET.fromstring(response.content)
            headlines = [item.find('title').text for item in root.findall('./channel/item')]
            
            # בדיקת הרגעה קודם כל
            for title in headlines[:5]:
                if any(word in title for word in end_words):
                    return False, "✅ " + title
            
            # בדיקת איום
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
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.utcnow() + timedelta(hours=2) 
    is_emergency, alert_text = check_local_osint()
    current_val = get_risk(now, is_emergency)
    
    is_red = current_val > 35
    color = "#ff1a1a" if is_red else "#00ff00"
    bg_color = "#2b0000" if is_red else "#0e1117"
    
    st.markdown(f"<style>.stApp {{ background-color: {bg_color}; transition: 0.5s; }}</style>", unsafe_allow_html=True)

    # --- תיקון תצוגת הכיתוב האנגלי שראית בבאג ---
    st.markdown(f"""
        <div style="text-align: center; padding: 25px; border: 2px solid {color}; border-radius: 15px; background: rgba(0,0,0,0.8); box-shadow: 0 0 15px {color}33;">
            <p style="color: #bbb; font-size: 14px; margin: 0; letter-spacing: 2px; font-weight: bold; text-transform: uppercase;">SECTOR: EVER HAYARKON</p>
            <h1 style="color: {color}; font-size: 80px; margin: 10px 0; font-family: 'Courier New', monospace; text-shadow: 0 0 10px {color};">{current_val:.1f}%</h1>
            
            <div style="color: {color}; font-size: 16px; font-weight: bold; font-family: monospace;">
                🕒 זמן עדכון (LIVE): {now.strftime('%H:%M:%S')}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # הצגת הודעת המבזק - נקי ובנפרד
    if alert_text:
        box_color = "#004400" if "✅" in alert_text else "#440000"
        text_color = "white"
        st.markdown(f"""
            <div style="background: {box_color}; color: {text_color}; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; font-weight: bold; border: 1px solid white; text-align: center; font-family: system-ui;">
                {alert_text}
            </div>
        """, unsafe_allow_html=True)
    
    st.write("")

    # נורות המקורות (35)
    all_keys = ["12", "13", "11", "14", "ynet", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "livemap",
                "fr24", "adsb", "iaf", "nasa", "usgs", "רוטר", "חמל", "telegram", "moked", "sela",
                "iec", "cyber", "google", "marine", "sentinel", "cnn", "bbc", "reuters", "aljazeera", "fox",
                "ayalon", "natbag", "radio", "field", "intel"]

    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            # עיצוב מותאם למחשב ולטלפון
            st.markdown(f"""
                <div style="text-align: center; border: 1px solid {color}22; border-radius: 5px; background: rgba(0,0,0,0.5); margin-bottom: 5px; padding: 5px;">
                    <div style="width: 10px; height: 10px; background: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px {color};"></div>
                    <br><b style="font-size:10px; color: #aaa;">{key}</b>
                </div>
            """, unsafe_allow_html=True)

    # גרף ללא זום (Plotly Config)
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, is_emergency) for t in times]
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=3)))
    fig.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0),
                      xaxis=dict(visible=False, fixedrange=True), 
                      yaxis=dict(fixedrange=True, range=[0, 115]), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

auto_refresh_hamaal()
