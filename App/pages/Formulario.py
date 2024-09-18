import streamlit as st

def app():
  st.set_page_config(
      page_title="Ordena Hoy",
      page_icon="🌿",
      layout="wide"
  )
  
  # Your website URL
  website_url = "https://pastoverde.durablesites.com/contact?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="
  
  # HTML and CSS to display only the top 80% of the webpage
  iframe_html = f"""
  <style>
  .iframe-container {{
      position: relative;
      width: 100%;
      height: 600px;  /* Adjust the container height as needed */
      overflow: hidden;
  }}
  .iframe-container iframe {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 125%;   /* Increase the iframe height to ensure content fills beyond the container */
      pointer-events: none;  /* Disable user interaction with the iframe */
  }}
  .overlay {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 20%;  /* Cover the bottom 20% of the container */
      background-color: white;  /* Or match your app's background color */
  }}
  </style>
  <div class="iframe-container">
      <iframe src="{website_url}" frameborder="0" scrolling="no"></iframe>
      <div class="overlay"></div>
  </div>
  """
  # Embed the HTML into the Streamlit app
  st.components.v1.html(iframe_html, height=600, scrolling=False)
  
  if st.button("Inicio"):
      st.experimental_rerun()

if __name__ == "__main__":
      app()
