import os, smtplib, ssl
from email.message import EmailMessage

def get_mail_config():
    return {
        "server": os.getenv("MAIL_SERVER", ""),
        "port": int(os.getenv("MAIL_PORT", "587")),
        "username": os.getenv("MAIL_USERNAME", ""),
        "password": os.getenv("MAIL_PASSWORD", ""),
        "use_tls": os.getenv("MAIL_USE_TLS", "true").lower() in ("1","true","yes"),
        "use_ssl": os.getenv("MAIL_USE_SSL", "false").lower() in ("1","true","yes"),
        "mail_from": os.getenv("MAIL_FROM", os.getenv("MAIL_USERNAME","no-reply@example.com")),
        "enabled": os.getenv("MAIL_ENABLED", "true").lower() in ("1","true","yes"),
    }

def send_mail(to_email: str, subject: str, body_text: str):
    cfg = get_mail_config()
    if not cfg["enabled"] or not cfg["server"] or not to_email:
        return False, "Email not configured"
    msg = EmailMessage()
    msg["From"] = cfg["mail_from"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body_text)

    context = ssl.create_default_context()
    try:
        if cfg["use_ssl"]:
            with smtplib.SMTP_SSL(cfg["server"], cfg["port"], context=context) as smtp:
                if cfg["username"]:
                    smtp.login(cfg["username"], cfg["password"])
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(cfg["server"], cfg["port"]) as smtp:
                if cfg["use_tls"]:
                    smtp.starttls(context=context)
                if cfg["username"]:
                    smtp.login(cfg["username"], cfg["password"])
                smtp.send_message(msg)
        return True, "Sent"
    except Exception as e:
        return False, str(e)
