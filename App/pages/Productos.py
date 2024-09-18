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
      width: 100%;
      height: {container_height}px;  /* Container height */
      overflow: hidden;              /* Hide overflowing content */
      border: 2px solid #4CAF50;     /* Optional: Add a border to the container */
      border-radius: 10px;           /* Optional: Rounded corners */
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);  /* Optional: Add a shadow */
  }}
  .iframe-container iframe {{
      position: absolute;
      top: -{shift_pixels_top}px;         /* Shift upwards to hide top {hide_top_pct}% */
      left: 0;
      width: 100%;
      height: {iframe_height}px;         /* Increase height to cover hidden top and bottom */
      border: none;                      /* Remove iframe border */
  }}
  </style>
  <div class="iframe-container">
      <iframe src="{url}" scrolling="no"></iframe>
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
  hide_percentage_bottom = 30      # Percentage of the bottom to hide

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
