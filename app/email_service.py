import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME")


def get_smtp_config_status() -> dict:
    """Return status of SMTP configuration (without secrets)."""
    return {
        "host": SMTP_HOST or "",
        "port": SMTP_PORT,
        "from_email": SMTP_FROM_EMAIL or "",
        "from_name": SMTP_FROM_NAME or "",
        "is_configured": bool(SMTP_HOST and SMTP_USERNAME and SMTP_PASSWORD and SMTP_FROM_EMAIL)
    }


def send_email(
    to: str,
    subject: str,
    body: str
) -> None:

    message = EmailMessage()

    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    message["To"] = to
    message["Subject"] = subject

    message.set_content(body)

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{subject}</title>
    </head>

    <body>

        <div style="
            max-width: 600px;
            margin: auto;
            padding: 30px;
            font-family: Arial, sans-serif;
        ">

            <h2>{SMTP_FROM_NAME}</h2>

            <p>{body}</p>

            <hr>

            <p style="color: gray;">
                This is an automated email.
            </p>

        </div>

    </body>
    </html>
    """

    message.add_alternative(
        html_body,
        subtype="html"
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=25) as server:

        server.starttls()

        server.login(
            SMTP_USERNAME,
            SMTP_PASSWORD
        )

        server.send_message(message)
