import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from jinja2 import Template
from folium import MacroElement
import streamlit as st

def display_map():
  st.subheader("🗺️ Zona de Entrega")
  
  # Coordinates for Tegucigalpa
  tegucigalpa_coords = [14.0818, -87.2068]
  
  # Create a map centered on Tegucigalpa
  m = folium.Map(location=tegucigalpa_coords, zoom_start=12)
  
  # Define delivery zones (adjusted to reduce overlap)
  zones = {
      "Zona 1": {
          "coordinates": [
              [14.1300, -87.2800],
              [14.1300, -87.1300],
              [14.0950, -87.1300],
              [14.0950, -87.2800]
          ],
          "color": "#00FF00"  # Green
      },
      "Zona 2": {
          "coordinates": [
              [14.0950, -87.2200],
              [14.0950, -87.1850],
              [14.0600, -87.1850],
              [14.0600, -87.2200]
          ],
          "color": "#FF0000"  # Red
      },
      "Zona 3": {
          "coordinates": [
              [14.0950, -87.1850],
              [14.0950, -87.1300],
              [14.0600, -87.1300],
              [14.0600, -87.1850]
          ],
          "color": "#FFFF00"  # Yellow
      },
      "Zona 4": {
          "coordinates": [
              [14.0950, -87.2800],
              [14.0950, -87.2200],
              [14.0600, -87.2200],
              [14.0600, -87.2800]
          ],
          "color": "#FF00FF"  # Magenta
      },
      "Zona 5": {
          "coordinates": [
              [14.0600, -87.2800],  # Extended left boundary
              [14.0600, -87.1300],  # Extended right boundary
              [14.0300, -87.1300],  # Bottom right
              [14.0300, -87.2800]   # Bottom left
          ],
          "color": "#0000FF"  # Blue
      },
      "Zona 6": {
          "coordinates": [
              [14.2000, -87.9000],
              [14.2000, -87.1500],
              [14.1700, -87.1500],
              [14.1700, -87.9000]
          ],
          "color": "#FFA500"  # Orange
      },
      "Zona 7": {
          "coordinates": [
              [14.1000, -87.3000],
              [14.1000, -87.2500],
              [14.0700, -87.2500],
              [14.0700, -87.3000]
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
