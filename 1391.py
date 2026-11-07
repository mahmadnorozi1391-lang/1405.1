from flask import Flask
import imaplib
import email
import requests
import threading
import time

app = Flask(__name__)

token = "[REDACTED]"
gmail = "gmail.1.1405@gmail.com"
password = "[REDACTED]"
target_channels = ["5671800143"]

BALE_API_URL = f"https://tapi.bale.ai/bot{token}/sendMessage"

def fetch_and_send():
    """تابع پس‌زمینه برای بررسی ایمیل و ارسال به بله"""
    while True:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(gmail, password)
            mail.select("inbox")

            status, messages = mail.search(None, 'UNSEEN')
            if status == 'OK':
                for num in messages[0].split():
                    status, data = mail.fetch(num, '(RFC822)')
                    if status == 'OK':
                        msg = email.message_from_bytes(data[0][1])
                        sender = msg['from']
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()
                        
                        text = f"پیام از طرف ایمیل: {sender}\nپیام:\n{body}"
                        for channel_id in target_channels:
                            requests.post(BALE_API_URL, json={"chat_id": channel_id, "text": text})

            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Error: {e}")
        
        # هر ۶۰ ثانیه یک بار ایمیل‌ها را چک می‌کند
        time.sleep(60)

@app.route("/")
def home():
    return "سایت ربات جیمیل به بله فعال است!"

if __name__ == "__main__":
    # اجرای چک کردن ایمیل در یک پردازش جداگانه (Thread) تا سایت بلاک نشود
    t = threading.Thread(target=fetch_and_send)
    t.daemon = True
    t.start()
    
    # اجرای سرور وب Flask
    app.run(host="0.0.0.0", port=5000)
