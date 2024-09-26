import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import random
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from auth0_component import login_button
from branca.element import Template, MacroElement
from models import User, Product, Order, Subscription, PaymentTransaction, setup_database, UserType, OrderStatus
from geopy.geocoders import Nominatim
import time
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import requests
from .modules.home import home_page





# Streamlit page configuration
st.set_page_config(
  page_title="Pasto Verde - Naturaleza en Casa para tus Mascotas",
  page_icon="🌿",
  layout="wide"
)

# Add custom CSS for green glow
st.markdown(
  """
  
  """,
  unsafe_allow_html=True,
)

# Load environment variables
load_dotenv()

# Database setup
try:
  database_url = st.secrets["database"]["url"]
except KeyError:
  database_url = os.getenv("DATABASE_URL")

if not database_url:
  st.error("Database URL not found. Please set it in Streamlit secrets or as an environment variable.")
  st.stop()

Session = setup_database(database_url)

# Helper functions
def generate_order_id():
  return f"ORD-{random.randint(10000, 99999)}"

def auth0_authentication():
  if 'user' not in st.session_state:
      st.session_state.user = None
  if 'auth_status' not in st.session_state:
      st.session_state.auth_status = None

  if st.session_state.user is None:
      auth_choice = st.sidebar.radio("Elige acción", ["🔑 Entrar"])
      
      if auth_choice == "🔑 Entrar":
          try:
              AUTH0_CLIENT_ID = st.secrets["auth0"]["AUTH0_CLIENT_ID"]
              AUTH0_DOMAIN = st.secrets["auth0"]["AUTH0_DOMAIN"]
              ADMIN_EMAIL = st.secrets["admin"]["email"]  # Get admin email from secrets
          except KeyError:
              st.error("Auth0 configuration not found. Please set AUTH0_CLIENT_ID and AUTH0_DOMAIN in Streamlit secrets.")
              return None
          
          user_info = login_button(
              AUTH0_CLIENT_ID, 
              domain=AUTH0_DOMAIN,
              redirect_uri="http://localhost:8501/callback"  # Adjust this if you're not running locally
          )
          
          if user_info and st.session_state.auth_status != "authenticated":
              session = Session()
              user = session.query(User).filter_by(email=user_info['email']).first()
              
              if not user:
                  # New user registration
                  user = User(
                      id=user_info['sub'],
                      name=user_info['name'],
                      email=user_info['email'],
                      type=UserType.admin if user_info['email'] == ADMIN_EMAIL else UserType.customer,  # Set type based on email
                      address='',
                      created_at=datetime.utcnow(),
                      welcome_email_sent=False
                  )
                  session.add(user)
                  session.commit()
              else:
                  # Check if the user is an admin
                  if user.email == ADMIN_EMAIL:
                      user.type = UserType.admin  # Set user type to admin if necessary

              if not user.welcome_email_sent:
                  send_welcome_email(user.email, user.name)  # Ensure this function is defined
                  user.welcome_email_sent = True
                  session.commit()
              
              user.last_login = datetime.utcnow()
              session.commit()
              
              st.session_state.user = user
              st.session_state.auth_status = "authenticated"
              st.success(f"Bienvenido, {user.name}!")
              session.close()
  
  return st.session_state.user

def main():
  st.title("Pasto Verde - Entrega de pasto para mascotas")
  user = auth0_authentication()  # Get the user from authentication

  if user:
      # Display a personalized welcome message
      st.write(f"Hola {user.name}, bienvenido a Pasto Verde! 🌿")  # Personalized greeting

      if 'current_page' not in st.session_state:
          st.session_state.current_page = "🏠 Inicio"  # Default page
      
      menu_items = {
          "🏠 Inicio": home_page,
          "🛒  Ordene Ahora": place_order,
          "📦 Mis Órdenes": display_user_orders,
          "🗺️ Zona De Envios": display_map,
          "ℹ️ Sobre Nosotros": about_us,
          "📖 Manual de Usuario": user_manual  # New menu item
      }
      
      if user.type == UserType.admin:
          menu_items["📊 Admin Dashboard"] = admin_dashboard  # Ensure this function is defined
      
      cols = st.columns(len(menu_items))
      for i, (emoji_label, func) in enumerate(menu_items.items()):
          if cols[i].button(emoji_label):
              st.session_state.current_page = emoji_label
      
      # Debugging line
      st.write(f"Current page: {st.session_state.current_page}")  
      
      try:
          menu_items[st.session_state.current_page]()
      except KeyError:
          st.session_state.current_page = "🏠 Inicio"  # Fallback to default page
          menu_items[st.session_state.current_page]()
      
      if st.sidebar.button("🚪 Finalizar la sesión"):
          for key in list(st.session_state.keys()):
              del st.session_state[key]
          st.success("Logged out successfully.")
          st.rerun()
  else:
      st.write("Por favor inicie sesión para acceder a los servicios de Pasto Verde")
      
      # Move the image to the bottom of the sidebar
      st.sidebar.markdown("---")
      image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
      st.sidebar.image(image_url, use_column_width=True, caption="La Naturaleza A Los Pies De Tus Mascota")
    

def place_order():
  st.subheader("🛒 Realizar pedido")
  session = Session()

  # Plan options
  plans = {
      "Suscripción Anual": {
          "id": "annual",
          "price": 720.00,
          "features": [
              "Entrega cada dos semanas",
              "Envío gratis",
              "Descuento del 29%",
              "Descuento adicional del 40%",
              "Personalización incluida",
              "Primer mes gratis"
          ]
      },
      "Suscripción Semestral": {
          "id": "semiannual",
          "price": 899.00,
          "features": [
              "Entrega cada dos semanas",
              "Envío gratis",
              "Descuento del 29%",
              "Descuento adicional del 25%",
              "Personalización incluida"
          ]
      },
      "Suscripción Mensual": {
          "id": "monthly",
          "price": 1080.00,
          "features": [
              "Entrega cada dos semanas",
              "Envío gratis",
              "Descuento del 29%",
              "Descuento adicional del 10%"
          ]
      },
      "Sin Suscripción": {
          "id": "one_time",
          "price": 850.00,
          "features": [
              "Compra única de alfombra de césped",
              "Envío gratis",
              "Pago único"
          ]
      }
  }

  # Display Plan Cards
  cols = st.columns(len(plans))
  selected_plan = st.radio("Selecciona un plan:", list(plans.keys()), horizontal=True)

  for i, (plan_name, plan_data) in enumerate(plans.items()):
      with cols[i]:
          st.write(f"## {plan_name}")
          if plan_name != "Sin Suscripción":
              st.write(f"### ~~L.1700.00~~ L. {plan_data['price']:.2f} por mes", unsafe_allow_html=True)
          else:
              st.write(f"### L. {plan_data['price']:.2f}", unsafe_allow_html=True)
          for feature in plan_data['features']:
              st.write(f"✅ {feature}")

  # Address Input and Map
  st.subheader("Dirección de entrega")
  
  # Colonia search
  col1, col2 = st.columns([3, 1])
  with col1:
      colonia = st.text_input("Buscar colonia", value="", key="colonia_search")
  with col2:
      search_button = st.button("Buscar")

  # Initialize map
  if 'map_center' not in st.session_state:
      st.session_state.map_center = [14.0818, -87.2068]  # Default to Tegucigalpa
  if 'search_result' not in st.session_state:
      st.session_state.search_result = None

  # Address search
  if search_button or (colonia and st.session_state.get('last_search') != colonia):
      st.session_state['last_search'] = colonia
      geolocator = Nominatim(user_agent="pasto_verde_app")
      try:
          search_query = f"{colonia}, Tegucigalpa, Honduras"
          location = geolocator.geocode(search_query)
          if location:
              st.session_state.map_center = [location.latitude, location.longitude]
              st.session_state.search_result = location.address
              st.success(f"Colonia encontrada: {location.address}")
          else:
              st.error("No se pudo encontrar la colonia.")
      except Exception as e:
          st.error(f"Error en el servicio de geolocalización: {str(e)}")

  # Create map
  m = folium.Map(location=st.session_state.map_center, zoom_start=15)
  marker = folium.Marker(st.session_state.map_center, draggable=True)
  marker.add_to(m)
  folium_static(m)

  # Specific address details
  specific_address = st.text_input("Número de casa y calle", value="")
  additional_references = st.text_area("Referencias adicionales (opcional)", value="", key="additional_refs")

  # Combine all address information
  full_address = f"{specific_address}, {st.session_state.search_result or colonia}"
  if additional_references:
      full_address += f" ({additional_references})"

  # User Information
  user_full_name = st.text_input("Nombre completo", value=st.session_state.user.name)
  user_email = st.text_input("Correo electrónico", value=st.session_state.user.email)
  user_phone = st.text_input("Número de teléfono", value="")
  delivery_date = st.date_input("Fecha de entrega", value=datetime.today())

  # Delivery Time Frame Selection
  delivery_time_frame = st.radio("Selecciona un horario de entrega:", ("AM (8am - 12pm)", "PM (12pm - 4pm)"))

  # Promo Code Input and Disclaimer
  promo_code = st.text_input("Código promocional (opcional)", value="")
  st.caption("Nota: Los códigos promocionales solo son válidos para productos sin suscripción.")

  # Order Review
  if selected_plan and st.session_state.map_center:
      with st.expander("Resumen del Pedido", expanded=True):
          st.write(f"Plan seleccionado: **{selected_plan}**")
          
          lempira_price = plans[selected_plan]['price']
          total_price = lempira_price
          
          # Apply promo code discount for "Sin Suscripción"
          if selected_plan == "Sin Suscripción" and promo_code.upper() == "VERDEHN":
              discount = total_price * 0.20
              total_price -= discount
              st.write(f"¡Código promocional aplicado! Descuento: L. {discount:.2f}")

          if selected_plan == "Suscripción Anual":
              total_price *= 11  # Multiply by 11 for annual subscription (1 month free)
              st.write("¡Tienes un mes gratis! Solo pagas por 11 meses.")
          elif selected_plan == "Suscripción Semestral":
              total_price = lempira_price * 6  # Total for semi-annual is 6 months
              st.write(f"Precio total para 6 meses: L. {total_price:.2f}")
          else:
              st.write(f"Precio: L. {lempira_price:.2f} por mes")
          
          st.write("Cambio de dólar: 1$ = L.25.00")
          st.write(f"Dirección de entrega: {full_address}")
          st.write(f"Nombre completo: {user_full_name}")
          st.write(f"Correo electrónico: {user_email}")
          st.write(f"Número de teléfono: {user_phone}")
          st.write(f"Fecha de entrega: {delivery_date}")
          st.write(f"Horario de entrega: {delivery_time_frame}")
          st.write(f"Total: L. {total_price:.2f}")
          st.write("**Nota:** En el checkout, se incluye una caja de madera con los planes de suscripción. One-time setup fee")

      if st.button("Confirmar pedido"):
          # Create new order
          new_order = Order(
              id=generate_order_id(),
              user_id=st.session_state.user.id,
              product_id=1,  # Assuming product_id 1 is for grass
              quantity=1,
              delivery_address=full_address,
              status=OrderStatus.pending,
              total_price=total_price  # Use the calculated total price
          )
          session.add(new_order)
          
          # If it's a subscription, create a subscription record
          if selected_plan != "Sin Suscripción":
              new_subscription = Subscription(
                  user_id=st.session_state.user.id,
                  plan_name=selected_plan,
                  start_date=datetime.utcnow(),
                  is_active=True
              )
              session.add(new_subscription)
          
          session.commit()
          
          st.success(f"*Pedido Procesando⌛* Por favor confirmar el pago para coordinar la entrega de su orden. Numero de pedido: {new_order.id}")

          # Trigger the balloon animation
          st.balloons()

          # PayPal integration
          paypal_client_id = st.secrets["paypal"]["client_id"]  # Access the PayPal Client ID from Streamlit secrets
          if selected_plan == "Sin Suscripción":
              paypal_html = f'''
              <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&currency=USD"></script>
              <div id="paypal-button-container"></div>
              <script>
                  paypal.Buttons({{
                      createOrder: function(data, actions) {{
                          return actions.order.create({{
                              purchase_units: [{{
                                  amount: {{
                                      value: '{total_price / 25:.2f}'  // Convert Lempira to USD
                                  }},
                                  description: '{selected_plan}',  // Use the selected plan name as the description
                                  custom_id: 'Instrucciones: {additional_references}',  // Use additional references as instructions
                                  shipping: {{
                                      name: {{
                                          full_name: '{user_full_name}'
                                      }},
                                      address: {{
                                          address_line_1: '{specific_address}',
                                          address_line_2: '{additional_references}',
                                          admin_area_2: 'Tegucigalpa',  // City
                                          admin_area_1: 'FM',  // State
                                          postal_code: '11101',  // Example postal code
                                          country_code: 'HN'  // Country code
                                      }}
                                  }}
                              }}]
                          }});
                      }},
                      onApprove: function(data, actions) {{
                          return actions.order.capture().then(function(details) {{
                              alert('¡Compra realizada con éxito! 🎉 ID de transacción: ' + details.id);
                              window.location.reload();
                          }});
                      }},
                      onError: function(err) {{
                          alert('Error al procesar el pago. Intenta de nuevo.');
                          console.error('PayPal error:', err);
                      }}
                  }}).render('#paypal-button-container');
              </script>
              '''
              components.html(paypal_html, height=1200)
          elif selected_plan == "Suscripción Mensual":
              paypal_html = f'''
              <div id="paypal-button-container-P-8JD80124L6471951GM3UKKHA"></div>
              <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
              <script>
                  paypal.Buttons({{
                      style: {{
                          shape: 'pill',
                          color: 'blue',
                          layout: 'horizontal',
                          label: 'subscribe'
                      }},
                      createSubscription: function(data, actions) {{
                          return actions.subscription.create({{
                              plan_id: 'P-8JD80124L6471951GM3UKKHA'
                          }});
                      }},
                      onApprove: function(data, actions) {{
                          alert('¡Pedido realizado con éxito! 🎉');
                          window.location.reload();
                      }},
                      onError: function(err) {{
                          alert('Error al procesar el pago. Intenta de nuevo.');
                      }}
                  }}).render('#paypal-button-container-P-8JD80124L6471951GM3UKKHA');
              </script>
              '''
              components.html(paypal_html, height=300)
          elif selected_plan == "Suscripción Semestral":
              paypal_html = f'''
              <div id="paypal-button-container-P-79741958WR506740HM3UPLFA"></div>
              <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
              <script>
                  paypal.Buttons({{
                      style: {{
                          shape: 'pill',
                          color: 'gold',
                          layout: 'horizontal',
                          label: 'subscribe'
                      }},
                      createSubscription: function(data, actions) {{
                          return actions.subscription.create({{
                              plan_id: 'P-79741958WR506740HM3UPLFA'
                          }});
                      }},
                      onApprove: function(data, actions) {{
                          alert('¡Pedido realizado con éxito! 🎉 ID de suscripción: ' + data.subscriptionID);
                          window.location.reload();
                      }},
                      onError: function(err) {{
                          alert('Error al procesar el pago. Intenta de nuevo.');
                      }}
                  }}).render('#paypal-button-container-P-79741958WR506740HM3UPLFA');
              </script>
              '''
              components.html(paypal_html, height=300)
          elif selected_plan == "Suscripción Anual":
              paypal_html = f'''
              <div id="paypal-button-container-P-4E978587FL636905DM3UPY3Q"></div>
              <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
              <script>
                  paypal.Buttons({{
                      style: {{
                          shape: 'pill',
                          color: 'black',
                          layout: 'horizontal',
                          label: 'subscribe'
                      }},
                      createSubscription: function(data, actions) {{
                          return actions.subscription.create({{
                              plan_id: 'P-4E978587FL636905DM3UPY3Q'
                          }});
                      }},
                      onApprove: function(data, actions) {{
                          alert('¡Suscripción Anual realizada con éxito! 🎉 ID de suscripción: ' + data.subscriptionID);
                          window.location.reload();
                      }},
                      onError: function(err) {{
                          alert('Error al procesar el pago. Intenta de nuevo.');
                      }}
                  }}).render('#paypal-button-container-P-4E978587FL636905DM3UPY3Q');
              </script>
              '''
              components.html(paypal_html, height=300)

  session.close()
def display_user_orders():
  st.subheader("📦 Mis Órdenes")
  
  session = Session()
  orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
  
  # Define order status mapping
  status_mapping = {
      OrderStatus.pending: ("Pago Pendiente", 0),
      OrderStatus.confirmed: ("Orden Confirmada", 33),
      OrderStatus.shipped: ("Orden Enviada", 66),
      OrderStatus.delivered: ("Orden Entregada", 100)
  }
  
  for order in orders:
      with st.expander(f"Order ID: {order.id} - Status: {order.status.value}"):
          st.write(f"**Fecha de entrega:** {order.date}")
          st.write(f"**Dirección de entrega:** {order.delivery_address}")
          st.write(f"**Precio total:** L. {order.total_price:.2f}")
          
          if order.product_id:
              product = session.query(Product).filter_by(id=order.product_id).first()
              if product:
                  st.write(f"**Producto:** {product.name}")

          # Display progress bar based on order status
          if order.status in status_mapping:
              status_label, progress_value = status_mapping[order.status]
              st.write(f"**Estado del pedido:** {status_label}")
              progress_bar = st.progress(progress_value)
          else:
              st.write("**Estado del pedido:** Desconocido")
              st.progress(0)  # Default to 0 if status is unknown

  session.close()
def user_manual():
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

def display_map():
  st.subheader("🗺️ Zona de Entrega")
  
  # Coordinates for Tegucigalpa
  tegucigalpa_coords = [14.0818, -87.2068]
  
  # Create a map centered on Tegucigalpa
  m = folium.Map(location=tegucigalpa_coords, zoom_start=12)
  
  # Define delivery zones (adjusted to reduce overlap)
  zones = {
      "Zona Norte": {
          "coordinates": [
              [14.1300, -87.2500],
              [14.1300, -87.1600],
              [14.0950, -87.1600],
              [14.0950, -87.2500]
          ],
          "color": "#00FF00"  # Green
      },
      "Zona Centro": {
          "coordinates": [
              [14.0950, -87.2200],
              [14.0950, -87.1850],
              [14.0700, -87.1850],
              [14.0700, -87.2200]
          ],
          "color": "#FF0000"  # Red
      },
      "Zona Este": {
          "coordinates": [
              [14.0950, -87.1850],
              [14.0950, -87.1500],
              [14.0600, -87.1500],
              [14.0600, -87.1850]
          ],
          "color": "#FFFF00"  # Yellow
      },
      "Zona Oeste": {
          "coordinates": [
              [14.1000, -87.2500],
              [14.1000, -87.2200],
              [14.0600, -87.2200],
              [14.0600, -87.2500]
          ],
          "color": "#FF00FF"  # Magenta
      },
      "Zona Sur": {
          "coordinates": [
              [14.0700, -87.2400],
              [14.0700, -87.1700],
              [14.0300, -87.1700],
              [14.0300, -87.2400]
          ],
          "color": "#0000FF"  # Blue
      }
  }
  
  # Add polygons for each zone
  for zone_name, zone_data in zones.items():
      folium.Polygon(
          locations=zone_data["coordinates"],
          color=zone_data["color"],
          fill=True,
          fill_color=zone_data["color"],
          fill_opacity=0.4,
          popup=zone_name
      ).add_to(m)
  
  # Add legend to the map
  legend_html = '''
  <div style="position: fixed; bottom: 50px; left: 50px; width: 120px; height: 160px; 
  border:2px solid grey; z-index:9999; font-size:14px; background-color:white;
  ">&nbsp;<b>Leyenda:</b><br>
  {% for zone, color in zones.items() %} 
  &nbsp;<i class="fa fa-map-marker" style="color:{{ color }}"></i>&nbsp;{{ zone }}<br>
  {% endfor %}
  </div>
  '''
  legend_template = Template(legend_html)
  macro = MacroElement()
  macro._template = legend_template
  m.get_root().add_child(macro)
  
  # Display the map
  folium_static(m)

def about_us():
  st.subheader("ℹ️ Sobre nosotros")
  st.write(""" 
  En Pasto Verde, creemos que cada mascota merece un toque de naturaleza en su vida diaria. Nuestra misión es llevar pasto fresco y exuberante directamente a tu puerta, brindando a tus amigos peludos una experiencia natural y placentera.
  🌿 ¿Por qué elegir Pasto Verde?
  Pasto fresco, libre de pesticidas
  Opciones de entrega convenientes
  Empaque ecológico
  ¡Mascotas felices, dueños felices!
  Únete a nosotros para hacer que el día de tu mascota sea un poco más verde y mucho más divertido.
  """)

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
def admin_dashboard():
  if st.session_state.user.type != UserType.admin:
      st.error("You don't have permission to access this page.")
      return
  st.subheader("📊 Admin Dashboard")
  
  session = Session()
  
  total_orders = session.query(Order).count()
  total_revenue = session.query(func.sum(Order.total_price)).scalar() or 0
  
  st.write(f"Total Orders: {total_orders}")
  st.write(f"Total Revenue: L. {total_revenue:.2f}")
  
  st.subheader("Recent Orders")
  recent_orders = session.query(Order).order_by(Order.date.desc()).limit(10).all()
  for order in recent_orders:
      st.write(f"Order ID: {order.id} - User: {order.user.name} - Total Price: L. {order.total_price:.2f} - Date: {order.date}")
  
  session.close()

if __name__ == "__main__":
  main()
