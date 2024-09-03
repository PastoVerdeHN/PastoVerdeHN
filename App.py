import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import random
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import sqlalchemy
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Pasto Verde",
    page_icon="🌿",
    layout="wide"
)

# Apply color theme
COLOR_PRIMARY = "#4CAF50"
COLOR_SECONDARY = "#8BC34A"
COLOR_BACKGROUND = "#E8F5E9"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLOR_BACKGROUND};
    }}
    .stButton>button {{
        background-color: {COLOR_PRIMARY};
        color: white;
    }}
    .stTextInput>div>div>input {{
        background-color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# Main title
st.title("🌿 Pasto Verde")
st.sidebar.success("Select a page above.")

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = st.secrets["database"]["url"]
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# SQLAlchemy models
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    direccion = Column(String)

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    precio = Column(Float, nullable=False)
    url_imagen = Column(String)

class Suscripcion(Base):
    __tablename__ = 'suscripciones'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(String, ForeignKey('usuarios.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    plan = Column(String, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime)
    estado = Column(String, nullable=False)
    usuario = relationship("Usuario")
    producto = relationship("Producto")

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(String, primary_key=True)
    usuario_id = Column(String, ForeignKey('usuarios.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False)
    estado = Column(String, nullable=False)
    personalizacion = Column(String)
    usuario = relationship("Usuario")
    producto = relationship("Producto")

Base.metadata.create_all(engine, checkfirst=True)
print("Database tables created successfully (or already exist).")

# Helper functions
def generate_order_id():
    return f"PED-{random.randint(10000, 99999)}"

# Authentication function (placeholder)
def authenticate():
    # Implement your authentication logic here
    # For now, we'll use a simple placeholder
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            # Here you would typically check the credentials
            # For this example, we'll just set a dummy user
            st.session_state.user = {"name": username, "email": f"{username}@example.com"}
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
    return st.session_state.user

# Main function
def main():
    user = authenticate()
    if user:
        menu_items = [
            "🏠 Home",
            "🌱 Products",
            "🔄 Subscriptions",
            "🛒 Orders",
            "👤 Profile",
            "📞 Support"
        ]
        
        st.sidebar.title("Menu")
        selection = st.sidebar.radio("Go to", menu_items)
        
        if selection == "🏠 Home":
            st.header("Welcome to Pasto Verde")
            st.write("Discover our premium and eco-friendly grass products for pets!")
        
        elif selection == "🌱 Products":
            st.header("Our Products")
            # Add product listing logic here
        
        elif selection == "🔄 Subscriptions":
            st.header("Manage Your Subscriptions")
            # Add subscription management logic here
        
        elif selection == "🛒 Orders":
            st.header("Your Orders")
            # Add order history and tracking logic here
        
        elif selection == "👤 Profile":
            st.header("Your Profile")
            # Add user profile management here
        
        elif selection == "📞 Support":
            st.header("Customer Support")
            # Add support features, FAQ, and contact information here

if __name__ == "__main__":
    main()
