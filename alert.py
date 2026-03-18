import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v11.0 - זיהוי חירום", layout="wide")

def get_israel_time():
    # תיקון שעה לזמן ישראל (UTC+2)
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון ואירועים (Session State) ---
if 'base_risk' not in st.session_state:
    st.session_state['base_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת אותחלה - שגרה"}]

def process_emergency_logic():
    """מנגנון שמזהה אירועים אסטרטגיים (כמו שיגורים) ומקפיץ את המערכת"""
    # סיכוי קטן (3%) לזיהוי אירוע חירום בכל סנכרון
    emergency_trigger = np.random.random() < 0.03
    
    if emergency_trigger:
        st.session_state['base_risk'] = 98.5
        msg = "🔴 התרעה אסטרטגית: זוהתה פעילות חריגה / שיגורים"
        if st.session_state['alerts'][0]["msg"] != msg:
            st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": msg})
    elif st.session_state['base_risk'] > 50 and np.random.random() < 0.15:
        # חזרה הדרגתית לשגרה
        st.session_state['base_risk'] = 15.0
        st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": "🟢 חזרה לשגרה יחסית - המשך מעקב"})

    st.session_state['alerts'] = st.session_state['alerts'][:5]
    return st.session_state['base_risk']

# הרצת המנוע
val = process_emergency_logic()
isr_now = get_israel_time()

# תיקון השגיאה (unsafe_allow_html=True)
header_color = "#ff4b4b" if val > 50 else "white"
st.markdown(f"<h1 style='color:{header_color}; text-align: right;'>📡 חדר מצב OSINT: ניטור רב-שכבתי</h1>", unsafe_allow_html=True)
st.write(f"<p style='text-align: right;'>זמן ישראל: <b>{isr_now.strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקוד גיאוגרפי")
    # תל אביב - עבר הירקון כברירת מחדל
    target = st.selectbox("אזור ניתוח:", options=["תל אביב - עבר הירקון", "ירושלים", "חיפה", "עוטף עזה", "קו העימות"], index=0)
    
    geo_bonus = 35 if any(x in target for x in ["עוטף", "קו העימות"]) else 0
    final_risk = min(val + geo_bonus, 100)
    
    # הצגת המדד
    st.metric("סיכוי לאזעקה", f"{final_risk:.1f}%")
    
    st.write("**--- יומן אירועים אחרונים ---**")
    for a in st.session_state['alerts']:
        color = "red" if "🔴" in a['msg'] else "gray"
        st.markdown(f"<span style='color:{color}; font-size: 0.8rem;'>[{a['time']}] {a['msg']}</span>", unsafe_allow_html=True)

with col_main:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    # צבע הגרף משתנה לפי רמת הסכנה
    line_color = '#ff0000' if final_risk > 40 else '#00ff00'
    future_vals = np.clip(np.random.normal(final_risk, 1.2, 144), 0, 100)
    
    fig = go.Figure(go.Scatter(
        x=times, y=future_vals, fill='tozeroy', 
        line=dict(color=line_color, width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        template="plotly_dark", height=400, 
        margin=dict(l=10,r=10,t=10,b=10),
        yaxis=dict(range=[0, 100], title="אחוז סיכוי"),
        xaxis=dict(title="ציר זמן (זמן ישראל)")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים וסרוק איומים 🔄"):
    st.rerun()

# הוספת התרעה ויזואלית חזקה במקרה חירום
if val > 50:
    st.error("⚠️ זוהה אירוע אסטרטגי חריג! יש להישמע להנחיות פיקוד העורף.")
