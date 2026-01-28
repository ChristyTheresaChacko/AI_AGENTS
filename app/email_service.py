import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str) -> Optional[bool]:
    """Send email using configured backend.

    Supported backends:
      - SMTP (default if SMTP_... env vars present)
      - console (if MAIL_BACKEND=console)

    If SMTP configuration is missing and MAIL_BACKEND is not 'smtp', the
    function falls back to writing the email to `sent_emails.log` and logs
    the action. This avoids hard failures in development.
    """
    mail_backend = os.getenv("MAIL_BACKEND", "auto").lower()

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM_EMAIL")

    use_smtp = False
    if mail_backend == "smtp":
        use_smtp = True
    elif mail_backend == "console":
        use_smtp = False
    else:
        # auto: use SMTP only if all required vars present
        use_smtp = all([smtp_server, smtp_user, smtp_pass, from_email])

    if use_smtp:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        try:
            server.starttls()
            # If credentials are provided, try to login (some servers allow anonymous send)
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            logger.info("Email sent to %s via SMTP", to_email)
            return True
        except Exception:
            logger.exception("SMTP send failed, falling back to file log for %s", to_email)
            # Fallback to file so the message is not lost in development
            log_msg = f"---\nTo: {to_email}\nSubject: {subject}\n\n{body}\n---\n"
            try:
                with open("sent_emails.log", "a", encoding="utf-8") as fh:
                    fh.write(log_msg)
            except Exception:
                logger.exception("Failed to write sent_emails.log during SMTP fallback")
            finally:
                try:
                    server.quit()
                except Exception:
                    pass
            return False
    else:
        # Console / file fallback for development.
        log_msg = f"---\nTo: {to_email}\nSubject: {subject}\n\n{body}\n---\n"
        logger.info("MAIL_BACKEND fallback: writing email to sent_emails.log for %s", to_email)
        try:
            with open("sent_emails.log", "a", encoding="utf-8") as fh:
                fh.write(log_msg)
        except Exception:
            logger.exception("Failed to write sent_emails.log")
        return False
