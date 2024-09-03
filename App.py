import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import pandas as pd
import numpy as np
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
from sqlalchemy import inspect
from functools import lru_cache
from pystrix import Manager

st.set_page_config(
    page_title="Entrar",
    page_icon="👋",
)

st.title("🚚 Pasto Verde")
st.sidebar.success("Select a page above.")

if "my_input" not in st.session_state:
    st.session_state["my_input"] = ""

my_input = st.text_input("Input a text here", st.session_state["my_input"])
submit = st.button("Submit")
if submit:
    st.session_state["my_input"] = my_input
    st.write("You have entered: ", my_input)




# Apply the color theme
st.set_page_config(page_title="Pasto Verde ", page_icon="https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/d26adea290c05289558f49c35697a7a491eb0f81/logo2.jpg", layout="wide")

# Load environment variables
load_dotenv()

AUTH0_CLIENT_ID = st.secrets["auth0"]["AUTH0_CLIENT_ID"]
AUTH0_DOMAIN = st.secrets["auth0"]["AUTH0_DOMAIN"]
AUTH0_CALLBACK_URL = os.getenv("https://PastoVerdeHN.streamlit.app/")

# SQLAlchemy setup
Base = sqlalchemy.orm.declarative_base()
engine = create_engine(st.secrets["database"]["url"], echo=True)
Session = sessionmaker(bind=engine)

# SQLAlchemy models
class User(Base):
    __tablename__ = 'usuarios'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    address = Column(String)

class Merchant(Base):
    __tablename__ = 'subs'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    website = Column(String)

class Order(Base):
    __tablename__ = 'ordenes'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    merchant_id = Column(Integer, ForeignKey('merchants.id'))
    service = Column(String)
    date = Column(DateTime, nullable=False)
    time = Column(String, nullable=False)
    address = Column(String, nullable=False)
    status = Column(String, nullable=False)
    user = relationship("User")
    merchant = relationship("Merchant")

@dataclass
class Service:
    name: str
    url: str
    instructions: list
    video_url: str = None
    video_title: str = None
    image_url: str = None
    address: str = None
    phone: str = None
    hours: str = None

Base.metadata.create_all(engine, checkfirst=True)
print("Database tables created successfully (or already exist).")

# Geocoding cache
geocoding_cache = {}

# Helper functions
def generate_order_id():
    return f"ORD-{random.randint(10000, 99999)}"

def is_terms_page():
    ctx = get_script_run_ctx()
    return ctx.page_script_hash == "terms_and_conditions"

# Color palette
PRIMARY_COLOR = "#FF4B4B"
SECONDARY_COLOR = "#0068C9"
BACKGROUND_COLOR = "#F0F2F6"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
    }}
    .stButton>button {{
        color: white;
        background-color: {PRIMARY_COLOR};
        border-radius: 20px;
    }}
    .stProgress > div > div > div > div {{
        background-color: {SECONDARY_COLOR};
    }}
    </style>
    """, unsafe_allow_html=True)

# Define GROCERY_STORES and RESTAURANTS dictionaries
GROCERY_STORES = {
    
}

RESTAURANTS = {

}

def auth0_authentication():
    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        auth_choice = st.sidebar.radio("Choose action", ["🔑 Entrar,📄Terms and Conditions"])
        
        if auth_choice == "🔑 Entrar":
            user_info = login_button(AUTH0_CLIENT_ID, domain=AUTH0_DOMAIN)
            
            if user_info:
                session = Session()
                user = session.query(User).filter_by(email=user_info['email']).first()
                if not user:
                    # Create a new user if they don't exist in your database
                    user = User(
                        id=user_info['sub'],
                        name=user_info['name'],
                        email=user_info['email'],
                        type='customer',  # Default type, can be updated later
                        address=''  # Can be updated later
                    )
                    session.add(user)
                    session.commit()
                
                st.session_state.user = user
                st.success(f"Bienvenido, {user.name}!")
                st.experimental_rerun()

    return st.session_state.user

def main():
    user = auth0_authentication()

    if user:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"

        # Creative menu
        menu_items = {
            "🏠 Home": home_page,
            "🛒 Order Now": place_order,
            "📦 My Orders": display_user_orders,
            "🗺️ Map": display_map,
            "🛍️ Services": display_services,
            "🎦 Live": live_shop
        }
        if user.type == 'driver':
            menu_items["🚗 Driver Dashboard"] = driver_dashboard

        cols = st.columns(len(menu_items))
        for i, (emoji_label, func) in enumerate(menu_items.items()):
            if cols[i].button(emoji_label):
                st.session_state.current_page = emoji_label

        # Display the current page
        menu_items[st.session_state.current_page]()

        if st.sidebar.button("🚪 Log Out,📄 Terms and Conditions"):
            st.session_state.user = None
            st.success("Logged out successfully.")
            st.experimental_rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")
    
    else:
        st.write("Please log in to access the full features of the app")
        st.sidebar.markdown("---")
        st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")
    
    else:
        st.write("Please log in to access the full features of the app")
        st.sidebar.markdown("---")
        st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")

def home_page():
    st.write(f"Bienvenidos a PASTO VERDE Honduras, {st.session_state.user.name}! 🎉")
    session = Session()
    merchants = session.query(Merchant).all()
    st.write("Servicios Disponibles")
    for merchant in merchants:
        st.write(f"- {merchant.name}")

def place_order():
    st.subheader("🛍️ Nueva Orden")
    if 'selected_merchant_type' not in st.session_state:
        st.session_state.selected_merchant_type = None
    if 'selected_merchant' not in st.session_state:
        st.session_state.selected_merchant = None
    if 'service' not in st.session_state:
        st.session_state.service = ""
    if 'date' not in st.session_state:
        st.session_state.date = datetime.now().date()
    if 'time' not in st.session_state:
        st.session_state.time = "07:00 AM EST"
    if 'address' not in st.session_state:
        st.session_state.address = st.session_state.user.address if st.session_state.user else ""
    if 'review_clicked' not in st.session_state:
        st.session_state.review_clicked = False

    session = Session()
    
    # Step 1: Select merchant type
    merchant_type = st.selectbox("Servicios", ["Restaurants", "Groceries"], key='selected_merchant_type')

    # Step 2: Select specific merchant based on type
    if merchant_type == "Restaurants":
        merchant = st.selectbox("Select Restaurant", list(RESTAURANTS.keys()), key='selected_merchant')
    else:
        merchant = st.selectbox("Select Grocery Store", list(GROCERY_STORES.keys()), key='selected_merchant')
 
    date = st.date_input("Select Date", min_value=datetime.now().date(), key='date')
    order_time = st.selectbox("Select Time", 
                        [f"{h:02d}:{m:02d} {'AM' if h < 12 else 'PM'} EST" 
                         for h in range(7, 22) for m in [0, 15, 30, 45]],
                        key='time')
    
    address = st.text_input("Delivery Address", value=st.session_state.address, key='address')
    
    if address:
        geolocator = Nominatim(user_agent="local_butler_app")
        try:
            location = geolocator.geocode(address)
            if location:
                m = folium.Map(location=[location.latitude, location.longitude], zoom_start=15)
                folium.Marker([location.latitude, location.longitude]).add_to(m)
                folium_static(m)
                
                # Update address with full address from geocoding
                address = location.address
                st.text_input("Verified address (you can edit if needed):", value=address, key="verified_address")
                st.write(f"Coordinates: {location.latitude}, {location.longitude}")
                
                # Add delivery notes text area
                delivery_notes = st.text_area("Delivery Notes (optional)")
            else:
                st.warning("Unable to locate the address. Please check and try again.")
        except Exception as e:
            st.error(f"An error occurred while processing the address: {str(e)}")

    if st.button("Review Order"):
        st.session_state.review_clicked = True

    if st.session_state.review_clicked:
        with st.expander("Order Details", expanded=True):
            st.write(f"Merchant Type: {merchant_type}")
            st.write(f"Merchant: {merchant}")
            st.write(f"Date: {date}")
            st.write(f"Time: {order_time}")
            st.write(f"Delivery Address: {address}")
            if 'delivery_notes' in locals():
                st.write(f"Delivery Notes: {delivery_notes}")

        if st.button("🚀 Confirmar Orden", key='confirmar_orden_button'):
            if not all([merchant, date, order_time, address]):
                st.error("Por Favor ")
            else:
                try:
                    order_id = generate_order_id()
                    new_order = Order(
                        id=order_id,
                        user_id=st.session_state.user.id,
                        merchant_id=merchant,
                        date=date,
                        time=order_time,
                        address=address,
                        status='Pendiente'
                    )
                    session.add(new_order)
                    session.commit()
                    
                    # Animated order confirmation
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        status_text.text(f"Orden... {i+1}%")
                        time.sleep(0.01)
                    status_text.text("TU ORDEN 🎉")
                    st.success(f"Numero de Orden {order_id}")
                    st.balloons()
                    
                    # Reset the review state
                    st.session_state.review_clicked = False
                except Exception as e:
                    st.error(f"error TU ORDEN: {str(e)}")
                    session.rollback()
                finally:
                    session.close()

def display_user_orders():
    st.subheader("📦 Mis Ordenes")
    
    session = Session()
    user_orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
    
    if not user_orders:
        st.info("Aun no tienes Ordenes.")
    else:
        for order in user_orders:
            with st.expander(f"🛍️ Order ID: {order.id} - Status: {order.status}"):
                st.write(f"📅 Date: {order.date}")
                st.write(f"🕒 Time: {order.time}")
                st.write(f"📍 Address: {order.address}")
                
                merchant = session.query(Merchant).filter_by(id=order.merchant_id).first()
                if merchant:
                    st.write(f"🏪 Merchant: {merchant.name}")
                else:
                    st.write("🏪 Merchant: Not available")
                
                if order.service:
                    st.write(f"🛒 Service: {order.service}")
                
                # Order status display
                statuses = ['Pendiente', 'Preparando', 'En Camino', 'Entregado']
                status_emojis = ['⏳', '👨‍🍳', '🚚', '✅']
                current_status_index = statuses.index(order.status)
                
                # Calculate progress based on current status
                progress = (current_status_index + 1) * 25
                
                st.write("Orden Progreso:")
                
                # Display progress bar
                progress_bar = st.progress(progress)
                
                # Display status indicators on the same line
                status_cols = st.columns(4)
                for i, (status, emoji) in enumerate(zip(statuses, status_emojis)):
                    with status_cols[i]:
                        if i < current_status_index:
                            st.markdown(f"<p style='text-align: center; color: green;'>{emoji}<br>{status}</p>", unsafe_allow_html=True)
                        elif i == current_status_index:
                            st.markdown(f"<p style='text-align: center; color: blue; font-weight: bold;'>{emoji}<br>{status}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='text-align: center; color: gray;'>{emoji}<br>{status}</p>", unsafe_allow_html=True)
                
                # Live order status update
                status_placeholder = st.empty()
                progress_bar = st.progress(0)
                
                # Update progress bar
                progress_bar.progress((current_status_index + 1) * 25)
                
                # Fading effect for current status
                for _ in range(5):  # Repeat the fading effect 5 times
                    for opacity in [1.0, 0.7, 0.4, 0.7, 1.0]:
                        status_placeholder.markdown(
                            f"<p style='text-align: center; font-size: 24px; opacity: {opacity};'>"
                            f"Current Status: {status_emojis[current_status_index]} {statuses[current_status_index]}"
                            f"</p>",
                            unsafe_allow_html=True
                        )
                        time.sleep(0.2)
                
                # Keep the final status displayed
                status_placeholder.markdown(
                    f"<p style='text-align: center; font-size: 24px;'>"
                    f"Current Status: {status_emojis[current_status_index]} {statuses[current_status_index]}"
                    f"</p>",
                    unsafe_allow_html=True
                )
    
    session.close()

def driver_dashboard():
    st.subheader("🚗 Driver Dashboard")
    session = Session()
    
    # Create an empty container for orders
    orders_container = st.empty()
    
    while True:
        available_orders = session.query(Order).filter_by(status='Pending').all()
        
        with orders_container.container():
            if not available_orders:
                st.info("Esperando nuevas ordenes... ⏳")
            else:
                for order in available_orders:
                    with st.expander(f"📦 Numero de Orden: {order.id}"):
                        merchant = session.query(Merchant).filter_by(id=order.merchant_id).first()
                        st.write(f"🏪 Pickup: {merchant.name if merchant else 'No Disponible'}")
                        st.write(f"📍 Direccion: {order.address}")
                        if st.button(f"✅ Acceptar Orden {order.id}", key=f"accept_{order.id}"):
                            order.status = 'Preparando'
                            session.commit()
                            st.success(f"Aceptastes Nueva Orden {order.id} 🎉")
                            time.sleep(2)  # Give time for the success message to be seen
                            st.experimental_rerun()  # Rerun the app to update the order list
        
        time.sleep(10)  # Check for new orders every 10 seconds
        session.commit()  # Refresh the session to get the latest data

    session.close()

def display_services():
    st.subheader("🛍️ Ordenes Dispibles")
    
    st.write("### 🛒 Grocery Stores")
    for store_name, store_info in GROCERY_STORES.items():
        with st.expander(store_name):
            display_service(Service(
                name=store_name,
                url=store_info['url'],
                instructions=store_info['instructions'],
                video_url=store_info.get('video_url'),
                video_title=store_info.get('video_title'),
                image_url=store_info.get('image_url'),
                address=store_info['address'],
                phone=store_info['phone']
            ))
    
    st.write("### 🍽️ Restaurants")
    for restaurant_name, restaurant_info in RESTAURANTS.items():
        with st.expander(restaurant_name):
            display_service(Service(
                name=restaurant_name,
                url=restaurant_info['url'],
                instructions=restaurant_info['instructions'],
                image_url=restaurant_info.get('image_url'),
                address=restaurant_info['address'],
                phone=restaurant_info['phone']
            ))



if __name__ == "__main__":
    main()
