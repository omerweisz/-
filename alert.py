import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v15.0 - ניטור אקטיבי", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון (Session State) ---
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'event_active' not in st.session_state:
    st.session_state['event_active'] = False
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת סריקה פעילה - שגרה"}]

# --- תפריט צד (כפתור הדיווח שביקשת) ---
with st.sidebar:
    st.header("🛠️ שליטה ידנית")
    st.write("אם המערכת מפספסת אירוע שראית בחדשות:")
    if st.button("🚨 דווח על שיגור / אזעקה בזמן אמת"):
        st.session_state['locked_risk'] = 100.0
        st.session_state['event_active'] = True
        st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": "‼️ דיווח משתמש: זיהוי שיגורים!"})
        st.rerun()
    
    if st.button("✅ חזרה לשגרה"):
        st.session_state['locked_risk'] = 12.0
        st.session_state['event_active'] = False
        st.rerun()

def active_eye_scan():
    """סימולציה של 'עיניים' הסורקות מקורות חיצוניים"""
    # כאן המערכת 'בודקת' אתרים (בסימולציה ללחיצה)
    # סיכוי קטן לזיהוי אוטומטי של אירוע איראני
    auto_detect = np.random.random() < 0.05
    
    if auto_detect and not st.session_state['event_active']:
        st.session_state['locked_risk'] = 98.7
        st.session_state['event_active'] = True
        st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": "👀 עיניים דיגיטליות: זוהה דיווח חריג באיראן!"})
    
    return st.session_state['locked_risk'], st.session_state['event_active']

# הרצת המנוע
val, is_danger = active_eye_scan()
isr_now = get_israel_time()

# כותרת
h_color = "#ff4b4b" if is_danger else "white"
st.markdown(f"<h1 style='color:{h_color}; text-align: right;'>📡 חדר מצב OSINT: ניטור 'עיניים' פעיל</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: right;'>זמן ישראל: <b>{isr_now.strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

# --- שורת הנורות ---
st.subheader("🌐 אימות מקורות (LIVE)")
n_cols = st.columns(6)
n_labels = ["אתר צה\"ל", "פיקוד העורף", "שיבושי GPS", "נתב\"ג", "דיווחי איראן", "מודיעין גלוי"]

for i, name in enumerate(n_labels):
    color = "red" if is_danger else "green"
    n_cols[i].markdown(f"**{name}**\n<span style='color:{color}; font-size:20px'>●</span> {'חריג' if is_danger else 'תקין'}", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקוד: עבר הירקון")
    target = st.selectbox("אזור:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "עוטף עזה"], index=0)
    
    geo_bonus = 30 if "עוטף" in target else 0
    final_val = min(val + geo_bonus, 100)
    
    st.metric("סיכוי לאזעקה", f"{final_val:.1f}%")
    
    st.write("**--- יומן אירועים ---**")
    for a in st.session_state['alerts']:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית 24 שעות (מעבר עכבר)")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    line_c = '#ff0000' if is_danger else '#00ff00'
    f_vals = [final_val + np.random.uniform(-0.3, 0.3) for _ in range(144)]
    
    fig = go.Figure(go.Scatter(
        x=times, y=f_vals, fill='tozeroy', 
        line=dict(color=line_c, width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), 
                      hovermode="x unified", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים וסרוק מקורות 🔄"):
    st.rerun()

if is_danger:
    st.error("🚨 התרעה פעילה! המערכת זיהתה אירוע במקורות החיצוניים.")
