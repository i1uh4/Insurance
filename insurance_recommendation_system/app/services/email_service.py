import os
import logging
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP
from app.services.auth_service import create_verification_token

load_dotenv()

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
BACKEND_URL = os.getenv('BACKEND_URL')


async def send_verification_email(recipient_email: str, user_id: int):
    """Send verification email to user using aiosmtplib"""
    token = create_verification_token(user_id)

    verification_link = f"{BACKEND_URL}/auth/verify/{token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your Email - Insurance Recommendation System"
    message["From"] = EMAIL_USERNAME
    message["To"] = recipient_email

    text = f"""
    Welcome to Insurance Recommendation System!

    Thank you for registering. Please verify your email address by clicking the link below:

    {verification_link}

    This link will expire in 24 hours.

    Best regards,
    Insurance Recommendation System Team
    """

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; 
                      text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to Insurance Recommendation System!</h2>
            <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
            <p><a class="button" href="{verification_link}">Verify Email</a></p>
            <p>If the button doesn't work, you can copy and paste the following link into your browser:</p>
            <p>{verification_link}</p>
            <p>This link will expire in 24 hours.</p>
            <p>Best regards,<br>Insurance Recommendation System Team</p>
        </div>
    </body>
    </html>
    """

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        logging.info(f"Attempting to send email to {recipient_email}")
        async with SMTP(
                hostname=EMAIL_HOST,
                port=EMAIL_PORT,
                use_tls=True
        ) as smtp:
            await smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            await smtp.send_message(message)

        logging.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return False
