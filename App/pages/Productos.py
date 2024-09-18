import streamlit as st

def generate_iframe_html(url, container_height, hide_top_pct, hide_bottom_pct):
    """
    Generates custom HTML and CSS to embed an iframe with specified hidden portions.

    Parameters:
    - url (str): The URL to embed in the iframe.
    - container_height (int or float): The height of the visible container in pixels.
    - hide_top_pct (float): The percentage of the top to hide.
    - hide_bottom_pct (float): The percentage of the bottom to hide.

    Returns:
    - str: The HTML string with embedded CSS and iframe.
    """
    hide_pixels_top = container_height * hide_top_pct / 100
    hide_pixels_bottom = container_height * hide_bottom_pct / 100
    iframe_height = container_height + hide_pixels_top + hide_pixels_bottom
    shift_pixels_top = hide_pixels_top

    iframe_html = f"""
    <style>
        .iframe-container {{
            position: relative;
            height: {iframe_height}px;
            overflow: hidden;
        }}
        .iframe-container iframe {{
            position: absolute;
            top: -{shift_pixels_top}px; /* Shift the iframe up to hide the top */
            height: {iframe_height}px; /* Set the height of the iframe */
            width: 100%; /* Full width */
            pointer-events: none; /* Disable pointer events */
            overflow: auto; /* Allow scrolling */
        }}
    </style>
    <div class="iframe-container">
        <iframe src="{url}" scrolling="yes"></iframe>
    </div>
    """
    return iframe_html

def app():
    # Configure the Streamlit page
    st.set_page_config(
        page_title="Productos",
        page_icon="🌿",
        layout="wide"
    )
    
    st.title("Productos")

    # Define the website URL to embed
    website_url = "https://pastoverde.durablesites.com/productos?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="
    
    # Define container and iframe dimensions
    container_height = 600           # Height of the visible container in pixels
    hide_percentage_top = 20         # Percentage of the top to hide
    hide_percentage_bottom = 10      # Percentage of the bottom to hide

    # Generate the iframe HTML
    iframe_html = generate_iframe_html(
        url=website_url,
        container_height=container_height,
        hide_top_pct=hide_percentage_top,
        hide_bottom_pct=hide_percentage_bottom
    )

    # Embed the HTML into the Streamlit app
    st.components.v1.html(
        iframe_html,
        height=container_height,    # Ensures the embedded HTML matches the container's height
        scrolling=False             # Disables Streamlit's own scrolling for this component
    )

    # Add a navigation button (optional)
    if st.button("Inicio"):
        st.switch_page("App.py")  # Ensure "App.py" exists and is correctly named

if __name__ == "__main__":
    app()
