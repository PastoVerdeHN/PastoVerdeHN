import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta
from contextlib import contextmanager
from modules.models import SessionLocal, User, Product, Order, Subscription, UserType, OrderStatus

@contextmanager
def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

# Sidebar for navigation
st.sidebar.title("Administración")
page = st.sidebar.selectbox("Ir a", ["Resumen", "Usuarios", "Productos", "Órdenes", "Suscripciones", "Analítica"])

def overview_page():
  with get_db() as session:
      st.title("Resumen del Dashboard de Comercio Electrónico")

      # Create columns for displaying metrics
      col1, col2, col3, col4 = st.columns(4)

      with col1:
          total_users = session.query(func.count(User.id)).scalar()
          st.metric("Usuarios Totales", total_users)

      with col2:
          total_products = session.query(func.count(Product.id)).scalar()
          st.metric("Productos Totales", total_products)

      with col3:
          total_orders = session.query(func.count(Order.id)).scalar()
          st.metric("Órdenes Totales", total_orders)

      with col4:
          total_revenue = session.query(func.sum(Order.total_price)).scalar()
          total_revenue = total_revenue if total_revenue is not None else 0.0
          st.metric("Ingresos Totales", f"L{total_revenue:.2f}")

      st.subheader("Órdenes Recientes")
      recent_orders = session.query(Order).order_by(Order.created_at.desc()).limit(5).all()
      if recent_orders:
          order_data = [{
              "ID": order.id,
              "Usuario": order.user.name if order.user else "N/A",
              "Producto": order.product.name if order.product else "N/A",
              "Estado": order.status.value.capitalize() if order.status else "N/A",
              "Total": f"L{order.total_price:.2f}" if order.total_price else "N/A",
              "Fecha": order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else "N/A"
          } for order in recent_orders]
          st.table(pd.DataFrame(order_data))
      else:
          st.info("No se encontraron órdenes recientes.")

def users_page():
  with get_db() as session:
      st.title("Gestión de Usuarios")

      st.subheader("Búsqueda y Filtro de Usuarios")
      search_term = st.text_input("Buscar por nombre o email")
      user_type_filter = st.selectbox("Filtrar por tipo de usuario", ["Todos"] + [type.value for type in UserType])
      is_active_filter = st.selectbox("Estado de actividad", ["Todos", "Activos", "Inactivos"])

      # Build query with filters
      query = session.query(User)
      if search_term:
          query = query.filter(or_(User.name.contains(search_term), User.email.contains(search_term)))
      if user_type_filter != "Todos":
          query = query.filter(User.type == UserType(user_type_filter))
      if is_active_filter != "Todos":
          is_active = is_active_filter == "Activos"
          query = query.filter(User.is_active == is_active)

      users = query.all()
      user_data = [{
          "ID": user.id,
          "Nombre": user.name,
          "Email": user.email,
          "Tipo": user.type.value,
          "Activo": "Sí" if user.is_active else "No",
          "Último Ingreso": user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "N/A"
      } for user in users]
      st.dataframe(pd.DataFrame(user_data))

      st.subheader("Editar Usuario")
      if users:
          selected_user_email = st.selectbox("Seleccionar Usuario para Editar", [user.email for user in users])
          selected_user = session.query(User).filter_by(email=selected_user_email).first()

          if selected_user:
              with st.form("edit_user_form"):
                  new_name = st.text_input("Nombre", value=selected_user.name)
                  new_email = st.text_input("Email", value=selected_user.email)
                  new_user_type = st.selectbox("Tipo de Usuario", [type.value for type in UserType], index=[type.value for type in UserType].index(selected_user.type.value))
                  new_address = st.text_input("Dirección", value=selected_user.address)
                  new_phone_number = st.text_input("Número de Teléfono", value=selected_user.phone_number or "")
                  new_is_active = st.checkbox("Activo", value=selected_user.is_active)

                  if st.form_submit_button("Actualizar Usuario"):
                      selected_user.name = new_name
                      selected_user.email = new_email
                      selected_user.type = UserType(new_user_type)
                      selected_user.address = new_address
                      selected_user.phone_number = new_phone_number
                      selected_user.is_active = new_is_active
                      session.commit()
                      st.success("Usuario actualizado exitosamente.")
      else:
          st.info("No hay usuarios para editar.")

def products_page():
  with get_db() as session:
      st.title("Gestión de Productos")

      st.subheader("Lista de Productos")
      products = session.query(Product).all()
      product_data = [{
          "ID": product.id,
          "Nombre": product.name,
          "Precio": f"L{product.price:.2f}",
          "Stock": product.stock,
          "Categoría": product.category
      } for product in products]
      st.dataframe(pd.DataFrame(product_data))

      st.subheader("Editar Producto")
      if products:
          selected_product_name = st.selectbox("Seleccionar Producto para Editar", [product.name for product in products])
          selected_product = session.query(Product).filter_by(name=selected_product_name).first()

          if selected_product:
              with st.form("edit_product_form"):
                  new_name = st.text_input("Nombre del Producto", value=selected_product.name)
                  new_description = st.text_area("Descripción", value=selected_product.description)
                  new_price = st.number_input("Precio", min_value=0.0, step=0.01, value=selected_product.price)
                  new_stock = st.number_input("Stock", min_value=0, step=1, value=selected_product.stock)
                  new_category = st.text_input("Categoría", value=selected_product.category)

                  if st.form_submit_button("Actualizar Producto"):
                      selected_product.name = new_name
                      selected_product.description = new_description
                      selected_product.price = new_price
                      selected_product.stock = new_stock
                      selected_product.category = new_category
                      session.commit()
                      st.success("Producto actualizado exitosamente.")
      else:
          st.info("No hay productos para editar.")

      st.subheader("Agregar Nuevo Producto")
      with st.form("new_product_form"):
          name = st.text_input("Nombre del Producto")
          description = st.text_area("Descripción")
          price = st.number_input("Precio", min_value=0.0, step=0.01)
          stock = st.number_input("Stock", min_value=0, step=1)
          category = st.text_input("Categoría")

          if st.form_submit_button("Agregar Producto"):
              new_product = Product(
                  name=name,
                  description=description,
                  price=price,
                  stock=stock,
                  category=category
              )
              session.add(new_product)
              session.commit()
              st.success("Producto agregado exitosamente.")

def orders_page():
  with get_db() as session:
      st.title("Gestión de Órdenes")

      st.subheader("Filtro de Órdenes")
      # Filters
      status_filter = st.multiselect("Filtrar por Estado", [status.value for status in OrderStatus], default=[status.value for status in OrderStatus])
      user_search = st.text_input("Buscar por Usuario")
      date_range = st.date_input("Rango de Fechas", [])
      date_filter = None

      if date_range and len(date_range) == 2:
          start_date = datetime.combine(date_range[0], datetime.min.time())
          end_date = datetime.combine(date_range[1], datetime.max.time())
          date_filter = and_(Order.created_at >= start_date, Order.created_at <= end_date)

      # Build query with filters
      query = session.query(Order).join(User).join(Product)

      if status_filter:
          query = query.filter(Order.status.in_([OrderStatus(status) for status in status_filter]))
      if user_search:
          query = query.filter(User.name.contains(user_search))
      if date_filter:
          query = query.filter(date_filter)

      orders = query.order_by(Order.created_at.desc()).all()

      st.subheader("Lista de Órdenes")
      if orders:
          order_data = [{
              "ID": order.id,
              "Usuario": order.user.name if order.user else "N/A",
              "Producto": order.product.name if order.product else "N/A",
              "Cantidad": order.quantity,
              "Total": f"L{order.total_price:.2f}" if order.total_price else "N/A",
              "Estado": order.status.value.capitalize() if order.status else "N/A",
              "Fecha": order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else "N/A"
          } for order in orders]
          st.dataframe(pd.DataFrame(order_data))
      else:
          st.info("No se encontraron órdenes con los criterios seleccionados.")

      st.subheader("Editar Órden")
      if orders:
          selected_order_id = st.selectbox("Seleccionar Órden para Editar", [order.id for order in orders])
          selected_order = session.query(Order).filter_by(id=selected_order_id).first()

          if selected_order:
              with st.form("edit_order_form"):
                  new_status = st.selectbox(
                      "Estado de la Órden",
                      [status.value for status in OrderStatus],
                      index=[status.value for status in OrderStatus].index(selected_order.status.value)
                  )
                  new_tracking_number = st.text_input("Número de Seguimiento", value=selected_order.transaction_id or "")
                  new_delivery_date = st.date_input("Fecha de Entrega", value=selected_order.date.date())
                  new_delivery_time = st.text_input("Horario de Entrega", value=selected_order.delivery_time)
                  new_additional_notes = st.text_area("Notas Adicionales", value=selected_order.additional_notes or "")

                  if st.form_submit_button("Actualizar Órden"):
                      selected_order.status = OrderStatus(new_status)
                      selected_order.transaction_id = new_tracking_number
                      selected_order.date = datetime.combine(new_delivery_date, datetime.min.time())
                      selected_order.delivery_time = new_delivery_time
                      selected_order.additional_notes = new_additional_notes
                      session.commit()
                      st.success("Órden actualizada exitosamente.")
      else:
          st.info("No hay órdenes para editar.")

def subscriptions_page():
  with get_db() as session:
      st.title("Gestión de Suscripciones")

      st.subheader("Lista de Suscripciones")
      subscriptions = session.query(Subscription).join(User).all()
      subscription_data = [{
          "ID": sub.id,
          "Usuario": sub.user.name if sub.user else "N/A",
          "Plan": sub.plan_name,
          "Fecha de Inicio": sub.start_date.strftime('%Y-%m-%d'),
          "Fecha de Fin": sub.end_date.strftime('%Y-%m-%d') if sub.end_date else "N/A",
          "Activo": "Sí" if sub.is_active else "No"
      } for sub in subscriptions]
      st.dataframe(pd.DataFrame(subscription_data))

      st.subheader("Editar Suscripción")
      if subscriptions:
          selected_sub_id = st.selectbox("Seleccionar Suscripción para Editar", [sub.id for sub in subscriptions])
          selected_sub = session.query(Subscription).filter_by(id=selected_sub_id).first()

          if selected_sub:
              with st.form("edit_subscription_form"):
                  new_plan_name = st.text_input("Nombre del Plan", value=selected_sub.plan_name)
                  new_start_date = st.date_input("Fecha de Inicio", value=selected_sub.start_date.date())
                  new_end_date = st.date_input("Fecha de Fin", value=selected_sub.end_date.date() if selected_sub.end_date else datetime.now().date())
                  new_is_active = st.checkbox("Activo", value=selected_sub.is_active)

                  if st.form_submit_button("Actualizar Suscripción"):
                      selected_sub.plan_name = new_plan_name
                      selected_sub.start_date = datetime.combine(new_start_date, datetime.min.time())
                      selected_sub.end_date = datetime.combine(new_end_date, datetime.min.time())
                      selected_sub.is_active = new_is_active
                      session.commit()
                      st.success("Suscripción actualizada exitosamente.")
      else:
          st.info("No hay suscripciones para editar.")

def analytics_page():
  with get_db() as session:
      st.title("Analíticas")

      # Date range selection
      col1, col2 = st.columns(2)
      with col1:
          start_date = st.date_input("Fecha de Inicio", datetime.now() - timedelta(days=30))
      with col2:
          end_date = st.date_input("Fecha de Fin", datetime.now())

      # Convert dates to datetime
      start_datetime = datetime.combine(start_date, datetime.min.time())
      end_datetime = datetime.combine(end_date, datetime.max.time())

      # Sales over time
      sales_data = session.query(
          func.date(Order.created_at).label('date'),
          func.sum(Order.total_price).label('total_sales')
      ).filter(Order.created_at.between(start_datetime, end_datetime)
      ).group_by(func.date(Order.created_at)).all()

      sales_df = pd.DataFrame(sales_data, columns=['Fecha', 'Ingresos Totales'])
      st.subheader("Ingresos a lo Largo del Tiempo")
      fig = px.line(sales_df, x='Fecha', y='Ingresos Totales', title='Ingresos Totales a lo Largo del Tiempo', labels={'Ingresos Totales': 'Ingresos Totales', 'Fecha': 'Fecha'})
      st.plotly_chart(fig)

      # Top Products
      st.subheader("Productos Más Vendidos")
      top_products_data = session.query(
          Product.name,
          func.sum(Order.quantity).label('quantity_sold')
      ).join(Order.product).group_by(Product.name).order_by(func.sum(Order.quantity).desc()).limit(5).all()

      top_products_df = pd.DataFrame(top_products_data, columns=['Producto', 'Cantidad Vendida'])
      fig = px.bar(top_products_df, x='Producto', y='Cantidad Vendida', title='Top 5 Productos Más Vendidos')
      st.plotly_chart(fig)

      # Customer Insights
      st.subheader("Nuevos Usuarios")
      new_users_count = session.query(func.count(User.id)).filter(User.created_at.between(start_datetime, end_datetime)).scalar()
      st.metric("Nuevos Usuarios en el Período", new_users_count)

      st.subheader("Órdenes por Estado")
      orders_by_status = session.query(
          Order.status,
          func.count(Order.id).label('count')
      ).group_by(Order.status).all()

      status_df = pd.DataFrame(orders_by_status, columns=['Estado', 'Cantidad'])
      status_df['Estado'] = status_df['Estado'].apply(lambda x: x.value.capitalize())
      fig = px.pie(status_df, names='Estado', values='Cantidad', title='Distribución de Órdenes por Estado')
      st.plotly_chart(fig)

# Page routing
if page == "Resumen":
  overview_page()
elif page == "Usuarios":
  users_page()
elif page == "Productos":
  products_page()
elif page == "Órdenes":
  orders_page()
elif page == "Suscripciones":
  subscriptions_page()
elif page == "Analítica":
  analytics_page()
