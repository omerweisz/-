import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# הגדרות דף רחב
st.set_page_config(page_title="מערכת מודיעין OSINT משולבת", layout="wide")

def get_external_sources():
    """מדמה סריקה של מקורות חיצוניים גלויים (OSINT) בזמן אמת"""
    sources = {
        "חדשות (N12/ynet)": np.random.choice(["תקין", "דיווח ראשוני על אירוע"], p=[0.8, 0.2]),
        "סטטוס נתב\"ג": np.random.choice(["פתוח", "שינויי נתיבים/השהייה"], p=[0.9, 0.1]),
        "עומסי תנועה (Waze)": np.random.choice(["שגרה", "חריג באזור המרכז"], p=[0.85, 0.15]),
        "פיקוד העורף": np.random.choice(["שגרה", "אזעקות בדרום"], p=[0.75, 0.25]),
        # פיצ'רים חדשים:
        "חיפושי גוגל (Trends)": np.random.choice(["שגרה", "זינוק בחיפושי 'בום/אזעקה'"], p=[0.8, 0.2]),
        "רשתות חברתיות/טלגרם": np.random.choice(["שגרה", "דיווחים לא מאומתים על שיגורים"], p=[0.7, 0.3])
    }
    return sources

def generate_ultra_pro_data(arena, sources):
    times = pd.date_range(start=datetime.now(), periods=144, freq='10min')
    
    # חישוב בונוס סיכון מכל המקורות החיצוניים (6 מקורות)
    external_bonus = 0
    anomalies_count = 0
    for status in sources.values():
        if status not in ["תקין", "פתוח", "שגרה"]:
            external_bonus += 12  # קצת פחות מ-15 כי יש יותר מקורות
            anomalies_count += 1
            
    # בסיס הסתברות לפי זירה
    if arena == "מתיחות בצפון (לבנון)":
        base_risk = np.random.normal(20, 5, size=144) + external_bonus
    elif arena == "התרעה אסטרטגית (איראן)":
        base_risk = np.zeros(144)
        base_risk[40:80] = 65 + external_bonus
    else:
        base_risk = np.random.uniform(2, 8, size=144) + (external_bonus / 1.5)
        
    risk = np.clip(base_risk, 0, 100)
    low = np.clip(risk - 10, 0, 100)
    high = np.clip(risk + 10, 0, 100)
    
    # מדד אמינות מורכב המושפע מכמות החריגות
    reliability = 98 - (anomalies_count * 3)
    
    return times, risk, low, high, reliability, anomalies_count

st.title("🛰️ מערכת ניתוח הסתברותית מרובת מקורות (OSINT Pulse)")
st.caption(f"העדכון האחרון בוצע ב: {datetime.now().strftime('%H:%M:%S')}")

# חלק עליון: נורות בקרה (מעודכן ל-6 נורות)
sources = get_external_sources()
st.subheader("סטטוס מקורות מודיעין גלויים")
cols = st.columns(6)
for i, (name, status) in enumerate(sources.items()):
    with cols[i]:
        color = "green" if status in ["תקין", "פתוח", "שגרה"] else "red"
        st.markdown(f"**{name}**")
        st.markdown(f"● <span style='color:{color}; font-size:20px'>{status}</span>", unsafe_allow_html=True)

st.markdown("---")

# חלק מרכזי: גרף ותפריט
col_side, col_main = st.columns([1, 3])

with col_side:
    st.subheader("הגדרות ניתוח")
    arena = st.selectbox("זירה פעילה אקטיבית:", ["שגרה", "מתיחות בצפון (לבנון)", "התרעה אסטרטגית (איראן)"])
    times, risk, low, high, acc, anomalies = generate_ultra_pro_data(arena, sources)
    
    st.metric("מדד אמינות תחזית משולב", f"{acc}%")
    
    if anomalies > 0:
        st.warning(f"זוהו {anomalies} חריגות במקורות החיצוניים. ההסתברות עודכנה כלפי מעלה.")
    else:
        st.success("✅ כל המקורות החיצוניים מדווחים על שגרה.")

with col_main:
    # בניית הגרף המקצועי
    fig = go.Figure()
    # טווח טעות
    fig.add_trace(go.Scatter(x=np.concatenate([times, times[::-1]]), y=np.concatenate([high, low[::-1]]),
                             fill='toself', fillcolor='rgba(255, 75, 75, 0.1)', line=dict(color='rgba(255,255,255,0)'),
                             name="טווח טעות סטטיסטי", showlegend=False))
    # קו ראשי
    fig.add_trace(go.Scatter(x=times, y=risk, mode='lines', line=dict(color='#ff4b4b', width=4), name="הסתברות משוקללת"))
    
    fig.update_layout(title=f"ניתוח סיכונים דינמי (24 שעות): {arena}",
                      template="plotly_dark", height=450, margin=dict(l=20, r=20, t=40, b=20),
                      yaxis=dict(range=[0, 100], title="אחוז הסתברות לאזעקה"), xaxis_title="ציר זמן")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# פיצ'ר המפה הנפתחת (רק אם לוחצים)
with st.expander("🗾 הצג מפת איומים דינמית (לחץ לפתיחה)", expanded=False):
    st.write("מפה סימולטיבית המציגה את מוקדי הסיכון המרכזיים:")
    
    # יצירת מפה פשוטה המבוססת על מיקום המשתמש (תל אביב כברירת מחדל)
    map_data = pd.DataFrame({
        'lat': [32.085], # תל אביב
        'lon': [34.78]
    })
    
    # במצב מתיחות בצפון, המפה תתמקד בצפון
    if arena == "מתיחות בצפון (לבנון)":
        map_data = pd.DataFrame({
            'lat': [32.8, 33.0, 32.9],
            'lon': [34.9, 35.1, 35.3]
        })
    
    st.map(map_data)
    st.info("המפה מציגה עיגולים אדומים על אזורי הסיכון הנגזרים מהזירה הפעילה.")
