import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.example.com"  # Replace with your SMTP server
        self.smtp_port = 587
        self.smtp_user = "user@example.com"  # Replace with your email
        self.smtp_password = "password"  # Replace with your password

    def send_email(self, to_email: str, subject: str, message: str):
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = to_email

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)