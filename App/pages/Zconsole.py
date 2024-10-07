import streamlit as st
import hashlib

st.warning("Si no eres un administrador, gerente o miembro del equipo de ventas de Pasto Verde, por favor abandona esta página. Gracias.")

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Retrieve the correct password and its hash from secrets
admin_access_password = st.secrets["admin2"]["password"]  # Retrieve the plain password
correct_password_hash = st.secrets["admin2"]["password_hash"]  # Retrieve the password hash

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login form
if not st.session_state.authenticated:
    st.title("Admin Login")
    password = st.text_input("Enter password", type="password")
    
    if st.button("Login"):
        # Hash the entered password and compare it with the stored hash
        if hash_password(password) == correct_password_hash:
            st.session_state.authenticated = True  # Set authentication to true
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
    page = st.sidebar.radio("Go to", ["Overview", "Users", "Products", "Orders", "Subscriptions", "Analytics"], key="sidebar_radio")

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
