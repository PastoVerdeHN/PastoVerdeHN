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

# Sidebar para la navegación
st.sidebar.title("Administración")
page = st.sidebar.selectbox("Ir a", ["Resumen", "Usuarios", "Productos", "Órdenes", "Suscripciones", "Analítica"])

def overview_page():
  with get_db() as session:
      st.title("Resumen del Dashboard de Comercio Electrónico")

      # Crear columnas para mostrar métricas
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

      # Órdenes por estado
      st.subheader("Órdenes por Estado")
      status_counts = session.query(
          Order.status,
          func.count(Order.id).label('Cantidad')
      ).group_by(Order.status).all()
      status_df = pd.DataFrame(status_counts, columns=['Estado', 'Cantidad'])
      status_df['Estado'] = status_df['Estado'].apply(lambda x: x.value.capitalize())
      fig = px.bar(status_df, x='Estado', y='Cantidad', title='Órdenes por Estado')
      st.plotly_chart(fig, key="overview_orders_by_status")  # Clave única

      # Órdenes recientes
      st.subheader("Órdenes Recientes")
      recent_orders = session.query(Order).order_by(Order.created_at.desc()).limit(5).all()
      if recent_orders:
          order_data = [{
              "ID": order.id,
              "Usuario": order.user.name if order.user else "N/A",
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

      # Construir consulta con filtros
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
                  new_address = st.text_input("Dirección", value=selected_user.address or "")
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

      st.subheader("Productos Disponibles")
      # Los productos son suscripciones y compras únicas
      products = session.query(Product).all()
      if not products:
          st.info("No hay productos disponibles.")
      else:
          product_data = [{
              "ID": product.id,
              "Nombre": product.name,
              "Descripción": product.description,
              "Precio": f"L{product.price:.2f}",
              "Categoría": product.category,
              "Tipo": "Suscripción" if "suscripción" in product.category.lower() else "Compra Única"
          } for product in products]
          st.table(pd.DataFrame(product_data))

          st.subheader("Editar Producto")
          selected_product_id = st.selectbox("Seleccionar Producto para Editar", [product.id for product in products])
          selected_product = session.query(Product).filter_by(id=selected_product_id).first()

          if selected_product:
              with st.form("edit_product_form"):
                  new_name = st.text_input("Nombre del Producto", value=selected_product.name)
                  new_description = st.text_area("Descripción", value=selected_product.description or "")
                  new_price = st.number_input("Precio", min_value=0.0, step=0.01, value=selected_product.price)
                  new_category = st.text_input("Categoría", value=selected_product.category or "")

                  if st.form_submit_button("Actualizar Producto"):
                      selected_product.name = new_name
                      selected_product.description = new_description
                      selected_product.price = new_price
                      selected_product.category = new_category
                      session.commit()
                      st.success("Producto actualizado exitosamente.")

def orders_page():
  with get_db() as session:
      st.title("Gestión de Órdenes")

      st.subheader("Buscar Órdenes")
      # Filtros
      filter_options = ["ID de Órden", "Nombre de Usuario", "Estado", "Rango de Fechas", "Colonia"]
      selected_filters = st.multiselect("Seleccionar Filtros", filter_options)

      # Variables para filtros
      order_id = None
      user_search = None
      status_filter = None
      colonia_search = None

      # Construir consulta con filtros
      query = session.query(Order).join(User).join(Product)

      if "ID de Órden" in selected_filters:
          order_id = st.text_input("Ingrese el ID de la Órden")
          if order_id:
              query = query.filter(Order.id == order_id)

      if "Nombre de Usuario" in selected_filters:
          user_search = st.text_input("Buscar por Nombre de Usuario")
          if user_search:
              query = query.filter(User.name.contains(user_search))

      if "Estado" in selected_filters:
          status_filter = st.multiselect("Filtrar por Estado", [status.value for status in OrderStatus], default=None)
          if status_filter:
              query = query.filter(Order.status.in_([OrderStatus(status) for status in status_filter]))

      if "Rango de Fechas" in selected_filters:
          date_range = st.date_input("Rango de Fechas", [])
          if len(date_range) == 2:
              start_date = datetime.combine(date_range[0], datetime.min.time())
              end_date = datetime.combine(date_range[1], datetime.max.time())
              query = query.filter(Order.created_at.between(start_date, end_date))

      if "Colonia" in selected_filters:
          colonia_search = st.text_input("Buscar por Colonia")
          if colonia_search:
              query = query.filter(Order.delivery_address.contains(colonia_search))

      orders = query.order_by(Order.created_at.desc()).all()

      st.subheader("Lista de Órdenes")
      if orders:
          order_data = [{
              "ID": order.id,
              "Usuario": order.user.name if order.user else "N/A",
              "Producto/Plan": order.plan_name if order.plan_name else "N/A",
              "Cantidad": order.quantity,
              "Total": f"L{order.total_price:.2f}" if order.total_price else "N/A",
              "Estado": order.status.value.capitalize() if order.status else "N/A",
              "Fecha": order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else "N/A"
          } for order in orders]
          st.dataframe(pd.DataFrame(order_data))

          st.subheader("Detalles de la Órden y Edición")
          selected_order_id = st.selectbox("Seleccionar Órden para Ver y Editar", [order.id for order in orders])
          selected_order = session.query(Order).filter_by(id=selected_order_id).first()

          if selected_order:
              st.write(f"### Detalles de la Órden ID: {selected_order.id}")
              st.write(f"**Usuario:** {selected_order.user.name if selected_order.user else 'N/A'}")
              st.write(f"**Email:** {selected_order.user.email if selected_order.user else 'N/A'}")
              st.write(f"**Producto/Plan:** {selected_order.plan_name if selected_order.plan_name else 'N/A'}")
              st.write(f"**Cantidad:** {selected_order.quantity}")
              st.write(f"**Total:** L{selected_order.total_price:.2f}")
              st.write(f"**Dirección de Entrega:** {selected_order.delivery_address}")
              
              # Extraer 'Colonia' de la dirección de entrega
              # Suponiendo que 'Colonia' es la primera parte de la dirección antes de la coma
              colonia = selected_order.delivery_address.split(",")[0] if "," in selected_order.delivery_address else selected_order.delivery_address
              st.write(f"**Colonia:** {colonia}")
              
              st.write(f"**Horario de Entrega:** {selected_order.delivery_time}")
              st.write(f"**Fecha de Entrega:** {selected_order.date.strftime('%Y-%m-%d')}")
              st.write(f"**Notas Adicionales:** {selected_order.additional_notes or ''}")
              st.write(f"**Estado:** {selected_order.status.value.capitalize()}")
              st.write(f"**Fecha de Creación:** {selected_order.created_at.strftime('%Y-%m-%d %H:%M')}")

              with st.form("edit_order_form"):
                  new_status = st.selectbox(
                      "Estado de la Órden",
                      [status.value for status in OrderStatus],
                      index=[status.value for status in OrderStatus].index(selected_order.status.value)
                  )
                  new_delivery_date = st.date_input("Fecha de Entrega", value=selected_order.date.date())
                  new_delivery_time = st.text_input("Horario de Entrega", value=selected_order.delivery_time or "")
                  new_additional_notes = st.text_area("Notas Adicionales", value=selected_order.additional_notes or "")

                  if st.form_submit_button("Actualizar Órden"):
                      selected_order.status = OrderStatus(new_status)
                      selected_order.date = datetime.combine(new_delivery_date, datetime.min.time())
                      selected_order.delivery_time = new_delivery_time
                      selected_order.additional_notes = new_additional_notes
                      session.commit()
                      st.success("Órden actualizada exitosamente.")
          else:
              st.info("Seleccione una ódren para ver y editar.")
      else:
          st.info("No se encontraron órdenes con los criterios seleccionados.")

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
      else:
          st.info("No existen suscripciones.")

def analytics_page():
  with get_db() as session:
      st.title("Analíticas")

      # Selección de rango de fechas
      st.subheader("Seleccione el Rango de Fechas para el Análisis")
      col1, col2 = st.columns(2)
      with col1:
          start_date = st.date_input("Fecha de Inicio", datetime.now() - timedelta(days=30))
      with col2:
          end_date = st.date_input("Fecha de Fin", datetime.now())

      # Verificar que ambas fechas estén seleccionadas
      if start_date and end_date:
          # Convertir fechas a datetime
          start_datetime = datetime.combine(start_date, datetime.min.time())
          end_datetime = datetime.combine(end_date, datetime.max.time())

          # Ingresos a lo largo del tiempo
          sales_data = session.query(
              func.date(Order.created_at).label('Fecha'),
              func.sum(Order.total_price).label('Ingresos Totales')
          ).filter(Order.created_at.between(start_datetime, end_datetime)
          ).group_by(func.date(Order.created_at)).all()

          sales_df = pd.DataFrame(sales_data, columns=['Fecha', 'Ingresos Totales'])
          st.subheader("Ingresos a lo Largo del Tiempo")
          fig = px.line(
              sales_df,
              x='Fecha',
              y='Ingresos Totales',
              title='Ingresos Totales a lo Largo del Tiempo',
              labels={'Ingresos Totales': 'Ingresos Totales', 'Fecha': 'Fecha'}
          )
          st.plotly_chart(fig, key="analytics_sales_over_time")  # Clave única

          # Órdenes por Colonia
          st.subheader("Órdenes por Colonia")
          # Suponiendo que 'Colonia' es la primera parte de delivery_address antes de la coma
          colonia_data = session.query(
              func.substr(Order.delivery_address, 1, func.instr(Order.delivery_address, ',') - 1).label('Colonia'),
              func.count(Order.id).label('Cantidad')
          ).filter(Order.created_at.between(start_datetime, end_datetime)
          ).group_by(func.substr(Order.delivery_address, 1, func.instr(Order.delivery_address, ',') - 1)).all()

          colonia_df = pd.DataFrame(colonia_data, columns=['Colonia', 'Cantidad'])
          # Eliminar posibles `None` o valores vacíos
          colonia_df = colonia_df[colonia_df['Colonia'].notna() & (colonia_df['Colonia'] != "")]
          fig = px.bar(
              colonia_df,
              x='Colonia',
              y='Cantidad',
              title='Órdenes por Colonia'
          )
          st.plotly_chart(fig, key="analytics_orders_by_colonia")  # Clave única

          # Órdenes por Estado
          st.subheader("Órdenes por Estado")
          orders_by_status = session.query(
              Order.status,
              func.count(Order.id).label('Cantidad')
          ).filter(Order.created_at.between(start_datetime, end_datetime)
          ).group_by(Order.status).all()

          status_df = pd.DataFrame(orders_by_status, columns=['Estado', 'Cantidad'])
          status_df['Estado'] = status_df['Estado'].apply(lambda x: x.value.capitalize())
          fig = px.pie(
              status_df,
              names='Estado',
              values='Cantidad',
              title='Distribución de Órdenes por Estado'
          )
          st.plotly_chart(fig, key="analytics_orders_by_status")  # Clave única

          # Productos/Planes Más Vendidos
          st.subheader("Productos/Planes Más Vendidos")
          top_products_data = session.query(
              Order.plan_name.label('Producto'),
              func.count(Order.id).label('Cantidad Vendida')
          ).filter(Order.created_at.between(start_datetime, end_datetime)
          ).group_by(Order.plan_name).order_by(func.count(Order.id).desc()).all()

          top_products_df = pd.DataFrame(top_products_data, columns=['Producto', 'Cantidad Vendida'])
          fig = px.bar(
              top_products_df,
              x='Producto',
              y='Cantidad Vendida',
              title='Top Productos/Planes'
          )
          st.plotly_chart(fig, key="analytics_top_products")  # Clave única

          # Demografía por Colonia
          st.subheader("Demografía de Clientes por Colonia")
          demographics_data = session.query(
              func.substr(User.address, 1, func.instr(User.address, ',') - 1).label('Colonia'),
              func.count(User.id).label('Cantidad de Clientes')
          ).join(Order, Order.user_id == User.id
          ).filter(Order.created_at.between(start_datetime, end_datetime)
          ).group_by(func.substr(User.address, 1, func.instr(User.address, ',') - 1)).all()

          demographics_df = pd.DataFrame(demographics_data, columns=['Colonia', 'Cantidad de Clientes'])
          demographics_df = demographics_df[demographics_df['Colonia'].notna() & (demographics_df['Colonia'] != "")]
          fig = px.bar(
              demographics_df,
              x='Colonia',
              y='Cantidad de Clientes',
              title='Cantidad de Clientes por Colonia'
          )
          st.plotly_chart(fig, key="analytics_demographics_by_colonia")  # Clave única
      else:
          st.warning("Por favor, seleccione un rango de fechas válido.")

# Routing de páginas
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
