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
import streamlit as st

def send_test_email():
  try:
      # Retrieve email credentials from Streamlit secrets
      sender_email = st.secrets["email"]["sender_email"]
      sender_password = st.secrets["email"]["sender_password"]
      recipient_email = "recipient@example.com"  # Replace with the recipient's email address

      # Create the email message
      message = MIMEMultipart()
      message["Subject"] = "Test Email"
      message["From"] = sender_email
      message["To"] = recipient_email

      body = "This is a test email."
      message.attach(MIMEText(body, "plain"))

      # Connect to the SMTP server and send the email
      with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
          server.starttls()
          server.login(sender_email, sender_password)
          server.sendmail(sender_email, recipient_email, message.as_string())
          st.success("Email sent successfully!")

  except Exception as e:
      st.error(f"Failed to send email: {e}")

# Streamlit app
st.title("Email Sender Test")

if st.button("Send Test Email"):
  send_test_email()
