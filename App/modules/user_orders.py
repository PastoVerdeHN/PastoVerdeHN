import streamlit as st
from sqlalchemy.orm import Session
from modules.models import User, Product, Order, Subscription, PaymentTransaction, OrderStatus, setup_database
from dotenv import load_dotenv
import os

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

def display_user_orders():
    st.subheader("📦 Mis Órdenes")
    
    # Create a new session from the session maker
    with SessionLocal() as session:  # Use SessionLocal here
        try:
            # Fetch orders for the logged-in user
            orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
            if not orders:
                st.warning("No tienes órdenes.")
                return
            
            # Define order status mapping
            status_mapping = {
                OrderStatus.pending: ("Pago Pendiente", 0),
                OrderStatus.confirmed: ("Orden Confirmada", 33),
                OrderStatus.shipped: ("Orden Enviada", 66),
                OrderStatus.delivered: ("Orden Entregada", 100)
            }
            
            # Loop through each order and display details
            for order in orders:
                with st.expander(f"Order ID: {order.id} - Status: {order.status.value}"):
                    st.write(f"**Fecha de entrega:** {order.date}")
                    st.write(f"**Dirección de entrega:** {order.delivery_address}")
                    st.write(f"**Precio total:** L. {order.total_price:.2f}")

                    # Fetch product details for each order
                    if order.product_id:
                        product = session.query(Product).filter_by(id=order.product_id).first()
                        if product:
                            st.write(f"**Producto:** {product.name}")

                    # Display progress bar based on order status
                    if order.status in status_mapping:
                        status_label, progress_value = status_mapping[order.status]
                        st.write(f"**Estado del pedido:** {status_label}")
                        st.progress(progress_value)
                    else:
                        st.write("**Estado del pedido:** Desconocido")
                        st.progress(0)  # Default to 0 if status is unknown
        except Exception as e:
            st.error(f"Error al cargar las órdenes: {str(e)}")
            # Consider logging the error for debugging
