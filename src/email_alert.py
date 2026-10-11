import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_email_alert(subject, body):
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    # Check environment variables
    if not sender_email or not app_password or not receiver_email:
        print("Email error: Missing email configuration in .env")
        return False

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, timeout=20
        ) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(message)

        print("Email submitted successfully to the SMTP server.")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Email error: Gmail authentication failed.")
        print("Check EMAIL_ADDRESS and your Gmail App Password.")
        return False

    except (smtplib.SMTPException, OSError) as error:
        print(f"Email sending failed: {type(error).__name__}: {error}")
        return False


