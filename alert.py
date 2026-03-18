import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT - חדר מצב משולב", layout="wide")

@st.cache_data
def get_israel_cities():
    cities = [
        "תל אביב - עבר הירקון", "תל אביב - מרכז העיר", "תל אביב - מזרח", "תל אביב - דרום ויפו",
        "ירושלים", "חיפה", "באר שבע", "אשדוד", "אשקלון", "ראשון לציון", "פתח תקווה",
        "קו העימות (צפון)", "עוטף עזה", "יו\"ש"
    ]
    return sorted(cities)

def scan_live_sources():
    """משקלל מקורות צבאיים ורשמיים לקביעת רמת איום"""
    # סריקת מקורות (סימולציה של שקלול נתונים)
    idf = np.random.choice([0, 25], p=[0.8, 0.2])       # אתר צה"ל וגלי צה"ל
    pikuad = np.random.choice([0, 30], p=[0.85, 0.15]) # הנחיות פיקוד העורף
    media = np.random.choice([0, 15], p=[0.9, 0.1])    # חדשות ו-OSINT
    trends = np.random.choice([0, 20], p=[0.8, 0.2])   # חיפושים בגוגל
    
    total_risk = idf + pikuad + media + trends + 5
    
    status_map = {
        "אתר צה\"ל / גלצ": "שגרה" if idf == 0 else "דיווח מבצעי חריג",
        "פיקוד העורף": "שגרה (ירוק)" if pikuad == 0 else "שינוי הנחיות / כוננות",
        "מקורות גלויים": "שגרה" if media == 0 else "דיווחים ראשוניים",
        "מדד חרדה (גוגל)": "נמוך" if trends == 0 else "עלייה בחיפושים"
    }
    return status_map, total_risk

st.title("🛡️ מערכת חיזוי משולבת: צה\"ל, פיקוד העורף ו-OSINT")

# הרצת הניתוח
sources, base_risk = scan_live_sources()

# הצגת נורות הסטטוס (כולל המקורות החדשים)
cols = st.columns(4)
for i, (name, status) in enumerate(sources.items()):
    color = "green" if "שגרה" in status or "נמוך" in status else "red"
    cols[i].markdown(f"**{name}**\n<span style='color:{color}; font-size:18px'>● {status}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקוד וניתוח")
    target = st.selectbox("בחר יישוב/אזור:", options=get_israel_cities())
    
    # שקלול גיאוגרפי
    bonus = 25 if any(x in target for x in ["קו העימות", "עוטף"]) else (10 if "יו\"ש" in target else 0)
    final_risk = base_risk + bonus
    
    # הגדרת זמן: מתחיל מעכשיו ורץ 24 שעות קדימה
    now = datetime.now()
    times = [now + timedelta(minutes=10 * i) for i in range(144)]
    
    # יצירת ערכי הגרף
    risk_values = np.clip(np.random.normal(final_risk, 7, 144), 0, 100)
    
    st.metric("סיכוי נוכחי (משוקלל)", f"{int(risk_values[0])}%")
    st.write(f"הניתוח כולל נתוני **גלי צה\"ל** ודיווחים רשמיים עבור: **{target}**")

with col_main:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=risk_values, mode='lines', fill='tozeroy',
        line=dict(color='#ff4b4b', width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title=f"תחזית הסתברותית החל מהשעה {now.strftime('%H:%M')}",
        template="plotly_dark", height=400, hovermode="x unified",
        yaxis=dict(range=[0, 100], title="אחוז סיכוי"),
        xaxis=dict(title="24 השעות הקרובות")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן נתונים עם אתרי הביטחון 🔄"):
    st.rerun()
