# email_service.py
import os
import base64
from pathlib import Path
import requests

#
BREVO_API_KEY = os.getenv("BREVO_API_KEY")  # Define this variable in your env
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "noreply@example.com")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Password Manager")


class EmailError(Exception):
    pass

# Send an email with one or more attachments using Brevo API.
def send_backup_email(to_email: str, attachments: list[Path]) -> None:
    if not BREVO_API_KEY:
        raise EmailError("BREVO_API_KEY is not configured.")

    attachment_payload = []
    for path in attachments:
        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {path}")

        with open(path, "rb") as f:
            file_bytes = f.read()

        attachment_payload.append({
            "name": path.name,
            "content": base64.b64encode(file_bytes).decode("ascii"),
        })

    payload = {
        "sender": {
            "email": BREVO_SENDER_EMAIL,
            "name": BREVO_SENDER_NAME,
        },
        "to": [{"email": to_email}],
        "subject": "Encrypted password vault backup",
        "textContent": (
            "Here is your encrypted password vault backup.\n\n"
            "Keep this file in a safe place. The backup can only be used "
            "together with your master password.\n"
        ),
        "attachment": attachment_payload,
    }

    headers = {
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
        "accept": "application/json",
    }

    resp = requests.post("https://api.brevo.com/v3/smtp/email",
                         json=payload, headers=headers)

    if not resp.ok:
        raise EmailError(f"Brevo API error: {resp.status_code} - {resp.text}")
