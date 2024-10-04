import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from modules.models import User, Product, Order, Subscription, PaymentTransaction, OrderStatus, setup_database
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
from st_link_analysis.component.icons import SUPPORTED_ICONS
import random

def generate_token():
  """Generate a secure random token"""
  return secrets.token_hex(16)

def hash_password(password):
  """Generate a secure hash of the password"""
  return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password, stored_hash):
  """Verify the input password against the stored hash"""
  return hash_password(input_password) == stored_hash

def initial_login():
  """Handle the initial login with hardcoded credentials"""
  st.subheader("Initial Admin Login")
  username = st.text_input("Username")
  password = st.text_input("Password", type="password")
  if st.button("Login"):
      if (username == st.secrets["hardcoded_username"] and 
          password == st.secrets["hardcoded_password"]):
          token = generate_token()
          expiration = datetime.now() + timedelta(minutes=15)
          st.session_state.admin_token = token
          st.session_state.token_expiration = expiration
          st.success("Initial login successful. Use this token for the second step:")
          st.code(token)
          return True
      else:
          st.error("Invalid username or password")
  return False

def token_login():
  """Handle the second step of login using the generated token"""
  st.subheader("Admin Token Login")
  token = st.text_input("Enter Admin Token")
  if st.button("Verify Token"):
      if token == st.session_state.get("admin_token") and datetime.now() < st.session_state.get("token_expiration", datetime.min):
          st.session_state.admin_logged_in = True
          del st.session_state.admin_token
          del st.session_state.token_expiration
          return True
      else:
          st.error("Invalid or expired token")
  return False

def show_admin_dashboard():
  st.set_page_config(layout="wide")

  # Setup database session
  SessionLocal = setup_database()
  session = SessionLocal()

  st.title("Admin Dashboard")

  # Sidebar for navigation
  st.sidebar.title("Navigation")
  page = st.sidebar.radio("Go to", ["Overview", "Network Analysis", "Order Management"])

  if page == "Overview":
      show_overview(session)
  elif page == "Network Analysis":
      show_network_analysis(session)
  elif page == "Order Management":
      show_order_management(session)

  session.close()

def show_overview(session):
  st.header("Platform Overview")
  
  col1, col2, col3, col4 = st.columns(4)
  
  with col1:
      user_count = session.query(User).count()
      st.metric("Total Users", user_count)
  
  with col2:
      product_count = session.query(Product).count()
      st.metric("Total Products", product_count)
  
  with col3:
      order_count = session.query(Order).count()
      st.metric("Total Orders", order_count)
  
  with col4:
      subscription_count = session.query(Subscription).count()
      st.metric("Active Subscriptions", subscription_count)

  # Recent Orders
  st.subheader("Recent Orders")
  recent_orders = session.query(Order).order_by(Order.created_at.desc()).limit(5).all()
  for order in recent_orders:
      st.write(f"Order ID: {order.id}, Status: {order.status.value}, Total: L. {order.total_price:.2f}")

def show_network_analysis(session):
  st.header("Network Analysis")

  def get_color():
      return f"#{random.randint(0, 0xFFFFFF):06x}"

  def get_icon():
      return random.choice(list(SUPPORTED_ICONS))

  # Prepare data for network analysis
  nodes = []
  edges = []

  # Users
  users = session.query(User).all()
  for user in users:
      nodes.append({
          "id": user.id,
          "label": "USER",
          "name": user.name,
          "email": user.email,
          "type": user.type.value,
          "color": get_color(),
          "icon": get_icon()
      })

  # Products
  products = session.query(Product).all()
  for product in products:
      nodes.append({
          "id": f"P{product.id}",
          "label": "PRODUCT",
          "name": product.name,
          "price": product.price,
          "color": get_color(),
          "icon": get_icon()
      })

  # Orders
  orders = session.query(Order).all()
  for order in orders:
      nodes.append({
          "id": order.id,
          "label": "ORDER",
          "status": order.status.value,
          "total_price": order.total_price,
          "color": get_color(),
          "icon": get_icon()
      })
      # User to Order edge
      edges.append({
          "id": f"UO{order.id}",
          "source": order.user_id,
          "target": order.id,
          "label": "PLACED"
      })
      # Order to Product edge
      edges.append({
          "id": f"OP{order.id}",
          "source": order.id,
          "target": f"P{order.product_id}",
          "label": "CONTAINS"
      })

  # Subscriptions
  subscriptions = session.query(Subscription).all()
  for sub in subscriptions:
      nodes.append({
          "id": f"S{sub.id}",
          "label": "SUBSCRIPTION",
          "plan_name": sub.plan_name,
          "is_active": sub.is_active,
          "color": get_color(),
          "icon": get_icon()
      })
      # User to Subscription edge
      edges.append({
          "id": f"US{sub.id}",
          "source": sub.user_id,
          "target": f"S{sub.id}",
          "label": "SUBSCRIBED"
      })

  # Create the network data structure
  network_data = {
      "nodes": nodes,
      "edges": edges
  }

  # Node and edge styles
  node_styles = [
      NodeStyle("USER", "#4CAF50", "name", "person"),
      NodeStyle("PRODUCT", "#2196F3", "name", "package"),
      NodeStyle("ORDER", "#FFC107", "status", "shopping-cart"),
      NodeStyle("SUBSCRIPTION", "#9C27B0", "plan_name", "calendar")
  ]

  edge_styles = [
      EdgeStyle("PLACED", labeled=True, directed=True),
      EdgeStyle("CONTAINS", labeled=True, directed=True),
      EdgeStyle("SUBSCRIBED", labeled=True, directed=True)
  ]

  # Layout settings
  layout = {"name": "cose", "animate": "end", "nodeDimensionsIncludeLabels": False}

  # Display the network
  st_link_analysis(
      network_data,
      node_styles=node_styles,
      edge_styles=edge_styles,
      layout=layout,
      key="network"
  )

def show_order_management(session):
  st.header("Order Management")

  # Function to update order status
  def update_order_status(order_id, new_status):
      order = session.query(Order).filter_by(id=order_id).first()
      if order:
          order.status = new_status
          order.updated_at = datetime.utcnow()
          session.commit()
          st.success(f"Order {order_id} updated to {new_status.value}")
      else:
          st.error(f"Order {order_id} not found")

  # Function to automatically update order status based on time
  def auto_update_order_status():
      current_time = datetime.utcnow()
      orders = session.query(Order).all()
      for order in orders:
          if order.status == OrderStatus.pending and (current_time - order.created_at) > timedelta(hours=1):
              update_order_status(order.id, OrderStatus.confirmed)
          elif order.status == OrderStatus.confirmed and (current_time - order.updated_at) > timedelta(days=1):
              update_order_status(order.id, OrderStatus.shipped)
          elif order.status == OrderStatus.shipped and (current_time - order.updated_at) > timedelta(days=3):
              update_order_status(order.id, OrderStatus.delivered)

  # Manual order status update
  st.subheader("Manual Order Status Update")
  orders = session.query(Order).all()
  order_id = st.selectbox("Select Order ID", [order.id for order in orders])
  new_status = st.selectbox("Select New Status", [status for status in OrderStatus])
  if st.button("Update Order Status"):
      update_order_status(order_id, new_status)

  # Automatic order status update
  st.subheader("Automatic Order Status Update")
  if st.button("Run Automatic Updates"):
      auto_update_order_status()
      st.success("Automatic updates completed")

  # Order Status Flow Visualization
  st.subheader("Order Status Flow")
  status_flow = {
      OrderStatus.pending: 0,
      OrderStatus.confirmed: 1,
      OrderStatus.shipped: 2,
      OrderStatus.delivered: 3,
      OrderStatus.completed: 4,
      OrderStatus.cancelled: -1
  }

  for order in orders:
      st.write(f"Order {order.id}: {order.status.value}")
      progress = status_flow[order.status] / 4  # Normalize to 0-1 range
      st.progress(progress)

def admin_dashboard():
  if "admin_logged_in" not in st.session_state:
      st.session_state.admin_logged_in = False

  if not st.session_state.admin_logged_in:
      if "admin_token" not in st.session_state:
          if initial_login():
              st.experimental_rerun()
      else:
          if token_login():
              st.experimental_rerun()
  
  if st.session_state.admin_logged_in:
      show_admin_dashboard()

if __name__ == "__main__":
  admin_dashboard()
