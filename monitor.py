import requests
import smtplib
import os
from email.message import EmailMessage

API_KEY = os.environ.get("AMBER_API_KEY")
SITE_ID = os.environ.get("AMBER_SITE_ID")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASS = os.environ.get("SENDER_PASS") 
RECIPIENT = os.environ.get("RECIPIENT_EMAIL")

def check_and_send():
    url = f"https://api.amber.com.au/v1/sites/{SITE_ID}/prices/current"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        currents = [i for i in data if i["type"] == "CurrentInterval"]
        buy = next(i["perKwh"] for i in currents if i["channelType"] == "general")
        sell = next(i["perKwh"] for i in currents if i["channelType"] == "feedIn")

        print(f"Prices - Buy: {buy}c, Sell: {sell}c")

        if buy < 0 or sell < 0:
            send_email(buy, sell)
        else:
            print("Prices are positive. No email sent.")

    except Exception as e:
        print(f"Error: {e}")

def send_email(b, s):
    msg = EmailMessage()
    msg.set_content(f"Alert: Negative Electricity Price!\n\nBuying: {b} c/kWh\nSelling: {s} c/kWh")
    msg['Subject'] = f"Amber Alert: {b}c / {s}c"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASS)
        smtp.send_message(msg)
    print("Email Sent Successfully!")

if __name__ == "__main__":
    check_and_send()
