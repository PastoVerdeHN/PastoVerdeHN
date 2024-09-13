import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import time
import sqlalchemy
from dataclasses import dataclass
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os
from dotenv import load_dotenv
from auth0_component import login_button
import sys

st.set_page_config(
    page_title="Pasto Verde - Naturaleza en Casa para tus Mascotas",
    page_icon="🌿",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Database setup
Base = declarative_base()

# Try to get the database URL from Streamlit secrets, fall back to environment variable if not found
try:
    database_url = st.secrets["database"]["url"]
except KeyError:
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

class Order(Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    delivery_address = Column(String, nullable=False)
    status = Column(String, nullable=False)
    user = relationship("User")
    product = relationship("Product")

Base.metadata.create_all(engine)

# Helper functions
def generate_order_id():
    return f"ORD-{random.randint(10000, 99999)}"

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
                
                st.session_state.user = user
                st.session_state.auth_status = "authenticated"
                st.success(f"Bienvenido, {user.name}!")
        elif auth_choice == "📄 Terms and Conditions":
            st.switch_page("/Terms_and_Conditions.py")

    return st.session_state.user

def main():
    st.title("🌿 Pasto Verde - Pet Grass Delivery")
    user = auth0_authentication()

    if user:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"

        menu_items = {
            "🏠 Inicio": home_page,
            "🛒  Ordene Ahora": place_order,
            "📦 Mis Ordenes": display_user_orders,
            "🗺️ Zona De Envios": display_map,
            "ℹ️ Sobre Nosotros": about_us,
        }
        if user.type == 'admin':
            menu_items["📊 Admin Dashboard"] = admin_dashboard

        cols = st.columns(len(menu_items))
        for i, (emoji_label, func) in enumerate(menu_items.items()):
            if cols[i].button(emoji_label):
                st.session_state.current_page = emoji_label

        menu_items[st.session_state.current_page]()

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

def place_order():
    st.subheader("🛒 Realizar pedido")
    
    session = Session()
    products = session.query(Product).all()
    
    selected_product = st.selectbox("Elige tu plan:", [p.name for p in products])
    quantity = st.number_input("Quantity:", min_value=1, value=1)
    delivery_date = st.date_input("Delivery Date:", min_value=datetime.now().date())
    delivery_address = st.text_input("Delivery Address:", value=st.session_state.user.address)
    
    product = next(p for p in products if p.name == selected_product)
    total_price = product.price * quantity
    
    st.write(f"Total Price: ${total_price:.2f}")
    
    if st.button("Realizar pedido"):
        new_order = Order(
            id=generate_order_id(),
            user_id=st.session_state.user.id,
            product_id=product.id,
            quantity=quantity,
            date=delivery_date,
            delivery_address=delivery_address,
            status='Pending'
        )
        session.add(new_order)
        session.commit()
        st.success("Pedido Exitoso!")
    
    session.close()

def display_user_orders():
    st.subheader("📦 Mis Ordenes")
    
    session = Session()
    orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
    
    for order in orders:
        with st.expander(f"Order ID: {order.id} - Status: {order.status}"):
            st.write(f"Product: {order.product.name}")
            st.write(f"Quantity: {order.quantity}")
            st.write(f"Delivery Date: {order.date}")
            st.write(f"Delivery Address: {order.delivery_address}")
    
    session.close()

def display_map():
    st.subheader("🗺️ Zona de Entrega")
    
    # Coordinates for Tegucigalpa
    tegucigalpa_coords = [14.0818, -87.2068]
    
    # Create a map centered on Tegucigalpa
    m = folium.Map(location=tegucigalpa_coords, zoom_start=12)
    
    # Define delivery zones (adjusted based on the new image)
    zones = {
        "Zona Norte": {
            "coordinates": [
                [14.1200, -87.2400],
                [14.1200, -87.1700],
                [14.0950, -87.1700],
                [14.0950, -87.2400]
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
                [14.0950, -87.2400],
                [14.0950, -87.2200],
                [14.0600, -87.2200],
                [14.0600, -87.2400]
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
    
    # Create a legend
    st.subheader("Leyenda")
    for zone_name, zone_data in zones.items():
        st.markdown(
            f'<span style="color:{zone_data["color"]};">■</span> {zone_name}',
            unsafe_allow_html=True
        )

    # Dropdown for zone selection
    selected_zone = st.selectbox(
        "Seleccione su zona de entrega:",
        list(zones.keys())
    )
    
    if selected_zone:
        st.write(f"Has seleccionado: {selected_zone}")

# Call the function to display the map
display_map()

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

def admin_dashboard():
    if st.session_state.user.type != 'admin':
        st.error("You don't have permission to access this page.")
        return

    st.subheader("📊 Admin Dashboard")
    
    session = Session()
    
    total_orders = session.query(Order).count()
    total_revenue = session.query(sqlalchemy.func.sum(Order.quantity * Product.price)).join(Product).scalar() or 0
    
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
