import streamlit as st
from sqlalchemy.orm import Session
from modules.models import User, Product, Order, Subscription, PaymentTransaction, OrderStatus, setup_database

def display_order_progress(status):
  stages = ['Pending', 'Preparing', 'On the way', 'Delivered']
  status_mapping = {
      'pending': 0,
      'confirmed': 1,
      'shipped': 2,
      'delivered': 3,
      'completed': 3,
      'cancelled': -1
  }
  current_stage = status_mapping.get(status.value, 0)
  
  if current_stage == -1:
      st.error("Order Cancelled")
      return

  st.write("Order Progress:")
  
  progress_html = ""
  for i, stage in enumerate(stages):
      if i < current_stage:
          progress_html += f"<span style='color: green;'>✅ {stage}</span>&nbsp;&nbsp;&nbsp;"
      elif i == current_stage:
          progress_html += f"<span style='color: blue; font-weight: bold;'>🔵 {stage}</span>&nbsp;&nbsp;&nbsp;"
      else:
          progress_html += f"<span style='color: gray;'>⚪ {stage}</span>&nbsp;&nbsp;&nbsp;"
  
  st.markdown(progress_html, unsafe_allow_html=True)
  st.progress(current_stage / (len(stages) - 1))
  st.markdown(f"<h4>Current Status: {status.value.capitalize()}</h4>", unsafe_allow_html=True)

def display_user_orders():
  st.subheader("📦 Mis Órdenes")
  
  Session = setup_database()
  session = Session()
  
  try:
      orders = session.query(Order).filter_by(user_id=st.session_state.user.id).all()
      
      if not orders:
          st.info("No tienes órdenes activas en este momento.")
      else:
          for order in orders:
              with st.expander(f"Order ID: {order.id} - Status: {order.status.value}"):
                  col1, col2 = st.columns([2, 1])
                  with col1:
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
                  
                  with col2:
                      display_order_progress(order.status)
                  
                  st.write("**Nota:** En el checkout, se incluye una caja de madera con los planes de suscripción. One-time setup fee")
  except Exception as e:
      st.error(f"An error occurred while fetching orders: {str(e)}")
  finally:
      session.close()

if __name__ == "__main__":
  display_user_orders()
