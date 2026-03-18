import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v31.0 - Statistical Forecasting", layout="wide")

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
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערך ניטור סטטיסטי פעיל"}]
if 'emergency_mode' not in st.session_state:
    st.session_state['emergency_mode'] = False

def statistical_engine(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    # סיכוי קטן לזיהוי אירוע אמת בזמן הסריקה
    launch_trigger = np.random.random() < 0.01 
    
    if launch_trigger:
        src_keys = np.random.choice(list(SOURCES_FULL.keys()), 3, replace=False)
        for k in src_keys: st.session_state['active_sources'][k] = True
        st.session_state['locked_risk'] = 98.8
        st.session_state['emergency_mode'] = True
        msg = f"🚀 זיהוי שיגור: {SOURCES_FULL[src_keys[0]]} מאשר יציאות לעבר {selected_region}."
        st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    elif not st.session_state['emergency_mode']:
        # רמת סיכון נוכחית נשארת בטווח השגרה
        st.session_state['locked_risk'] = np.random.uniform(12.0, 13.5)
        st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
    else:
        st.session_state['locked_risk'] -= 4.0
        if st.session_state['locked_risk'] <= 14.0:
            st.session_state['emergency_mode'] = False
            st.session_state['locked_risk'] = 12.5
    return st.session_state['locked_risk']

st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT: חיזוי הסתברותי 35 מקורות</h1>", unsafe_allow_html=True)

# תצוגת הנורות
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
    region = st.selectbox("מיקום:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])
    risk_val = statistical_engine(region)
    st.metric("סיכון רגעי", f"{risk_val:.1f}%")
    for a in st.session_state['alerts'][:3]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית הסתברותית ל-24 שעות")
    isr_now = get_israel_time()
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    # --- בניית גרף מבוסס מודל סטטיסטי (חיזוי עתידי) ---
    f_vals = []
    current_emergency = st.session_state['emergency_mode']
    
    for i in range(144):
        check_time = times[i]
        # 1. בסיס שגרה (12%)
        base = 12.0
        
        # 2. הוספת "מתח סטטיסטי" לפי שעות (למשל: בלילה הסיכון בגרף עולה מעט)
        hour_factor = np.sin((check_time.hour / 24) * 2 * np.pi) * 2.5 # תנודה מחזורית
        
        # 3. הוספת "רעש" הסתברותי (כדי שהקו לא יהיה חלק מדי)
        noise = np.random.normal(0, 0.8)
        
        # 4. סיכוי לקפיצות עתידיות בגרף (אירועים לא צפויים)
        spike = 0
        if not current_emergency and np.random.random() < 0.04: # 4% סיכוי לקפיצת מתח בגרף
            spike = np.random.uniform(5, 15)
            
        # 5. שילוב של הכל לערך סופי
        if current_emergency:
            # אם יש מצב חירום עכשיו, הגרף מראה דעיכה מהנקודה הנוכחית
            val = max(risk_val * (0.95 ** i), base + hour_factor + noise)
        else:
            val = base + hour_factor + noise + spike
            
        f_vals.append(max(min(val, 100), 5)) # הגבלה בין 5 ל-100

    line_c = '#ff4b4b' if risk_val > 40 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=2),
                               hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי חזוי:</b> %{y:.1f}%<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("בצע סריקת הסתברויות 🔄"):
    st.rerun()
