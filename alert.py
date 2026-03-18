import streamlit as st
import plotly.graph_objects as go
import requests
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

# הגדרות דף
st.set_page_config(page_title="חמ\"ל OSINT - עדכון אוטומטי", layout="wide")

# --- רכיב רענון אוטומטי (כל 15 שניות) ---
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# שימוש ב-st_autorefresh (או סימולציה שלו באמצעות streamlit native)
st.empty() # עוזר בריענון הוויזואלי
st.write(f"🔄 עדכון אחרון: {datetime.now().strftime('%H:%M:%S')}")

# --- פונקציות סריקה ממקורות שונים ---
@st.cache_data(ttl=15) # שומר בזיכרון ל-15 שניות בלבד
def fetch_headlines():
    headlines = {
        "חדשות": "אין עדכון חדש",
        "צבאי": "שגרה מבצעית",
        "תעופה": "תנועה כסדרה",
        "כללי": "סריקה פעילה"
    }
    try:
        # מקור 1: ynet
        r1 = requests.get("https://www.ynet.co.il/Integration/StoryRss2.xml", timeout=3)
        headlines["חדשות"] = ET.fromstring(r1.content).find('./channel/item/title').text
        
        # מקור 2: mako (N12)
        r2 = requests.get("https://feeds.feedburner.com/mako-news", timeout=3)
        headlines["צבאי"] = ET.fromstring(r2.content).find('./channel/item/title').text
        
        # מקור 3: וואלה (לגיוון)
        r3 = requests.get("https://rss.walla.co.il/feed/1?type=main", timeout=3)
        headlines["כללי"] = ET.fromstring(r3.content).find('./channel/item/title').text
    except:
        pass
    return headlines

# לוגיקה של סיכון וסטטיסטיקה (ללא שינוי)
def get_minute_statistic(dt):
    base = 8 + 7 * (1 - math.cos(math.pi * (dt.hour - 3) / 12)) 
    variation = 4 * math.sin(dt.minute * 0.5)
    return max(min(base + variation, 25), 3)

# נתונים
now = datetime.now()
data_headlines = fetch_headlines()
current_risk = get_minute_statistic(now)
status_color = "#00ff00" # שגרה כברירת מחדל

st.markdown("<h1 style='text-align: right;'>🛰️ חמ\"ל OSINT אינטראקטיבי - ריענון אוטומטי (15 ש')</h1>", unsafe_allow_html=True)

# --- תצוגת 35 מקורות עם כותרות שונות ---
SOURCES = {
    "12": ("חדשות 12", "חדשות"), "13": ("חדשות 13", "חדשות"), "11": ("כאן 11", "חדשות"),
    "ynet": ("ynet", "חדשות"), "אבו-עלי": ("אבו עלי", "צבאי"), "צה\"ל": ("דובר צה\"ל", "צבאי"),
    "fr24": ("FlightRadar24", "תעופה"), "adsb": ("ADSB Exch", "תעופה"), "iec": ("חברת חשמל", "כללי")
    # ... שאר המקורות יחולקו לקטגוריות אלו
}

all_keys = [
    "12", "13", "11", "14", "ynet", "פקע\"ר", "צה\"ל", "אבו-עלי", "צופר", "livemap",
    "fr24", "adsb", "iaf", "nasa", "usgs", "רוטר", "חמל", "telegram", "moked", "sela",
    "iec", "cyber", "google", "marine", "sentinel", "cnn", "bbc", "reuters", "aljazeera", "fox",
    "ayalon", "natbag", "radio", "field", "intel"
]

cols = st.columns(7)
for idx, key in enumerate(all_keys):
    name = all_keys[idx] # שם המקור מהרשימה המקורית
    # שיוך קטגוריה לצורך הכותרת
    if idx < 5: cat = "חדשות"
    elif idx < 15: cat = "צבאי"
    elif idx < 25: cat = "תעופה"
    else: cat = "כללי"
    
    with cols[idx % 7]:
        with st.popover(name, use_container_width=True):
            st.write(f"**מקור:** {name}")
            st.info(data_headlines.get(cat, "סורק..."))

st.divider()

# גרף 24 שעות
times, values = [], []
for i in range(1440):
    future_time = now + timedelta(minutes=i)
    times.append(future_time)
    values.append(get_minute_statistic(future_time))

fig = go.Figure(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=status_color, width=1.5)))
fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0))
st.plotly_chart(fig, use_container_width=True)

# לוגיקת ריענון אוטומטי (Javascript קטן שיבצע refresh)
st.components.v1.html(
    """
    <script>
    window.parent.document.querySelectorAll('[data-testid="stSidebar"]').forEach(el => el.style.display = 'none');
    setTimeout(function(){
        window.parent.location.reload();
    }, 15000);
    </script>
    """,
    height=0
)
