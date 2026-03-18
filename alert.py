import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT - כל יישובי ישראל", layout="wide")

# מאגר יישובים מורחב (דוגמה למבנה - ניתן להוסיף כאן מאות שורות)
# בייצור אמיתי, אפשר לטעון כאן קובץ CSV עם כל ה-1100 יישובים
@st.cache_data
def load_yishuvim():
    data = {
        "תל אביב - עבר הירקון": {"lat": 32.11, "lon": 34.81, "region": "מרכז"},
        "תל אביב - מרכז העיר": {"lat": 32.07, "lon": 34.77, "region": "מרכז"},
        "תל אביב - מזרח": {"lat": 32.06, "lon": 34.80, "region": "מרכז"},
        "תל אביב - דרום ויפו": {"lat": 32.04, "lon": 34.75, "region": "מרכז"},
        "ירושלים - צפון": {"lat": 31.81, "lon": 35.21, "region": "ירושלים"},
        "ירושלים - מרכז": {"lat": 31.78, "lon": 35.22, "region": "ירושלים"},
        "ירושלים - דרום": {"lat": 31.75, "lon": 35.20, "region": "ירושלים"},
        "חיפה - כרמל": {"lat": 32.79, "lon": 34.99, "region": "צפון"},
        "חיפה - מפרץ": {"lat": 32.81, "lon": 35.02, "region": "צפון"},
        "ראשון לציון - מזרח": {"lat": 31.96, "lon": 34.82, "region": "מרכז"},
        "ראשון לציון - מערב": {"lat": 31.97, "lon": 34.77, "region": "מרכז"},
        "אשדוד - צפון": {"lat": 31.82, "lon": 34.66, "region": "דרום"},
        "אשדוד - דרום": {"lat": 31.78, "lon": 34.64, "region": "דרום"},
        "באר שבע - צפון": {"lat": 31.27, "lon": 34.80, "region": "דרום"},
        "פתח תקווה": {"lat": 32.08, "lon": 34.88, "region": "מרכז"},
        "נתניה": {"lat": 32.32, "lon": 34.85, "region": "שרון"},
        "חולון": {"lat": 32.01, "lon": 34.77, "region": "מרכז"},
        "בני ברק": {"lat": 32.08, "lon": 34.83, "region": "מרכז"},
        "רמת גן": {"lat": 32.06, "lon": 34.82, "region": "מרכז"},
        "אשקלון - צפון": {"lat": 31.68, "lon": 34.57, "region": "דרום"},
        "אשקלון - דרום": {"lat": 31.65, "lon": 34.56, "region": "דרום"},
        "הרצליה": {"lat": 32.16, "lon": 34.83, "region": "שרון"},
        "כפר סבא": {"lat": 32.17, "lon": 34.90, "region": "שרון"},
        "רעננה": {"lat": 32.18, "lon": 34.87, "region": "שרון"},
        "מודיעין": {"lat": 31.89, "lon": 35.01, "region": "מרכז"},
        "בית שמש": {"lat": 31.74, "lon": 34.98, "region": "ירושלים"},
        "לוד": {"lat": 31.95, "lon": 34.89, "region": "מרכז"},
        "רמלה": {"lat": 31.92, "lon": 34.86, "region": "מרכז"},
        "נהריה": {"lat": 33.00, "lon": 35.09, "region": "צפון"},
        "עכו": {"lat": 32.92, "lon": 35.08, "region": "צפון"},
        "קרית שמונה": {"lat": 33.20, "lon": 35.57, "region": "צפון"},
        "אילת": {"lat": 29.55, "lon": 34.95, "region": "דרום"}
    }
    return data

yishuvim = load_yishuvim()

def get_status():
    """מדמה בדיקת סטטוס מקורות"""
    return {
        "חדשות": np.random.choice(["שגרה", "אירוע חריג"], p=[0.9, 0.1]),
        "פיקוד העורף": np.random.choice(["שגרה", "אזעקות"], p=[0.85, 0.15]),
        "גוגל טרנדס": np.random.choice(["שגרה", "זינוק בחיפושים"], p=[0.9, 0.1]),
        "טלגרם": np.random.choice(["שגרה", "דיווח ראשוני"], p=[0.8, 0.2])
    }

# כותרת האפליקציה
st.title("🛡️ מערכת חיזוי הסתברותית - כל יישובי פיקוד העורף")

# הצגת נורות סטטוס בשורה אחת
stats = get_status()
status_cols = st.columns(len(stats))
for i, (name, status) in enumerate(stats.items()):
    color = "green" if status == "שגרה" else "red"
    status_cols[i].markdown(f"**{name}**\n<span style='color:{color}'>● {status}</span>", unsafe_allow_html=True)

st.divider()

# חלק הבחירה והניתוח
col_input, col_graph = st.columns([1, 2])

with col_input:
    st.subheader("📍 הגדרות מיקום")
    
    # חיפוש חכם עם השלמה אוטומטית (Autocomplete)
    # המשתמש יכול להקליד כל שם והוא ימצא אותו מיד
    target = st.selectbox(
        "הקלד שם יישוב או שכונה:",
        options=sorted(list(yishuvim.keys())),
        help="התחל להקליד את שם היישוב (לדוגמה: תל אביב...)"
    )
    
    arena = st.selectbox("זירת איום פעילה:", ["שגרה", "מתיחות בצפון (לבנון)", "התרעה אסטרטגית (איראן)"])
    
    # חישוב הסתברות דמיונית לגרף
    times = pd.date_range(start=datetime.now(), periods=144, freq='10min')
    base_risk = 5 if arena == "שגרה" else (25 if arena == "מתיחות בצפון (לבנון)" else 60)
    risk_values = np.clip(np.random.normal(base_risk, 5, 144), 0, 100)
    
    st.metric("רמת סיכון מחושבת", f"{int(risk_values.max())}%", delta=f"{arena}")
    st.info(f"המערכת ממוקדת על: {target}")

with col_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=risk_values, fill='tozeroy', line=dict(color='#ff4b4b', width=3)))
    fig.update_layout(title=f"תחזית הסתברות ל-24 שעות - {target}", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

# המפה הנפתחת (רק בלחיצה)
with st.expander("🗾 פתח מפת מיקוד והתמצאות", expanded=False):
    sel_data = yishuvim[target]
    m_df = pd.DataFrame({'lat': [sel_data['lat']], 'lon': [sel_data['lon']]})
    st.map(m_df, zoom=13)
    st.caption(f"נ.צ ממוקד עבור אזור התרעה: {target}")
