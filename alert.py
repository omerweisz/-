import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# הגדרות דף
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

# כותרת האפליקציה
st.title("🛡️ מערכת ניטור והתראות OSINT")
st.markdown("---")

# בחירת גזרה
sector = st.selectbox("בחר גזרת ניטור:", ["תל אביב - עבר הירקון", "גוש דן", "צפון", "דרום"])

# כפתור סנכרון
if st.button("סנכרן נתונים ידנית 🔄"):
    with st.spinner("מושך נתונים ממקורות גלויים..."):
        # הדמיית זמן טעינה
        import time
        time.sleep(1)
        
        # עדכון זמן סנכרון
        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
        
        # --- בדיקת טסט (שונה ל-True כדי שישלח הודעה תמיד) ---
        if True:
            send_telegram_message(f"🚨 התראת OSINT חמה! גזרה: {sector}")
            st.error(f"🚨 זיהוי אירוע חריג בגזרת {sector}!")
            st.toast("הודעה נשלחה לטלגרם!", icon="📲")
        else:
            st.success("הסנכרון הושלם: לא זוהו אירועים חריגים.")

# הצגת נתונים פיקטיביים לגרפים
st.subheader(f"סטטיסטיקת ניטור - {sector}")
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['חריגות', 'דיווחים', 'בוטים'])
st.line_chart(chart_data)

if 'last_sync' in st.session_state:
    st.info(f"סנכרון אחרון בוצע בשעה: {st.session_state.last_sync}")
