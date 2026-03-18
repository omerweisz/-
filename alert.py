import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT - ניתוח לפי יישוב", layout="wide")

# מאגר מידע של יישובים ואזורי התרעה (דוגמה למרכזיים - ניתן להוסיף עוד)
YISHUVIM_DATA = {
    "תל אביב - עבר הירקון": {"lat": 32.11, "lon": 34.81, "region": "מרכז"},
    "תל אביב - מרכז העיר": {"lat": 32.07, "lon": 34.77, "region": "מרכז"},
    "תל אביב - מזרח": {"lat": 32.06, "lon": 34.80, "region": "מרכז"},
    "תל אביב - דרום ויפו": {"lat": 32.04, "lon": 34.75, "region": "מרכז"},
    "רמת גן": {"lat": 32.07, "lon": 34.82, "region": "מרכז"},
    "גבעתיים": {"lat": 32.07, "lon": 34.81, "region": "מרכז"},
    "חיפה - מערב": {"lat": 32.81, "lon": 34.96, "region": "צפון"},
    "חיפה - כרמל": {"lat": 32.79, "lon": 34.99, "region": "צפון"},
    "קרית שמונה": {"lat": 33.20, "lon": 35.57, "region": "צפון"},
    "נהריה": {"lat": 33.00, "lon": 35.09, "region": "צפון"},
    "אשקלון - צפון": {"lat": 31.69, "lon": 34.58, "region": "דרום"},
    "אשקלון - דרום": {"lat": 31.65, "lon": 34.55, "region": "דרום"},
    "באר שבע": {"lat": 31.25, "lon": 34.79, "region": "דרום"},
    "ירושלים": {"lat": 31.76, "lon": 35.21, "region": "ירושלים"}
}

def get_external_sources():
    sources = {
        "חדשות (N12/ynet)": np.random.choice(["תקין", "דיווח ראשוני"], p=[0.8, 0.2]),
        "סטטוס נתב\"ג": np.random.choice(["פתוח", "השהייה"], p=[0.9, 0.1]),
        "Waze (עומסים)": np.random.choice(["שגרה", "חריג"], p=[0.85, 0.15]),
        "גוגל טרנדס": np.random.choice(["שגרה", "זינוק בחיפושים"], p=[0.8, 0.2]),
        "טלגרם": np.random.choice(["שגרה", "דיווח על שיגור"], p=[0.75, 0.25]),
        "פיקוד העורף": np.random.choice(["שגרה", "אזעקות"], p=[0.8, 0.2])
    }
    return sources

def generate_custom_risk(arena, selected_yishuv, sources):
    times = pd.date_range(start=datetime.now(), periods=144, freq='10min')
    yishuv_info = YISHUVIM_DATA[selected_yishuv]
    
    # חישוב בונוס חיצוני
    ext_bonus = sum(10 for s in sources.values() if s not in ["תקין", "פתוח", "שגרה"])
    
    # התאמת סיכון לפי אזור גיאוגרפי
    regional_multiplier = 1.0
    if arena == "מתיחות בצפון (לבנון)" and yishuv_info["region"] == "צפון":
        regional_multiplier = 2.5
    elif arena == "מתיחות בצפון (לבנון)" and yishuv_info["region"] == "מרכז":
        regional_multiplier = 1.2
        
    if arena == "התרעה אסטרטגית (איראן)":
        base = np.zeros(144)
        base[40:80] = 70
        risk = (base + ext_bonus)
    else:
        risk = (np.random.uniform(5, 15, size=144) + ext_bonus) * regional_multiplier
        
    risk = np.clip(risk, 0, 100)
    return times, risk

# UI
st.title("🛡️ ניתוח הסתברותי לפי יישוב - OSINT Pulse")

# שורה של נורות סטטוס
sources = get_external_sources()
cols = st.columns(6)
for i, (name, status) in enumerate(sources.items()):
    color = "green" if status in ["תקין", "פתוח", "שגרה"] else "red"
    cols[i].markdown(f"**{name}**\n<span style='color:{color}'>● {status}</span>", unsafe_allow_html=True)

st.markdown("---")

col_side, col_main = st.columns([1, 2])

with col_side:
    st.subheader("הגדרות מיקום וזירה")
    
    # תיבת החיפוש עם השלמה אוטומטית
    selected_yishuv = st.selectbox("חפש יישוב או אזור התרעה:", options=list(YISHUVIM_DATA.keys()))
    
    arena = st.selectbox("זירה אקטיבית:", ["שגרה", "מתיחות בצפון (לבנון)", "התרעה אסטרטגית (איראן)"])
    
    times, risk = generate_custom_risk(arena, selected_yishuv, sources)
    
    st.metric("רמת סיכון נוכחית", f"{int(risk.max())}%")
    st.info(f"מנתח נתונים עבור: {selected_yishuv}")

with col_main:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=risk, mode='lines', fill='tozeroy', line=dict(color='#ff4b4b', width=3)))
    fig.update_layout(title=f"תחזית סיכון ל-24 שעות: {selected_yishuv}", template="plotly_dark", yaxis=dict(range=[0,100]))
    st.plotly_chart(fig, use_container_width=True)

# המפה הנפתחת
with st.expander("🗾 הצג מפה ומיקום אזור התרעה", expanded=False):
    st.write(f"מיקוד מערכת עבור {selected_yishuv}:")
    lat = YISHUVIM_DATA[selected_yishuv]["lat"]
    lon = YISHUVIM_DATA[selected_yishuv]["lon"]
    
    # יצירת מפה ממוקדת ביישוב שנבחר
    map_df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(map_df, zoom=12)
