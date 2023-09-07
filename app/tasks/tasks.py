from app.tasks.celery_app import celery_app
from pydantic import EmailStr
from app.tasks.email_templates import (
    create_register_confirmation_template,
    sending_new_password_template,
    sending_activate_code_template,
)
import smtplib
from app.core.config import config


@celery_app.task
def send_register_confirmation_email(code: str, email_to: EmailStr):
    message_content = create_register_confirmation_template(code, email_to)
    with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
        server.login(config.smtp_user, config.smtp_pass)
        server.send_message(message_content)


@celery_app.task
def send_new_password_by_email(new_password: str, email_to: EmailStr):
    message_content = sending_new_password_template(new_password, email_to)
    with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
        server.login(config.smtp_user, config.smtp_pass)
        server.send_message(message_content)


@celery_app.task
def send_activate_code_by_email(code: str, email_to: EmailStr):
    message_content = sending_activate_code_template(code, email_to)
    with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
        server.login(config.smtp_user, config.smtp_pass)
        server.send_message(message_content)
