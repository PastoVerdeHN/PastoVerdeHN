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
from models import User, Product, Order, setup_database
from geopy.geocoders import Nominatim
import time
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
                  user = User(
                      id=user_info['sub'],
                      name=user_info['name'],
                      email=user_info['email'],
                      type='customer',
                      address=''
                  )
                  session.add(user)
                  session.commit()
                  send_welcome_email(user.email, user.name)
              
              st.session_state.user = user
              st.session_state.auth_status = "authenticated"
              st.success(f"Bienvenido, {user.name}!")
  return st.session_state.user

def main():
  st.title("Pasto Verde - Entrega de pasto para mascotas")
  user = auth0_authentication()
  
  if user:
      if 'current_page' not in st.session_state:
          st.session_state.current_page = "🏠 Inicio"  # Default page
      
      menu_items = {
          "🏠 Inicio": home_page,
          "🛒  Ordene Ahora": place_order,
          "📦 Mis Órdenes": display_user_orders,
          "🗺️ Zona De Envios": display_map,
          "ℹ️ Sobre Nosotros": about_us,
      }
      
      if user.type == 'admin':
          menu_items["📊 Admin Dashboard"] = admin_dashboard
      
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
    
def home_page():
  st.write(f"Bienvenido/a Pasto Verde, {st.session_state.user.name}! 🌿")
  st.write("¡Llevando pasto fresco a tus mascotas, una caja a la vez!")
  
  # Video section
  st.subheader("Conozca Pasto Verde")
  video_file = open('PastoVerdeHN/PASTO VERDE AD FINAL.mp4', 'rb')
  video_bytes = video_file.read()
  st.video(video_bytes)

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

  # Order Review
  if selected_plan and st.session_state.map_center:
      with st.expander("Resumen del Pedido", expanded=True):
          st.write(f"Plan seleccionado: **{selected_plan}**")
          
          lempira_price = plans[selected_plan]['price']
          if selected_plan != "Sin Suscripción":
              st.write(f"Precio: L. {lempira_price:.2f} por mes")
          else:
              st.write(f"Precio: L. {lempira_price:.2f}")
          
          st.write("Cambio de dólar: 1$ = L.25.00")
          st.write(f"Dirección de entrega: {full_address}")

      if st.button("Confirmar pedido"):
          if selected_plan == "Suscripción Anual":
              paypal_html = '''
              <div id="paypal-button-container-P-4E978587FL636905DM3UPY3Q"></div>
              <script src="https://www.paypal.com/sdk/js?client-id=Ad_76woIrZWXf2QX3KYxFd-iAKTTCqxTtLYB0GOYK4weEQYf52INL5SREytqj4mY84BOVy9wWTsrvcxI&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
              <script>
                paypal.Buttons({
                    style: {
                        shape: 'pill',
                        color: 'black',
                        layout: 'horizontal',
                        label: 'subscribe'
                    },
                    createSubscription: function(data, actions) {
                      return actions.subscription.create({
                        plan_id: 'P-4E978587FL636905DM3UPY3Q'
                      });
                    },
                    onApprove: function(data, actions) {
                      alert('¡Suscripción Anual realizada con éxito! 🎉 ID de suscripción: ' + data.subscriptionID);
                      window.location.reload();
                    },
                    onError: function(err) {
                      alert('Error al procesar el pago. Intenta de nuevo.');
                    }
                }).render('#paypal-button-container-P-4E978587FL636905DM3UPY3Q');
              </script>
              '''
              components.html(paypal_html, height=300)
          elif selected_plan == "Suscripción Mensual":
              paypal_html = '''
              <div id="paypal-button-container-P-8JD80124L6471951GM3UKKHA"></div>
              <script src="https://www.paypal.com/sdk/js?client-id=Ad_76woIrZWXf2QX3KYxFd-iAKTTCqxTtLYB0GOYK4weEQYf52INL5SREytqj4mY84BOVy9wWTsrvcxI&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
              <script>
                paypal.Buttons({
                    style: {
                        shape: 'pill',
                        color: 'blue',
                        layout: 'horizontal',
                        label: 'subscribe'
                    },
                    createSubscription: function(data, actions) {
                      return actions.subscription.create({
                        plan_id: 'P-8JD80124L6471951GM3UKKHA'
                      });
                    },
                    onApprove: function(data, actions) {
                      alert('¡Pedido realizado con éxito! 🎉');
                      window.location.reload();
                    },
                    onError: function(err) {
                      alert('Error al procesar el pago. Intenta de nuevo.');
                    }
                }).render('#paypal-button-container-P-8JD80124L6471951GM3UKKHA');
              </script>
              '''
              components.html(paypal_html, height=300)
          elif selected_plan == "Suscripción Semestral":
              paypal_html = '''
              <div id="paypal-button-container-P-79741958WR506740HM3UPLFA"></div>
              <script src="https://www.paypal.com/sdk/js?client-id=Ad_76woIrZWXf2QX3KYxFd-iAKTTCqxTtLYB0GOYK4weEQYf52INL5SREytqj4mY84BOVy9wWTsrvcxI&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
              <script>
                paypal.Buttons({
                    style: {
                        shape: 'pill',
                        color: 'gold',
                        layout: 'horizontal',
                        label: 'subscribe'
                    },
                    createSubscription: function(data, actions) {
                      return actions.subscription.create({
                        plan_id: 'P-79741958WR506740HM3UPLFA'
                      });
                    },
                    onApprove: function(data, actions) {
                      alert('¡Pedido realizado con éxito! 🎉 ID de suscripción: ' + data.subscriptionID);
                      window.location.reload();
                    },
                    onError: function(err) {
                      alert('Error al procesar el pago. Intenta de nuevo.');
                    }
                }).render('#paypal-button-container-P-79741958WR506740HM3UPLFA');
              </script>
              '''
              components.html(paypal_html, height=300)
          else:  # Sin Suscripción (one-time purchase)
              paypal_html = '''
              <script src="https://www.paypal.com/sdk/js?client-id=BAAmZb8q_th0dhU_yFYAOp1HcFnZXsBa-Hf3qv-QhyDOOit1Qvkjc5_3rBFkG8s4VjvmVOyqrh_B7n1Ic0&components=hosted-buttons&disable-funding=venmo&currency=USD"></script>
              <div id="paypal-container-AMM5P24GTYSR8"></div>
              <script>
                paypal.HostedButtons({
                  hostedButtonId: "AMM5P24GTYSR8",
                  onApprove: function(data) {
                    alert('¡Compra realizada con éxito! 🎉 ID de transacción: ' + data.orderID);
                    window.location.reload();
                  },
                  onError: function(err) {
                    alert('Error al procesar el pago. Intenta de nuevo.');
                    console.error('PayPal error:', err);
                  }
                }).render("#paypal-container-AMM5P24GTYSR8");
              </script>
              '''
              components.html(paypal_html, height=300)

  session.close()

def display_user_orders():
  st.subheader("📦 Mis Órdenes")
  
  session = Session()
  orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
  
  for order in orders:
      with st.expander(f"Order ID: {order.id} - Status: {order.status}"):
          st.write(f"Delivery Date: {order.date}")
          st.write(f"Delivery Address: {order.delivery_address}")
          if order.product_id:
              product = session.query(Product).filter_by(id=order.product_id).first()
              if product:
                  st.write(f"Product: {product.name} - Price: ${product.price:.2f}")

  session.close()

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

  message = MIMEMultipart("alternative")
  message["Subject"] = "Welcome to Pasto Verde!"
  message["From"] = sender_email
  message["To"] = user_email

  text = f"""\
  Hola {user_name},
  
  ¡Bienvenido a Pasto Verde! Gracias por registrarte en nuestra plataforma.
  
  Estamos emocionados de tenerte con nosotros y esperamos que disfrutes de nuestros servicios de entrega de pasto fresco para tus mascotas.
  
  Si tienes alguna pregunta, no dudes en contactarnos.
  
  ¡Que tengas un gran día!
  
  El equipo de Pasto Verde
  """

  html = f"""\
  <html>
    <body>
      <p>Hola {user_name},</p>
      <p>¡Bienvenido a Pasto Verde! Gracias por registrarte en nuestra plataforma.</p>
      <p>Estamos emocionados de tenerte con nosotros y esperamos que disfrutes de nuestros servicios de entrega de pasto fresco para tus mascotas.</p>
      <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
      <p>¡Que tengas un gran día!</p>
      <p>El equipo de Pasto Verde</p>
    </body>
  </html>
  """

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  try:
      with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
          server.starttls()
          server.login(sender_email, sender_password)
          server.sendmail(sender_email, user_email, message.as_string())
      print(f"Welcome email sent to {user_email}")
  except Exception as e:
      print(f"Error sending email to {user_email}: {str(e)}")

def admin_dashboard():
  if st.session_state.user.type != 'admin':
      st.error("You don't have permission to access this page.")
      return
  st.subheader("📊 Admin Dashboard")
  
  session = Session()
  
  total_orders = session.query(Order).count()
  total_revenue = session.query(func.sum(Product.price)).join(Order).scalar() or 0
  
  st.write(f"Total Orders: {total_orders}")
  st.write(f"Total Revenue: ${total_revenue:.2f}")
  
  st.subheader("Recent Orders")
  recent_orders = session.query(Order).order_by(Order.date.desc()).limit(10).all()
  for order in recent_orders:
      st.write(f"Order ID: {order.id} - User: {order.user.name} - Product: {order.product.name} - Date: {order.date}")
  
  session.close()
  st.sidebar.markdown("---")
  if st.sidebar.button("Pagina Web"):
      st.switch_page("pages/pagina_web.py")

if __name__ == "__main__":
  main()
