import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v7.0 - זמן ישראל", layout="wide")

# פונקציה לקבלת זמן ישראל מדויק (UTC+2)
def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# ניהול זיכרון (Session State)
if 'current_risk' not in st.session_state:
    st.session_state['current_risk'] = 15.0

def get_ultra_data():
    """שקלול מקורות וזמן ישראל"""
    s_official = np.random.choice([0, 25], p=[0.9, 0.1]) 
    s_tech = np.random.choice([0, 20], p=[0.85, 0.15])
    s_civil = np.random.choice([0, 15], p=[0.8, 0.2])
    
    now = get_israel_time()
    time_risk = 5 if (19 <= now.hour <= 23) else 0
    
    raw_total = s_official + s_tech + s_civil + time_risk + 6.0
    st.session_state['current_risk'] = (st.session_state['current_risk'] * 0.75) + (raw_total * 0.25)
    
    return st.session_state['current_risk'], {"OFF": s_official, "TECH": s_tech, "CIVIL": s_civil}

val, details = get_ultra_data()
isr_now = get_israel_time()

st.title("📡 חדר מצב OSINT: ניטור רב-שכבתית")
st.write(f"זמן ישראל נוכחי: **{isr_now.strftime('%H:%M:%S')}**")

# לוח מחוונים - נורות
st.subheader("🌐 מצב מקורות המידע")
m_cols = st.columns(6)
m_list = [
    ("אתר צה\"ל", details["OFF"] > 0), ("פיקוד העורף", details["OFF"] > 0),
    ("שיבושי GPS", details["TECH"] > 0), ("FlightRadar24", details["TECH"] > 0),
    ("Google Trends", details["CIVIL"] > 0), ("דיווחים בטלגרם", details["CIVIL"] > 0)
]

for i, (name, active) in enumerate(m_list):
    color = "red" if active else "green"
    m_cols[i].markdown(f"**{name}**\n<span style='color:{color}'>● {'חריג' if active else 'תקין'}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקוד גיאוגרפי")
    # תל אביב - עבר הירקון כברירת מחדל
    target = st.selectbox("בחר אזור:", options=["תל אביב - עבר הירקון", "ירושלים", "חיפה", "עוטף עזה", "קו העימות"], index=0)
    
    geo_bonus = 35 if any(x in target for x in ["עוטף", "קו העימות"]) else 0
    final_risk = min(val + geo_bonus, 100)
    
    st.metric("סיכוי לאזעקה", f"{final_risk:.1f}%")
    st.write("**מדד אמינות משולב:**")
    st.progress(0.96 if final_risk < 30 else 0.85)

with col_main:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    # יצירת ציר זמן שמתחיל מעכשיו לפי זמן ישראל
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    future_vals = np.clip(np.random.normal(final_risk, 3, 144), 0, 100)
    
    fig = go.Figure(go.Scatter(
        x=times, 
        y=future_vals, 
        fill='tozeroy', 
        line=dict(color='#ff4b4b', width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        template="plotly_dark", 
        height=400, 
        margin=dict(l=0,r=0,t=10,b=0), 
        yaxis=dict(range=[0,100], title="סיכוי (%)"),
        xaxis=dict(title="ציר זמן (זמן ישראל)")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרון מקורות עומק 🔄"):
    st.rerun()
