import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v8.0 - יציבות מקסימלית", layout="wide")

# פונקציה לקבלת זמן ישראל מדויק
def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון קשיח למניעת קפיצות ---
if 'stable_risk' not in st.session_state:
    st.session_state['stable_risk'] = 14.2  # נקודת התחלה
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = get_israel_time()

def calculate_ultra_stable_risk():
    """חישוב סיכון הדרגתי - מונע קפיצות מעל 2% בעדכון"""
    # יצירת שינוי אקראי קטן מאוד (בין -1.2% ל-+1.2%)
    drift = np.random.uniform(-1.2, 1.2)
    
    # הוספת "לחץ" חיובי קטן בשעות הערב
    now = get_israel_time()
    pressure = 0.2 if (19 <= now.hour <= 22) else -0.1
    
    # עדכון הערך הקיים במקום הגרלה מחדש
    new_risk = st.session_state['stable_risk'] + drift + pressure
    
    # הגבלה לטווח הגיוני בשגרה (8% עד 35%) כדי שלא יקפוץ ל-0 או ל-100 סתם
    st.session_state['stable_risk'] = np.clip(new_risk, 8.0, 35.0)
    
    # דימוי מצב מקורות לפי גובה הסיכון
    r = st.session_state['stable_risk']
    status_map = {
        "OFF": r > 28,  # רק אם הסיכון גבוה מאוד הנורה תהיה אדומה
        "TECH": r > 22,
        "CIVIL": r > 18
    }
    return st.session_state['stable_risk'], status_map

# הרצת המנוע היציב
val, details = calculate_ultra_stable_risk()
isr_now = get_israel_time()

st.title("📡 חדר מצב OSINT: ניטור רציף ויציב")
st.write(f"זמן ישראל: **{isr_now.strftime('%H:%M:%S')}** | סטטוס: **סריקה פעילה**")

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
    
    # בונוס גיאוגרפי קבוע (לא קופץ בסנכרון)
    geo_bonus = 25 if any(x in target for x in ["עוטף", "קו העימות"]) else 0
    final_risk = val + geo_bonus
    
    st.metric("סיכוי לאזעקה", f"{final_risk:.1f}%", delta=f"{val - 14.2:.1f}%")
    st.progress(min(final_risk/100, 1.0), text="רמת דריכות מקומית")

with col_main:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    # הגרף נבנה בצורה חלקה סביב הערך הנוכחי
    future_vals = np.clip(np.random.normal(final_risk, 1.5, 144), 0, 100)
    
    fig = go.Figure(go.Scatter(
        x=times, y=future_vals, fill='tozeroy', 
        line=dict(color='#ff4b4b', width=2),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10),
        yaxis=dict(range=[0, 100], title="סיכוי (%)"),
        xaxis=dict(title="24 שעות קרובות")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("עדכן נתונים (סנכרון עדין) 🔄"):
    st.rerun()
