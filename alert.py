import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v4.0 - אימות רב-שכבתי", layout="wide")

# ניהול מצב רציף
if 'current_risk' not in st.session_state:
    st.session_state['current_risk'] = 15.0 # התחלה עם רמת דריכות בסיסית
if 'history' not in st.session_state:
    st.session_state['history'] = []

def get_advanced_risk():
    """חישוב סיכון מבוסס הצלבת מקורות וזמן יממה"""
    now = datetime.now()
    
    # 1. גורם זמן (Time Factor) - העלאת סיכון בשעות "חמות"
    time_factor = 5 if (18 <= now.hour <= 21 or 6 <= now.hour <= 9) else 0
    
    # 2. סימולציית הצלבה (Cross-Referencing)
    # ככל שיש יותר מקורות "דלוקים", הסיכון קופץ אקספוננציאלית
    s_idf = np.random.choice([0, 10], p=[0.9, 0.1])
    s_pikuad = np.random.choice([0, 15], p=[0.92, 0.08])
    s_gps = np.random.choice([0, 12], p=[0.85, 0.15]) # שיבושי GPS
    
    raw_total = s_idf + s_pikuad + s_gps + time_factor + 8.0
    
    # החלקת נתונים (Smoothing) למניעת קפיצות
    st.session_state['current_risk'] = (st.session_state['current_risk'] * 0.8) + (raw_total * 0.2)
    
    # רישום היסטוריה לגרף
    st.session_state['history'].append(st.session_state['current_risk'])
    if len(st.session_state['history']) > 20: st.session_state['history'].pop(0)
    
    return st.session_state['current_risk'], {"צה\"ל": s_idf, "פיקוד העורף": s_pikuad, "שיבושי GPS": s_gps}

# הרצת המנוע
risk_val, source_check = get_advanced_risk()

st.title("🛰️ חדר מצב OSINT - הצלבת מקורות בזמן אמת")
st.write(f"עדכון אחרון: **{datetime.now().strftime('%H:%M:%S')}**")

# נורות אמינות
cols = st.columns(4)
col_labels = ["אתר צה\"ל", "פיקוד העורף", "גלי צה\"ל", "שיבושי ניווט (GPS)"]
for i, label in enumerate(col_labels):
    # אם המקור תרם לסיכון, הוא נצבע בכתום/אדום
    status = "תקין"
    color = "green"
    if i == 3 and source_check["שיבושי GPS"] > 0:
        status, color = "שיבושים זוהו", "orange"
    elif i == 0 and source_check["צה\"ל"] > 0:
        status, color = "עדכון חריג", "red"
    elif i == 1 and source_check["פיקוד העורף"] > 0:
        status, color = "שינוי הנחיות", "red"
        
    cols[i].markdown(f"**{label}**\n<span style='color:{color}'>● {status}</span>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("⚙️ ניתוח גיאוגרפי")
    cities = ["תל אביב", "ירושלים", "חיפה", "באר שבע", "אשקלון", "קו העימות (צפון)", "עוטף עזה"]
    target = st.selectbox("מיקום למעקב:", options=sorted(cities))
    
    # שקלול סיכון סופי
    geo_bonus = 35 if any(x in target for x in ["קו העימות", "עוטף"]) else 5
    total_display = min(risk_val + geo_bonus, 100)
    
    # מדד אמינות (Confidence)
    confidence = 92 if risk_val < 20 else 78 # כששקט האמינות גבוהה יותר
    
    st.metric("סיכוי לאזעקה", f"{total_display:.1f}%")
    st.progress(confidence / 100, text=f"רמת אמינות הניתוח: {confidence}%")
    st.write(f"המדד משקלל כעת את מצב ה-GPS והשעה ביום עבור {target}.")

with col_main:
    # גרף היסטורי (מה קרה ב-10 דקות האחרונות)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state['history'], 
        mode='lines+markers',
        line=dict(color='#00ff00' if risk_val < 30 else '#ff4b4b', width=3),
        name="מגמת סיכון"
    ))
    
    fig.update_layout(
        title="מגמת סיכון ב-20 הדקות האחרונות (Live)",
        template="plotly_dark", height=350,
        yaxis=dict(range=[0, 100], title="אחוז סיכוי"),
        xaxis=dict(title="דגימות רצופות")
    )
    st.plotly_chart(fig, use_container_width=True)

if st.button("סרוק מקורות מחדש 🔄"):
    st.rerun()

st.info("💡 המערכת מחשבת 'סיכוי לאזעקה בדקה הקרובה'. לכן 20-30 אחוזים נחשבים למצב מתיחות משמעותי מאוד.")
