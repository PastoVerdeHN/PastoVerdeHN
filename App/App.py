import streamlit as st
from streamlit_folium import folium_static
import folium
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
from dotenv import load_dotenv
from auth0_component import login_button
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up the page configuration
st.set_page_config(
  page_title="Pasto Verde - Naturaleza en Casa para tus Mascotas",
  page_icon="🌿",
  layout="wide"
)

# Load environment variables
load_dotenv()

# Database setup
Base = declarative_base()
database_url = os.getenv("DATABASE_URL")

if not database_url:
  st.error("Database URL not found. Please set it in Streamlit secrets or as an environment variable.")
  st.stop()

engine = create_engine(database_url, echo=True)
Session = sessionmaker(bind=engine)

# SQLAlchemy models
class User(Base):
  __tablename__ = 'users'
  id = Column(String, primary_key=True)
  name = Column(String, nullable=False)
  email = Column(String, unique=True, nullable=False)
  type = Column(String, nullable=False)
  address = Column(String)

class Product(Base):
  __tablename__ = 'products'
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  description = Column(String)
  price = Column(Float, nullable=False)
  stock = Column(Integer, default=0)  # Added stock for inventory management

class Order(Base):
  __tablename__ = 'orders'
  id = Column(String, primary_key=True)
  user_id = Column(String, ForeignKey('users.id'))
  status = Column(String, nullable=False)
  total_amount = Column(Float)

class OrderItem(Base):
  __tablename__ = 'order_items'
  id = Column(Integer, primary_key=True)
  order_id = Column(String, ForeignKey('orders.id'))
  product_id = Column(Integer, ForeignKey('products.id'))
  quantity = Column(Integer, nullable=False)
  price = Column(Float)

Base.metadata.create_all(engine)

# Helper functions
def auth0_authentication():
  if 'user' not in st.session_state:
      st.session_state.user = None
  if 'auth_status' not in st.session_state:
      st.session_state.auth_status = None
  if st.session_state.user is None:
      auth_choice = st.sidebar.radio("Choose action", ["🔑 Entrar"])
      
      if auth_choice == "🔑 Entrar":
          try:
              AUTH0_CLIENT_ID = st.secrets["auth0"]["AUTH0_CLIENT_ID"]
              AUTH0_DOMAIN = st.secrets["auth0"]["AUTH0_DOMAIN"]
          except KeyError:
              st.error("Auth0 configuration not found.")
              return None
          
          user_info = login_button(
              AUTH0_CLIENT_ID, 
              domain=AUTH0_DOMAIN,
              redirect_uri="http://localhost:8501/callback"
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
              
              st.session_state.user = user
              st.session_state.auth_status = "authenticated"
              st.success(f"Bienvenido, {user.name}!")
  return st.session_state.user

def create_order(user_id: str, product_ids: list, quantities: list) -> dict:
  logging.info(f"Starting order creation for user_id: {user_id}")

  # Create a new session
  db = Session()

  try:
      # Get user from the database
      user = db.query(User).filter(User.id == user_id).first()
      if not user:
          return {"status": "error", "message": "User not found"}

      # Create an order record
      new_order = Order(user_id=user_id, status="Pending")
      db.add(new_order)
      db.commit()

      # Add order items
      total_amount = 0
      for product_id, quantity in zip(product_ids, quantities):
          product = db.query(Product).filter(Product.id == product_id).first()
          if not product:
              return {"status": "error", "message": f"Product ID {product_id} not found"}

          if quantity > product.stock:
              return {"status": "error", "message": f"Not enough stock for Product ID {product_id}"}

          # Create order item
          order_item = OrderItem(order_id=new_order.id, product_id=product_id, quantity=quantity, price=product.price)
          db.add(order_item)
          
          # Update stock
          product.stock -= quantity
          total_amount += product.price * quantity

      # Update total amount in order
      new_order.total_amount = total_amount
      db.commit()

      logging.info(f"Order created successfully with ID: {new_order.id}")
      return {"status": "success", "order_id": new_order.id}
  
  except Exception as e:
      db.rollback()
      logging.error(f"Error occurred: {str(e)}")
      return {"status": "error", "message": "An error occurred while creating the order."}

  finally:
      db.close()
      logging.info("Order creation process completed.")

def place_order():
  st.subheader("🛒 Realizar pedido")
  session = Session()
  
  # Fetch products from the database
  products = session.query(Product).all()

  # Display products for selection
  product_ids = [product.id for product in products]
  quantities = []

  for product in products:
      quantity = st.number_input(f"Cantidad para {product.name} (ID: {product.id})", min_value=1, value=1)
      quantities.append(quantity)

  if st.button("Confirmar pedido"):
      result = create_order(st.session_state.user.id, product_ids, quantities)

      if result['status'] == "success":
          st.success(f"¡Pedido realizado con éxito! Order ID: {result['order_id']}")
      else:
          st.error(f"Error: {result['message']}")

  session.close()

def display_user_orders():
  st.subheader("📦 Mis Ordenes")
  
  session = Session()
  orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
  
  for order in orders:
      with st.expander(f"Order ID: {order.id} - Status: {order.status}"):
          st.write(f"Total Amount: ${order.total_amount:.2f}")
  
  session.close()

def main():
  st.title("🌿 Pasto Verde - Pet Grass Delivery")
  user = auth0_authentication()
  
  if user:
      # Display menu items as buttons
      menu_items = {
          "🏠 Inicio": home_page,
          "🛒 Ordene Ahora": place_order,
          "📦 Mis Ordenes": display_user_orders,
          "🗺️ Zona De Envios": display_map,
          "ℹ️ Sobre Nosotros": about_us,
      }

      cols = st.columns(len(menu_items))
      for i, (emoji_label, func) in enumerate(menu_items.items()):
          if cols[i].button(emoji_label):
              st.session_state.current_page = emoji_label
              func()  # Call the function directly

      if st.sidebar.button("🚪 Log Out"):
          for key in list(st.session_state.keys()):
              del st.session_state[key]
          st.success("Logged out successfully.")
          st.rerun()
  else:
      st.write("Por favor inicie sesión para acceder a los servicios de Pasto Verde")

def home_page():
  st.write(f"Bienvenido/a Pasto Verde, {st.session_state.user.name}! 🌿")
  st.write("¡Llevando pasto fresco a tus mascotas, una caja a la vez!")
  
  session = Session()
  products = session.query(Product).all()
  st.subheader("Nuestros Servicios")
  for product in products:
      st.write(f"- {product.name}: ${product.price:.2f}")
      st.write(product.description)
  session.close()

def display_map():
  st.subheader("🗺️ Zona de Entrega")
  
  # Coordinates for Tegucigalpa
  tegucigalpa_coords = [14.0818, -87.2068]
  
  # Create a map centered on Tegucigalpa
  m = folium.Map(location=tegucigalpa_coords, zoom_start=12)
  
  # Define delivery zones
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

if __name__ == "__main__":
  main()
