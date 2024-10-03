import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import streamlit as st


def send_welcome_email(user_email, user_name):
  sender_email = st.secrets["email"]["sender_email"]
  sender_password = st.secrets["email"]["sender_password"]

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
  response = requests.get(image_url)
  if response.status_code == 200:
      img_data = response.content
      image = MIMEImage(img_data)
      image.add_header('Content-ID', '<image1>')  # Ensure this matches the HTML
      image.add_header('Content-Disposition', 'inline', filename="Email Banner.jpg")
      message.attach(image)
  else:
      print("Failed to download image from GitHub")

  try:
      with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
          server.starttls()
          server.login(sender_email, sender_password)
          server.sendmail(sender_email, user_email, message.as_string())
      print(f"Welcome email sent to {user_email}")
  except Exception as e:
      print(f"Error sending email to {user_email}: {str(e)}")

if not user.welcome_email_sent:
    email_sent = send_welcome_email(user.email, user.name)
    if email_sent:
        user.welcome_email_sent = True
        session.commit()
    else:
        st.warning("Failed to send welcome email. Please check your email configuration.")
