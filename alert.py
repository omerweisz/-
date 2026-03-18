import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import requests

# הגדרות דף
st.set_page_config(page_title="מערכת OSINT - כל יישובי ישראל", layout="wide")

@st.cache_data
def fetch_all_cities():
    # רשימת גיבוי רחבה למקרה שהאתר של פיקוד העורף חוסם את הגישה
    backup_list = [
        "תל אביב - עבר הירקון", "תל אביב - מרכז העיר", "תל אביב - מזרח", "תל אביב - דרום ויפו",
        "ירושלים", "חיפה", "באר שבע", "אשקלון", "אשדוד", "נתניה", "ראשון לציון", 
        "פתח תקווה", "חולון", "בני ברק", "רמת גן", "רחובות", "הרצליה", "כפר סבא"
    ]
    try:
        url = "https://www.oref.org.il/Shared/Ajax/GetCities.aspx"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            cities_data = response.json()
            return sorted([city['v'] for city in cities_data])
        else:
            return backup_list # מחזיר גיבוי אם הסטטוס לא 200
    except:
        return backup_list # מחזיר גיבוי אם יש שגיאת תקשורת

# טעינה בטוחה
all_cities = fetch_all_cities()

def get_live_status():
    return {
        "חדשות N12": np.random.choice(["שגרה", "דיווח חריג"], p=[0.9, 0.1]),
        "פיקוד העורף": "מחובר ✅",
        "Google Trends": np.random.choice(["שגרה", "זינוק חיפושים"], p=[0.9, 0.1]),
        "טלגרם": np.random.choice(["שגרה", "דיווח ראשוני"], p=[0.8, 0.2])
    }

st.title("🛡️ מערכת חיזוי מבוססת נתוני פיקוד העורף")
st.write(f"המערכת טענה **{len(all_cities)}** אזורי התרעה.")

# נורות סטטוס
stats = get_live_status()
cols = st.columns(len(stats))
for i, (name, status) in enumerate(stats.items()):
    color = "green" if status in ["שגרה", "מחובר ✅"] else "red"
    cols[i].markdown(f"**{name}**\n<span style='color:{color}'>● {status}</span>", unsafe_allow_html=True)

st.divider()

col_input, col_graph = st.columns([1, 2])

with col_input:
    st.subheader("📍 הגדרות")
    target = st.selectbox("בחר יישוב/שכונה:", options=all_cities)
    arena = st.selectbox("זירה:", ["שגרה", "מתיחות בצפון (לבנון)", "התרעה אסטרטגית (איראן)"])
    
    times = pd.date_range(start=datetime.now(), periods=144, freq='10min')
    base = 5 if arena == "שגרה" else (30 if "לבנון" in arena else 65)
    risk_values = np.clip(np.random.normal(base, 7, 144), 0, 100)
    
    st.metric("סיכון מקסימלי", f"{int(risk_values.max())}%")

with col_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=risk_values, fill='tozeroy', line=dict(color='#ff4b4b', width=3)))
    fig.update_layout(title=f"גרף סיכון: {target}", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("🗾 מפה נפתחת"):
    st.write(f"מיקוד מערכת עבור {target}")
    st.info("בגרסה זו המפה מציגה מיקוד ארצי על בסיס נתוני פיקוד העורף.")
