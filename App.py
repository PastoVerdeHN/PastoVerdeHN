import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import time
import sqlalchemy
from dataclasses import dataclass
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os
from dotenv import load_dotenv
from auth0_component import login_button
from sqlalchemy import inspect
from functools import lru_cache
from pystrix import Manager

# ... (rest of the imports and initial setup)

def main():
    user = auth0_authentication()

    if user:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"

        # Creative menu
        menu_items = {
            "🏠 Home": home_page,
            "🛒 Order Now": place_order,
            "📦 My Orders": display_user_orders,
            "🗺️ Map": display_map,
            "🛍️ Services": display_services,
        }
        if user.type == 'driver':
            menu_items["🚗 Driver Dashboard"] = driver_dashboard

        cols = st.columns(len(menu_items))
        for i, (emoji_label, func) in enumerate(menu_items.items()):
            if cols[i].button(emoji_label):
                st.session_state.current_page = emoji_label

        # Display the current page
        menu_items[st.session_state.current_page]()

        if st.sidebar.button("🚪 Log Out"):
            st.session_state.user = None
            st.success("Logged out successfully.")
            st.experimental_rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")
    else:
        st.write("Please log in to access the full features of the app")
        st.sidebar.markdown("---")
        st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")

if __name__ == "__main__":
    main()

# The following lines are redundant and should be removed:
# else:
#     st.write("Please log in to access the full features of the app")
#     st.sidebar.markdown("---")
#     st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")

# else:
#     st.write("Please log in to access the full features of the app")
#     st.sidebar.markdown("---")
#     st.sidebar.markdown("[Terms and Conditions](/Terms_and_Conditions)")

def home_page():
    st.write(f"Bienvenidos a PASTO VERDE Honduras, {st.session_state.user.name}! 🎉")
    session = Session()
    merchants = session.query(Merchant).all()
    st.write("Servicios Disponibles")
    for merchant in merchants:
        st.write(f"- {merchant.name}")

# ... (rest of the functions)

def display_services():
    st.subheader("🛍️ Ordenes Dispibles")
    
    st.write("### 🛒 Grocery Stores")
    for store_name, store_info in GROCERY_STORES.items():
        with st.expander(store_name):
            display_service(Service(
                name=store_name,
                url=store_info['url'],
                instructions=store_info['instructions'],
                video_url=store_info.get('video_url'),
                video_title=store_info.get('video_title'),
                image_url=store_info.get('image_url'),
                address=store_info['address'],
                phone=store_info['phone']
            ))
    
    st.write("### 🍽️ Restaurants")
    for restaurant_name, restaurant_info in RESTAURANTS.items():
        with st.expander(restaurant_name):
            display_service(Service(
                name=restaurant_name,
                url=restaurant_info['url'],
                instructions=restaurant_info['instructions'],
                image_url=restaurant_info.get('image_url'),
                address=restaurant_info['address'],
                phone=restaurant_info['phone']
            ))

# The following line is redundant and should be removed:
# if __name__ == "__main__":
#     main()
