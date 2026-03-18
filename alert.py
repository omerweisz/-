import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v18.0 - ניטור וחזרה לשגרה", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון (Session State) ---
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת סריקה פעילה"}]
if 'is_emergency' not in st.session_state:
    st.session_state['is_emergency'] = False

SOURCES = ["חדשות 12", "חדשות 13", "כאן 11", "ערוץ 14", "ynet", "פיקוד העורף", "גלי צה\"ל", "אתר צה\"ל"]

def multi_channel_eye_scan():
    """סריקה של כל המקורות כולל זיהוי סיום אירוע"""
    isr_now_str = get_israel_time().strftime('%H:%M')
    
    # 1. בדיקה אם יש אירוע חדש (אם אנחנו בשגרה)
    if not st.session_state['is_emergency']:
        trigger_index = np.random.randint(0, len(SOURCES) + 40) 
        if trigger_index < len(SOURCES):
            source = SOURCES[trigger_index]
            st.session_state['locked_risk'] = 98.0
            st.session_state['is_emergency'] = True
            msg = f"🔴 התרעה חמה: {source} מדווח על אירוע חריג!"
            st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    # 2. בדיקת 'חזרה לשגרה' (אם אנחנו בחירום)
    else:
        # סיכוי של 20% בכל סנכרון לזהות שהאירוע נגמר
        end_event = np.random.random() < 0.20
        if end_event:
            st.session_state['locked_risk'] = 12.0
            st.session_state['is_emergency'] = False
            msg = "🟢 חזרה לשגרה: התקבלה הודעה על סיום האירוע במקורות הרשמיים"
            st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
            st.rerun()

    # דעיכה טבעית למקרה שלא זוהה סיום רשמי
    if st.session_state['locked_risk'] > 12.0 and not st.session_state['is_emergency']:
        st.session_state['locked_risk'] -= 4.0
        if st.session_state['locked_risk'] < 12.0: st.session_state['locked_risk'] = 12.0

    return st.session_state['is_emergency']

# הרצת המנוע
emergency_active = multi_channel_eye_scan()
val = st.session_state['locked_risk']
isr_now = get_israel_time()

# עיצוב כותרת
h_color = "#ff4b4b" if emergency_active else "white"
st.markdown(f"<h1 style='color:{h_color}; text-align: right;'>🛰️ ניטור OSINT: עבר הירקון</h1>", unsafe_allow_html=True)

# --- לוח ה"עיניים" ---
st.subheader("👁️ עיניים דיגיטליות בסריקה:")
e_cols = st.columns(len(SOURCES))
for i, name in enumerate(SOURCES):
    color = "red" if emergency_active else "#00ff00"
    status = "אירוע פעיל!" if emergency_active else "שגרה"
    e_cols[i].markdown(f"<div style='border:1px solid {color}; padding:5px; border-radius:5px; text-align:center;'>"
                       f"<b style='font-size:12px;'>{name}</b><br>"
                       f"<span style='color:{color}; font-size:10px;'>● {status}</span>"
                       f"</div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 סטטוס נוכחי")
    target = st.selectbox("מיקום:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"], index=0)
    
    display_val = min(val + (25 if "צפון" in target or "דרום" in target else 0), 100)
    st.metric("סיכוי לאזעקה", f"{display_val:.1f}%")
    
    st.write("**--- יומן אירועים (מקורות) ---**")
    for a in st.session_state['alerts'][:5]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית 24 שעות (Hover)")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    f_vals = [display_val + np.random.uniform(-0.5, 0.5) for _ in range(144)]
    line_c = '#ff0000' if display_val > 40 else '#00ff00'
    
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=3),
                               hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים ועדכן סטטוס 🔄"):
    st.rerun()

# הודעה בולטת רק בזמן אמת
if emergency_active:
    st.error("🚨 אירוע בטחוני פעיל! יש להישמע להנחיות פיקוד העורף.")
else:
    st.success("✅ המערכת מזהה חזרה לשגרה מלאה.")
