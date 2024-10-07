import streamlit as st
from sqlalchemy.orm import Session
from modules.models import User, Product, Order, Subscription, PaymentTransaction, OrderStatus, setup_database

def display_order_progress(status):
  stages = ['Pendiente', 'Preparando', 'En camino', 'Entregado']
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
      st.error("Pedido Cancelado")
      return

  st.write("Progreso del Pedido:")
  
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
  st.markdown(f"<h4>Estado Actual: {status.value.capitalize()}</h4>", unsafe_allow_html=True)

def display_user_orders():
  st.subheader("📦 Mis Órdenes")
  
  Session = setup_database()
  session = Session()
  
  try:
      orders = session.query(Order).order_by(Order.created_at.desc()).all()
      
      if not orders:
          st.info("No tienes órdenes activas en este momento.")
      else:
          for order in orders:
              with st.expander(f"ID de Pedido: {order.id} - Estado: {order.status.value}"):
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
                  
                  # Move the progress display to the bottom
                  display_order_progress(order.status)
                  
                  st.write("**Nota:** Todos nuestros ©Pasto Verde Boxes vienen listos para usar tan pronto como los recibes. Todos los pedidos vienen en cajas reciclables que puedes simplemente reciclar cuando llegue el nuevo reemplazo. ♻️🐾📦")
  except Exception as e:
      st.error(f"Ocurrió un error al obtener las órdenes: {str(e)}")
  finally:
      session.close()

if __name__ == "__main__":
  display_user_orders()
