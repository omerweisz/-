import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="מערכת OSINT v10.0 - תגובה מהירה", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון ואירועים ---
if 'base_risk' not in st.session_state:
    st.session_state['base_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת אותחלה - שגרה"}]

def process_strategic_event():
    """בודק אם יש אירוע קיצוני ומעדכן את המערכת"""
    # סימולציה של זיהוי אירוע אסטרטגי (כמו שיגור מאיראן)
    # במציאות כאן יתחבר API של חדשות/פיקוד העורף
    strategic_trigger = np.random.random() < 0.03 # סיכוי קטן לזיהוי אירוע
    
    if strategic_trigger:
        st.session_state['base_risk'] = 98.0
        new_alert = {"time": get_israel_time().strftime('%H:%M'), "msg": "🔴 התרעה אסטרטגית: זיהוי שיגורים/פעילות חריגה"}
        if new_alert not in st.session_state['alerts']:
            st.session_state['alerts'].insert(0, new_alert)
    elif st.session_state['base_risk'] > 50 and np.random.random() < 0.1:
        # חזרה הדרגתית משגרת חירום
        st.session_state['base_risk'] = 15.0
        st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": "🟢 חזרה לשגרה יחסית - המשך מעקב"})

    # הגבלת יומן ל-5 הודעות
    st.session_state['alerts'] = st.session_state['alerts'][:5]
    return st.session_state['base_risk']

# הרצת המנוע
val = process_strategic_event()
isr_now = get_israel_time()

# עיצוב כותרת לפי מצב סיכון
header_color = "red" if val > 50 else "white"
st.markdown(f"<h1 style='color:{header_color};'>📡 חדר מצב OSINT: ניטור רב-שכבתי</h1>", unsafe_allow_allow_html=True)
st.write(f"זמן ישראל: **{isr_now.strftime('%H:%M:%S')}**")

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקוד גיאוגרפי")
    target = st.selectbox("אזור ניתוח:", options=["תל אביב - עבר הירקון", "ירושלים", "חיפה", "עוטף עזה", "קו העימות"], index=0)
    
    geo_bonus = 35 if any(x in target for x in ["עוטף", "קו העימות"]) else 0
    final_risk = min(val + geo_bonus, 100)
    
    st.metric("סיכוי לאזעקה", f"{final_risk:.1f}%")
    
    # הצגת יומן אירועים
    st.write("**--- יומן אירועים אחרונים ---**")
    for a in st.session_state['alerts']:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    # יצירת גרף
    color = '#ff0000' if final_risk > 40 else '#00ff00'
    future_vals = np.clip(np.random.normal(final_risk, 1.5, 144), 0, 100)
    
    fig = go.Figure(go.Scatter(
        x=times, y=future_vals, fill='tozeroy', 
        line=dict(color=color, width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים וסרוק איומים 🔄"):
    st.rerun()
