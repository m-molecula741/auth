from email.message import EmailMessage

from pydantic import EmailStr

from app.core.config import config


def create_register_confirmation_template(
    code: str,
    email_to: EmailStr,
):
    email = EmailMessage()
    email["Subject"] = "Подтверждение почты"
    email["From"] = config.smtp_user
    email["To"] = email_to

    email.set_content(
        f"""
        <h2>Ваш код подтверждения</h2>
        <h2>{code}</h2>
        <h2>Не сообщайте код никому!</h2>
        """,
        subtype="html",
    )
    return email


def sending_new_password_template(
    new_password: str,
    email_to: EmailStr,
):
    email = EmailMessage()
    email["Subject"] = "Новый пароль"
    email["From"] = config.smtp_user
    email["To"] = email_to

    email.set_content(
        f"""
        <h2>Ваш новый пароль</h2>
        <h2>{new_password}</h2>
        <h2>Вы его сможете изменить в настройках аккаунта</h2>
        <h2>Не сообщайте пароль никому!</h2>
        """,
        subtype="html",
    )
    return email


def sending_activate_code_template(
    code: str,
    email_to: EmailStr,
):
    email = EmailMessage()
    email["Subject"] = "Восстановление аккаунта"
    email["From"] = config.smtp_user
    email["To"] = email_to

    email.set_content(
        f"""
        <h2>Ваш код для восстановления</h2>
        <h2>{code}</h2>
        <h2>Не сообщайте код никому!</h2>
        """,
        subtype="html",
    )
    return email
