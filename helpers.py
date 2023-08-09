import logging
import os
import smtplib
from contextlib import contextmanager
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException


def create_message(name: str, company: str, phone: str, email: str,
                   selected_items: list[str], project_description: str,
                   promo_code: str, discount: str, subscribe: bool) -> str:
    """
    Создает текст сообщения для электронной почты с переданными данными.

    Параметры:
    - name: Имя пользователя
    - company: Название компании пользователя
    - phone: Номер телефона пользователя
    - email: Адрес электронной почты пользователя
    - selected_items: Список выбранных позиций
    - project_description: Описание проекта
    - promo_code: Промо-код
    - discount: Скидка
    - subscribe: Подписка на рассылку

    Возвращает:
    Текст сообщения для электронной почты в виде строки.
    """

    subscribe_str = "Да" if subscribe else "Нет"
    promo_code = promo_code if promo_code is not None else "Нет"
    discount = discount if discount is not None else "Нет"
    selected_items_str = ", ".join(selected_items)

    message = f"""
    Имя: {name}
    Название компании: {company}
    Телефон: {phone}
    Почта: {email}
    Выбранные позиции: {selected_items_str}
    Описание проекта: {project_description}
    Промокод: {promo_code}
    Скидка: {discount}
    Подписка на рассылку: {subscribe_str}
    """

    return message


def send_email(smtp_host: str, smtp_username: str,
               smtp_password: str, msg: MIMEMultipart) -> bool:
    """
    Отправляет электронное письмо.

    Параметры:
    - smtp_host: SMTP-хост
    - smtp_username: Имя пользователя для SMTP-аутентификации
    - smtp_password: Пароль для SMTP-аутентификации
    - msg: Объект MIMEMultipart с данными письма

    Возвращает:
    True, если письмо отправлено успешно, иначе False.
    """

    try:
        with get_smtp_connection(smtp_host, smtp_username, smtp_password) as server:
            server.sendmail(smtp_username, smtp_username, msg.as_string())
        logging.info("Email sent successfully")
        return True
    except smtplib.SMTPException as e:
        logging.error(f"Error sending email: {e}")
        return False


@contextmanager
def get_smtp_connection(host, username, password):
    """
    Контекстный менеджер для управления соединением с SMTP-сервером.

    Параметры:
    - host: SMTP-хост
    - username: Имя пользователя для аутентификации на SMTP-сервере
    - password: Пароль для аутентификации на SMTP-сервере
    """

    server = smtplib.SMTP_SSL(host)
    server.set_debuglevel(0)
    server.login(username, password)
    yield server
    server.quit()


def create_email_message(name: str, email: str, company: str, phone: str,
                         promo_code: str, discount: str,
                         selected_items: list[str],
                         project_description: str, file_data: bytes,
                         filename: str, subscribe: bool) -> MIMEMultipart:
    """
    Создает объект MIMEMultipart для электронного письма.

    Параметры:
    - name: Имя пользователя
    - email: Адрес электронной почты пользователя
    - company: Название компании пользователя
    - phone: Номер телефона пользователя
    - promo_code: Промо-код
    - discount: Скидка
    - selected_items: Список выбранных позиций
    - project_description: Описание проекта
    - file_data: Данные файла (в виде байтов)
    - filename: Имя файла
    - subscribe: Подписка на рассылку

    Возвращает:
    Объект MIMEMultipart для электронного письма.
    """

    msg = MIMEMultipart()
    msg['From'] = os.getenv("MESSAGE_FROM")
    msg['To'] = os.getenv("MESSAGE_TO")
    msg['Subject'] = os.getenv("MESSAGE_SUBJECT")

    message = create_message(name, company, phone,
                             email, selected_items,
                             project_description,
                             promo_code, discount, subscribe)

    msg.attach(MIMEText(message, 'plain'))

    if file_data and filename:
        attachment = MIMEApplication(file_data, Name=filename)
        attachment['Content-Disposition'] = f'attachment; filename={filename}'
        msg.attach(attachment)

    return msg
