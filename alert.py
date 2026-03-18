import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v20.0 - עבר הירקון", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון (Session State) ---
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "סורק רב-ערוצי מופעל"}]
if 'active_sources' not in st.session_state:
    st.session_state['active_sources'] = {s: False for s in ["12", "13", "11", "14", "ynet", "צה\"ל"]}

SOURCES_LABELS = {
    "12": "חדשות 12", "13": "חדשות 13", "11": "כאן 11", 
    "14": "ערוץ 14", "ynet": "ynet", "צה\"ל": "פיקוד העורף"
}

def localized_eye_scan(selected_region):
    isr_now_str = get_israel_time().strftime('%H:%M')
    
    # סימולציה של זיהוי אירוע חדשותי כללי
    any_news_event = np.random.random() < 0.15 
    
    if any_news_event:
        # בחירת מקור אקראי ש"קלט" את האירוע
        src_key = np.random.choice(list(SOURCES_LABELS.keys()))
        st.session_state['active_sources'][src_key] = True
        
        # האם זה רלוונטי לאזור שבחרת?
        is_relevant = np.random.random() < 0.25 
        
        if is_relevant:
            st.session_state['locked_risk'] = 98.0
            msg = f"🔴 התרעה מקומית: {SOURCES_LABELS[src_key]} מדווח על איום ב{selected_region}!"
            st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
        else:
            st.session_state['locked_risk'] = 25.0
            msg = f"⚠️ מתח גזרה: {SOURCES_LABELS[src_key]} מדווח על אירוע מרוחק. רמת הדריכות עלתה."
            if st.session_state['alerts'][0]["msg"] != msg:
                st.session_state['alerts'].insert(0, {"time": isr_now_str, "msg": msg})
    
    # דעיכה אוטומטית לשגרה
    elif st.session_state['locked_risk'] > 12.0:
        st.session_state['locked_risk'] -= 3.0
        if st.session_state['locked_risk'] <= 12.0:
            st.session_state['locked_risk'] = 12.0
            st.session_state['active_sources'] = {s: False for s in SOURCES_LABELS.keys()}

    return st.session_state['locked_risk']

# --- ממשק משתמש ---
st.markdown("<h1 style='text-align: right;'>🛰️ חדר מצב OSINT: עבר הירקון</h1>", unsafe_allow_html=True)

# שורת הנורות (העיניים הדיגיטליות)
st.write("**אימות מקורות בזמן אמת:**")
n_cols = st.columns(len(SOURCES_LABELS))
for i, (key, name) in enumerate(SOURCES_LABELS.items()):
    active = st.session_state['active_sources'][key]
    color = "red" if active else "#00ff00"
    n_cols[i].markdown(f"<div style='text-align:center; border:1px solid {color}; border-radius:5px; padding:5px;'>"
                       f"<b style='font-size:12px;'>{name}</b><br>"
                       f"<span style='color:{color};'>●</span></div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 הגדרת מיקוד")
    current_region = st.selectbox("בחר אזור לניטור:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"], index=0)
    
    # הרצת המנוע
    risk_val = localized_eye_scan(current_region)
    
    st.metric("סיכוי לאזעקה במיקומך", f"{risk_val:.1f}%", delta=f"{risk_val-12:.1f}%" if risk_val > 12 else None, delta_color="inverse")
    
    st.write("**--- יומן אירועים ממוקד ---**")
    for a in st.session_state['alerts'][:4]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader(f"🕒 תחזית 24 שעות: {current_region}")
    times = [get_israel_time() + timedelta(minutes=10 * i) for i in range(144)]
    
    # יצירת גרף עם Hover (עכבר)
    f_vals = [risk_val + np.random.uniform(-0.3, 0.3) for _ in range(144)]
    line_c = '#ff4b4b' if risk_val > 30 else '#00ff00'
    
    fig = go.Figure(go.Scatter(
        x=times, y=f_vals, fill='tozeroy', 
        line=dict(color=line_c, width=3),
        hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"
    ))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

if st.button("בצע סריקת עומק 🔄"):
    st.rerun()
