import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import time
from dataclasses import dataclass
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os
from dotenv import load_dotenv
from auth0_component import login_button
from sqlalchemy import inspect
from functools import lru_cache

# Load environment variables
load_dotenv()

# Database setup
Base = declarative_base()
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    address = Column(String)
    type = Column(String)  # 'customer' or 'admin'
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="orders")
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product")
    quantity = Column(Integer)
    total_price = Column(Float)
    order_date = Column(DateTime, default=datetime.utcnow)
    is_subscription = Column(Boolean, default=False)
    delivery_frequency = Column(String, nullable=True)  # 'weekly', 'biweekly', 'monthly'
    next_delivery_date = Column(DateTime, nullable=True)
    status = Column(String, default='Pending')  # 'Pending', 'Shipped', 'Delivered'

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)

# Create tables
Base.metadata.create_all(engine)

# Authentication
def auth0_authentication():
    user_info = login_button(
        auth0_client_id=os.getenv("AUTH0_CLIENT_ID"),
        domain=os.getenv("AUTH0_DOMAIN"),
        auth0_client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
        redirect_path=os.getenv("AUTH0_CALLBACK_URL")
    )
    if user_info:
        session = Session()
        user = session.query(User).filter_by(email=user_info['email']).first()
        if not user:
            user = User(name=user_info['name'], email=user_info['email'], type='customer')
            session.add(user)
            session.commit()
        session.close()
        return user
    return None

def main():
    st.set_page_config(page_title="PetGrass Delivery", page_icon="🌿", layout="wide")
    user = auth0_authentication()

    if user:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"

        menu_items = {
            "🏠 Home": home_page,
            "🛒 Order Now": place_order,
            "📦 My Orders": display_user_orders,
            "🗺️ Delivery Map": display_map,
            "ℹ️ About Us": about_us,
        }
        if user.type == 'admin':
            menu_items["📊 Admin Dashboard"] = admin_dashboard

        cols = st.columns(len(menu_items))
        for i, (emoji_label, func) in enumerate(menu_items.items()):
            if cols[i].button(emoji_label):
                st.session_state.current_page = emoji_label

        menu_items[st.session_state.current_page]()

        if st.sidebar.button("🚪 Log Out"):
            st.session_state.user = None
            st.success("Logged out successfully.")
            st.experimental_rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")
    else:
        st.write("Please log in to access PetGrass Delivery services")
        st.sidebar.markdown("---")
        st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")

def home_page():
    st.write(f"Welcome to PetGrass Delivery, {st.session_state.user.name}! 🌿🐾")
    st.write("Bring a piece of nature to your pet's life with our fresh grass delivery service!")
    
    st.subheader("Our Products")
    session = Session()
    products = session.query(Product).all()
    for product in products:
        st.write(f"- {product.name}: ${product.price:.2f}")
        st.image(product.image_url, width=200)
        st.write(product.description)
    session.close()

def place_order():
    st.subheader("🛒 Place Your Order")
    
    session = Session()
    products = session.query(Product).all()
    
    selected_product = st.selectbox("Choose your grass type:", [p.name for p in products])
    quantity = st.number_input("Quantity:", min_value=1, value=1)
    is_subscription = st.checkbox("Subscribe for regular deliveries")
    
    if is_subscription:
        frequency = st.selectbox("Delivery frequency:", ["Weekly", "Biweekly", "Monthly"])
    
    product = next(p for p in products if p.name == selected_product)
    total_price = product.price * quantity
    
    st.write(f"Total Price: ${total_price:.2f}")
    
    if st.button("Place Order"):
        new_order = Order(
            user_id=st.session_state.user.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total_price,
            is_subscription=is_subscription,
            delivery_frequency=frequency if is_subscription else None,
            next_delivery_date=datetime.utcnow() + timedelta(days=7) if is_subscription else None
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
        st.write(f"Order ID: {order.id}")
        st.write(f"Product: {order.product.name}")
        st.write(f"Quantity: {order.quantity}")
        st.write(f"Total Price: ${order.total_price:.2f}")
        st.write(f"Order Date: {order.order_date}")
        st.write(f"Status: {order.status}")
        if order.is_subscription:
            st.write(f"Subscription: {order.delivery_frequency}")
            st.write(f"Next Delivery: {order.next_delivery_date}")
        st.write("---")
    
    session.close()

def display_map():
    st.subheader("🗺️ Delivery Map")
    
    # This is a placeholder. In a real application, you'd fetch actual delivery locations.
    delivery_locations = [
        {"lat": 14.0723, "lon": -87.1921, "name": "Tegucigalpa"},
        {"lat": 15.5050, "lon": -88.0250, "name": "San Pedro Sula"},
        {"lat": 15.7835, "lon": -86.7830, "name": "La Ceiba"}
    ]
    
    m = folium.Map(location=[14.6349, -86.8167], zoom_start=7)
    
    for location in delivery_locations:
        folium.Marker(
            [location["lat"], location["lon"]], 
            popup=location["name"],
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(m)
    
    folium_static(m)

def about_us():
    st.subheader("ℹ️ About PetGrass Delivery")
    st.write("""
    At PetGrass Delivery, we believe that every pet deserves a touch of nature in their daily lives. 
    Our mission is to bring fresh, lush grass directly to your doorstep, providing your furry friends 
    with a natural and enjoyable experience.

    🌿 Why choose PetGrass Delivery?
    - Fresh, pesticide-free grass
    - Convenient delivery options
    - Subscription plans available
    - Eco-friendly packaging
    - Happy pets, happy owners!

    Join us in making your pet's day a little greener and a lot more fun!
    """)

def admin_dashboard():
    if st.session_state.user.type != 'admin':
        st.error("You don't have permission to access this page.")
        return

    st.subheader("📊 Admin Dashboard")
    
    session = Session()
    
    # Order Statistics
    total_orders = session.query(Order).count()
    total_revenue = session.query(func.sum(Order.total_price)).scalar() or 0
    
    st.write(f"Total Orders: {total_orders}")
    st.write(f"Total Revenue: ${total_revenue:.2f}")
    
    # Recent Orders
    st.subheader("Recent Orders")
    recent_orders = session.query(Order).order_by(Order.order_date.desc()).limit(10).all()
    for order in recent_orders:
        st.write(f"Order ID: {order.id} - User: {order.user.name} - Product: {order.product.name} - Date: {order.order_date}")
    
    # User Management
    st.subheader("User Management")
    users = session.query(User).all()
    for user in users:
        st.write(f"User: {user.name} - Email: {user.email} - Type: {user.type}")
    
    session.close()

if __name__ == "__main__":
    main()
