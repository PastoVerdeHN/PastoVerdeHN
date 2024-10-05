import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def send_welcome_email(user_email, user_name):
    logger.info(f"Attempting to send welcome email to {user_email}")
    
    try:
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]
    except KeyError as e:
        logger.error(f"Email configuration not found in secrets: {e}")
        return False

    message = MIMEMultipart("related")
    message["Subject"] = "Welcome to Pasto Verde!"
    message["From"] = sender_email
    message["To"] = user_email

    text = f"""\
🌿🐾🐕🐈
Hola {user_name}, 👋
¡Bienvenido a Pasto Verde! 🌿 Gracias por registrarte en nuestra plataforma.
Estamos emocionados de tenerte con nosotros 🐾 y esperamos que disfrutes de nuestros servicios de entrega de pasto fresco para tus mascotas. 🐕🐈
Si tienes alguna pregunta, no dudes en contactarnos. 📞💬
¡Que tengas un gran día! ☀️
El equipo de Pasto Verde 🌱
🌿🐾🐕🐈
    """

    html = f"""\
    <html>
    <body>
        <p>Hola {user_name}, 👋</p>
        <p>¡Bienvenido a Pasto Verde! 🌿 Gracias por registrarte en nuestra plataforma.</p>
        <p>Estamos emocionados de tenerte con nosotros 🐾 y esperamos que disfrutes de nuestros servicios de entrega de pasto fresco para tus mascotas. 🐕🐈</p>
        <p>Si tienes alguna pregunta, no dudes en contactarnos. 📞💬</p>
        <p>¡Que tengas un gran día! ☀️</p>
        <p>El equipo de Pasto Verde 🌱</p>
        <img src="cid:image1" alt="Pasto Verde Logo" style="width:300px;height:auto;">
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/Email%20Banner.jpg"
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img_data = response.content
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        image.add_header('Content-Disposition', 'inline', filename="Email Banner.jpg")
        message.attach(image)
    except requests.RequestException as e:
        logger.error(f"Failed to download image from GitHub: {e}")

    try:
        logger.info(f"Connecting to SMTP server: smtp-mail.outlook.com")
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            server.starttls()
            logger.info(f"Logging in with sender email: {sender_email}")
            server.login(sender_email, sender_password)
            logger.info(f"Sending email to: {user_email}")
            server.sendmail(sender_email, user_email, message.as_string())
        logger.info(f"Welcome email sent successfully to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {user_email}: {e}")
        return False
