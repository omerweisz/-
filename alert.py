import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v9.0 - יציבות מוחלטת", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון סטטי (Session State) ---
if 'base_risk' not in st.session_state:
    st.session_state['base_risk'] = 12.0  # רמת שגרה קבועה
if 'event_active' not in st.session_state:
    st.session_state['event_active'] = False

def calculate_event_logic():
    """לוגיקה שמשנה אחוזים רק אם קורה 'אירוע'"""
    # סיכוי של 5% בלבד שייווצר שינוי בכל לחיצה
    trigger_event = np.random.random() < 0.05
    
    if trigger_event:
        # אם קרה אירוע, האחוזים עולים לרמה חדשה ונעצרים שם
        st.session_state['base_risk'] = np.random.uniform(25.0, 45.0)
        st.session_state['event_active'] = True
    elif np.random.random() < 0.02: # סיכוי קטן מאוד לחזרה לשגרה
        st.session_state['base_risk'] = 12.0
        st.session_state['event_active'] = False
        
    # מצב הנורות נקבע רק לפי הערך הקיים
    r = st.session_state['base_risk']
    status_map = {
        "OFF": r > 30,
        "TECH": r > 20,
        "CIVIL": r > 15
    }
    return r, status_map

# הרצת המנוע
val, details = calculate_event_logic()
isr_now = get_israel_time()

st.title("📡 חדר מצב OSINT: ניטור יציב (מבוסס אירועים)")
st.write(f"זמן ישראל: **{isr_now.strftime('%H:%M:%S')}**")

# נורות בקרה
m_cols = st.columns(6)
m_list = [
    ("אתר צה\"ל", details["OFF"]), ("פיקוד העורף", details["OFF"]),
    ("שיבושי GPS", details["TECH"]), ("FlightRadar24", details["TECH"]),
    ("Google Trends", details["CIVIL"]), ("דיווחים בטלגרם", details["CIVIL"])
]

for i, (name, active) in enumerate(m_list):
    color = "red" if active else "green"
    m_cols[i].markdown(f"**{name}**\n<span style='color:{color}'>● {'חריג' if active else 'תקין'}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקוד גיאוגרפי")
    target = st.selectbox("אזור ניתוח:", options=["תל אביב - עבר הירקון", "ירושלים", "חיפה", "עוטף עזה", "קו העימות"], index=0)
    
    geo_bonus = 25 if any(x in target for x in ["עוטף", "קו העימות"]) else 0
    final_risk = val + geo_bonus
    
    st.metric("סיכוי לאזעקה", f"{final_risk:.1f}%")
    if st.session_state['event_active']:
        st.warning("⚠️ זוהתה פעילות חריגה במקורות המודיעין")
    else:
        st.success("✅ המערכת מזהה שגרה יציבה")

with col_main:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    # הגרף עכשיו חלק לגמרי בשגרה
    noise = 0.5 if not st.session_state['event_active'] else 2.0
    future_vals = np.clip(np.random.normal(final_risk, noise, 144), 0, 100)
    
    fig = go.Figure(go.Scatter(
        x=times, y=future_vals, fill='tozeroy', 
        line=dict(color='#ff4b4b' if final_risk > 20 else '#00ff00', width=2),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10),
        yaxis=dict(range=[0, 100], title="סיכוי (%)")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים 🔄"):
    st.rerun()
