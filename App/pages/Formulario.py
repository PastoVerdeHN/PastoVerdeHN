import streamlit as st

def app():
  # Configure the Streamlit page
  st.set_page_config(
      page_title="Ordena Hoy",
      page_icon="🌿",
      layout="wide"
  )
  
  # Load and display the sidebar image with green glow
  image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
  st.sidebar.image(image_url, use_column_width=True, caption="La Naturaleza A Los Pies De Tus Mascota")

  # Define the website URL to embed
  website_url = "https://pastoverde.durablesites.com/contact?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="

  # Define container and iframe dimensions
  container_height = 600  # Height of the visible container in pixels
  hide_percentage_top = 20  # Percentage of the top to hide
  hide_percentage_bottom = 10  # Percentage of the bottom to hide

  hide_pixels_top = container_height * hide_percentage_top / 100  # Pixels to hide from top
  hide_pixels_bottom = container_height * hide_percentage_bottom / 100  # Pixels to hide from bottom

  visible_percentage = 100 - (hide_percentage_top + hide_percentage_bottom)  # 70%
  iframe_height = container_height + hide_pixels_top + hide_pixels_bottom  # Total iframe height
  shift_pixels_top = hide_pixels_top  # Pixels to shift upwards

  # HTML and CSS to embed the iframe with hidden top and bottom portions
  iframe_html = f"""
  <div class="iframe-container" style="height: {iframe_height}px; overflow: hidden;">
      <iframe src="{website_url}" style="height: {iframe_height}px; width: 100%;" scrolling="no"></iframe>
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
      st.experimental_rerun()

if __name__ == "__main__":
  app()
