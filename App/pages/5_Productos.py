import streamlit as st

# --- SHARED ON ALL PAGES ---
st.logo("https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/menu_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.png")

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

    iframe_html = f"""
    <div class="iframe-container" style="height: {iframe_height}px; overflow: hidden;">
        <iframe src="{url}" scrolling="no" style="height: {iframe_height}px; width: 100%; border: none; transform: translateY(-{hide_pixels_top}px);"></iframe>
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
    
    # Load and display the sidebar image
    image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
    st.sidebar.image(image_url, use_column_width=True, caption="© La Naturaleza A Los Pies De Tus Mascota")

    st.title("Productos")

    # Define the website URL to embed
    website_url = "https://pastoverde.durablesites.com/productos?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="
    
    # Define container and iframe dimensions
    container_height = 600           # Height of the visible container in pixels
    hide_percentage_top = 20         # Percentage of the top to hide
    hide_percentage_bottom = 7.2      # Percentage of the bottom to hide

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
