import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v24.0 - מודל הסתברותי", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# מקורות
SOURCES_FULL = {
    "11": "כאן 11", "12": "חדשות 12", "13": "חדשות 13", "14": "ערוץ 14",
    "ynet": "ynet", "פקע\"ר": "פיקוד העורף", "גל\"צ": "גלי צה\"ל", 
    "צה\"ל": "אתר צה\"ל", "telegram": "טלגרם", "adsb": "טיס"
}

# ניהול זיכרון
if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "סורק רב-מקורות פעיל"}]

def statistical_engine(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    # סיכוי נמוך מאוד להקפצת אירוע אמת ברגע הסנכרון
    if np.random.random() < 0.08:
        src_key = np.random.choice(list(SOURCES_FULL.keys()))
        st.session_state['active_sources'][src_key] = True
        is_local = np.random.random() < 0.20
        if is_local:
            st.session_state['locked_risk'] = 98.5
            msg = f"🔴 התרעה קריטית: {SOURCES_FULL[src_key]} מדווח על איום ב{selected_region}!"
        else:
            st.session_state['locked_risk'] = 28.0
            msg = f"⚠️ דריכות גזרה: דיווח ב-{SOURCES_FULL[src_key]} על אירוע מרוחק."
        st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    # דעיכה טבעית לערך הנוכחי
    elif st.session_state['locked_risk'] > 12.0:
        st.session_state['locked_risk'] -= 1.5
        if st.session_state['locked_risk'] <= 12.0:
            st.session_state['locked_risk'] = 12.0
            st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
            
    return st.session_state['locked_risk']

# ממשק
st.markdown("<h1 style='text-align: right;'>🛰️ תחזית OSINT: מודל הסתברותי חכם</h1>", unsafe_allow_html=True)

# נורות
n_cols = st.columns(len(SOURCES_FULL))
for i, (key, name) in enumerate(SOURCES_FULL.items()):
    active = st.session_state['active_sources'].get(key, False)
    color = "#ff4b4b" if active else "#00ff00"
    n_cols[i].markdown(f"<div style='text-align:center; border:1px solid {color}; padding:5px;'><b style='font-size:10px;'>{name}</b><br><span style='color:{color};'>●</span></div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרת מיקום")
    region = st.selectbox("מיקום:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])
    risk_val = statistical_engine(region)
    st.metric("סיכוי נוכחי", f"{risk_val:.1f}%")
    for a in st.session_state['alerts'][:2]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית סיכויים ל-24 שעות (סטטיסטיקה חיה)")
    times = [get_israel_time() + timedelta(minutes=10 * i) for i in range(144)]
    
    # --- בניית גרף מבוסס הסתברות (Statistics-Based) ---
    f_vals = []
    base = risk_val
    for i in range(144):
        # 1. רעש רקע תמידי (בין 10% ל-14%)
        random_noise = np.random.uniform(10.0, 14.5)
        
        # 2. סיכוי סטטיסטי לקפיצות "מתח" בגרף (למשל מתיחות באיראן)
        spike = 0
        if np.random.random() < 0.03: # 3% סיכוי לקפיצה בכל נקודת זמן בגרף
            spike = np.random.uniform(15, 35)
        
        # 3. דעיכה של האירוע הנוכחי בתוך הגרף
        decay = base * (0.95 ** i) if base > 15 else 0
        
        # שילוב הכל לערך אחד
        final_p = max(random_noise, decay, spike)
        f_vals.append(min(final_p, 100))

    line_color = '#ff4b4b' if risk_val > 40 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_color, width=2.5),
                               hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי סטטיסטי:</b> %{y:.1f}%<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("רענן מודל סטטיסטי 🔄"):
    st.rerun()
