import streamlit as st
from datetime import datetime
import random
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from branca.element import Template, MacroElement
import streamlit.components.v1 as components
from modules.models import User, Product, Order, Subscription, PaymentTransaction, OrderStatus, UserType
from dotenv import load_dotenv
import os

# If you're using any secrets or environment variables
load_dotenv()

# Database setup (if needed in this file)
try:
    database_url = st.secrets["database"]["url"]
except KeyError:
    database_url = os.getenv("DATABASE_URL")

if not database_url:
    st.error("Database URL not found. Please set it in Streamlit secrets or as an environment variable.")
    st.stop()

# Setup database session
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)

# Helper functions
def generate_order_id():
    return f"ORD-{random.randint(10000, 99999)}"

def update_order_status(order_id, transaction_id):
    session = Session()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.confirmed
            order.payment_status = "paid"
            order.transaction_id = transaction_id
            order.updated_at = datetime.utcnow()
            session.commit()
            return True
    except Exception as e:
        session.rollback()
        st.error(f"Error updating order status: {str(e)}")
        return False
    finally:
        session.close()

def place_order():
    st.subheader("🛒 Realizar pedido")
    session = Session()

    # Plan options
    plans = {
        "Suscripción Anual": {
            "id": "annual",
            "price": 720.00,
            "features": [
                "Entrega cada dos semanas",
                "Envío gratis",
                "Descuento del 29%",
                "Descuento adicional del 40%",
                "Personalización incluida",
                "Primer mes gratis"
            ]
        },
        "Suscripción Semestral": {
            "id": "semiannual",
            "price": 899.00,
            "features": [
                "Entrega cada dos semanas",
                "Envío gratis",
                "Descuento del 29%",
                "Descuento adicional del 25%",
                "Personalización incluida"
            ]
        },
        "Suscripción Mensual": {
            "id": "monthly",
            "price": 1080.00,
            "features": [
                "Entrega cada dos semanas",
                "Envío gratis",
                "Descuento del 29%",
                "Descuento adicional del 10%"
            ]
        },
        "Sin Suscripción": {
            "id": "one_time",
            "price": 850.00,
            "features": [
                "Compra única de alfombra de césped",
                "Envío gratis",
                "Pago único"
            ]
        }
    }

    # Display Plan Cards
    cols = st.columns(len(plans))
    selected_plan = st.radio("Selecciona un plan:", list(plans.keys()), horizontal=True)

    for i, (plan_name, plan_data) in enumerate(plans.items()):
        with cols[i]:
            st.write(f"## {plan_name}")
            if plan_name != "Sin Suscripción":
                st.write(f"### ~~L.1700.00~~ L. {plan_data['price']:.2f} por mes", unsafe_allow_html=True)
            else:
                st.write(f"### L. {plan_data['price']:.2f}", unsafe_allow_html=True)
            for feature in plan_data['features']:
                st.write(f"✅ {feature}")

    # Address Input and Map
    st.subheader("Dirección de entrega")

    # Colonia search
    col1, col2 = st.columns([3, 1])
    with col1:
        colonia = st.text_input("Buscar colonia", value="", key="colonia_search")
    with col2:
        search_button = st.button("Buscar")

    # Initialize map
    if 'map_center' not in st.session_state:
        st.session_state.map_center = [14.0818, -87.2068]  # Default to Tegucigalpa
    if 'search_result' not in st.session_state:
        st.session_state.search_result = None

    # Address search
    if search_button or (colonia and st.session_state.get('last_search') != colonia):
        st.session_state['last_search'] = colonia
        geolocator = Nominatim(user_agent="pasto_verde_app")
        try:
            search_query = f"{colonia}, Tegucigalpa, Honduras"
            location = geolocator.geocode(search_query)
            if location:
                st.session_state.map_center = [location.latitude, location.longitude]
                st.session_state.search_result = location.address
                st.success(f"Colonia encontrada: {location.address}")
            else:
                st.error("No se pudo encontrar la colonia.")
        except Exception as e:
            st.error(f"Error en el servicio de geolocalización: {str(e)}")

    # Create map
    m = folium.Map(location=st.session_state.map_center, zoom_start=15)
    marker = folium.Marker(st.session_state.map_center, draggable=True)
    marker.add_to(m)
    folium_static(m)

    # Specific address details
    specific_address = st.text_input("Número de casa y calle", value="")
    additional_references = st.text_area("Referencias adicionales (opcional)", value="", key="additional_refs")

    # Combine all address information
    full_address = f"{specific_address}, {st.session_state.search_result or colonia}"
    if additional_references:
        full_address += f" ({additional_references})"

    # User Information
    user_full_name = st.text_input("Nombre completo", value=st.session_state.user.name)
    user_email = st.text_input("Correo electrónico", value=st.session_state.user.email)
    user_phone = st.text_input("Número de teléfono", value="")
    delivery_date = st.date_input("Fecha de entrega", value=datetime.today())

    # Delivery Time Frame Selection
    delivery_time_frame = st.radio("Horario de entrega Lunes a Sabado:", ("AM (7am - 12pm)"))

    # Promo Code Input and Disclaimer
    promo_code = st.text_input("Código promocional (opcional)", value="")
    st.caption("Nota: Los códigos promocionales solo son válidos para productos sin suscripción.")

    # Order Review
    if selected_plan and st.session_state.map_center:
        with st.expander("Resumen del Pedido", expanded=True):
            st.write(f"Plan seleccionado: **{selected_plan}**")
            lempira_price = plans[selected_plan]['price']
            total_price = lempira_price

            # Apply promo code discount for "Sin Suscripción"
            if selected_plan == "Sin Suscripción" and promo_code.upper() == "VERDEHN":
                discount = total_price * 0.20
                total_price -= discount
                st.write(f"¡Código promocional aplicado! Descuento: L. {discount:.2f}")

            if selected_plan == "Suscripción Anual":
                total_price *= 11  # Multiply by 11 for annual subscription (1 month free)
                st.write("¡Tienes un mes gratis! Solo pagas por 11 meses.")
            elif selected_plan == "Suscripción Semestral":
                total_price = lempira_price * 6  # Total for semi-annual is 6 months
                st.write(f"Precio total para 6 meses: L. {total_price:.2f}")
            else:
                st.write(f"Precio: L. {lempira_price:.2f} por mes")

            st.write("Cambio de dólar: 1$ = L.25.00")
            st.write(f"Dirección de entrega: {full_address}")
            st.write(f"Nombre completo: {user_full_name}")
            st.write(f"Correo electrónico: {user_email}")
            st.write(f"Número de teléfono: {user_phone}")
            st.write(f"Fecha de entrega: {delivery_date}")
            st.write(f"Horario de entrega: {delivery_time_frame}")
            st.write(f"Total: L. {total_price:.2f}")
            st.write("**Nota:** En el checkout, se incluye una caja de madera con los planes de suscripción. One-time setup fee")

    if st.button("Confirmar pedido"):
        # Create new order
        new_order = Order(
            id=generate_order_id(),
            user_id=st.session_state.user.id,
            product_id=1,  # Assuming product_id 1 is for grass
            quantity=1,
            delivery_address=full_address,
            status=OrderStatus.pending,
            total_price=total_price
        )
        session.add(new_order)

        # If it's a subscription, create a subscription record
        if selected_plan != "Sin Suscripción":
            new_subscription = Subscription(
                user_id=st.session_state.user.id,
                plan_name=selected_plan,
                start_date=datetime.utcnow(),
                is_active=True
            )
            session.add(new_subscription)

        session.commit()
        st.success(f"*Pedido Procesando⌛* Por favor confirmar el pago para coordinar la entrega de su orden. Numero de pedido: {new_order.id}")
        st.balloons()

# PayPal integration
paypal_client_id = st.secrets["paypal"]["client_id"]
paypal_html = f'''
<div id="paypal-button-container"></div>
<script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&currency=USD"></script>
<script>
  paypal.Buttons({{
    createOrder: function(data, actions) {{
      return actions.order.create({{
        purchase_units: [{{
          amount: {{
            value: '{total_price / 25:.2f}'  // Convert to USD
          }}
        }}]
      }});
    }},
    onApprove: function(data, actions) {{
      return actions.order.capture().then(function(details) {{
        fetch("/update_order", {{
          method: "POST",
          headers: {{"Content-Type": "application/json"}},
          body: JSON.stringify({{
            order_id: "{new_order.id}",
            transaction_id: details.id
          }})
        }})
        .then(response => response.json())
        .then(data => {{
          if (data.success) {{
            alert("Payment processed successfully. Your order is confirmed!");
          }} else {{
            alert("Payment processed, but there was an issue updating your order. Please contact support.");
          }}
        }});
      }});
    }}
  }}).render('#paypal-button-container');
</script>
'''
components.html(paypal_html, height=300)

session.close()

def update_order_status(order_id, transaction_id):
    session = Session()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.confirmed
            order.payment_status = "paid"
            order.transaction_id = transaction_id
            order.updated_at = datetime.utcnow()
            session.commit()
            return True
    except Exception as e:
        session.rollback()
        st.error(f"Error updating order status: {str(e)}")
        return False
    finally:
        session.close()

def update_order_endpoint():
    if st.request.method == "POST":
        data = st.request.json
        order_id = data.get("order_id")
        transaction_id = data.get("transaction_id")
        
        success = update_order_status(order_id, transaction_id)
        
        return {"success": success}

# Add this to your Streamlit app setup
st.add_page("update_order", update_order_endpoint)
