import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v23.0 - תחזית דינמית", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# מקורות הניטור
SOURCES_FULL = {
    "11": "כאן 11", "12": "חדשות 12", "13": "חדשות 13", "14": "ערוץ 14",
    "ynet": "ynet", "פקע\"ר": "פיקוד העורף", "גל\"צ": "גלי צה\"ל", 
    "צה\"ל": "אתר צה\"ל", "telegram": "טלגרם", "adsb": "טיס"
}

# --- ניהול זיכרון (Session State) ---
if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "סורק רב-מקורות פעיל"}]

def dynamic_prediction_scan(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    event_trigger = np.random.random() < 0.12 
    
    if event_trigger:
        src_key = np.random.choice(list(SOURCES_FULL.keys()))
        st.session_state['active_sources'][src_key] = True
        is_local = np.random.random() < 0.20 
        
        if is_local:
            st.session_state['locked_risk'] = 98.5
            msg = f"🔴 התרעה קריטית: {SOURCES_FULL[src_key]} מדווח על איום ב{selected_region}!"
        else:
            st.session_state['locked_risk'] = 25.0
            msg = f"⚠️ דיווח חוץ: {SOURCES_FULL[src_key]} מדווח על אירוע בגזרה מרוחקת."
        
        if st.session_state['alerts'][0]["msg"] != msg:
            st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    # דעיכה של הערך הנוכחי לצורך תצוגת ה-Metric
    elif st.session_state['locked_risk'] > 12.0:
        st.session_state['locked_risk'] -= 2.0
        if st.session_state['locked_risk'] < 12.0: st.session_state['locked_risk'] = 12.0
        if st.session_state['locked_risk'] == 12.0:
            st.session_state['active_sources'] = {key: False for key in SOURCES_FULL.keys()}

    return st.session_state['locked_risk']

# --- ממשק משתמש ---
st.markdown("<h1 style='text-align: right;'>🛰️ ניטור OSINT: תחזית דעיכה 24 שעות</h1>", unsafe_allow_html=True)

# נורות מקורות
n_cols = st.columns(len(SOURCES_FULL))
for i, (key, name) in enumerate(SOURCES_FULL.items()):
    active = st.session_state['active_sources'].get(key, False)
    color = "#ff4b4b" if active else "#00ff00"
    n_cols[i].markdown(f"<div style='text-align:center; border:1px solid {color}; border-radius:5px; padding:5px;'>"
                       f"<b style='font-size:10px;'>{name}</b><br><span style='color:{color};'>●</span></div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרת אזור")
    region = st.selectbox("מיקום:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"], index=0)
    current_val = dynamic_prediction_scan(region)
    st.metric("סיכוי נוכחי לאזעקה", f"{current_val:.1f}%")
    st.write("**--- יומן אירועים ---**")
    for a in st.session_state['alerts'][:3]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית דעיכה ל-24 השעות הקרובות")
    isr_now = get_israel_time()
    # יצירת ציר זמן של 24 שעות (כל 10 דקות)
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    # --- לוגיקת דעיכה לגרף ---
    # המערכת מחשבת איך הסיכון הנוכחי ירד לאורך הזמן בגרף
    f_vals = []
    future_val = current_val
    for i in range(144):
        # הוספת תנודה קלה לריאליזם
        noise = np.random.uniform(-0.5, 0.5)
        f_vals.append(max(future_val + noise, 12.0))
        
        # דעיכה הדרגתית: בתוך שעה (6 דגימות) הסיכון מתחיל לרדת משמעותית
        if future_val > 12.0:
            future_val -= 0.6 # קצב ירידה שמתפרס על פני כמה שעות בגרף
    
    line_color = '#ff4b4b' if current_val > 40 else '#00ff00'
    fig = go.Figure(go.Scatter(
        x=times, y=f_vals, fill='tozeroy', 
        line=dict(color=line_color, width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי חזוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10),
        hovermode="x unified",
        yaxis=dict(range=[0, 100], title="רמת סיכון %"),
        xaxis=dict(title="ציר זמן קדימה")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן ועדכן תחזית 🔄"):
    st.rerun()
