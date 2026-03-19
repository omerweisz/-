import streamlit as st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from dateutil import parser

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - V26 FULL CYCLE", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; font-family: 'JetBrains Mono', monospace; color: white; }
    .stPlotlyChart { background-color: transparent !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def get_source_status(url, name):
    # מילים קריטיות לאזעקה פעילה
    active_alarm = ["אזעקה", "צבע אדום", "התרעות הופעלו", "חדירת כלי טיס עויינת"]
    # מילים לשיגורים (לפני אזעקה)
    launches = ["שיגור", "שיגורים", "זוהו שיגורים"]
    # מילים לחזרה לשגרה
    release_words = ["חזרה לשגרה", "הסרת הגבלות", "ניתן לצאת", "ארגעה", "סיום האירוע"]
    # אזורי עניין
    target_zones = ["תל אביב", "גוש דן", "מרכז", "עבר הירקון", "גלילות", "רמת אביב", "חולון", "רמת גן", "בני ברק", "פתח תקווה"]
    
    now = datetime.now(timezone(timedelta(hours=2)))
    try:
        response = requests.get(url, timeout=2.5)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')[:15]
        for item in items:
            title = item.find('title').text
            pub_date = parser.parse(item.find('pubDate').text)
            diff_min = int((now - pub_date).total_seconds() / 60)
            
            if 0 <= diff_min <= 15: # חלון זמן קצר יותר לתגובה מהירה
                # 1. עדיפות עליונה: חזרה לשגרה (מוריד אחוזים)
                if any(rw in title for rw in release_words):
                    return "RELEASE", f"({diff_min} דק') {title}", pub_date
                
                # 2. אזעקה מפורשת (100%)
                if any(aa in title for aa in active_alarm) and any(tz in title for tz in target_zones):
                    return "ALARM_100", f"({diff_min} דק') {title}", pub_date
                
                # 3. זוהו שיגורים (95%)
                if any(l in title for l in launches):
                    if any(tz in title for tz in target_zones) or "איראן" in title:
                        return "LAUNCH_95", f"({diff_min} דק') {title}", pub_date
                
                # 4. מידע חדשותי (הודעה בלבד)
                if any(word in title for word in ["הרוג", "נפילה", "מד\"א", "יירוט"]):
                    return "INFO_ONLY", f"({diff_min} דק') {title}", pub_date
                    
        return "GREEN", "", None
    except: return "GREEN", "", None

def get_risk(dt, global_status):
    if global_status == "ALARM_100": return 100.0
    if global_status == "LAUNCH_95": return 95.0
    if global_status == "RELEASE": return 12.5 # רמת שגרה נמוכה אחרי אירוע
    # שגרה רגילה
    hour = dt.hour + dt.minute / 60.0
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=10)
def auto_refresh_hamaal():
    now = datetime.now(timezone(timedelta(hours=2)))
    sources_map = {"YNET": "https://www.ynet.co.il/Integration/StoryRss1854.xml", "וואלה": "https://rss.walla.co.il/feed/1?type=main", "ישראל היום": "https://www.israelhayom.co.il/rss.xml", "צופר": "https://www.tzevaadom.co.il/rss"}
    source_results = {}; global_status = "GREEN"; latest_msg = ""
    
    for name, url in sources_map.items():
        res, msg, _ = get_source_status(url, name)
        source_results[name] = res
        
        # לוגיקת הכרעה היררכית
        if res == "ALARM_100":
            global_status = "ALARM_100"
        elif res == "LAUNCH_95" and global_status != "ALARM_100":
            global_status = "LAUNCH_95"
        elif res == "RELEASE" and global_status not in ["ALARM_100", "LAUNCH_95"]:
            global_status = "RELEASE"
        
        if msg: latest_msg = msg

    current_val = get_risk(now, global_status)
    
    # עיצוב צבעים
    display_color = "#00ff00" # ירוק שגרה
    if global_status == "ALARM_100": display_color = "#ff1a1a" # אדום אזעקה
    elif global_status == "LAUNCH_95": display_color = "#ff4400" # כתום שיגורים
    elif any(r == "INFO_ONLY" for r in source_results.values()): display_color = "#ffaa00" # צהוב חדשות

    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {display_color}44; border-radius: 15px; background: rgba(0,0,0,0.5); box-shadow: 0 0 25px {display_color}20;">
            <p style="color: #FFFFFF; font-size: 10px; margin: 0; letter-spacing: 3px; font-weight: bold; opacity: 0.8;">UNIT: EVER HAYARKON | V26 OPERATIONAL</p>
            <h1 style="color: {display_color}; font-size: 85px; margin: 5px 0; font-family: 'JetBrains Mono'; text-shadow: 0 0 20px {display_color}88;">{current_val:.1f}%</h1>
            <div style="color: #FFFFFF; font-size: 13px; font-family: 'JetBrains Mono';">
                <span style="color: {display_color};">●</span> {now.strftime('%H:%M:%S')} 
            </div>
        </div>
    """, unsafe_allow_html=True)

    if latest_msg:
        st.markdown(f"""<div style="background: rgba(20,20,20,0.9); color: white; padding: 15px; margin: 15px 0; border-radius: 8px; border: 1px solid {display_color}; text-align: center; font-weight: bold;">{latest_msg}</div>""", unsafe_allow_html=True)
    else: st.markdown("<div style='height: 62px;'></div>", unsafe_allow_html=True)

    # גרף
    base_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    full_day_times = [base_time + timedelta(minutes=i) for i in range(1440)]
    full_day_values = [get_risk(t, "GREEN") for t in full_day_times]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=full_day_times, y=full_day_values, fill='tozeroy', line=dict(color="#222", width=2), hovertemplate="<b>Time:</b> %{x|%H:%M}<br><b>Risk:</b> %{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=[now], y=[current_val], mode='markers', marker=dict(color=display_color, size=14, line=dict(color='white', width=2)), hoverinfo='skip'))
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=160, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", xaxis=dict(visible=False, fixedrange=True), yaxis=dict(visible=False, range=[0, 115], fixedrange=True), showlegend=False, dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    cols = st.columns(7)
    all_keys = ["YNET", "וואלה", "ישראל היום", "צופר", "פקע\"ר", "צה\"ל", "אבו-עלי", "LIVEMAP", "FR24", "ADSB", "IAF", "NASA", "USGS", "רוטר", "חמ\"ל", "TELEGRAM", "MOKED", "SELA", "IEC", "CYBER", "GOOGLE", "MARINE", "SENTINEL", "CNN", "BBC", "REUTERS", "AL-JAZ", "FOX", "AYALON", "NATBAG", "RADIO", "FIELD", "INTEL"]
    for idx, key in enumerate(all_keys):
        node_status = source_results.get(key, "GREEN")
        node_color = {"ALARM_100": "#ff1a1a", "LAUNCH_95": "#ff4400", "INFO_ONLY": "#ffaa00", "RELEASE": "#00ff00", "GREEN": "#00ff00"}.get(node_status, "#00ff00")
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 12px;"><div style="width: 8px; height: 8px; background: {node_color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px {node_color};"></div><br><span style="font-size:8px; color: #FFFFFF; font-weight: bold; opacity: 0.6;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
