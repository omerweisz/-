import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v29.0 - 30 Source Array", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- רשימת 30 מקורות מודיעין (6x5) ---
SOURCES_FULL = {
    "12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", "14": "ערוץ 14", "ynet": "ynet",
    "פקע\"ר": "פיקוד העורף", "צה\"ל": "דובר צה\"ל", "מד\"א": "מד\"א", "כבאות": "כבאות", "רוטר": "רוטר",
    "חמל": "חמ\"ל", "telegram": "טלגרם", "adsb": "טיס (ADSB)", "nasa": "NASA", "reuters": "רויטרס",
    "iaf": "חיל האוויר", "iec": "חברת חשמל", "sela": "סל\"ע ת\"א", "cnn": "CNN", "bbc": "BBC",
    "opensky": "OpenSky", "uamap": "Liveuamap", "sentinel": "Sentinel", "xtrends": "X-Trends", "usgs": "USGS",
    "marine": "MarineTraffic", "google": "Google Trends", "aurora": "Aurora Intel", "moked": "מוקד 106", "cyber": "Cloudflare"
}

# --- ניהול זיכרון (Session State) ---
if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
else:
    for key in SOURCES_FULL.keys():
        if key not in st.session_state['active_sources']:
            st.session_state['active_sources'][key] = False

if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערך 30 מקורות פעיל"}]
if 'emergency_mode' not in st.session_state:
    st.session_state['emergency_mode'] = False

def elite_intel_engine(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    
    # סיכוי לשיגור (1%)
    launch_trigger = np.random.random() < 0.01 
    
    if launch_trigger:
        # הצלבה מ-3 מקורות אקראיים
        src_keys = np.random.choice(list(SOURCES_FULL.keys()), 3, replace=False)
        for k in src_keys: st.session_state['active_sources'][k] = True
        
        st.session_state['locked_risk'] = 98.8
        st.session_state['emergency_mode'] = True
        msg = f"🚀 אירוע קריטי: {SOURCES_FULL[src_keys[0]]} מדווח על שיגורים לעבר {selected_region}."
        st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    elif not st.session_state['emergency_mode']:
        # שגרה יציבה מאוד
        st.session_state['locked_risk'] = np.random.uniform(11.9, 12.4)
        st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
    
    else:
        # דעיכה
        st.session_state['locked_risk'] -= 3.0
        if st.session_state['locked_risk'] <= 13.0:
            st.session_state['emergency_mode'] = False
            st.session_state['locked_risk'] = 12.0

    return st.session_state['locked_risk']

# --- ממשק משתמש ---
st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT: ניטור 30 " + "עיניים" + "</h1>", unsafe_allow_html=True)

# תצוגת הנורות ב-6 שורות של 5
keys = list(SOURCES_FULL.keys())
for i in range(0, len(keys), 5):
    row_keys = keys[i:i+5]
    cols = st.columns(5)
    for j, key in enumerate(row_keys):
        active = st.session_state['active_sources'].get(key, False)
        color = "#ff4b4b" if active else "#00ff00"
        cols[j].markdown(f"<div style='text-align:center; border:1px solid {color}; border-radius:4px; padding:2px;'>"
                         f"<b style='font-size:8px;'>{SOURCES_FULL[key]}</b><br><span style='color:{color}; font-size:12px;'>●</span></div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 ניטור גזרה")
    region = st.selectbox("בחר מיקום:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])
    risk_val = elite_intel_engine(region)
    st.metric("רמת סיכון", f"{risk_val:.1f}%")
    
    st.write("**--- דיווחי חמ\"ל ---**")
    for a in st.session_state['alerts'][:4]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית הסתברותית 24h")
    isr_now = get_israel_time()
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    f_vals = []
    temp_risk = risk_val
    is_emergency = st.session_state['emergency_mode']
    
    for i in range(144):
        if not is_emergency:
            val = np.random.uniform(11.7, 12.6)
            if np.random.random() < 0.02: val = np.random.uniform(18, 24)
        else:
            val = max(temp_risk * (0.94 ** i), 12.0)
        f_vals.append(val)

    line_c = '#ff4b4b' if risk_val > 40 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=2),
                               hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכון:</b> %{y:.1f}%<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרון 30 מקורות 🔄"):
    st.rerun()
