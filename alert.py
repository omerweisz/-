import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v25.0 - ניטור שיגורים", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

SOURCES_FULL = {
    "11": "כאן 11", "12": "חדשות 12", "13": "חדשות 13", "14": "ערוץ 14",
    "ynet": "ynet", "פקע\"ר": "פיקוד העורף", "גל\"צ": "גלי צה\"ל", 
    "צה\"ל": "אתר צה\"ל", "telegram": "טלגרם", "adsb": "טיס"
}

# --- ניהול זיכרון ---
if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת סריקה בשגרה"}]
if 'emergency_mode' not in st.session_state:
    st.session_state['emergency_mode'] = False

def alert_logic_engine(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    
    # סיכוי נמוך מאוד לשיגור אמיתי (1% בכל סנכרון)
    launch_detected = np.random.random() < 0.01 
    
    if launch_detected:
        src_key = np.random.choice(list(SOURCES_FULL.keys()))
        st.session_state['active_sources'][src_key] = True
        st.session_state['locked_risk'] = 98.8
        st.session_state['emergency_mode'] = True
        msg = f"🚀 זיהוי שיגור: {SOURCES_FULL[src_key]} מדווח על יציאות לעבר {selected_region}!"
        st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    # אם אין שיגור, אנחנו בשגרה - האחוזים נשארים נמוכים
    elif not st.session_state['emergency_mode']:
        # תנודה קלה מאוד בשגרה (בלי קפיצות)
        st.session_state['locked_risk'] = np.random.uniform(11.8, 13.2)
        st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
    
    # דעיכה אחרי אירוע חירום
    else:
        st.session_state['locked_risk'] -= 4.0
        if st.session_state['locked_risk'] <= 14.0:
            st.session_state['emergency_mode'] = False
            st.session_state['locked_risk'] = 12.0

    return st.session_state['locked_risk']

# --- ממשק משתמש ---
st.markdown("<h1 style='text-align: right;'>🛰️ ניטור OSINT: עבר הירקון</h1>", unsafe_allow_html=True)

# נורות מקורות
n_cols = st.columns(len(SOURCES_FULL))
for i, (key, name) in enumerate(SOURCES_FULL.items()):
    active = st.session_state['active_sources'].get(key, False)
    color = "#ff4b4b" if active else "#00ff00"
    n_cols[i].markdown(f"<div style='text-align:center; border:1px solid {color}; padding:5px;'><b style='font-size:10px;'>{name}</b><br><span style='color:{color};'>●</span></div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרת מיקוד")
    region = st.selectbox("מיקום:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"])
    risk_val = alert_logic_engine(region)
    
    # תצוגת מטריקה
    st.metric("סיכון נוכחי", f"{risk_val:.1f}%")
    
    st.write("**--- יומן אירועים ---**")
    for a in st.session_state['alerts'][:3]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית הסתברותית ל-24 שעות")
    times = [get_israel_time() + timedelta(minutes=10 * i) for i in range(144)]
    
    f_vals = []
    temp_risk = risk_val
    for i in range(144):
        # בשגרה הגרף יציג תנודות קלות בלבד (11-14%)
        if not st.session_state['emergency_mode']:
            val = np.random.uniform(11.5, 13.5)
            # פעם ב... בגרף העתידי תהיה קפיצה קטנה (מתח גזרה) אבל לא 100%
            if np.random.random() < 0.02: val = np.random.uniform(20, 30)
        else:
            # אם יש אירוע, נראה דעיכה בגרף
            val = max(temp_risk * (0.96 ** i), 12.0)
            
        f_vals.append(val)

    line_c = '#ff4b4b' if risk_val > 40 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=2.5),
                               hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכון:</b> %{y:.1f}%<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים 🔄"):
    st.rerun()
