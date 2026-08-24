import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional, Dict, Any

def load_env_file():
    """Automatically loads .env file from project root without external dependencies."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k:
                    os.environ[k] = v

load_env_file()

def send_application_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_paths: List[str],
    user_email: Optional[str] = None,
    app_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends application email with attachments via Gmail SMTP SSL.
    If app_password is not set in environment or arguments, runs in dry-run mode.
    """
    load_env_file()
    sender_email = user_email or os.getenv("GMAIL_USER", "adepunikhil79@gmail.com")
    # Clean app password of spaces if user pasted it with spaces (e.g. 'abcd efgh ijkl mnop' -> 'abcdefghijklmnop')
    raw_pass = app_password or os.getenv("GMAIL_APP_PASSWORD", "")
    secret_pass = raw_pass.replace(" ", "").strip()

    if not secret_pass:
        return {
            "status": "dry_run_success",
            "message": "GMAIL_APP_PASSWORD is not configured in .env. Simulated email dispatch (no actual email sent).",
            "to": to_email,
            "subject": subject,
            "attachments": [os.path.basename(p) for p in attachment_paths]
        }

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach Plain-text body
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDFs
    for file_path in attachment_paths:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)
        else:
            return {
                "status": "error",
                "message": f"Attachment file not found: {file_path}"
            }

    try:
        # Standard Gmail SMTP connection (Port 465 SSL)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=25)
        server.login(sender_email, secret_pass)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return {
            "status": "sent",
            "message": f"Real email successfully dispatched to {to_email} via Gmail SMTP.",
            "to": to_email,
            "subject": subject,
            "attachments": [os.path.basename(p) for p in attachment_paths]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gmail SMTP authentication/sending failed: {str(e)}"
        }
