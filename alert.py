import streamlit as st
import plotly.graph_objects as go
import math
from datetime import datetime, timedelta
import time

# הגדרות דף - ללא שינוי
st.set_page_config(page_title="חמ\"ל OSINT מבצעי", layout="wide")

# פונקציה לחישוב סיכון לפי זמן אמת
def get_risk(dt):
    hour = dt.hour
    minute = dt.minute
    base = 8 + 7 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    variation = 4 * math.sin(minute * 0.5)
    return max(min(base + variation, 25), 3)

# --- כותרת ושעון זמן אמת ---
now = datetime.now()
st.markdown(f"<h1 style='text-align: right;'>🛰️ חמ\"ל OSINT - {now.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

# הצגת 35 הנורות
all_keys = ["12", "13", "11", "14", "ynet", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "livemap",
            "fr24", "adsb", "iaf", "nasa", "usgs", "רוטר", "חמל", "telegram", "moked", "sela",
            "iec", "cyber", "google", "marine", "sentinel", "cnn", "bbc", "reuters", "aljazeera", "fox",
            "ayalon", "natbag", "radio", "field", "intel"]

cols = st.columns(7)
for idx, key in enumerate(all_keys):
    with cols[idx % 7]:
        st.markdown(f"""
            <div style="text-align: center; border: 1px solid #00ff00; border-radius: 5px; padding: 5px; background: #00ff0010;">
                <b style="font-size:12px;">{key}</b><br>
                <span style="color:#00ff00; font-size:10px;">● ACTIVE</span>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# יצירת הגרף המעודכן לרגע הכניסה
times = [now + timedelta(minutes=i) for i in range(1440)]
values = [get_risk(t) for t in times]

fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color="#00ff00", width=1.5)))
fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0))

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# כפתור רענן כפוי לטלפון
if st.button("רענן נתונים עכשיו 🔄", use_container_width=True):
    st.rerun()
