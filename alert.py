import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v16.0 - ניטור דינמי", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון (Session State) ---
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'event_active' not in st.session_state:
    st.session_state['event_active'] = False
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת סריקה פעילה"}]

# --- לוגיקת דעיכה (Decay Logic) ---
# בכל פעם שהדף נטען, אם אנחנו מעל השגרה, אנחנו מורידים קצת את האחוזים
if st.session_state['locked_risk'] > 12.5:
    # דעיכה של 2% בכל רענון/סנכרון עד שחוזרים ל-12%
    st.session_state['locked_risk'] -= 2.0
    if st.session_state['locked_risk'] < 15:
        st.session_state['event_active'] = False

# --- תפריט צד (דיווח ידני) ---
with st.sidebar:
    st.header("🛠️ שליטה ידנית")
    if st.button("🚨 דווח על שיגור (הקפצה ל-100%)"):
        st.session_state['locked_risk'] = 100.0
        st.session_state['event_active'] = True
        st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": "‼️ דיווח משתמש: זיהוי שיגורים!"})
        st.rerun()
    
    if st.button("✅ איפוס לשגרה"):
        st.session_state['locked_risk'] = 12.0
        st.session_state['event_active'] = False
        st.rerun()

def active_eye_scan():
    """סריקה אוטומטית - מקפיצה רק אם מזוהה אירוע חדש"""
    auto_detect = np.random.random() < 0.04
    if auto_detect and not st.session_state['event_active']:
        st.session_state['locked_risk'] = 98.0
        st.session_state['event_active'] = True
        st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": "👀 עיניים דיגיטליות: זוהה אירוע חריג!"})
    
    return st.session_state['locked_risk'], st.session_state['event_active']

# הרצת המנוע
val, is_danger = active_eye_scan()
isr_now = get_israel_time()

# כותרת
h_color = "#ff4b4b" if val > 30 else "white"
st.markdown(f"<h1 style='color:{h_color}; text-align: right;'>📡 חדר מצב OSINT: עבר הירקון</h1>", unsafe_allow_html=True)

# --- נורות סטטוס ---
st.subheader("🌐 אימות מקורות")
n_cols = st.columns(6)
n_labels = ["אתר צה\"ל", "פיקוד העורף", "שיבושי GPS", "נתב\"ג", "דיווחי איראן", "מודיעין גלוי"]
for i, name in enumerate(n_labels):
    color = "red" if val > 40 else "green"
    n_cols[i].markdown(f"**{name}**\n<span style='color:{color}; font-size:20px'>●</span> {'חריג' if val > 40 else 'תקין'}", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 סטטוס נוכחי")
    target = st.selectbox("אזור:", ["תל אביב - עבר הירקון", "מרכז", "צפון", "דרום"], index=0)
    
    # תצוגת מטריקה עם חץ דעיכה
    delta_val = "-2.0%" if val > 12.5 else "0%"
    st.metric("סיכוי לאזעקה", f"{val:.1f}%", delta=delta_val, delta_color="inverse")
    
    st.write("**--- יומן אירועים ---**")
    for a in st.session_state['alerts'][:4]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית 24 שעות (Hover פעיל)")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    # יצירת עקומת דעיכה לגרף (שייראה שהסיכון יורד לאורך היום)
    f_vals = []
    temp_val = val
    for _ in range(144):
        f_vals.append(temp_val + np.random.uniform(-0.5, 0.5))
        if temp_val > 12.0: temp_val -= 0.3 # דעיכה ויזואלית בגרף
        
    line_c = '#ff0000' if val > 30 else '#00ff00'
    fig = go.Figure(go.Scatter(
        x=times, y=f_vals, fill='tozeroy', 
        line=dict(color=line_c, width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), 
                      hovermode="x unified", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים 🔄"):
    st.rerun()
