import smtplib
from email.message import EmailMessage
import os
# Step 6: Send myself a direct link to streamit app

#Sender and recepient
to_email = "gaston.aveline@gmail.com"
from_email = "alerts@silkworm.cloud"
#Link for streamlit
streamlit_url = "https://jobrecommendationservice-4stmmtham4zdobmxptb6f3.streamlit.app/"

# SendGrid SMTP credentials
smtp_server = 'smtp.sendgrid.net'
smtp_port = 587
username = 'apikey'  # Literally the word 'apikey'
api_key  = os.getenv("SENDGRID_API_KEY")

def send_email(N):
    msg = EmailMessage()
    msg["Subject"] = f"[Jobs Update] {N} new jobs ready"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(f"""
    Hi,

    The job list has just been updated with {N} offers.
    Click below to rate them:

    🔗 {streamlit_url}

    –––
    Your data pipeline
    """)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(username, api_key)
        smtp.send_message(msg)