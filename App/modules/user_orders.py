import streamlit as st
from sqlalchemy.orm import Session
from modules.models import User, Product, Order, Subscription, PaymentTransaction, OrderStatus
from dotenv import load_dotenv
import os
import random

# Load environment variables
load_dotenv()

def display_user_orders():
    st.subheader("📦 Mis Órdenes")
    
    with Session() as session:
        try:
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
                        st.progress(progress_value)
                    else:
                        st.write("**Estado del pedido:** Desconocido")
                        st.progress(0)  # Default to 0 if status is unknown
        except Exception as e:
            st.error(f"Error al cargar las órdenes: {str(e)}")
