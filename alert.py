import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# הגדרות דף רחב ועיצוב
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
        st.error(f"שגיאה בשליחת הודעה: {e}")

# עיצוב כותרת
st.title("🛡️ מערכת ניטור והתראות OSINT")
st.markdown(f"**סטטוס מערכת:** 🔥 מבצעי | **זמן מקומי:** {datetime.now().strftime('%H:%M')}")
st.markdown("---")

# תפריט צד
st.sidebar.header("הגדרות חמ״ל")
sector = st.sidebar.selectbox("גזרת ניטור:", ["תל אביב - עבר הירקון", "גוש דן", "צפון", "דרום"])
sensitivity = st.sidebar.slider("רגישות אלגוריתם", 0, 100, 85)

# שורת מדדים (KPIs) - זה מה שהיה חסר בעיצוב!
col1, col2, col3, col4 = st.columns(4)
col1.metric("איומים פעילים", "3", "1")
col2.metric("מקורות מידע", "14", "2")
col3.metric("דירוג אמינות", "98%", "0.5%")
col4.metric("זמן תגובה", "1.2s", "-0.1s")

st.markdown("---")

# אזור תצוגה מרכזי
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader(f"ניתוח זרימת מידע - {sector}")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['חריגות', 'דיווחים', 'בוטים'])
    st.line_chart(chart_data)

with c2:
    st.subheader("פעולות מהירות")
    if st.button("سנכרן נתונים ידנית 🔄", use_container_width=True):
        with st.spinner("סורק רשתות חברתיות וערוצי טלגרם..."):
            import time
            time.sleep(1.5)
            st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
            
            # לוגיקת התראה (1%)
            if np.random.random() < 0.01:
                send_telegram_message(f"🚨 זיהוי חריג בגזרת {sector}!")
                st.error(f"🚨 זיהוי אירוע חריג בגזרת {sector}!")
                st.toast("הודעה נשלחה לטלגרם!", icon="🚨")
            else:
                st.success("לא זוהו חריגות בסריקה האחרונה.")

    if 'last_sync' in st.session_state:
        st.write(f"⏱️ סנכרון אחרון: **{st.session_state.last_sync}**")
    
    st.info("המערכת סורקת באופן אוטומטי מילות מפתח, מיקומי GPS ודיווחים גלויים.")

st.markdown("---")
st.caption("מערכת זו מיועדת למטרות למידה וניטור OSINT בלבד.")
