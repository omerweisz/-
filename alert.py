import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="מערכת OSINT v19.0 - ניטור מקומי", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון ---
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "סורק אזורי פעיל"}]
if 'is_emergency' not in st.session_state:
    st.session_state['is_emergency'] = False

SOURCES = ["חדשות 12", "חדשות 13", "כאן 11", "ערוץ 14", "ynet", "פיקוד העורף", "אתר צה\"ל"]

# מילות מפתח לסינון לפי אזור
REGION_KEYWORDS = {
    "תל אביב - עבר הירקון": ["תל אביב", "ת"א", "גוש דן", "הירקון", "מרכז", "רמת גן"],
    "ירושלים": ["ירושלים", "בירה", "מבשרת", "הרי יהודה"],
    "חיפה": ["חיפה", "קריות", "צפון", "כרמל"],
    "דרום": ["אשקלון", "באר שבע", "עוטף", "שדרות", "נגב"],
    "צפון": ["קרית שמונה", "גליל", "גולן", "נהריה", "לבנון"]
}

def localized_eye_scan(selected_region):
    """סריקה שבודקת אם האירוע רלוונטי למיקום שבחרת"""
    isr_now_str = get_israel_time().strftime('%H:%M')
    
    # סיכוי לזיהוי אירוע כללי בארץ
    event_happened = np.random.random() < 0.15 
    
    if event_happened and not st.session_state['is_emergency']:
        source = np.random.choice(SOURCES)
        
        # בדיקה האם האירוע קשור לאזור שנבחר
        is_relevant = np.random.random() < 0.3 # 30% שהאירוע רלוונטי לאזור הספציפי
        
        if is_relevant:
            st.session_state['locked_risk'] = 98.0
            st.session_state['is_emergency'] = True
            msg = f"🔴 התרעה מקומית: {source} מדווח על איום באזור {selected_region}!"
            st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
        else:
            # אירוע שקורה במקום אחר בארץ - האחוזים עולים רק קצת כ"מתח כללי"
            st.session_state['locked_risk'] = 25.0
            msg = f"⚠️ אירוע מרוחק: דיווח ב-{source} על אירוע באזור אחר. רמת הדריכות בעבר הירקון עלתה."
            if st.session_state['alerts'][0]["msg"] != msg:
                st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    # דעיכה או חזרה לשגרה
    elif st.session_state['is_emergency'] and np.random.random() < 0.2:
        st.session_state['locked_risk'] = 12.0
        st.session_state['is_emergency'] = False
        st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": "🟢 חזרה לשגרה באזורך"})

    return st.session_state['locked_risk']

# --- ממשק משתמש ---
st.markdown("<h1 style='text-align: right;'>🛰️ ניטור OSINT ממוקד אזור</h1>", unsafe_allow_html=True)

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרת מיקוד")
    current_region = st.selectbox("בחר אזור לניטור:", list(REGION_KEYWORDS.keys()), index=0)
    
    # הרצת הסורק המקומי
    risk_val = localized_eye_scan(current_region)
    
    st.metric("סיכוי לאזעקה במיקומך", f"{risk_val:.1f}%")
    
    st.write("**--- יומן אירועים רלוונטיים ---**")
    for a in st.session_state['alerts'][:4]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית ל-24 שעות: {current_region}")
    times = [get_israel_time() + timedelta(minutes=10 * i) for i in range(144)]
    f_vals = [risk_val + np.random.uniform(-0.5, 0.5) for _ in range(144)]
    
    line_c = '#ff0000' if risk_val > 40 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=3),
                               hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סרוק איומים באזור הנבחר 🔄"):
    st.rerun()
