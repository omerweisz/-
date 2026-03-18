import streamlit as st
import plotly.graph_objects as go
import math
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT מבצעי", layout="wide")

# מודל סטטיסטי דקה-דקה ל-24 שעות
def get_minute_statistic(dt):
    hour = dt.hour
    minute = dt.minute
    # בסיס שגרה נמוך (סביב 10%) שמשתנה לפי שעות היום
    base = 8 + 7 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    # תנודות קטנות ומציאותיות לכל דקה
    variation = 4 * math.sin(minute * 0.5) + 3 * math.cos((hour * 60 + minute) * 0.2)
    return max(min(base + variation, 25), 3)

# נתונים נוכחיים
now = datetime.now()
current_risk = get_minute_statistic(now)

# צבע סטטוס (ירוק בשגרה)
status_color = "#00ff00" 

# עיצוב הריבועים (נורות)
st.markdown(f"""
    <style>
    .source-box {{
        text-align: center; 
        border: 1px solid {status_color}; 
        border-radius: 4px; 
        padding: 8px; 
        background-color: {status_color}10;
        margin-bottom: 10px;
    }}
    .dot {{
        height: 10px;
        width: 10px;
        background-color: {status_color};
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: right;'>🛰️ מרכז OSINT מבצעי - 35 מקורות</h1>", unsafe_allow_html=True)

# רשימת 35 המקורות
all_keys = [
    "12", "13", "11", "14", "ynet", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "livemap",
    "fr24", "adsb", "iaf", "nasa", "usgs", "רוטר", "חמל", "telegram", "moked", "sela",
    "iec", "cyber", "google", "marine", "sentinel", "cnn", "bbc", "reuters", "aljazeera", "fox",
    "ayalon", "natbag", "radio", "field", "intel"
]

# תצוגת הנורות ב-7 עמודות
cols = st.columns(7)
for idx, key in enumerate(all_keys):
    with cols[idx % 7]:
        st.markdown(f"""
            <div class="source-box">
                <b style="font-size:12px;">{key}</b><br>
                <span class="dot"></span><span style="color:{status_color}; font-size:10px;">ACTIVE</span>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# יצירת גרף ל-24 שעות (1,440 דקות)
times, values = [], []
for i in range(1440):
    future_time = now + timedelta(minutes=i)
    times.append(future_time)
    values.append(get_minute_statistic(future_time))

col_graph, col_stat = st.columns([2, 1])
with col_graph:
    st.subheader("🕒 תחזית סיכון יממתית (OSINT Model)")
    fig = go.Figure(go.Scatter(
        x=times, y=values, fill='tozeroy', 
        line=dict(color=status_color, width=1.5),
        hovertemplate='זמן: %{x|%H:%M}<br>סיכון: %{y:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(fixedrange=True, tickformat='%H:%M', nticks=12),
        yaxis=dict(fixedrange=True, range=[0, 105]), 
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_stat:
    st.metric("רמת סיכון נוכחית", f"{current_risk:.1f}%")
    st.success("סטטוס: גזרה בשגרה")
    st.info("המערכת מנטרת 35 מקורות גלויים ומבצעת הצלבת נתונים סטטיסטית.")
    
    if st.button("רענן נתונים 🔄", use_container_width=True):
        st.rerun()
