import streamlit as st
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from modules.models import User, UserType, Base
from auth0_component import login_button
from sqlalchemy import create_engine
from modules.email import send_welcome_email
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database(database_url):
    try:
        debug_mode = st.secrets.get("debug", False)
        logger.info("Setting up database with debug mode: %s", debug_mode)
        engine = create_engine(database_url, echo=debug_mode)
        Base.metadata.create_all(engine)
        logger.info("Database setup complete.")
        return sessionmaker(bind=engine)
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        st.error("An error occurred while setting up the database. Please check your configuration.")
        st.stop()

def auth0_authentication():
    logger.info("Starting authentication process")
    
    current_time = time.time()
    if 'last_auth_time' not in st.session_state or (current_time - st.session_state.get('last_auth_time', 0)) > 3600:  # 1 hour
        st.session_state.user = None
        st.session_state.auth_status = None
    
    if st.session_state.get('user') is None:
        auth_choice = st.sidebar.radio("Elige acción", ["🔑 Entrar"])
        
        if auth_choice == "🔑 Entrar":
            try:
                AUTH0_CLIENT_ID = st.secrets["auth0"]["AUTH0_CLIENT_ID"]
                AUTH0_DOMAIN = st.secrets["auth0"]["AUTH0_DOMAIN"]
                ADMIN_EMAIL = st.secrets["admin"]["email"]
                database_url = st.secrets["database"]["url"]
                logger.info("Auth0 configuration loaded successfully.")
            except KeyError as e:
                logger.error(f"Configuration not found: {e}")
                st.error("Configuration not found. Please check your Streamlit secrets.")
                return None
            
            Session = setup_database(database_url)
            
            user_info = login_button(
                AUTH0_CLIENT_ID, 
                domain=AUTH0_DOMAIN,
                redirect_uri="http://localhost:8501/callback"
            )
            
            if user_info and st.session_state.get('auth_status') != "authenticated":
                logger.info(f"User info retrieved: {user_info}")
                session = Session()
                try:
                    user = session.query(User).filter_by(email=user_info['email']).first()
                    
                    if not user:
                        logger.info(f"New user registration for email: {user_info['email']}")
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
                        logger.info(f"User found: {user.email}")
                        if user.email == ADMIN_EMAIL:
                            user.type = UserType.admin
                    
                    if not user.welcome_email_sent:
                        logger.info(f"Attempting to send welcome email to: {user.email}")
                        email_sent = send_welcome_email(user.email, user.name)
                        logger.info(f"Welcome email sent successfully: {email_sent}")
                        if email_sent:
                            user.welcome_email_sent = True
                            session.commit()
                            logger.info("User welcome_email_sent status updated in database")
                        else:
                            st.warning("Failed to send welcome email. Please check your email configuration.")
                            logger.error(f"Failed to send welcome email to: {user.email}")
                    
                    user.last_login = datetime.utcnow()
                    session.commit()
                    logger.info("User last login updated.")
                    
                    st.session_state.user = user
                    st.session_state.auth_status = "authenticated"
                    st.session_state.last_auth_time = current_time
                    st.success(f"Bienvenido, {user.name}!")
                except Exception as e:
                    logger.error(f"Error during user authentication: {e}")
                    st.error("An error occurred during authentication. Please try again.")
                finally:
                    session.close()

    return st.session_state.get('user')
