import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import streamlit as st
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def send_welcome_email(user_email, user_name):
    logging.debug("Starting send_welcome_email function")
    
    try:
        sender_email = st.secrets["email"]["sender_email"]
        logging.debug(f"Retrieved sender_email: {sender_email}")
    except Exception as e:
        logging.error(f"Error retrieving sender_email: {str(e)}")
        return

    try:
        sender_password = st.secrets["email"]["sender_password"]
        logging.debug("Retrieved sender_password (not logging the actual password)")
    except Exception as e:
        logging.error(f"Error retrieving sender_password: {str(e)}")
        return

    message = MIMEMultipart("related")  # Use "related" to embed images
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

    # Download the image from GitHub
    image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/Email%20Banner.jpg"
    logging.debug(f"Attempting to download image from: {image_url}")
    response = requests.get(image_url)
    if response.status_code == 200:
        img_data = response.content
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')  # Ensure this matches the HTML
        image.add_header('Content-Disposition', 'inline', filename="Email Banner.jpg")
        message.attach(image)
        logging.debug("Image successfully downloaded and attached")
    else:
        logging.error(f"Failed to download image from GitHub. Status code: {response.status_code}")

    try:
        logging.debug("Attempting to connect to SMTP server")
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            logging.debug("Connected to SMTP server")
            server.starttls()
            logging.debug("TLS started")
            logging.debug(f"Attempting to login with email: {sender_email}")
            server.login(sender_email, sender_password)
            logging.debug("Login successful")
            server.sendmail(sender_email, user_email, message.as_string())
            logging.debug(f"Welcome email sent to {user_email}")
    except Exception as e:
        logging.error(f"Error sending email to {user_email}: {str(e)}")

# Test the function
if __name__ == "__main__":
    test_email = "test@example.com"
    test_name = "Test User"
    send_welcome_email(test_email, test_name)
