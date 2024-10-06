import streamlit as st
from modules.zadmin import (
    overview_page, users_page, products_page, orders_page,
    subscriptions_page, analytics_page
)

st.set_page_config(page_title="Admin Dashboard", page_icon="🛍️", layout="wide")

# Prompt for password before displaying the dashboard
password = st.text_input("Enter password to access Admin Dashboard", type="password")

if password == st.secrets["admin"]["dashboard_password"]:
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview", "Users", "Products", "Orders", "Subscriptions", "Analytics"])

    # Main app logic
    if page == "Overview":
        overview_page()
    elif page == "Users":
        users_page()
    elif page == "Products":
        products_page()
    elif page == "Orders":
        orders_page()
    elif page == "Subscriptions":
        subscriptions_page()
    elif page == "Analytics":
        analytics_page()
else:
    st.error("Incorrect password. Access denied.")
