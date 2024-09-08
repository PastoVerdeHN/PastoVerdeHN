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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Pages.Terms_and_Conditions import main as terms_and_conditions_main

# New imports for LiveKit integration
from livekit_client import RoomServiceClient, Room, RTCStats
from streamlit_livekit import LiveKitComponent
import asyncio
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Pasto Verde - Pet Grass Delivery",
    page_icon="🌿",
    layout="wide"
)

# Load environment variables
load_dotenv()

# LiveKit configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_HOST = os.getenv("LIVEKIT_HOST")

if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_HOST]):
    st.error("LiveKit configuration not found. Please set LIVEKIT_API_KEY, LIVEKIT_API_SECRET, and LIVEKIT_HOST in your environment variables.")
    st.stop()

# Initialize LiveKit client
room_service = RoomServiceClient(
    host=LIVEKIT_HOST,
    api_key=LIVEKIT_API_KEY,
    api_secret=LIVEKIT_API_SECRET
)

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
        auth_choice = st.sidebar.radio("Choose action", ["🔑 Entrar",])
        
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
            st.sidebar.markdown("# Terms and Conditions")
            st.sidebar.markdown("Please read our terms and conditions here.")

    return st.session_state.user

def livekit_component():
    st.subheader("LiveKit Voice Chat and Screen Share")
    
    if 'livekit_room' not in st.session_state:
        st.session_state.livekit_room = None

    if st.button("Start Voice Chat"):
        try:
            room_name = f"pasto-verde-{st.session_state.user.id}"
            token = room_service.create_token(room_name, st.session_state.user.name)
            st.session_state.livekit_room = Room(room_name, token)
            st.success("Voice chat started!")
            st.audio("path/to/start_chat_sound.mp3")  # Add a sound effect
        except Exception as e:
            logger.error(f"Error starting voice chat: {str(e)}")
            st.error("Failed to start voice chat. Please try again.")

    if st.session_state.livekit_room:
        livekit_component = LiveKitComponent(
            room=st.session_state.livekit_room,
            audio=True,
            video=False,
            screen_share=True
        )
        st.write(livekit_component)

        if st.button("End Voice Chat"):
            try:
                st.session_state.livekit_room.disconnect()
                st.session_state.livekit_room = None
                st.success("Voice chat ended!")
                st.audio("path/to/end_chat_sound.mp3")  # Add a sound effect
            except Exception as e:
                logger.error(f"Error ending voice chat: {str(e)}")
                st.error("Failed to end voice chat. Please try again.")

    # Display active users
    if st.session_state.livekit_room:
        st.subheader("Active Users")
        for participant in st.session_state.livekit_room.participants:
            st.write(f"- {participant.name}")

def main():
    st.title("🌿 Pasto Verde - Pet Grass Delivery")
    user = auth0_authentication()

    if user:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"

        menu_items = {
            "🏠 Home": home_page,
            "🛒 Order Now": place_order,
            "📦 My Orders": display_user_orders,
            "🗺️ Delivery Map": display_map,
            "ℹ️ About us": about_us,
            "🎙️ Voice Chat": livekit_component,
        }
        if user.type == 'admin':
            menu_items["📊 Admin Dashboard"] = admin_dashboard

        cols = st.columns(len(menu_items))
        for i, (emoji_label, func) in enumerate(menu_items.items()):
            if cols[i].button(emoji_label):
                st.session_state.current_page = emoji_label

        menu_items[st.session_state.current_page]()

        if st.sidebar.button("🚪 Log Out"):
            # Clear the session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully.")
            st.rerun()

    else:
        st.write("Please log in to access Pasto Verde services")

    st.sidebar.markdown("---")
    st.sidebar.markdown("[Terms and Conditions](/App/Pages/Terms_and_Conditions.py)")

def home_page():
    st.write(f"Welcome to Pasto Verde, {st.session_state.user.name}! 🌿")
    st.write("Bringing fresh grass to your pets, one box at a time!")
    
    session = Session()
    products = session.query(Product).all()
    st.subheader("Our Products")
    for product in products:
        st.write(f"- {product.name}: ${product.price:.2f}")
        st.write(product.description)
    session.close()

def place_order():
    st.subheader("🛒 Place Your Order")
    
    session = Session()
    products = session.query(Product).all()
    
    selected_product = st.selectbox("Choose your grass type:", [p.name for p in products])
    quantity = st.number_input("Quantity:", min_value=1, value=1)
    delivery_date = st.date_input("Delivery Date:", min_value=datetime.now().date())
    delivery_address = st.text_input("Delivery Address:", value=st.session_state.user.address)
    
    product = next(p for p in products if p.name == selected_product)
    total_price = product.price * quantity
    
    st.write(f"Total Price: ${total_price:.2f}")
    
    if st.button("Place Order"):
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
        st.success("Order placed successfully!")
    
    session.close()

def display_user_orders():
    st.subheader("📦 My Orders")
    
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
    st.subheader("🗺️ Delivery Map")
    
    # This is a placeholder. You'd need to implement actual delivery locations.
    m = folium.Map(location=[15.5, -88.0], zoom_start=7)
    folium_static(m)

def about_us():
    st.subheader("ℹ️ About us")
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

if __name__ == "__main__":
    main()
