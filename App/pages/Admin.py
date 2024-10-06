import streamlit as st
import hashlib

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Original password and its hash
admin_access_password = "simpleadminpass"
correct_password_hash = "5d8923f10a5c0939a945d6fe7bedaea6cdc10e94eb3dc40ad1428a246288c3bf"  # Updated hash

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login form
if not st.session_state.authenticated:
    st.title("Admin Login")
    password = st.text_input("Enter password", type="password")
    
    if st.button("Login"):
        # Hash the entered password
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
