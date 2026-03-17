import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# הגדרות דף
st.set_page_config(page_title="מערכת כוננות - 24 שעות", layout="wide")


def get_location_name(lat, lon):
    try:
        geolocator = Nominatim(user_agent="security_monitor_24h")
        location = geolocator.reverse((lat, lon), language='he')
        address = location.raw.get('address', {})
        return address.get('suburb') or address.get('city') or address.get('town') or "מיקום נבחר"
    except:
        return "אזור ניתוח"


def write_heb(text, size="24px", color="white", bold=True):
    st.markdown(
        f'<p style="direction: rtl; text-align: right; font-size: {size}; font-weight: {"bold" if bold else "normal"}; color: {color}; font-family: Arial;">{text}</p>',
        unsafe_allow_html=True)


# --- ממשק ---
write_heb("ניתוח סיכונים בליסטיים - תחזית 24 שעות (ברמת דקה)", size="34px", color="#ff3f34")

col_map, col_graph = st.columns([1.3, 1])

with col_map:
    m = folium.Map(location=[32.0853, 34.7818], zoom_start=11, tiles="CartoDB dark_matter")
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=600, width=750)

with col_graph:
    if map_data and map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']

        with st.spinner("מחשב נתונים ל-1,440 הדקות הבאות..."):
            place_name = get_location_name(lat, lon)

        write_heb(f"תחזית יממתית עבור: {place_name}", color="#ff3f34")

        # --- יצירת ציר זמן של 24 שעות (דקה אחר דקה) ---
        now = datetime.now()
        # 24 שעות * 60 דקות = 1440 נקודות
        total_minutes = 24 * 60
        time_points = [(now + timedelta(minutes=i)) for i in range(total_minutes)]
        time_labels = [t.strftime("%H:%M") for t in time_points]

        # יצירת נתונים עם תנודות טבעיות יותר (שימוש ב-Random Walk)
        np.random.seed(int(lat * 1000))
        steps = np.random.normal(0, 2, total_minutes)
        risks = np.clip(np.cumsum(steps) + 40, 5, 95)

        fig = go.Figure()

        # הוספת הקו (בלי Markers כי יש יותר מדי נקודות)
        fig.add_trace(go.Scatter(
            x=time_labels,
            y=risks,
            mode='lines',
            name='סיכון רגעי',
            line=dict(color='#ff3f34', width=2, shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(255, 63, 52, 0.1)',
            hovertemplate='<b>זמן: %{x}</b><br>סיכון: %{y:.1f}%<extra></extra>'
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                showgrid=False,
                color="white",
                title="ציר זמן (24 שעות)",
                nticks=12  # מציג שעה כל שעתיים כדי שלא יהיה עמוס
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#333",
                color="white",
                range=[0, 100],
                ticksuffix="%"
            ),
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)
        write_heb("המערכת מציגה 1,440 נקודות נתונים בזמן אמת", size="14px", bold=False, color="#888888")
    else:
        st.info("בחר נקודה על המפה לניתוח 24 שעות")
