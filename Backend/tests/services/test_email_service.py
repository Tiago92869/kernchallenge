from app.services.email_service import EmailService


def test_send_password_reset_email_with_tls_and_login(app, monkeypatch):
    calls = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            calls["host"] = host
            calls["port"] = port
            calls["timeout"] = timeout
            calls["starttls_called"] = False
            calls["login_called"] = False
            calls["message"] = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            calls["starttls_called"] = True

        def login(self, username, password):
            calls["login_called"] = True
            calls["username"] = username
            calls["password"] = password

        def send_message(self, message):
            calls["message"] = message

    monkeypatch.setattr("app.services.email_service.smtplib.SMTP", FakeSMTP)

    app.config.update(
        MAIL_SERVER="smtp.test.local",
        MAIL_PORT=587,
        MAIL_TIMEOUT=15,
        MAIL_USE_TLS=True,
        MAIL_USERNAME="mailer-user",
        MAIL_PASSWORD="mailer-pass",
        MAIL_DEFAULT_SENDER="noreply@test.local",
    )

    with app.app_context():
        EmailService.send_password_reset_email(
            to_email="target@test.local",
            temporary_password="TempPass123!",
        )

    assert calls["host"] == "smtp.test.local"
    assert calls["port"] == 587
    assert calls["timeout"] == 15
    assert calls["starttls_called"] is True
    assert calls["login_called"] is True
    assert calls["username"] == "mailer-user"
    assert calls["password"] == "mailer-pass"

    message = calls["message"]
    assert message is not None
    assert message["Subject"] == "Your password has been reset"
    assert message["From"] == "noreply@test.local"
    assert message["To"] == "target@test.local"
    assert "TempPass123!" in message.get_content()


def test_send_password_reset_email_without_login(app, monkeypatch):
    calls = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            calls["starttls_called"] = False
            calls["login_called"] = False
            calls["message_sent"] = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            calls["starttls_called"] = True

        def login(self, username, password):
            calls["login_called"] = True

        def send_message(self, message):
            calls["message_sent"] = True

    monkeypatch.setattr("app.services.email_service.smtplib.SMTP", FakeSMTP)

    app.config.update(
        MAIL_SERVER="smtp.test.local",
        MAIL_PORT=1025,
        MAIL_TIMEOUT=10,
        MAIL_USE_TLS=False,
        MAIL_USERNAME=None,
        MAIL_PASSWORD=None,
        MAIL_DEFAULT_SENDER="noreply@test.local",
    )

    with app.app_context():
        EmailService.send_password_reset_email(
            to_email="target@test.local",
            temporary_password="AnotherTemp123!",
        )

    assert calls["starttls_called"] is False
    assert calls["login_called"] is False
    assert calls["message_sent"] is True
