import streamlit as st
from sqlalchemy.orm import Session
from modules.models import User, Product, Order, Subscription, PaymentTransaction, OrderStatus, setup_database

def display_user_orders():
    st.subheader("📦 Mis Órdenes")
    
    Session = setup_database()
    session = Session()
    
    try:
        orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
        
        status_mapping = {
            OrderStatus.pending: ("Pago Pendiente", 0),
            OrderStatus.confirmed: ("Orden Confirmada", 33),
            OrderStatus.shipped: ("Orden Enviada", 66),
            OrderStatus.delivered: ("Orden Entregada", 100)
        }
        
        if not orders:
            st.info("No tienes órdenes activas en este momento.")
        else:
            for order in orders:
                with st.expander(f"Order ID: {order.id} - Status: {order.status.value}"):
                    st.write(f"**Plan seleccionado:** {order.plan_name}")
                    st.write(f"**Fecha de entrega:** {order.date.strftime('%Y-%m-%d')}")
                    st.write(f"**Horario de entrega:** {order.delivery_time}")
                    st.write(f"**Dirección de entrega:** {order.delivery_address}")
                    st.write(f"**Precio total:** L. {order.total_price:.2f}")
                    st.write(f"**Cambio de dólar:** 1$ = L.25.00")
                    
                    if order.additional_notes:
                        st.write(f"**Referencias adicionales:** {order.additional_notes}")
                    
                    if order.product_id:
                        product = session.query(Product).filter_by(id=order.product_id).first()
                        if product:
                            st.write(f"**Producto:** {product.name}")
                    
                    if order.status in status_mapping:
                        status_label, progress_value = status_mapping[order.status]
                        st.write(f"**Estado del pedido:** {status_label}")
                        st.progress(progress_value)
                    else:
                        st.write("**Estado del pedido:** Desconocido")
                        st.progress(0)
                    
                    st.write("**Nota:** En el checkout, se incluye una caja de madera con los planes de suscripción. One-time setup fee")
    except Exception as e:
        st.error(f"An error occurred while fetching orders: {str(e)}")
    finally:
        session.close()
if __name__ == "__main__":
    display_user_orders()
