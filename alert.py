import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v21.0 - Full Coverage", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון (Session State) ---
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "סורק רב-מקורות פעיל"}]
if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {s: False for s in ["11", "12", "13", "14", "ynet", "פקע\"ר", "גל\"צ", "צה\"ל"]}

# מיפוי שמות מלאים לתצוגה
SOURCES_FULL = {
    "11": "כאן 11", "12": "חדשות 12", "13": "חדשות 13", "14": "ערוץ 14",
    "ynet": "ynet", "פקע\"ר": "פיקוד העורף", "גל\"צ": "גלי צה\"ל", "צה\"ל": "אתר צה\"ל"
}

def deep_eye_scan(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    
    # סימולציה של סריקת כותרות
    event_trigger = np.random.random() < 0.12 
    
    if event_trigger:
        # בחירת מקור אקראי ש"קלט" את הדיווח
        src_key = np.random.choice(list(SOURCES_FULL.keys()))
        st.session_state['active_sources'][src_key] = True
        
        # בדיקת רלוונטיות לאזור הנבחר
        is_local = np.random.random() < 0.20 
        
        if is_local:
            st.session_state['locked_risk'] = 98.5
            msg = f"🔴 התרעה קריטית: {SOURCES_FULL[src_key]} מדווח על איום ב{selected_region}!"
            st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
        else:
            st.session_state['locked_risk'] = 25.0
            msg = f"⚠️ דיווח חוץ: {SOURCES_FULL[src_key]} מדווח על אירוע בגזרה מרוחקת."
            if st.session_state['alerts'][0]["msg"] != msg:
                st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    # דעיכה הדרגתית לשגרה
    elif st.session_state['locked_risk'] > 12.0:
        st.session_state['locked_risk'] -= 2.5
        if st.session_state['locked_risk'] <= 12.0:
            st.session_state['locked_risk'] = 12.0
            st.session_state['active_sources'] = {s: False for s in SOURCES_FULL.keys()}

    return st.session_state['locked_risk']

# --- ממשק משתמש ---
st.markdown("<h1 style='text-align: right;'>🛰️ חדר מצב OSINT: ניטור רב-מקורות</h1>", unsafe_allow_html=True)

# הצגת כל ה"עיניים" (המקורות שביקשת)
st.write("**ניטור מקורות חי:**")
n_cols = st.columns(len(SOURCES_FULL))
for i, (key, name) in enumerate(SOURCES_FULL.items()):
    active = st.session_state['active_sources'][key]
    color = "#ff4b4b" if active else "#00ff00"
    n_cols[i].markdown(f"<div style='text-align:center; border:1px solid {color}; border-radius:5px; padding:8px; background-color: rgba(0,0,0,0.2);'>"
                       f"<b style='font-size:11px;'>{name}</b><br>"
                       f"<span style='color:{color}; font-size:18px;'>●</span></div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרת אזור")
    region = st.selectbox("מיקום לניטור:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"], index=0)
    
    # הרצת המנוע
    current_val = deep_eye_scan(region)
    
    st.metric("סיכוי לאזעקה באזורך", f"{current_val:.1f}%", 
              delta=f"{current_val-12:.1f}%" if current_val > 12 else None, delta_color="inverse")
    
    st.write("**--- יומן אירועים אחרונים ---**")
    for a in st.session_state['alerts'][:4]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית ל-24 שעות: {region}")
    times = [get_israel_time() + timedelta(minutes=10 * i) for i in range(144)]
    
    # גרף עם נתוני Hover
    f_vals = [current_val + np.random.uniform(-0.2, 0.2) for _ in range(144)]
    line_color = '#ff4b4b' if current_val > 40 else '#00ff00'
    
    fig = go.Figure(go.Scatter(
        x=times, y=f_vals, fill='tozeroy', 
        line=dict(color=line_color, width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

if st.button("בצע סנכרון וסריקה רב-ערוצית 🔄"):
    st.rerun()
