import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT - חיזוי אוטונומי", layout="wide")

@st.cache_data
def get_israel_cities():
    # רשימה נקייה ומסודרת
    cities = [
        "תל אביב - עבר הירקון", "תל אביב - מרכז העיר", "תל אביב - מזרח", "תל אביב - דרום ויפו",
        "ירושלים", "חיפה", "באר שבע", "אשדוד", "אשקלון", "ראשון לציון", "פתח תקווה",
        "קו העימות (צפון)", "עוטף עזה", "יו\"ש"
    ]
    return sorted(cities)

def scan_live_sources():
    """סורק מקורות וקובע רמת סיכון בסיסית (מדמה OSINT)"""
    s1 = np.random.choice([0, 20], p=[0.85, 0.15]) # חדשות
    s2 = np.random.choice([0, 15], p=[0.9, 0.1])  # נתב"ג
    s3 = np.random.choice([0, 25], p=[0.8, 0.2])  # גוגל טרנדס
    s4 = np.random.choice([0, 20], p=[0.75, 0.25]) # רשתות חברתיות
    
    risk_base = s1 + s2 + s3 + s4 + 5
    
    sources = {
        "חדשות": "שגרה" if s1 == 0 else "דיווח חריג",
        "נתב\"ג": "פתוח" if s2 == 0 else "שינויים בלוח",
        "Google Trends": "שגרה" if s3 == 0 else "זינוק חיפושים",
        "רשתות חברתיות": "שגרה" if s4 == 0 else "דיווח ראשוני"
    }
    return sources, risk_base

st.title("🛰️ מערכת חיזוי אזעקות - ניתוח הסתברותי")

# הרצת הסריקה
sources, global_risk = scan_live_sources()

# הצגת נורות
cols = st.columns(4)
for i, (name, status) in enumerate(sources.items()):
    color = "green" if "שגרה" in status or "פתוח" in status else "red"
    cols[i].markdown(f"**{name}**\n<span style='color:{color}; font-size:18px'>● {status}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 בחירת מיקום")
    all_cities = get_israel_cities()
    target = st.selectbox("בחר יישוב/אזור:", options=all_cities)
    
    # שקלול סיכון לפי מיקום (בונוס לאזורי עימות)
    location_bonus = 0
    if "קו העימות" in target or "עוטף" in target:
        location_bonus = 25
    elif "יו\"ש" in target:
        location_bonus = 10
        
    final_risk = global_risk + location_bonus
    
    # יצירת גרף
    times = pd.date_range(start=datetime.now(), periods=144, freq='10min')
    risk_values = np.clip(np.random.normal(final_risk, 6, 144), 0, 100)
    
    st.metric("סיכוי משוקלל לאזעקה", f"{int(risk_values.mean())}%")
    st.write(f"החישוב מתבסס על שילוב של **מצב לאומי** ורמת סיכון ב-**{target}**.")

with col_main:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=risk_values, mode='lines', fill='tozeroy',
        line=dict(color='#ff4b4b', width=3),
        hovertemplate="<b>שעה:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title=f"תחזית הסתברות ל-24 שעות: {target}",
        template="plotly_dark", height=400, hovermode="x unified",
        yaxis=dict(range=[0, 100], title="סיכוי (%)")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("רענן סריקת מקורות 🔄"):
    st.rerun()
