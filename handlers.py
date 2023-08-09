import os
from typing import List
from fastapi import HTTPException, Form, UploadFile, File
from helpers import create_email_message, send_email
from fastapi import FastAPI

app = FastAPI()


@app.post("/send_email")
async def send_email_endpoint(name: str = Form(...),
                              email: str = Form(...),
                              company: str = Form(...),
                              phone: str = Form(...),
                              promo_code: str = Form(None),
                              discount: str = Form(None),
                              project_description: str = Form(...),
                              file: UploadFile = File(None),
                              selected_items: List[str] = Form(...),
                              subscribe: bool = Form(None)):
    """
    Отправляет электронное письмо с данными о пользователе.

    Параметры:
    - name: Имя пользователя (обязательный)
    - email: Адрес электронной почты пользователя (обязательный)
    - company: Название компании пользователя (обязательный)
    - phone: Номер телефона пользователя (обязательный)
    - promo_code: Промо-код (необязательный)
    - discount: Скидка (необязательный)
    - project_description: Описание проекта (обязательный)
    - file: Загруженный файл (необязательный)
    - selected_items: Список выбранных позиций (обязательный)
    - subscribe: Подписка на рассылку (необязательный)
    """

    file_data = await file.read() if file else None
    filename = file.filename if file else None

    msg = create_email_message(name, email, company, phone, promo_code,
                               discount,
                               selected_items, project_description,
                               file_data, filename, subscribe)

    smtp_host = os.getenv("SMTP_HOST")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if send_email(smtp_host, smtp_username, smtp_password, msg):
        raise HTTPException(status_code=200,
                            detail="Письмо успешно отправлено!")
    else:
        raise HTTPException(status_code=400, detail="Ошибка при отправке "
                                                    "письма!")
