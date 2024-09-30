import streamlit as st
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from modules.models import User, UserType
from auth0_component import login_button
from .models import setup_database
from modules.email import send_welcome_email


# Database setup
try:
  database_url = st.secrets["database"]["url"]
except KeyError:
  database_url = os.getenv("DATABASE_URL")

if not database_url:
  st.error("Database URL not found. Please set it in Streamlit secrets or as an environment variable.")
  st.stop()

Session = setup_database(database_url)

def auth0_authentication():
  if 'user' not in st.session_state:
      st.session_state.user = None
  if 'auth_status' not in st.session_state:
      st.session_state.auth_status = None

  if st.session_state.user is None: 
      if auth_choice == "🔑 Entrar":
          try:
              AUTH0_CLIENT_ID = st.secrets["auth0"]["AUTH0_CLIENT_ID"]
              AUTH0_DOMAIN = st.secrets["auth0"]["AUTH0_DOMAIN"]
              ADMIN_EMAIL = st.secrets["admin"]["email"]  # Get admin email from secrets
          except KeyError:
              st.error("Auth0 configuration not found. Please set AUTH0_CLIENT_ID and AUTH0_DOMAIN in Streamlit secrets.")
              return None
          
          user_info = login_button(
              AUTH0_CLIENT_ID, 
              domain=AUTH0_DOMAIN,
              redirect_uri="http://localhost:8501/callback"  # Adjust this if you're not running locally
          )
          
          if user_info and st.session_state.auth_status != "authenticated":
              session = Session()
              user = session.query(User).filter_by(email=user_info['email']).first()
              
              if not user:
                  # New user registration
                  user = User(
                      id=user_info['sub'],
                      name=user_info['name'],
                      email=user_info['email'],
                      type=UserType.admin if user_info['email'] == ADMIN_EMAIL else UserType.customer,  # Set type based on email
                      address='',
                      created_at=datetime.utcnow(),
                      welcome_email_sent=False
                  )
                  session.add(user)
                  session.commit()
              else:
                  # Check if the user is an admin
                  if user.email == ADMIN_EMAIL:
                      user.type = UserType.admin  # Set user type to admin if necessary

              if not user.welcome_email_sent:
                  send_welcome_email(user.email, user.name)  # Ensure this function is defined
                  user.welcome_email_sent = True
                  session.commit()
              
              user.last_login = datetime.utcnow()
              session.commit()
              
              st.session_state.user = user
              st.session_state.auth_status = "authenticated"
              st.success(f"Bienvenido, {user.name}!")
              session.close()
  
  return st.session_state.user
