import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from contextlib import contextmanager
from modules.models import SessionLocal, User, Product, Order, Subscription, UserType, OrderStatus
import base64


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
            st.metric("Ingresos Totales", f"L.{total_revenue:.2f}")

        # Orders by status
        st.subheader("Órdenes por Estado")
        status_counts = session.query(
            Order.status,
            func.count(Order.id).label('Cantidad')
        ).group_by(Order.status).all()
        status_df = pd.DataFrame(status_counts, columns=['Estado', 'Cantidad'])
        status_df['Estado'] = status_df['Estado'].apply(lambda x: x.value.capitalize())
        fig = px.bar(status_df, x='Estado', y='Cantidad', title='Órdenes por Estado')
        st.plotly_chart(fig, key=f"overview_orders_by_status_{datetime.now().timestamp()}")  # Unique key

        # Recent Orders
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

        # Build query with filters
        query = session.query(User)
        if search_term:
            query = query.filter(or_(User.name.ilike(f"%{search_term}%"), User.email.ilike(f"%{search_term}%")))
            st.write(f"Filtrando por Nombre o Email: {search_term}")
        if user_type_filter != "Todos":
            query = query.filter(User.type == UserType(user_type_filter))
            st.write(f"Filtrando por Tipo de Usuario: {user_type_filter}")
        if is_active_filter != "Todos":
            is_active = is_active_filter == "Activos"
            query = query.filter(User.is_active == is_active)
            st.write(f"Filtrando por Estado de Actividad: {'Activo' if is_active else 'Inactivo'}")

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

def update_order_status(order_id, new_status):
  with get_db() as session:
      order = session.query(Order).filter(Order.id == order_id).first()
      if order:
          if isinstance(new_status, OrderStatus):
              order.status = new_status
              order.updated_at = datetime.utcnow()
              session.commit()
              return True
          else:
              st.error("Invalid status type. Must be an instance of OrderStatus.")
      return False

def orders_page():
    with get_db() as session:
        st.title("Gestión de Órdenes")
        
        start_date, end_date = date_range_selector()
        
        orders = session.query(Order).filter(
            Order.created_at.between(start_date, end_date)
        ).order_by(Order.created_at.desc()).all()
        st.write(f"Total de órdenes encontradas: {len(orders)}")
        
        if orders:
            for order in orders:
                with st.expander(f"Orden ID: {order.id} - Estado: {order.status.value.capitalize()}"):
                    st.write(f"**Usuario:** {order.user.name if order.user else 'N/A'}")
                    st.write(f"**Correo:** {order.user.email if order.user else 'N/A'}")
                    st.write(f"**Teléfono:** {order.phone_number if order.phone_number else 'N/A'}")
                    st.write(f"**Producto/Plan:** {order.plan_name if order.plan_name else 'N/A'}")
                    st.write(f"**Cantidad:** {order.quantity}")
                    st.write(f"**Total:** L{order.total_price:.2f}")
                    st.write(f"**Fecha de Creación:** {order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else 'N/A'}")
                    st.write(f"**Fecha de Entrega:** {order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else 'N/A'}")
                    st.write(f"**Horario de Entrega:** {order.delivery_time if order.delivery_time else 'N/A'}")
                    st.write(f"**Dirección:** {order.delivery_address if order.delivery_address else 'N/A'}")
                    st.write(f"**Referencias:** {order.additional_notes if order.additional_notes else 'N/A'}")
                    st.write("---")
                    
                    st.write(f"**Estado actual:** {order.status.value.capitalize()}")
                    
                    status_options = [status for status in OrderStatus]
                    
                    new_status = st.selectbox(
                        "Actualizar estado",
                        options=status_options,
                        format_func=lambda x: x.value.capitalize(),
                        index=status_options.index(order.status),
                        key=f"status_select_{order.id}"
                    )
                    
                    if st.button("Actualizar Estado", key=f"update_status_{order.id}"):
                        if new_status != order.status:
                            update_success = update_order_status(order.id, new_status)
                            if update_success:
                                st.success(f"Estado actualizado a {new_status.value.capitalize()}")
                                st.experimental_set_query_params(updated_order=order.id)
                            else:
                                st.error("Error al actualizar el estado")
                        else:
                            st.info("El estado seleccionado es el mismo que el actual")
            
            order_data = [{
                "ID": order.id,
                "Usuario": order.user.name if order.user else "N/A",
                "Correo": order.user.email if order.user else "N/A",
                "Teléfono": order.phone_number if order.phone_number else "N/A",
                "Producto/Plan": order.plan_name if order.plan_name else "N/A",
                "Cantidad": order.quantity,
                "Total": f"L{order.total_price:.2f}" if order.total_price else "N/A",
                "Estado": order.status.value.capitalize() if order.status else "N/A",
                "Fecha de Creación": order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else "N/A",
                "Fecha de Entrega": order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else "N/A",
                "Horario de Entrega": order.delivery_time if order.delivery_time else "N/A",
                "Dirección": order.delivery_address if order.delivery_address else "N/A",
                "Referencias": order.additional_notes if order.additional_notes else "N/A"
            } for order in orders]
            
            df = pd.DataFrame(order_data)
            
            st.dataframe(df, use_container_width=True)
            
            if st.button("Exportar a CSV"):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="ordenes.csv">Descargar CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("No se encontraron órdenes en el período seleccionado.")

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
      else:  # This else is correctly associated with the if subscriptions:
          st.info("No hay suscripciones para editar.")

from sqlalchemy import func, distinct
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

def analytics_page():
    with get_db() as session:
        st.title("Analíticas")

        # Existing date range selection
        st.subheader("Seleccione el Rango de Fechas para el Análisis")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Fecha de Inicio", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("Fecha de Fin", datetime.now())

        if start_date and end_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            # Existing analytics (keep as is)
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
            st.plotly_chart(fig, use_container_width=True)

            # Keep other existing analytics (Órdenes por Colonia, Órdenes por Estado, etc.)
            # ...

            # New analytics inspired by YouTube Dashboard

            # 1. Métricas clave (similar to All-Time Statistics in YouTube Dashboard)
            st.subheader("Métricas Clave")
            col1, col2, col3, col4 = st.columns(4)

            total_orders = session.query(func.count(Order.id)).filter(Order.created_at.between(start_datetime, end_datetime)).scalar()
            total_revenue = session.query(func.sum(Order.total_price)).filter(Order.created_at.between(start_datetime, end_datetime)).scalar()
            avg_order_value = total_revenue / total_orders if total_orders else 0
            total_customers = session.query(func.count(distinct(Order.user_id))).filter(Order.created_at.between(start_datetime, end_datetime)).scalar()

            col1.metric("Total de Órdenes", f"{total_orders:,}")
            col2.metric("Ingresos Totales", f"${total_revenue:,.2f}")
            col3.metric("Valor Promedio de Orden", f"${avg_order_value:.2f}")
            col4.metric("Clientes Únicos", f"{total_customers:,}")

            # 2. Tendencias semanales (similar to Weekly data in YouTube Dashboard)
            st.subheader("Tendencias Semanales")
            weekly_data = session.query(
                func.date_trunc('week', Order.created_at).label('Semana'),
                func.count(Order.id).label('Órdenes'),
                func.sum(Order.total_price).label('Ingresos')
            ).filter(Order.created_at.between(start_datetime, end_datetime)
            ).group_by(func.date_trunc('week', Order.created_at)).all()

            weekly_df = pd.DataFrame(weekly_data, columns=['Semana', 'Órdenes', 'Ingresos'])
            fig = px.line(
                weekly_df,
                x='Semana',
                y=['Órdenes', 'Ingresos'],
                title='Tendencias Semanales de Órdenes e Ingresos'
            )
            st.plotly_chart(fig, use_container_width=True)

            # 3. Distribución de Productos (similar to Top Products in YouTube Dashboard)
            st.subheader("Distribución de Productos")
            product_data = session.query(
                Order.plan_name.label('Producto'),
                func.count(Order.id).label('Cantidad'),
                func.sum(Order.total_price).label('Ingresos')
            ).filter(Order.created_at.between(start_datetime, end_datetime)
            ).group_by(Order.plan_name).order_by(func.sum(Order.total_price).desc()).limit(10).all()

            product_df = pd.DataFrame(product_data, columns=['Producto', 'Cantidad', 'Ingresos'])
            fig = px.bar(
                product_df,
                x='Producto',
                y=['Cantidad', 'Ingresos'],
                title='Top 10 Productos por Cantidad e Ingresos',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)

            # 4. Mapa de Calor de Órdenes (inspired by the time-based charts in YouTube Dashboard)
            st.subheader("Mapa de Calor de Órdenes")
            heatmap_data = session.query(
                func.extract('dow', Order.created_at).label('Día de la Semana'),
                func.extract('hour', Order.created_at).label('Hora'),
                func.count(Order.id).label('Cantidad de Órdenes')
            ).filter(Order.created_at.between(start_datetime, end_datetime)
            ).group_by('Día de la Semana', 'Hora').all()

            heatmap_df = pd.DataFrame(heatmap_data, columns=['Día de la Semana', 'Hora', 'Cantidad de Órdenes'])
            heatmap_df = heatmap_df.pivot(index='Hora', columns='Día de la Semana', values='Cantidad de Órdenes')
            
            fig = px.imshow(
                heatmap_df,
                labels=dict(x="Día de la Semana", y="Hora del Día", color="Cantidad de Órdenes"),
                x=['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'],
                y=[f"{i:02d}:00" for i in range(24)],
                title="Mapa de Calor de Órdenes por Día y Hora"
            )
            st.plotly_chart(fig, use_container_width=True)

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
