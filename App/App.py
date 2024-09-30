# app.py

import os
import random
import time
from datetime import datetime

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
from auth0_component import login_button
from modules.models import User, Product, Order, Subscription, PaymentTransaction, setup_database, UserType, OrderStatus
from modules.home import home_page
from modules.order import place_order
from modules.user_orders import display_user_orders
from modules.auth import auth0_authentication
from modules.email import send_welcome_email
from modules.map import display_map

# Standard library imports
import logging

# Configure logging
logging.basicConfig(
  level=logging.INFO,  # Set to DEBUG for more detailed output
  format='%(asctime)s - %(levelname)s - %(message)s',
  handlers=[
      logging.FileHandler("app.log"),  # Log to a file named app.log
      logging.StreamHandler()          # Also output to console
  ]
)

# Streamlit page configuration
st.set_page_config(
  page_title="Pasto Verde - Naturaleza en Casa para tus Mascotas",
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

Session = setup_database(database_url)

import streamlit as st

def show_policy_banner():
  if 'policy_accepted' not in st.session_state:
      st.session_state.policy_accepted = False

  if not st.session_state.policy_accepted:
      # CSS for the banner
      st.markdown(
          """
          <style>
          .policy-banner {
              position: fixed;
              bottom: 0;
              left: 0;
              right: 0;
              background-color: #f1f1f1;
              padding: 10px;
              text-align: center;
              z-index: 1000;
          }
          .policy-banner button {
              margin: 0 10px;
          }
          </style>
          """,
          unsafe_allow_html=True
      )

      # Banner content
      banner_html = """
      <div class="policy-banner">
          <p>Al usar este sitio, aceptas nuestra política de privacidad y cookies.</p>
          <button onclick="accept_policy()">Aceptar</button>
          <button onclick="reject_policy()">Rechazar</button>
      </div>
      <script>
      function accept_policy() {
          window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'accept'}, '*');
      }
      function reject_policy() {
          window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'reject'}, '*');
      }
      </script>
      """
      
      policy_action = st.markdown(banner_html, unsafe_allow_html=True)
      
      # Handle button clicks
      if policy_action == 'accept':
          st.session_state.policy_accepted = True
          st.experimental_rerun()
      elif policy_action == 'reject':
          st.error("Debes aceptar la política para usar este sitio.")
          st.stop()

def main():
  """Main function to run the Streamlit app."""
  logging.info("Starting the Pasto Verde application.")
  
  st.title("Pasto Verde - Entrega de pasto para mascotas")
  
  # Show policy banner
  show_policy_banner()
  
  # Check if there's a logout message to display
  if 'logout_message' in st.session_state:
      st.success(st.session_state['logout_message'])
      del st.session_state['logout_message']  # Clear the message after displaying
      logging.info("Displayed logout message to user.")
  
  # Authenticate the user
  user = auth0_authentication()
  
  if user:
      logging.info(f"User '{user.name}' authenticated successfully.")
      st.write(f"Hola {user.name}, bienvenido a Pasto Verde! 🌿")  # Personalized greeting

      # Initialize session state for current page
      if 'current_page' not in st.session_state:
          st.session_state.current_page = "🏠 Inicio"  # Default page
          logging.debug("Current page set to default (Inicio).")

      # Define the available menu items and their corresponding functions
      menu_items = {
          "🏠 Inicio": home_page,
          "🛒  Ordene Ahora": place_order,
          "📦 Mis Órdenes": display_user_orders,
          "🗺️ Zona De Envios": display_map,
          "ℹ️ Sobre Nosotros": about_us,
          "📖 Manual de Usuario": user_manual
      }

      # Add admin dashboard option for admin users
      if user.type == UserType.admin:
          menu_items["📊 Admin Dashboard"] = admin_dashboard
          logging.info("Admin dashboard added to menu for admin user.")

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
          # Fallback to default page in case of error
          st.session_state.current_page = "🏠 Inicio"
          menu_items[st.session_state.current_page]()
          logging.warning("KeyError encountered. Reset current page to Inicio.")
      except Exception as e:
          logging.error(f"An error occurred while loading the page '{st.session_state.current_page}': {e}")
          st.error("Ha ocurrido un error al cargar la página. Por favor, intenta de nuevo más tarde.")

      # Logout button functionality in the sidebar
      if st.sidebar.button("🚪 Finalizar la sesión"):
          # Set logout message
          st.session_state['logout_message'] = "Has cerrado la sesión exitosamente."
          # Clear session state (except for the logout message)
          for key in list(st.session_state.keys()):
              if key != 'logout_message':
                  del st.session_state[key]
          logging.info("User logged out and session state cleared.")
          st.rerun()

      # Display logo or image in the sidebar
      st.sidebar.markdown("---")
      image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
      st.sidebar.image(image_url, use_column_width=True, caption="La Naturaleza A Los Pies De Tus Mascota")

  else:
      # Prompt the user to log in
      st.write("Por favor inicie sesión para acceder a los servicios de Pasto Verde")
      logging.info("User not authenticated. Displaying login prompt.")
      


      # Display logo or image in the sidebar
      st.sidebar.markdown("---")
      image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
      st.sidebar.image(image_url, use_column_width=True, caption="La Naturaleza A Los Pies De Tus Mascota")

def user_manual():
  """Display the user manual page."""
  logging.info("Displaying the user manual page.")
  st.subheader("📖 Manual de Usuario")
  st.write("""
  Bienvenido al Manual de Usuario de Pasto Verde. Aquí encontrarás información útil para navegar y utilizar la aplicación de manera efectiva.
  
  ## ¿Qué es Pasto Verde?
  Pasto Verde es un servicio de entrega de pasto fresco para tus mascotas. Ofrecemos diferentes planes de suscripción y opciones de compra única.

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
  En Pasto Verde, creemos que cada mascota merece un toque de naturaleza en su vida diaria. Nuestra misión es llevar pasto fresco y exuberante directamente a tu puerta, brindando a tus amigos peludos una experiencia natural y placentera.
  
  🌿 **¿Por qué elegir Pasto Verde?**
  - Pasto fresco, libre de pesticidas
  - Opciones de entrega convenientes
  - Empaque ecológico
  - ¡Mascotas felices, dueños felices!

  Únete a nosotros para hacer que el día de tu mascota sea un poco más verde y mucho más divertido.
  """)

def admin_dashboard():
  """Display the admin dashboard page."""
  logging.info("Accessing the admin dashboard.")
  if st.session_state.user.type != UserType.admin:
      st.error("No tienes permiso para acceder a esta página.")
      logging.warning("Unauthorized access attempt to admin dashboard.")
      return

  st.subheader("📊 Admin Dashboard")

  session = Session()
  try:
      # Fetch total orders and revenue from the database
      total_orders = session.query(Order).count()
      total_revenue = session.query(func.sum(Order.total_price)).scalar() or 0.0
      logging.info(f"Total orders retrieved: {total_orders}")
      logging.info(f"Total revenue calculated: {total_revenue}")

      # Display total orders and revenue
      st.write(f"**Total de órdenes**: {total_orders}")
      st.write(f"**Ingresos totales**: L. {total_revenue:.2f}")

      # Display recent orders
      st.subheader("Órdenes recientes")
      recent_orders = session.query(Order).order_by(Order.date.desc()).limit(10).all()
      logging.info("Recent orders fetched for display.")
      for order in recent_orders:
          st.write(f"**Order ID**: {order.id} - **Usuario**: {order.user.name} - **Total**: L. {order.total_price:.2f} - **Fecha**: {order.date}")
  except Exception as e:
      logging.error(f"An error occurred in admin dashboard: {e}")
      st.error("Ha ocurrido un error al obtener los datos de administrador.")
  finally:
      session.close()
      logging.info("Database session closed in admin dashboard.")

  # If policy is not accepted, don't show the main content
  if not st.session_state.get('policy_accepted', False):
      st.stop()

if __name__ == "__main__":
  main()  # Run the main function when the script is executed
