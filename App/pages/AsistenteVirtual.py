import streamlit as st
import streamlit.components.v1 as components

# Retrieve the iframe URL from the secrets file
iframe_url = st.secrets["iframe_url"]["url"]

# Create the iframe HTML using the secret URL
iframe_html = f"""
<iframe title="embed" src="{iframe_url}" width="100%" height="500px" style="background:white"></iframe>
"""

# Render the iframe using Streamlit's components.html function
components.html(iframe_html, height=500)

