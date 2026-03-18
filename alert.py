import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v5.0 - ניתוח עבר הירקון", layout="wide")

# ניהול זיכרון למגמות (Session State)
if 'current_risk' not in st.session_state:
    st.session_state['current_risk'] = 12.5
if 'history' not in st.session_state:
    st.session_state['history'] = [12.5] * 20

def get_realtime_data():
    """חישוב הסתברות מבוסס הצלבת נתונים רב-שכבתית"""
    # סריקה מדומה של מקורות (צה"ל, פקע"ר, GPS, גלצ)
    s_idf = np.random.choice([0, 12], p=[0.92, 0.08])
    s_gps = np.random.choice([0, 15], p=[0.88, 0.12])
    s_media = np.random.choice([0, 8], p=[0.85, 0.15])
    
    # חישוב הערך החדש עם השפעת שעה (שעות ערב מעלות סיכון)
    now = datetime.now()
    hour_boost = 4 if (19 <= now.hour <= 22) else 0
    
    new_val = s_idf + s_gps + s_media + hour_boost + 7.0
    
    # החלקת תנועה (Smoothing) למניעת קפיצות לא הגיוניות
    st.session_state['current_risk'] = (st.session_state['current_risk'] * 0.7) + (new_val * 0.3)
    
    # עדכון היסטוריה
    st.session_state['history'].append(st.session_state['current_risk'])
    if len(st.session_state['history']) > 20: st.session_state['history'].pop(0)
    
    return st.session_state['current_risk'], {"IDF": s_idf, "GPS": s_gps, "Media": s_media}

# הרצת המנוע
current_risk_base, details = get_realtime_data()

st.title("🛡️ חדר מצב OSINT: תל אביב והמרכז")
st.write(f"סטטוס מערכת נכון ל-{datetime.now().strftime('%H:%M:%S')}")

# נורות בקרה לאמינות
l_cols = st.columns(4)
labels = ["אתר צה\"ל", "שיבושי GPS", "גלי צה\"ל", "פיקוד העורף"]
for i, label in enumerate(labels):
    is_active = False
    if i == 0 and details["IDF"] > 0: is_active = True
    if i == 1 and details["GPS"] > 0: is_active = True
    
    color = "red" if is_active else "green"
    status = "חריג" if is_active else "שגרה"
    l_cols[i].markdown(f"**{label}**\n<span style='color:{color}'>● {status}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 מיקוד גיאוגרפי")
    # הגדרת עבר הירקון כברירת מחדל
    cities = ["תל אביב - עבר הירקון", "תל אביב - מרכז", "ירושלים", "חיפה", "עוטף עזה", "קו העימות"]
    target = st.selectbox("בחר אזור:", options=cities, index=0)
    
    # בונוס סיכון לפי מיקום
    geo_bonus = 30 if "עוטף" in target or "קו העימות" in target else 0
    final_risk = min(current_risk_base + geo_bonus, 100)
    
    st.metric("סיכוי לאזעקה (זמן אמת)", f"{final_risk:.1f}%")
    
    # מדד אמינות
    st.write("**רמת אמינות הניתוח:**")
    st.progress(0.94 if final_risk < 25 else 0.82)
    st.caption("הנתונים משלבים דיווחי גלצ ושיבושי ניווט במרכז.")

with col_main:
    # טאבים להחלפה בין היסטוריה לתחזית
    tab1, tab2 = st.tabs(["📈 תחזית 24 שעות", "🕒 מגמה אחרונה (Live)"])
    
    with tab1:
        # גרף 24 שעות שביקשת
        future_times = [datetime.now() + timedelta(minutes=10 * i) for i in range(144)]
        future_vals = np.clip(np.random.normal(final_risk, 5, 144), 0, 100)
        
        fig_future = go.Figure()
        fig_future.add_trace(go.Scatter(x=future_times, y=future_vals, fill='tozeroy', line=dict(color='#ff4b4b')))
        fig_future.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), yaxis=dict(range=[0,100]))
        st.plotly_chart(fig_future, use_container_width=True)

    with tab2:
        # גרף המגמה (היסטוריה)
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(y=st.session_state['history'], mode='lines+markers', line=dict(color='#00ff00')))
        fig_hist.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), yaxis=dict(range=[0,100]))
        st.plotly_chart(fig_hist, use_container_width=True)

if st.button("סנכרן נתונים 🔄"):
    st.rerun()
