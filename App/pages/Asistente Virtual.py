import streamlit as st

# --- SHARED ON ALL PAGES ---
st.logo("https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/menu_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.png")

def app():
    # Configure the Streamlit page
    st.set_page_config(
        page_title="Asistente Virtual",
        page_icon="🤖",
        layout="wide"
    )

    # Load and display the sidebar image
    image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
    st.sidebar.image(image_url, use_column_width=True, caption="La Naturaleza A Los Pies De Tus Mascota")

    st.title("Asistente Virtual")

        # Add a submessage about the AI nature of the assistant
    st.markdown("""
    <div style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 20px;">
    <p style="font-style: italic; color: #4a4a4a;">
    Bienvenido a nuestro Asistente Virtual impulsado por IA. Estoy aquí para responder a cualquier pregunta que tengas sobre Pasto Verde, nuestros productos, o cuidado de mascotas. No dudes en preguntar lo que quieras - ¡estoy listo para ayudarte!
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Load the link from the secrets.toml file
    try:
        link = st.secrets["asistente_virtual_link"]["link"]
    except KeyError as e:
        st.error(f"Error accessing secret: {e}")
        st.stop()

    # Embed the link into the Streamlit app
    try:
        st.components.v1.iframe(
            src=link,
            height=600,  # Adjust the height as needed
            scrolling=True
        )
    except Exception as e:
        st.error(f"Error embedding iframe: {e}")
        st.write("Attempting to display link as text:")
        st.write(link)

    # Add a navigation button
    if st.button("Inicio"):
        st.switch_page("App.py")  # Ensure "App.py" is the correct target page name


if __name__ == "__main__":
    app()


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import streamlit as st

def send_welcome_email(user_email, user_name):
    sender_email = st.secrets["email"]["sender_email"]
    sender_password = st.secrets["email"]["sender_password"]

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

    # Download the image from GitHub
    image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/Email%20Banner.jpg"
    response = requests.get(image_url)
    if response.status_code == 200:
        img_data = response.content
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        image.add_header('Content-Disposition', 'inline', filename="Email Banner.jpg")
        message.attach(image)
    else:
        print("Failed to download image from GitHub")

    try:
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message.as_string())
        st.success(f"Welcome email sent to {user_email}")
    except smtplib.SMTPAuthenticationError:
        st.error("Authentication failed. Check your email and password.")
    except smtplib.SMTPConnectError:
        st.error("Failed to connect to the SMTP server. Check your network connection.")
    except smtplib.SMTPException as e:
        st.error(f"SMTP error occurred: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Debugging section to check secrets
if st.checkbox("Show email configuration"):
    st.write("Sender Email:", st.secrets["email"]["sender_email"])
    st.write("Sender Password: [hidden]")  # Mask the password for security

# Test button to send a test email
if st.button("Send Test Email"):
    # Replace with a valid test email address
    test_email = "test@example.com"  # Change this to your test email
    test_user_name = "Test User"
    send_welcome_email(test_email, test_user_name)
