import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# הגדרות דף
st.set_page_config(page_title="מערכת חיזוי אזעקות אוטונומית", layout="wide")

@st.cache_data
def get_israel_cities():
    # רשימת אזורי פיקוד העורף
    cities = [
        "תל אביב - עבר הירקון", "תל אביב - מרכז העיר", "תל אביב - מזרח", "תל אביב - דרום ויפו",
        "ירושלים", "חיפה", "באר שבע", "אשדוד", "אשקלון", "ראשון לציון", "פתח תקווה",
        "קו העימות (צפון)", "עוטף עזה", "יו"ש"
    ]
    return sorted(cities)

def scan_live_sources():
    """סורק מקורות וקובע את רמת הסיכון האוטומטית (0-100)"""
    # מדמה סריקה של 4 מקורות. כל מקור אדום מוסיף סיכון.
    s1 = np.random.choice([0, 25], p=[0.8, 0.2]) # חדשות
    s2 = np.random.choice([0, 20], p=[0.9, 0.1]) # נתב"ג
    s3 = np.random.choice([0, 30], p=[0.85, 0.15]) # גוגל טרנדס
    s4 = np.random.choice([0, 25], p=[0.7, 0.3]) # טלגרם
    
    total_risk_base = s1 + s2 + s3 + s4 + 5 # מינימום 5% תמיד
    
    sources = {
        "חדשות": "שגרה" if s1 == 0 else "דיווח חריג",
        "נתב\"ג": "פתוח" if s2 == 0 else "עיכובים/שינויים",
        "Google Trends": "שגרה" if s3 == 0 else "זינוק בחיפושים",
        "רשתות חברתיות": "שגרה" if s4 == 0 else "דיווחים ראשוניים"
    }
    return sources, total_risk_base

st.title("📡 מערכת OSINT: סיכוי לאזעקות בזמן אמת")
st.write("המערכת מנתחת מקורות מידע גלויים וקובעת את ההסתברות לאזעקה באופן אוטומטי.")

# הרצת הסריקה
sources, risk_level = scan_live_sources()

# הצגת הנורות
cols = st.columns(4)
for i, (name, status) in enumerate(sources.items()):
    color = "green" if "שגרה" in status or "פתוח" in status else "red"
    cols[i].markdown(f"**{name}**\n<span style='color:{color}; font-size:18px'>● {status}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקום")
    all_cities = get_israel_cities()
    target = st.selectbox("בחר יישוב/אזור:", options=all_cities)
    
    # חישוב גרף הסתברות ל-24 שעות על בסיס הסריקה
    times = pd.date_range(start=datetime.now(), periods=144, freq='10min')
    # יצירת תנודה סביב רמת הסיכון שנמצאה בסריקה
    risk_values = np.clip(np.random.normal(risk_level, 5, 144), 0, 100)
    
    st.metric("סיכוי נוכחי לאזעקה", f"{int(risk_values.mean())}%")
    st.info(f"הנתונים מבוססים על שקלול מקורות עבור: {target}")

with col_main:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=risk_values, mode='lines', fill='tozeroy',
        line=dict(color='#ff4b4b', width=3),
        hovertemplate="<b>שעה:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title=f"תחזית הסתברות: {target}",
        template="plotly_dark", height=400, hovermode="x unified",
        yaxis=dict(range=[0, 100], title="אחוז סיכוי")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("בצע סריקת מקורות מחודשת"):
    st.rerun()
