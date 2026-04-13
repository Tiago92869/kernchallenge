import smtplib
from email.message import EmailMessage

from flask import current_app


class EmailService:
    @staticmethod
    def send_password_reset_email(*, to_email: str, temporary_password: str) -> None:
        message = EmailMessage()
        message["Subject"] = "Your password has been reset"
        message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
        message["To"] = to_email
        message.set_content(
            "Your password has been reset automatically. "
            f"Your temporary password is: {temporary_password}"
        )

        with smtplib.SMTP(
            host=current_app.config["MAIL_SERVER"],
            port=current_app.config["MAIL_PORT"],
            timeout=current_app.config["MAIL_TIMEOUT"],
        ) as smtp:
            if current_app.config["MAIL_USE_TLS"]:
                smtp.starttls()

            username = current_app.config.get("MAIL_USERNAME")
            password = current_app.config.get("MAIL_PASSWORD")
            if username and password:
                smtp.login(username, password)

            smtp.send_message(message)
