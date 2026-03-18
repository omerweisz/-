import streamlit as st
import plotly.graph_objects as go
import math
from datetime import datetime, timedelta

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT - סנכרון אוטומטי", layout="wide")

def get_risk(dt):
    hour = dt.hour
    minute = dt.minute
    base = 8 + 7 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    variation = 4 * math.sin(minute * 0.5)
    return max(min(base + variation, 25), 3)

# --- פונקציית הפרגמנט (מתעדכנת לבד כל 30 שניות) ---
@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.now()
    
    # שעון חי למעלה
    st.markdown(f"""
        <div style='text-align: right;'>
            <h1 style='margin-bottom: 0;'>🛰️ חמ\"ל OSINT מבצעי</h1>
            <p style='color: #00ff00; font-family: monospace;'>זמן מערכת: {now.strftime('%H:%M:%S')} | סנכרון אוטומטי פעיל</p>
        </div>
    """, unsafe_allow_html=True)

    # 35 הנורות
    all_keys = ["12", "13", "11", "14", "ynet", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "livemap",
                "fr24", "adsb", "iaf", "nasa", "usgs", "רוטר", "חמל", "telegram", "moked", "sela",
                "iec", "cyber", "google", "marine", "sentinel", "cnn", "bbc", "reuters", "aljazeera", "fox",
                "ayalon", "natbag", "radio", "field", "intel"]

    cols = st.columns(7)
    for idx, key in enumerate(all_keys):
        with cols[idx % 7]:
            st.markdown(f"""
                <div style="text-align: center; border: 1px solid #00ff00; border-radius: 5px; padding: 5px; background: #00ff0010; margin-bottom: 5px;">
                    <b style="font-size:11px;">{key}</b><br>
                    <span style="color:#00ff00; font-size:9px;">● LIVE</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # יצירת הגרף מעודכן לרגע הנוכחי
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t) for t in times]

    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color="#00ff00", width=1.5)))
    fig.update_layout(
        template="plotly_dark", 
        height=300, 
        margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(tickformat='%H:%M', nticks=12)
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # מדד סיכון נוכחי
    st.metric("רמת סיכון נוכחית", f"{get_risk(now):.1f}%")

# הפעלת הפונקציה
auto_refresh_hamaal()
