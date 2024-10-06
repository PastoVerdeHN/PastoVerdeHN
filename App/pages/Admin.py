import streamlit as st
import hashlib

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Admin access password (temporary hardcoded for simplicity)
admin_access_password = "simpleadminpass"

# Check if the admin has accessed the hash generator
if 'admin_access_granted' not in st.session_state:
    st.session_state.admin_access_granted = False

# Admin password entry for accessing the hash generator
if not st.session_state.admin_access_granted:
    st.title("Admin Access")
    admin_password = st.text_input("Enter admin password to access hashing tool", type="password")
    if st.button("Verify Admin"):
        if admin_password == admin_access_password:
            st.session_state.admin_access_granted = True
            st.success("Access granted. You can now generate hashed passwords.")
        else:
            st.error("Incorrect admin password.")
else:
    # Hash generation logic for the admin once access is granted
    st.title("Generate Hashed Password")
    new_password = st.text_input("Enter a password to hash", type="password")
    if st.button("Generate Hash"):
        hashed = hash_password(new_password)
        st.write(f"Hashed password: {hashed}")

# After admin tools, your login logic continues...

# Get the correct password hash from secrets
correct_password_hash = st.secrets["admin2"]["password_hash"]

# Initialize session state for the main login
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Main login form for the admin dashboard
if not st.session_state.authenticated:
    st.title("Admin Login")
    password = st.text_input("Enter password", type="password")
    
    if st.button("Login"):
        # Hash the entered password
        if hash_password(password) == correct_password_hash:
            st.session_state.authenticated = True
            st.experimental_rerun()  # Rerun the app to show the dashboard after login
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
