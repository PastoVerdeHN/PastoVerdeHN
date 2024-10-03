import streamlit as st
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from modules.models import User, UserType, Base
from auth0_component import login_button
from sqlalchemy import create_engine
from modules.email import send_welcome_email
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database(database_url):
  try:
      debug_mode = st.secrets.get("debug", False)  # Default to False if not specified
      logger.info("Setting up database with debug mode: %s", debug_mode)
  except KeyError:
      st.error("Database URL not found in Streamlit secrets. Please check your configuration.")
      logger.error("Database URL not found in Streamlit secrets.")
      st.stop()
  
  engine = create_engine(database_url, echo=debug_mode)
  Base.metadata.create_all(engine)
  logger.info("Database setup complete.")
  return sessionmaker(bind=engine)

def auth0_authentication():
  logger.info("Starting authentication process")
  
  if 'user' not in st.session_state:
      st.session_state.user = None
  if 'auth_status' not in st.session_state:
      st.session_state.auth_status = None
  
  if st.session_state.user is None:
      auth_choice = st.sidebar.radio("Elige acción", ["🔑 Entrar"])
      
      if auth_choice == "🔑 Entrar":
          try:
              AUTH0_CLIENT_ID = st.secrets["auth0"]["AUTH0_CLIENT_ID"]
              AUTH0_DOMAIN = st.secrets["auth0"]["AUTH0_DOMAIN"]
              ADMIN_EMAIL = st.secrets["admin"]["email"]  # Get admin email from secrets
              database_url = st.secrets["database"]["url"]
              logger.info("Auth0 configuration loaded successfully.")
          except KeyError as e:
              st.error("Configuration not found. Please check your Streamlit secrets.")
              logger.error("Configuration not found: %s", e)
              return None
          
          Session = setup_database(database_url)
          
          user_info = login_button(
              AUTH0_CLIENT_ID, 
              domain=AUTH0_DOMAIN,
              redirect_uri="http://localhost:8501/callback"  # Adjust this if you're not running locally
          )
          
          if user_info and st.session_state.auth_status != "authenticated":
              logger.info("User info retrieved: %s", user_info)
              session = Session()
              user = session.query(User).filter_by(email=user_info['email']).first()
              
              if not user:
                  logger.info("New user registration for email: %s", user_info['email'])
                  user = User(
                      id=user_info['sub'],
                      name=user_info['name'],
                      email=user_info['email'],
                      type=UserType.admin if user_info['email'] == ADMIN_EMAIL else UserType.customer,
                      address='',
                      created_at=datetime.utcnow(),
                      welcome_email_sent=False
                  )
                  session.add(user)
                  session.commit()
                  logger.info("User registered successfully.")
              else:
                  logger.info("User found: %s", user.email)
                  if user.email == ADMIN_EMAIL:
                      user.type = UserType.admin  # Set user type to admin if necessary
              
              if not user.welcome_email_sent:
                  logger.info("Sending welcome email to: %s", user.email)
                  email_sent = send_welcome_email(user.email, user.name)
                  if email_sent:
                      user.welcome_email_sent = True
                      session.commit()
                      logger.info("Welcome email sent successfully.")
                  else:
                      st.warning("Failed to send welcome email. Please check your email configuration.")
                      logger.error("Failed to send welcome email to: %s", user.email)
              
              user.last_login = datetime.utcnow()
              session.commit()
              logger.info("User last login updated.")
              
              st.session_state.user = user
              st.session_state.auth_status = "authenticated"
              st.success(f"Bienvenido, {user.name}!")
              session.close()

  return st.session_state.user
