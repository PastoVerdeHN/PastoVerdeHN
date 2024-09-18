import streamlit as st

def app():
  # Configure the Streamlit page
  st.set_page_config(
      page_title="Pagina Web",
      page_icon="🌿",
      layout="wide"
  )

  # Define the website URL to embed
  website_url = "https://pastoverde.durablesites.com/?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="

  # Define container and iframe dimensions
  container_height = 600  # Height of the visible container in pixels
  hide_percentage_top = 20    # Percentage of the top to hide
  hide_percentage_bottom = 10 # Percentage of the bottom to hide

  # Calculate the pixel values to hide
  hide_pixels_top = container_height * hide_percentage_top / 100  # Pixels to hide from top (20% of 600px = 120px)
  hide_pixels_bottom = container_height * hide_percentage_bottom / 100  # Pixels to hide from bottom (10% of 600px = 60px)

  # Calculate total iframe height and shift
  iframe_height = container_height + hide_pixels_top + hide_pixels_bottom  # Total iframe height (600 + 120 + 60 = 780px)
  shift_pixels_top = hide_pixels_top  # Pixels to shift upwards (120px)

  # HTML and CSS to embed the iframe with hidden top and bottom portions
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
      top: -{shift_pixels_top}px;          /* Shift upwards to hide top 20% */
      left: 0;
      width: 100%;
      height: {iframe_height}px;      /* Increase height to cover hidden top and bottom */
      border: none;                   /* Remove iframe border */
  }}
  </style>
  <div class="iframe-container">
      <iframe src="{website_url}" scrolling="no"></iframe>
  </div>
  """

  # Embed the HTML into the Streamlit app
  st.components.v1.html(
      iframe_html,
      height=container_height,  # Match the container's height
      scrolling=False           # Disable Streamlit's own scrolling for this component
  )

  # Add a navigation button (optional)
  if st.button("Inicio"):
      st.switch_page("App.py")  # Ensure "App.py" is the correct target page name

if __name__ == "__main__":
  app()
