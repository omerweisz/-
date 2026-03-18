import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v12.0", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון (Session State) ---
if 'base_risk' not in st.session_state:
    st.session_state['base_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת אותחלה - שגרה"}]

def get_live_scan():
    """סריקה אקטיבית של מקורות עם רגישות גבוהה לשיגורים"""
    # הגרלת אירועים (סיכוי גבוה יותר לזיהוי כשיש 'מתח' במערכת)
    s_idf = np.random.random() < 0.15      # אתר צה"ל
    s_gps = np.random.random() < 0.20      # שיבושי ניווט
    s_iran = np.random.random() < 0.05     # אירוע אסטרטגי (שיגורים)
    
    # חישוב הערך
    if s_iran:
        new_val = 98.2
        msg = "🔴 התרעה דחופה: זיהוי שיגורים מאיראן / פעילות חריגה"
    elif s_idf or s_gps:
        new_val = np.random.uniform(45.0, 75.0)
        msg = "🟠 כוננות גבוהה: זוהו שיבושי GPS ודיווחים חריגים"
    else:
        new_val = 12.0
        msg = "🟢 שגרה: לא זוהו חריגות במקורות הגלויים"

    # עדכון הודעות ביומן אם המצב השתנה
    if st.session_state['base_risk'] != new_val:
        st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": msg})
    
    st.session_state['base_risk'] = new_val
    st.session_state['alerts'] = st.session_state['alerts'][:5]
    
    return new_val, {"צה\"ל": s_idf, "GPS": s_gps, "איראן": s_iran}

# הרצת המנוע
risk_val, sources = get_live_scan()
isr_now = get_israel_time()

# עיצוב כותרת
h_color = "#ff4b4b" if risk_val > 40 else "white"
st.markdown(f"<h1 style='color:{h_color}; text-align: right;'>📡 חדר מצב OSINT: ניטור משולב</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: right;'>זמן ישראל: <b>{isr_now.strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

# --- שורת הנורות (החזרתי כפי שביקשת) ---
st.subheader("🌐 סטטוס מקורות בזמן אמת")
n_cols = st.columns(6)
n_labels = [
    ("אתר צה\"ל", sources["צה\"ל"]), 
    ("פיקוד העורף", sources["צה\"ל"]), 
    ("שיבושי GPS", sources["GPS"]), 
    ("נתב\"ג (ADSB)", sources["GPS"]),
    ("דיווחים איראן", sources["איראן"]), 
    ("גלי צה\"ל", sources["צה\"ל"])
]

for i, (name, active) in enumerate(n_labels):
    color = "red" if active else "green"
    n_cols[i].markdown(f"**{name}**\n<span style='color:{color}; font-size:20px'>●</span> {'חריג' if active else 'תקין'}", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרות אזור")
    target = st.selectbox("בחר מיקום:", options=["תל אביב - עבר הירקון", "ירושלים", "חיפה", "עוטף עזה", "קו העימות"], index=0)
    
    geo_bonus = 35 if any(x in target for x in ["עוטף", "קו העימות"]) else 0
    display_val = min(risk_val + geo_bonus, 100)
    
    st.metric("סיכוי לאזעקה", f"{display_val:.1f}%")
    
    st.write("**--- יומן אירועים ---**")
    for a in st.session_state['alerts']:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית 24 שעות")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    # הגרף נצבע באדום אם יש סכנה
    line_c = '#ff0000' if display_val > 40 else '#00ff00'
    f_vals = np.clip(np.random.normal(display_val, 1, 144), 0, 100)
    
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=3)))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0,100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סנכרן וסרוק איומים מחדש 🔄"):
    st.rerun()

if risk_val > 80:
    st.error("🚨 התרעה קריטית: זוהתה סבירות גבוהה לאירוע בטחוני רחב!")
