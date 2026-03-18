import streamlit as st
import plotly.graph_objects as go
import math
from datetime import datetime, timedelta

# הגדרות דף - מותאם לנייד
st.set_page_config(page_title="חמ\"ל OSINT - Risk 35", layout="wide")

def get_risk(dt):
    hour = dt.hour
    minute = dt.minute
    # נוסחה לחישוב סיכון (0-40)
    base = 8 + 7 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    variation = 4 * math.sin(minute * 0.5)
    return max(min(base + variation, 40), 3)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    # תיקון זמן ישראל (UTC+2)
    now = datetime.utcnow() + timedelta(hours=2) 
    current_val = get_risk(now)
    
    # --- שינוי צבע רק ב-35 אחוז ומעלה ---
    color = "#ff4b4b" if current_val >= 35 else "#00ff00"
    bg_color = "#440000" if current_val >= 35 else "#1e1e1e"
    
    st.markdown(f"""
        <div style="text-align: center; background-color: {bg_color}; padding: 20px; border-radius: 10px; border: 2px solid {color}; margin-bottom: 20px;">
            <p style="color: gray; margin: 0; font-size: 14px;">מדד סיכון נוכחי</p>
            <h1 style="color: {color}; font-size: 60px; margin: 0;">{current_val:.1f}%</h1>
            <p style="color: {color}; margin: 0; font-size: 12px;">סנכרון אחרון: {now.strftime('%H:%M:%S')}</p>
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
                <div style="text-align: center; border: 1px solid #444; border-radius: 3px; background: #222; margin-bottom: 3px;">
                    <span style="color:{color}; font-size:8px;">●</span> <b style="font-size:9px; color: white;">{key}</b>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # גרף ללא זום עם טווח עד 40
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t) for t in times]
    fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=2)))
    
    fig.update_layout(
        template="plotly_dark", height=250, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(tickformat='%H:%M', nticks=6, fixedrange=True),
        yaxis=dict(fixedrange=True, range=[0, 40]), # הגדלתי את הטווח ל-40
        dragmode=False
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

auto_refresh_hamaal()
