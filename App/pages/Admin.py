import streamlit as st
import pandas as pd
from sqlalchemy import func
from datetime import datetime
from contextlib import contextmanager
from .models import SessionLocal, User, Product, Order, Subscription, PaymentTransaction, UserType

# Set up page config
st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simplified Admin View
def simple_admin_page():
    st.title("Simple Admin View")

    # Total Users
    with get_db() as session:
        total_users = session.query(func.count(User.id)).scalar()
        st.metric("Total Users", total_users)

        # Latest Orders
        latest_orders = session.query(Order).order_by(Order.created_at.desc()).limit(5).all()
        if latest_orders:
            order_data = [{
                "ID": order.id,
                "User": order.user.name if order.user else "N/A",
                "Product": order.product.name if order.product else "N/A",
                "Total": f"${order.total_price:.2f}",
                "Created At": order.created_at
            } for order in latest_orders]
            st.table(pd.DataFrame(order_data))
        else:
            st.info("No recent orders found.")
