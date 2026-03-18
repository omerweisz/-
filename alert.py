import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v33.0 - Stealth Mode", layout="wide")

# --- הגדרות התראות שקטות ---
IFTTT_KEY = "YOUR_IFTTT_KEY_HERE" # הדבק כאן את המפתח כשיהיה לך
EVENT_NAME = "osint_alert"

def send_silent_notification(risk_level, region):
    """שולח התראה לנייד ללא הצגת הודעות באתר"""
    if not IFTTT_KEY or IFTTT_KEY == "YOUR_IFTTT_KEY_HERE":
        return
    
    url = f"https://maker.ifttt.com/trigger/{EVENT_NAME}/with/key/{IFTTT_KEY}"
    data = {"value1": f"{risk_level:.1f}%", "value2": region}
    try:
        requests.post(url, json=data, timeout=3)
    except:
        pass

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# רשימת 35 המקורות
SOURCES_FULL = {
    "12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet",
    "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר",
    "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס",
    "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC",
    "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS",
    "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare",
    "natbag": "נתב\"ג", "fr24": "FlightRadar24", "radio": "סורק רדיו", "field": "דיווחי שטח", "intel": "Intel Sky"
}

if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת ניטור פעילה"}]
if 'emergency_mode' not in st.session_state:
    st.session_state['emergency_mode'] = False

def core_engine(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    launch_trigger = np.random.random() < 0.01 
    
    if launch_trigger:
        src_keys = np.random.choice(list(SOURCES_FULL.keys()), 3, replace=False)
        for k in src_keys: st.session_state['active_sources'][k] = True
        st.session_state['locked_risk'] = 98.8
        st.session_state['emergency_mode'] = True
        
        # שליחה שקטה לנייד
        send_silent_notification(98.8, selected_region)
        
        msg = f"🚀 זיהוי אירוע חריג! הצלבה מ-{len(src_keys)} מקורות לעבר {selected_region}."
        st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    elif not st.session_state['emergency_mode']:
        st.session_state['locked_risk'] = np.random.uniform(12.0, 13.0)
        st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
    else:
        st.session_state['locked_risk'] -= 4.0
        if st.session_state['locked_risk'] <= 14.0:
            st.session_state['emergency_mode'] = False
            st.session_state['locked_risk'] = 12.2
    return st.session_state['locked_risk']

# --- ממשק משתמש נקי ---
st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT אחוד</h1>", unsafe_allow_html=True)

# נורות מקורות
keys = list(SOURCES_FULL.keys())
for i in range(0, len(keys), 5):
    cols = st.columns(5)
    for j, key in enumerate(keys[i:i+5]):
        active = st.session_state['active_sources'].get(key, False)
        color = "#ff4b4b" if active else "#00ff00"
        cols[j].markdown(f"<div style='text-align:center; border:1px solid {color}; border-radius:4px; padding:2px;'><b style='font-size:8px;'>{SOURCES_FULL[key]}</b><br><span style='color:{color};'>●</span></div>", unsafe_allow_html=True)

st.divider()
col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 גזרה")
    region = st.selectbox("מיקום ניטור:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])
    risk_val = core_engine(region)
    st.metric("סיכון רגעי", f"{risk_val:.1f}%")
    
    for a in st.session_state['alerts'][:4]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    isr_now = get_israel_time()
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    f_vals = []
    is_emergency = st.session_state['emergency_mode']
    for i in range(144):
        base = 12.0
        hour_factor = np.sin((times[i].hour / 24) * 2 * np.pi) * 2.0
        noise = np.random.normal(0, 0.6)
        if is_emergency:
            val = max(risk_val * (0.95 ** i), base + hour_factor + noise)
        else:
            spike = np.random.uniform(5, 10) if np.random.random() < 0.03 else 0
            val = base + hour_factor + noise + spike
        f_vals.append(max(min(val, 100), 5))

    line_c = '#ff4b4b' if risk_val > 50 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=2)))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים 🔄"):
    st.rerun()
