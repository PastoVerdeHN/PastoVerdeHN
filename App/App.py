import os
import random
import time
from datetime import datetime
import logging

# Third-party imports
import folium
import pandas as pd
import requests
import smtplib
import streamlit as st
import streamlit.components.v1 as components
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from geopy.geocoders import Nominatim
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_folium import folium_static
from dotenv import load_dotenv
from branca.element import Template, MacroElement

# Local application imports
from modules.models import User, Product, Order, Subscription, PaymentTransaction, setup_database, UserType, OrderStatus
from modules.home import home_page
from modules.order import place_order
from modules.user_orders import display_user_orders
from modules.auth import auth0_authentication
from modules.map import display_map

# --- SHARED ON ALL PAGES ---
st.logo("https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/menu_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.png")

# Configure logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  handlers=[
      logging.FileHandler("app.log"),
      logging.StreamHandler()
  ]
)

# Streamlit page configuration
st.set_page_config(
  page_title="©Pasto Verde - Naturaleza en Casa para tus Mascotas",
  page_icon="🌿",
  layout="wide"
)

# Load environment variables
load_dotenv()

# Database setup
try:
  database_url = st.secrets["database"]["url"]
  logging.info("Database URL retrieved from Streamlit secrets.")
except KeyError:
  database_url = os.getenv("DATABASE_URL")
  logging.info("Database URL retrieved from environment variables.")

if not database_url:
  st.error("Database URL not found. Please set it in Streamlit secrets or as an environment variable.")
  logging.error("Database URL not found. Cannot proceed without database access.")
  st.stop()

def show_policy_banner():
    if 'policy_accepted' not in st.session_state:
        st.session_state.policy_accepted = False
    
    if not st.session_state.policy_accepted:
        st.markdown(
            """
            <style>
            .policy-banner {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .policy-text {
                font-size: 16px;
                color: #333;
                margin-bottom: 15px;
            }
            .policy-link {
                color: #4CAF50;
                text-decoration: none;
                font-weight: bold;
            }
            .policy-image {
                max-width: 100%;
                border-radius: 5px;
                margin-bottom: 15px;
            }
            .policy-caption {
                font-size: 14px;
                color: #666;
                font-style: italic;
                margin-bottom: 15px;
            }
            .stButton > button {
                width: 100%;
            }
            </style>
            <div class="policy-banner">
                <div class="policy-text">
                    Al usar este sitio, aceptas nuestra <a href="https://pastoverdehn.streamlit.app/T%C3%A9rminos_y_Condiciones" target="_blank" class="policy-link">política de privacidad y cookies</a>.
                </div>
                <img src="https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/Privacybanner.png" class="policy-image">
                <p class="policy-caption">Al hacer clic en Aceptar, usted confirma que ha leído y está de acuerdo con nuestras política de privacidad y cookies.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Use columns to create space between buttons
        col1, col2, col3, col4 = st.columns([1,2,2,1])
        with col2:
            accept = st.button("Aceptar", key="accept_policy", type="primary")
        with col3:
            reject = st.button("Rechazar", key="reject_policy")
        
        if accept:
            st.session_state.policy_accepted = True
            st.rerun()
        elif reject:
            st.error("Debes aceptar la política para usar esta aplicación.")

def main():
  """Main function to run the Streamlit app."""
  logging.info("Starting the ©Pasto Verde application.")
  
  # Show policy banner only if it hasn't been accepted
  if not st.session_state.get('policy_accepted', False):
      show_policy_banner()
  
  # Only proceed if policy is accepted
  if not st.session_state.get('policy_accepted', False):
      return

  st.title("©Pasto Verde - Entrega de pasto para mascotas")
  
  # Check if there's a logout message to display
  if 'logout_message' in st.session_state:
      st.success(st.session_state['logout_message'])
      del st.session_state['logout_message']
      logging.info("Displayed logout message to user.")
  
  # Authenticate the user
  user = auth0_authentication()
  
  if user:
      logging.info(f"User '{user.name}' authenticated successfully.")
      st.write(f"Hola {user.name}, bienvenido a ©Pasto Verde! 🌿")

      # Initialize session state for current page
      if 'current_page' not in st.session_state:
          st.session_state.current_page = "🏠 Inicio"
          logging.debug("Current page set to default (Inicio).")

      # Define the available menu items and their corresponding functions
      menu_items = {
          "🏠 Inicio": home_page,
          "🛒 Ordene Ahora": place_order,
          "📦 Mis Órdenes": display_user_orders,
          "🗺️ Zona De Envios": display_map,
          "ℹ️ Sobre Nosotros": about_us,
          "📖 Manual de Usuario": user_manual,
      }

      # Display the menu as buttons in columns
      cols = st.columns(len(menu_items))
      for i, (emoji_label, func) in enumerate(menu_items.items()):
          if cols[i].button(emoji_label):
              st.session_state.current_page = emoji_label
              logging.info(f"User selected menu item: {emoji_label}")

      # Show currently selected page
      st.write(f"Current page: {st.session_state.current_page}")
      logging.debug(f"Current page is set to: {st.session_state.current_page}")

      # Execute the function for the current page
      try:
          menu_items[st.session_state.current_page]()
          logging.info(f"Displayed page: {st.session_state.current_page}")
      except KeyError:
          st.session_state.current_page = "🏠 Inicio"
          menu_items[st.session_state.current_page]()
          logging.warning("KeyError encountered. Reset current page to Inicio.")
      except Exception as e:
          logging.error(f"An error occurred while loading the page '{st.session_state.current_page}': {e}")
          st.error("Ha ocurrido un error al cargar la página. Por favor, intenta de nuevo más tarde.")

      # Logout button functionality in the sidebar
      if st.sidebar.button("🚪 Finalizar la sesión"):
          st.session_state['logout_message'] = "Has cerrado la sesión exitosamente."
          policy_accepted = st.session_state.get('policy_accepted', False)
          for key in list(st.session_state.keys()):
              if key not in ['logout_message', 'policy_accepted']:
                  del st.session_state[key]
          st.session_state.policy_accepted = policy_accepted
          logging.info("User logged out and session state cleared, preserving policy acceptance.")
          st.rerun()

      # Display logo or image in the sidebar
      st.sidebar.markdown("---")
      image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
      st.sidebar.image(image_url, use_column_width=True, caption="© La Naturaleza A Los Pies De Tus Mascota")

  else:
      # Prompt the user to log in
      st.write("Por favor inicie sesión para acceder a los servicios de ©Pasto Verde")
      logging.info("User not authenticated. Displaying login prompt.")

      # Display logo or image in the sidebar
      st.sidebar.markdown("---")
      image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
      st.sidebar.image(image_url, use_column_width=True, caption="© La Naturaleza A Los Pies De Tus Mascota")

def user_manual():
  """Display the user manual page."""
  logging.info("Displaying the user manual page.")
  st.subheader("📖 Manual de Usuario")
  st.write("""
  Bienvenido al Manual de Usuario de ©Pasto Verde. Aquí encontrarás información útil para navegar y utilizar la aplicación de manera efectiva.
  
  ## ¿Qué es ©Pasto Verde?
  ©Pasto Verde es un servicio de entrega de pasto fresco para tus mascotas. Ofrecemos diferentes planes de suscripción y opciones de compra única.

  ## ¿Cómo registrarse?
  1. Haz clic en el botón "Entrar" en la barra lateral.
  2. Completa el formulario de registro con tu información.
  3. Recibirás un correo electrónico de bienvenida.

  ## ¿Cómo realizar un pedido?
  1. Selecciona el plan que deseas en la sección "Ordene Ahora".
  2. Ingresa tu dirección de entrega.
  3. Revisa tu pedido y haz clic en "Confirmar pedido".

  ## ¿Cómo ver mis órdenes?
  - Ve a la sección "Mis Órdenes" para ver el estado de tus pedidos anteriores.

  ## ¿Cómo contactar al soporte?
  Si tienes alguna pregunta o necesitas ayuda, puedes contactarnos a través del correo electrónico proporcionado en la sección "Sobre Nosotros".

  ## Preguntas Frecuentes (FAQ)
  **¿Puedo cancelar mi suscripción?**
  Sí, puedes cancelar tu suscripción en cualquier momento. Simplemente contáctanos.

  **¿Qué métodos de pago aceptan?**
  Aceptamos pagos a través de PayPal y tarjetas de crédito.

  **¿Cómo puedo cambiar mi dirección de entrega?**
  Puedes actualizar tu dirección de entrega en la sección de "Ordene Ahora" antes de confirmar tu pedido.
  """)

def about_us():
  """Display the about us page."""
  logging.info("Displaying the 'About Us' page.")
  st.subheader("ℹ️ Sobre nosotros")
  st.write("""
  En  ©Pasto Verde, creemos que cada mascota merece un toque de naturaleza en su vida diaria. Nuestra misión es llevar pasto fresco y exuberante directamente a tu puerta, brindando a tus amigos peludos una experiencia natural y placentera.
  
  🌿 **¿Por qué elegir  ©Pasto Verde?**
  - Pasto fresco, libre de pesticidas
  - Opciones de entrega convenientes
  - Empaque ecológico
  - ¡Mascotas felices, dueños felices!

  Únete a nosotros para hacer que el día de tu mascota sea un poco más verde y mucho más divertido.
  """)

if __name__ == "__main__":
  main()
