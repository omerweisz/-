import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT - גרסה יציבה", layout="wide")

# שימוש ב-Session State כדי לזכור את הסיכון הקודם ולמנוע קפיצות ל-0
if 'last_risk' not in st.session_state:
    st.session_state['last_risk'] = 5.0

@st.cache_data
def get_israel_cities():
    cities = [
        "תל אביב - עבר הירקון", "תל אביב - מרכז העיר", "תל אביב - מזרח", "תל אביב - דרום ויפו",
        "ירושלים", "חיפה", "באר שבע", "אשדוד", "אשקלון", "ראשון לציון", "פתח תקווה",
        "קו העימות (צפון)", "עוטף עזה", "יו\"ש", "אילת", "רמת הגולן"
    ]
    return sorted(cities)

def scan_all_sources_stable():
    """סריקה עם מנגנון החלקת נתונים למניעת קפיצות פתאומיות"""
    # דגימת מקורות (0 או ערך גבוה)
    s_official = np.random.choice([0, 35], p=[0.9, 0.1]) 
    s_civilian = np.random.choice([0, 20], p=[0.85, 0.15])
    s_infra = np.random.choice([0, 15], p=[0.92, 0.08])
    
    current_raw_risk = s_official + s_civilian + s_infra + 5.0
    
    # מנגנון החלקה: משקל של 60% למצב החדש ו-40% למצב הקודם
    smoothed_risk = (current_raw_risk * 0.6) + (st.session_state['last_risk'] * 0.4)
    st.session_state['last_risk'] = smoothed_risk
    
    status = {
        "מקורות ביטחון": "שגרה" if s_official == 0 else "כוננות",
        "מדד חרדה": "יציב" if s_civilian == 0 else "זינוק חיפושים",
        "תעופה/תשתיות": "תקין" if s_infra == 0 else "שיבושים"
    }
    return status, smoothed_risk

st.title("🛡️ חדר מצב OSINT - ניתוח הסתברותי רציף")

# הרצת סריקה יציבה
sources_data, final_calculated_risk = scan_all_sources_stable()

# הצגת נורות
cols = st.columns(3)
for i, (name, status_text) in enumerate(sources_data.items()):
    color = "red" if status_text not in ["שגרה", "יציב", "תקין"] else "green"
    cols[i].markdown(f"**{name}**\n<span style='color:{color}; font-size:18px'>● {status_text}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרות מיקום")
    target = st.selectbox("בחר אזור ניתוח:", options=get_israel_cities())
    
    # תוספת סיכון גיאוגרפית (קבועה ולא משתנה בסנכרון)
    geo_bonus = 30 if any(x in target for x in ["קו העימות", "עוטף"]) else (10 if "יו\"ש" in target else 0)
    
    # סיכוי סופי משולב
    display_risk = min(final_calculated_risk + geo_bonus, 100)
    
    now = datetime.now()
    times = [now + timedelta(minutes=10 * i) for i in range(144)]
    risk_values = np.clip(np.random.normal(display_risk, 4, 144), 0, 100)
    
    st.metric("סיכוי נוכחי משוקלל", f"{int(display_risk)}%")
    st.write(f"המדד מציג הסתברות רציפה עבור: **{target}**")

with col_main:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=risk_values, mode='lines', fill='tozeroy',
        line=dict(color='#ff4b4b', width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title=f"תחזית 24 שעות (החל מ-{now.strftime('%H:%M')})",
        template="plotly_dark", height=400, hovermode="x unified",
        yaxis=dict(range=[0, 100], title="סיכוי (%)")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("עדכן נתוני זמן אמת 🔄"):
    st.rerun()

st.caption("⚠️ המערכת משתמשת בזיכרון קצר-טווח כדי למנוע תנודות קיצוניות ודיווחי שווא.")
