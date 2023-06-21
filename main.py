from typing import List

import uvicorn
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

app = FastAPI()


def create_email_message(name: str, email: str, company: str, phone: str,
                         promo_code: str, discount: str,
                         selected_items: list[str],
                         project_description: str, file_data: bytes,
                         filename: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = 'example@mail.ru'  # Замените на нужный адрес получателя
    msg['Subject'] = 'Новое письмо с формы'

    message = f"""
    Имя: {name}
    Почта: {email}
    Название компании: {company}
    Телефон: {phone}
    Промокод: {promo_code}
    Скидка: {discount}
    Выбранные позиции: {selected_items}
    Описание проекта: {project_description}
    """
    print(message)
    msg.attach(MIMEText(message, 'plain'))

    attachment = MIMEApplication(file_data, Name=filename)
    attachment['Content-Disposition'] = f'attachment; filename={filename}'
    msg.attach(attachment)

    return msg


def send_email(smtp_host: str, smtp_port: int, smtp_username: str,
               smtp_password: str, msg: MIMEMultipart) -> bool:
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True
    except smtplib.SMTPException:
        return False


@app.post("/send_email")
async def send_email_endpoint(name: str, email: str, company: str, phone: str,
                              promo_code: str, discount: str,
                              project_description: str,
                              file: UploadFile = File(...),
                              selected_items: List[str] = Query(...)):
    smtp_host = 'smtp.mail.ru'
    smtp_port = 587
    smtp_username = 'your_username'  # Замените на ваше имя пользователя SMTP
    smtp_password = 'your_password'  # Замените на ваш пароль SMTP

    msg = create_email_message(name, email, company, phone, promo_code,
                               discount,
                               selected_items, project_description,
                               await file.read(), file.filename)

    if send_email(smtp_host, smtp_port, smtp_username, smtp_password, msg):
        return JSONResponse(content={"message": "Письмо успешно отправлено!"})
    else:
        return JSONResponse(content={"message": "Ошибка при отправке письма"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
