import smtplib
import logging
from email.mime.text import MIMEText
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_enabled = settings.ENABLE_EMAIL_NOTIFICATIONS

    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return (
            self.email_enabled and
            bool(self.smtp_server) and
            bool(self.smtp_user) and
            bool(self.smtp_password) and
            self.smtp_server != "smtp.example.com"  # Avoid placeholder values
        )

    def send_email(self, to_email: str, subject: str, message: str):
        """Send email if properly configured, otherwise log the attempt."""
        logger.info(f"Email send attempt initiated for {to_email}")
        
        if not self.is_configured():
            logger.warning(f"Email service not configured or disabled. Would have sent email to {to_email} with subject: {subject}")
            return False

        logger.info(f"Email service is configured. SMTP Server: {self.smtp_server}, Port: {self.smtp_port}")
        
        try:
            logger.info(f"Creating email message for {to_email}")
            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to_email

            logger.info(f"Attempting SMTP connection to {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.info(f"SMTP connection established, starting TLS")
                server.starttls()
                logger.info(f"TLS started, attempting login with user: {self.smtp_user}")
                server.login(self.smtp_user, self.smtp_password)
                logger.info(f"SMTP login successful, sending message")
                server.send_message(msg)
                logger.info(f"Message sent successfully via SMTP")
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            logger.error(f"Email error type: {type(e).__name__}")
            logger.error(f"Email error details: {repr(e)}")
            return False