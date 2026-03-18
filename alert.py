import st
import plotly.graph_objects as go
import math
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# הגדרות דף
st.set_page_config(page_title="חמ\"ל עבר הירקון - LIVE", layout="wide")

# CSS להעלמת הלבן בגרף ובמובייל
st.markdown("""
    <style>
    .stPlotlyChart { background-color: transparent !important; }
    div[data-testid="stPlotlyChart"] { background-color: transparent !important; }
    .main { background-color: #0a0a0a; }
    </style>
""", unsafe_allow_html=True)

def check_multi_source_osint():
    sources = [
        "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "https://rss.walla.co.il/feed/1?type=main",
        "https://www.israelhayom.co.il/rss.xml",
        "https://m.maariv.co.il/Rss/RssFeeds0"
    ]
    threat_words = ["טילים", "כטב\"מ", "יירוט", "נפילה", "אזעקה", "פיצוץ", "חדירה", "ירי"]
    local_targets = ["עבר הירקון", "רמת אביב", "צהלה", "נאות אפקה", "תל אביב", "גלילות", "פי גלילות", "הדר יוסף"]
    end_words = ["חזרה לשגרה", "הוסרה ההתרעה", "סיום האירוע", "האירוע הסתיים", "ניתן לצאת", "לצאת מהממד"]
    
    combined_headlines = []
    for url in sources:
        try:
            response = requests.get(url, timeout=2)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                if title: combined_headlines.append(title)
        except: continue

    # בדיקת הרגעה (✅)
    for title in combined_headlines[:10]:
        if any(word in title for word in end_words):
            return False, title
    
    # בדיקת איום (⚠️)
    for title in combined_headlines[:25]:
        if any(word in title for word in threat_words) and any(loc in title for loc in local_targets):
            return True, title
        if "איראן" in title:
            return True, title
            
    return False, ""

def get_risk(dt, emergency_active):
    if emergency_active: return 99.8
    hour = dt.hour
    base = 10 + 5 * (1 - math.cos(math.pi * (hour - 3) / 12)) 
    return max(min(base, 100), 4.2)

@st.fragment(run_every=30)
def auto_refresh_hamaal():
    now = datetime.utcnow() + timedelta(hours=2) 
    
    # ניהול זיכרון חכם עם טיימר התיישנות
    if 'alert_start_time' not in st.session_state:
        st.session_state.alert_start_time = None
    if 'current_active_alert' not in st.session_state:
        st.session_state.current_active_alert = ""

    is_emergency, raw_text = check_multi_source_osint()
    
    # אם הטקסט השתנה, מאפסים טיימר
    if raw_text != st.session_state.current_active_alert:
        st.session_state.current_active_alert = raw_text
        st.session_state.alert_start_time = now if raw_text else None

    # בדיקת התיישנות: אם עברו 10 דקות, מנקים את ההודעה
    display_text = raw_text
    if st.session_state.alert_start_time:
        minutes_passed = (now - st.session_state.alert_start_time).total_seconds() / 60
        if minutes_passed >= 10:
            display_text = ""
            is_emergency = False # מחזיר לשגרה גם אם המבזק עדיין שם

    current_val = get_risk(now, is_emergency)
    color = "#ff1a1a" if (current_val > 35 and is_emergency) else "#00ff00"
    
    # תצוגה
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {color}44; border-radius: 10px; background: #000;">
            <p style="color: #666; font-size: 10px; margin: 0; letter-spacing: 2px;">SECTOR: EVER HAYARKON</p>
            <h1 style="color: {color}; font-size: 65px; margin: 5px 0; font-family: monospace;">{current_val:.1f}%</h1>
            <p style="color: {color}aa; font-size: 12px; font-family: monospace;">🕒 {now.strftime('%H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)

    if display_text:
        is_safe_msg = any(word in display_text for word in ["סיום", "שגרה", "לצאת", "הסתיים"])
        box_color = "#002200" if is_safe_msg else "#220000"
        prefix = "✅ " if is_safe_msg else "⚠️ "
        st.markdown(f"""<div style="background: {box_color}; color: white; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 13px; font-weight: bold; border: 1px solid {color}; text-align: center;">{prefix}{display_text}</div>""", unsafe_allow_html=True)

    # גרף
    times = [now + timedelta(minutes=i) for i in range(1440)]
    values = [get_risk(t, is_emergency) for t in times]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=values, fill='tozeroy', line=dict(color=color, width=2), fillcolor=f"rgba({255 if color=='#ff1a1a' else 0}, {26 if color=='#ff1a1a' else 255}, 0, 0.1)"))
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=150, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False, range=[0, 110]), showlegend=False, dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # נורות
    cols = st.columns(7)
    for idx, key in enumerate(["YNET", "WALLA", "N12", "HAYOM", "MAARIV", "צה\"ל", "צופר", "TG", "ROTER", "MOKED", "SIRI", "MAPS", "FR24", "NASA", "CNN", "BBC", "FOX", "IAF", "IEC", "GOOGLE", "AYALON"]):
        with cols[idx % 7]:
            st.markdown(f"""<div style="text-align: center;"><div style="width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block;"></div><br><span style="font-size:7px; color: #444;">{key}</span></div>""", unsafe_allow_html=True)

auto_refresh_hamaal()
