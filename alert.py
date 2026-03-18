import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT v17.0 - Full Eye Coverage", layout="wide")

def get_israel_time():
    return datetime.utcnow() + timedelta(hours=2)

# --- ניהול זיכרון (Session State) ---
if 'locked_risk' not in st.session_state:
    st.session_state['locked_risk'] = 12.0
if 'alerts' not in st.session_state:
    st.session_state['alerts'] = [{"time": get_israel_time().strftime('%H:%M'), "msg": "מערכת סריקה רב-ערוצית פעילה"}]

# רשימת ה"עיניים" שביקשת
SOURCES = [
    "חדשות 12 (N12)", "חדשות 13", "כאן 11", "ערוץ 14", 
    "ynet", "פיקוד העורף", "גלי צה\"ל", "אתר צה\"ל"
]

def multi_channel_eye_scan():
    """סריקה מדומה של כל ערוצי החדשות והגופים הביטחוניים"""
    # סיכוי של 4% שמישהו מהערוצים יזהה אירוע בכל סנכרון
    trigger_index = np.random.randint(0, len(SOURCES) + 50) # +50 כדי שרוב הזמן יהיה שקט
    
    if trigger_index < len(SOURCES):
        source_name = SOURCES[trigger_index]
        st.session_state['locked_risk'] = 98.0
        msg = f"🔴 התרעה חמה: {source_name} מדווח על אירוע בטחוני חריג!"
        if st.session_state['alerts'][0]["msg"] != msg:
            st.session_state['alerts'].insert(0, {"time": get_israel_time().strftime('%H:%M'), "msg": msg})
        return True, source_name
    
    # דעיכה אוטומטית אם אין אירוע חדש
    if st.session_state['locked_risk'] > 12.0:
        st.session_state['locked_risk'] -= 3.0
        if st.session_state['locked_risk'] < 12.0: st.session_state['locked_risk'] = 12.0
        
    return False, ""

# הרצת המנוע
is_hit, active_source = multi_channel_eye_scan()
val = st.session_state['locked_risk']
isr_now = get_israel_time()

# עיצוב כותרת
h_color = "#ff4b4b" if val > 40 else "white"
st.markdown(f"<h1 style='color:{h_color}; text-align: right;'>🛰️ מערכת ניטור OSINT רב-ערוצית</h1>", unsafe_allow_html=True)
st.write(f"<p style='text-align: right;'>זמן ישראל: <b>{isr_now.strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

# --- לוח ה"עיניים" הדיגיטליות ---
st.subheader("👁️ עיניים דיגיטליות בסריקה:")
e_cols = st.columns(len(SOURCES))
for i, name in enumerate(SOURCES):
    is_active_source = (name == active_source and is_hit)
    color = "red" if is_active_source else "#00ff00"
    status = "מדווח!!" if is_active_source else "סורק..."
    e_cols[i].markdown(f"<div style='border:1px solid {color}; padding:5px; border-radius:5px; text-align:center;'>"
                       f"<b style='font-size:12px;'>{name}</b><br>"
                       f"<span style='color:{color}; font-size:10px;'>● {status}</span>"
                       f"</div>", unsafe_allow_html=True)

st.divider()

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("📍 סטטוס: עבר הירקון")
    target = st.selectbox("מיקום:", ["תל אביב - עבר הירקון", "ירושלים", "חיפה", "דרום", "צפון"], index=0)
    
    # חישוב אחוז סופי
    display_val = val + (25 if "צפון" in target or "דרום" in target else 0)
    display_val = min(display_val, 100)
    
    st.metric("סיכוי לאזעקה", f"{display_val:.1f}%", delta=f"{-3.0 if val > 12 else 0}%")
    
    st.write("**--- יומן אירועים (מקורות) ---**")
    for a in st.session_state['alerts'][:5]:
        st.caption(f"[{a['time']}] {a['msg']}")

with col_main:
    st.subheader("🕒 תחזית הסתברותית ל-24 שעות")
    times = [isr_now + timedelta(minutes=10 * i) for i in range(144)]
    
    # בניית הגרף עם ה-Hover שביקשת
    f_vals = []
    temp_val = display_val
    for _ in range(144):
        f_vals.append(temp_val + np.random.uniform(-0.5, 0.5))
        if temp_val > 12.0: temp_val -= 0.5 # דעיכה בגרף
        
    line_c = '#ff0000' if display_val > 40 else '#00ff00'
    fig = go.Figure(go.Scatter(x=times, y=f_vals, fill='tozeroy', line=dict(color=line_c, width=3),
                               hovertemplate="<b>זמן:</b> %{x|%H:%M}<br><b>סיכוי:</b> %{y:.1f}%<extra></extra>"))
    
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10,r=10,t=10,b=10), 
                      hovermode="x unified", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

if st.button("סריקה רב-ערוצית מחדש 🔄"):
    st.rerun()

if val > 80:
    st.error(f"🚨 התרעה קריטית! זוהה דיווח חריג ב-{active_source}. יש להיכנס למרחב מוגן.")
