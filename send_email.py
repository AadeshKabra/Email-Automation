
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
from dotenv import load_dotenv



def send_email_smtp(sender_email, sender_password, recipient_email, subject, body):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

load_dotenv()

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

client = gspread.authorize(creds)

sheet = client.open("Emails").sheet1
data = sheet.get_all_records()

df = pd.DataFrame(data)
# print(df)

emails = df['Email'].tolist()
print(emails)

for i in emails:
    send_email_smtp(
        email,
        password,
        i,
        "Test Email from Python",
        "Hello, this is a test email"
    )
    time.sleep(2)
