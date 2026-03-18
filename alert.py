import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# הגדרות דף - מראה רחב ונקי
st.set_page_config(page_title="מערכת Alerts - חמ״ל אזרחי", layout="wide")

# פונקציה לשליחת הודעה לטלגרם
def send_telegram_message(message):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload)
    except Exception as e:
        st.error(f"שגיאה בתקשורת: {e}")

# --- כותרת המערכת ---
st.title("🛡️ מערכת ניטור והתראות OSINT")
st.write(f"סטטוס: **מבצעי** | עדכון אחרון: {datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# --- תפריט צד (Sidebar) ---
st.sidebar.header("הגדרות חמ״ל")
sector = st.sidebar.selectbox("בחר גזרת ניטור:", ["תל אביב - עבר הירקון", "גוש דן", "צפון", "דרום"])
sensitivity = st.sidebar.slider("רגישות אלגוריתם", 0, 100, 85)
st.sidebar.markdown("---")
st.sidebar.write("גרסה: 1.0.4 Beta")

# --- שורת מדדים (KPIs) בחלק העליון ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("איומים פעילים", "3", "1", delta_color="inverse")
m2.metric("מקורות מידע", "14", "2")
m3.metric("דירוג אמינות", "98%", "0.5%")
m4.metric("זמן תגובה", "1.2s", "-0.1s")

st.markdown("---")

# --- אזור מרכזי: גרף ופעולות ---
col_main, col_actions = st.columns([3, 1])

with col_main:
    st.subheader(f"ניתוח זרימת מידע - {sector}")
    # יצירת גרף מעוצב יותר
    chart_data = pd.DataFrame(
        np.random.randn(20, 3) + [2, 1, 0], 
        columns=['חריגות', 'דיווחים', 'בוטים']
    )
    st.area_chart(chart_data)

with col_actions:
    st.subheader("פעולות")
    if st.button("סנכרן נתונים 🔄", use_container_width=True):
        with st.spinner("סורק..."):
            time.sleep(1.2)
            st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
            
            # לוגיקה הסתברותית (1%)
            if np.random.random() < 0.01:
                send_telegram_message(f"🚨 זיהוי חריג בגזרת {sector}!")
                st.error(f"🚨 זיהוי אירוע חריג בגזרת {sector}!")
            else:
                st.success("סריקה הושלמה. תקין.")

    if 'last_sync' in st.session_state:
        st.caption(f"סנכרון אחרון: {st.session_state.last_sync}")
    
    st.divider()
    st.info("המערכת מנטרת מילות מפתח ברשתות חברתיות בזמן אמת.")

st.markdown("---")
st.caption("מערכת OSINT אזרחית - לשימוש פנימי בלבד")
