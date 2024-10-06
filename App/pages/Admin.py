import streamlit as st
import hashlib
from modules.zadmin import (
    overview_page, users_page, products_page, orders_page,
    subscriptions_page, analytics_page
)
st.set_page_config(page_title="Admin Dashboard", page_icon="🛍️", layout="wide")

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Get the correct password hash from secrets
correct_password_hash = st.secrets["admin2"]["password_hash"]

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login form
if not st.session_state.authenticated:
    st.title("Admin Login")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if hash_password(password) == correct_password_hash:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password")
else:
    # Your existing admin dashboard code goes here
    from modules.zadmin import (
        overview_page, users_page, products_page, orders_page,
        subscriptions_page, analytics_page
    )

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

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
