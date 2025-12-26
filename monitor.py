import requests
import smtplib
import os
from email.message import EmailMessage

API_KEY = os.environ.get("AMBER_API_KEY")
SITE_ID = os.environ.get("AMBER_SITE_ID")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASS = os.environ.get("SENDER_PASS")
RECIPIENT = os.environ.get("RECIPIENT_EMAIL")

STATUS_FILE = "alert_status.txt"

def get_last_status():
    if not os.path.exists(STATUS_FILE):
        return "clear"
    with open(STATUS_FILE, "r") as f:
        return f.read().strip()

def set_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(status)

def check_and_send():
    url = f"https://api.amber.com.au/v1/sites/{SITE_ID}/prices/current"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        currents = [i for i in data if i["type"] == "CurrentInterval"]
        
        buy = next(i["perKwh"] for i in currents if i["channelType"] == "general")
        sell = next(i["perKwh"] for i in currents if i["channelType"] == "feedIn")
        
        last_status = get_last_status()
        print(f"Current Buy: {buy}c | Last Status: {last_status}")

        if (buy < 0 or sell < 0):
            if last_status == "clear":
                send_email(buy, sell)
                set_status("sent")
            else:
                print("Price still negative, but alert already sent. Skipping...")
        else:
            if last_status == "sent":
                print("Price back to positive. Resetting alert status.")
            set_status("clear")

    except Exception as e:
        print(f"Error: {e}")

def send_email(b, s):
    msg = EmailMessage()
    msg.set_content(f"Alert: Negative Price Detected!\n\nBuy: {b}c\nSell: {s}c")
    msg['Subject'] = f"Amber Alert: {b}c"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASS)
        smtp.send_message(msg)
    print("Email Sent!")

if __name__ == "__main__":
    check_and_send()
