import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from jinja2 import Template
from folium import MacroElement
import streamlit as st

def display_map():
  st.subheader("🗺️ Zona de Entrega")
  st.subheader("Envíos gratuitos a las 7 zonas del mapa 🚚📦")
  
  # Coordinates for Tegucigalpa
  tegucigalpa_coords = [14.0818, -87.2068]
  
  # Create a map centered on Tegucigalpa
  m = folium.Map(location=tegucigalpa_coords, zoom_start=12)
  
  # Define delivery zones (adjusted to reduce overlap)
  zones = {
      "Zona 5": {
          "coordinates": [
              [14.1300, -87.2800],
              [14.1300, -87.1450],
              [14.0950, -87.1450],
              [14.0950, -87.2800]
          ],
          "color": "#00FF00"  # Green
      },
      "Zona 3": {
          "coordinates": [
              [14.0950, -87.2200],
              [14.0950, -87.1850],
              [14.0600, -87.1850],
              [14.0600, -87.2200]
          ],
          "color": "#FF0000"  # Red
      },
      "Zona 4": {
          "coordinates": [
              [14.0950, -87.1850],
              [14.0950, -87.1400],
              [14.0600, -87.1400],
              [14.0600, -87.1850]
          ],
          "color": "#FFFF00"  # Yellow
      },
      "Zona 2": {
          "coordinates": [
              [14.0950, -87.2800],
              [14.0950, -87.2200],
              [14.0600, -87.2200],
              [14.0600, -87.2800]
          ],
          "color": "#FF00FF"  # Magenta
      },
      "Zona 1": {
          "coordinates": [
              [14.0600, -87.2800],  # Extended left boundary
              [14.0600, -87.1600],  # Extended right boundary
              [14.0300, -87.1600],  # Bottom right
              [14.0300, -87.2800]   # Bottom left
          ],
          "color": "#0000FF"  # Blue
      },
      "Zona 6": {
          "coordinates": [
         [14.1100, -87.1450],  # Santa Lucía
         [14.1100, -87.0650],
         [14.1400, -87.0650],
         [14.1400, -87.1450]
     ],
          "color": "#FFA500"  # Orange
      },
      "Zona 7": {
          "coordinates": [
         [14.1350, -87.0650],  # Valle de Ángeles
         [14.1350, -87.0299],
         [14.1800, -87.0299],
         [14.1800, -87.0650]
     ],
          "color": "#800080"  # Purple
      }
  }
  
  # Add polygons for each zone
  for zone_name, zone_data in zones.items():
      folium.Polygon(
          locations=zone_data["coordinates"],
          color=zone_data["color"],
          fill=True,
          fill_color=zone_data["color"],
          fill_opacity=0.4,
          popup=zone_name
      ).add_to(m)
  
  # Add legend to the map
  legend_html = '''
  <div style="position: fixed; bottom: 50px; left: 50px; width: 120px; height: 160px; 
  border:2px solid grey; z-index:9999; font-size:14px; background-color:white;
  ">&nbsp;<b>Leyenda:</b><br>
  {% for zone, color in zones.items() %} 
  &nbsp;<i class="fa fa-map-marker" style="color:{{ color }}"></i>&nbsp;{{ zone }}<br>
  {% endfor %}
  </div>
  '''
  legend_template = Template(legend_html)
  macro = MacroElement()
  macro._template = legend_template
  m.get_root().add_child(macro)
  
  # Display the map
  folium_static(m)

  # Add message about Pasto Verde Boxes
  st.markdown("### 📦 Pasto Verde Boxes")
  st.markdown("Todos nuestros **Pasto Verde Boxes** vienen listos para usar tan pronto como los recibes. "
              "Todos los pedidos vienen en cajas de cartón reciclable que puedes simplemente reciclar "
              "cuando llegue el nuevo reemplazo. ♻️🐾📦")

  # Add the "BUY NOW" button
  if st.button("BUY NOW"):
      st.session_state.current_page = "🛒  Ordene Ahora"  # Change to the order page
      # No need for rerun or flags, just let the main loop handle it

# In your main function, ensure you handle the page rendering correctly
def main():
  st.title("Pasto Verde - Entrega de pasto para mascotas")
  user = auth0_authentication()  # Get the user from authentication

  if user:
      # Display a personalized welcome message
      st.write(f"Hola {user.name}, bienvenido a Pasto Verde! 🌿")  # Personalized greeting

      if 'current_page' not in st.session_state:
          st.session_state.current_page = "🏠 Inicio"  # Default page
      
      menu_items = {
          "🏠 Inicio": home_page,
          "🛒  Ordene Ahora": place_order,
          "📦 Mis Órdenes": display_user_orders,
          "🗺️ Zona De Envios": display_map,
          "ℹ️ Sobre Nosotros": about_us,
          "📖 Manual de Usuario": user_manual  # New menu item
      }
      
      if user.type == UserType.admin:
          menu_items["📊 Admin Dashboard"] = admin_dashboard  # Ensure this function is defined
      
      cols = st.columns(len(menu_items))
      for i, (emoji_label, func) in enumerate(menu_items.items()):
          if cols[i].button(emoji_label):
              st.session_state.current_page = emoji_label
      
      # Debugging line
      st.write(f"Current page: {st.session_state.current_page}")  
      
      try:
          menu_items[st.session_state.current_page]()
      except KeyError:
          st.session_state.current_page = "🏠 Inicio"  # Fallback to default page
          menu_items[st.session_state.current_page]()
      
      if st.sidebar.button("🚪 Finalizar la sesión"):
          for key in list(st.session_state.keys()):
              del st.session_state[key]
          st.success("Logged out successfully.")
          st.rerun()
  else:
      st.write("Por favor inicie sesión para acceder a los servicios de Pasto Verde")
      
      # Move the image to the bottom of the sidebar
      st.sidebar.markdown("---")
      image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
      st.sidebar.image(image_url, use_column_width=True, caption="La Naturaleza A Los Pies De Tus Mascota")
