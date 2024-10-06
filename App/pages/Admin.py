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

# Admin access password (temporary hardcoded for simplicity)
admin_access_password = "simpleadminpass"

# Initialize session state for admin access and authentication
if 'admin_access_granted' not in st.session_state:
    st.session_state.admin_access_granted = False

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Admin access for password hashing
if not st.session_state.admin_access_granted:
    st.title("Admin Access")
    admin_password = st.text_input("Enter admin password to access hashing tool", type="password")
    if st.button("Verify Admin"):
        if admin_password == admin_access_password:
            st.session_state.admin_access_granted = True
            st.success("Access granted to generate hashed passwords.")
        else:
            st.error("Incorrect admin password.")
else:
    # Only show the hashing tool after admin verification
    st.title("Generate Hashed Password (For Admin Use Only)")
    if st.checkbox("Generate hashed password (for admin use only)"):
        new_password = st.text_input("Enter a password to hash", type="password")
        if st.button("Generate Hash"):
            hashed = hash_password(new_password)
            st.write(f"Hashed password: {hashed}")

# Separate section for the main admin login
st.title("Admin Login")
password = st.text_input("Enter password", type="password")
if st.button("Login"):
    correct_password_hash = st.secrets["admin2"]["password_hash"]
    if hash_password(password) == correct_password_hash:
        st.session_state.authenticated = True
        st.success("Logged in successfully!")
        st.experimental_rerun()  # Rerun to load the admin dashboard
    else:
        st.error("Incorrect password.")

# If logged in, display admin dashboard features
if st.session_state.authenticated:
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview", "Users", "Products", "Orders", "Subscriptions", "Analytics"])

    # Main app logic for the selected page
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
