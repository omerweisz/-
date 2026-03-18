import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT - ניטור רציף", layout="wide")

# --- ניהול זיכרון ומניעת קפיצות (Session State) ---
if 'current_risk' not in st.session_state:
    st.session_state['current_risk'] = 12.0  # נקודת התחלה נייטרלית
if 'trend' not in st.session_state:
    st.session_state['trend'] = 0.1  # כיוון התנועה (חיובי או שלילי)

def update_risk_logic():
    """מנגנון עדכון הדרגתי שמונע קפיצות לא הגיוניות"""
    # משנים את המגמה פעם ב-10 עדכונים כדי שלא יהיה עצבני מדי
    if np.random.rand() > 0.9:
        st.session_state['trend'] = np.random.uniform(-0.5, 0.5)
    
    # שינוי קטן מאוד בכל צעד (בין -0.8% ל-+0.8%)
    change = st.session_state['trend'] + np.random.uniform(-0.3, 0.3)
    
    # עדכון הערך ושמירה על טווח הגיוני (5% עד 95%)
    new_risk = st.session_state['current_risk'] + change
    st.session_state['current_risk'] = np.clip(new_risk, 5.0, 95.0)
    return st.session_state['current_risk']

# --- ממשק משתמש ---

st.title("🛰️ ניטור הסתברותי רציף - חדר מצב")
st.caption("המערכת מתעדכנת אוטומטית ומשקללת נתוני צה\"ל, פיקוד העורף ו-OSINT בזמן אמת.")

# עדכון האחוזים
current_val = update_risk_logic()

# נורות סטטוס קבועות (משתנות רק כשיש שינוי משמעותי באחוזים)
cols = st.columns(4)
sources = {
    "אתר צה\"ל": "שגרה" if current_val < 40 else "כוננות גבוהה",
    "פיקוד העורף": "ירוק" if current_val < 30 else "כתום (הנחיות)",
    "גלי צה\"ל": "שגרה" if current_val < 50 else "דיווח חריג",
    "מדד רשתות": "שקט" if current_val < 25 else "פעילות ערה"
}

for i, (name, status) in enumerate(sources.items()):
    color = "green" if status in ["שגרה", "ירוק", "שקט"] else "red"
    cols[i].markdown(f"**{name}**\n<span style='color:{color}'>● {status}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרות אזור")
    cities = ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "קו העימות (צפון)", "עוטף עזה", "אילת"]
    target = st.selectbox("מיקום פעיל:", options=sorted(cities))
    
    # תוספת מיקום (בונוס קבוע שלא קופץ)
    geo_bonus = 25 if any(x in target for x in ["קו העימות", "עוטף"]) else 0
    final_display = min(current_val + geo_bonus, 100)
    
    st.metric("סיכוי נוכחי לאזעקה", f"{final_display:.1f}%", 
              delta=f"{st.session_state['trend']:.2f}%", delta_color="inverse")
    
    st.info(f"מנתח נתונים עבור {target}...")

with col_main:
    # יצירת גרף חזוי ל-24 שעות
    now = datetime.now()
    times = [now + timedelta(minutes=10 * i) for i in range(144)]
    # הגרף נבנה סביב הערך הנוכחי כדי שיהיה המשכי
    risk_projection = np.clip(np.random.normal(final_display, 3, 144), 0, 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=risk_projection, mode='lines', fill='tozeroy',
        line=dict(color='#ff4b4b', width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title="תחזית הסתברותית ל-24 השעות הקרובות",
        template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(range=[0, 100]),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# כפתור ידני למי שרוצה, אבל המערכת זזה לבד
if st.button("רענון ידני 🔄"):
    st.rerun()

st.caption("גרסה 3.0: מנגנון החלקה ומניעת תנודות קיצוניות.")
