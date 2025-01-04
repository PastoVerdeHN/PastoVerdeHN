import streamlit as st
import streamlit.components.v1 as components

# Streamlit app layout
st.title("Llamada Virtual - Atención al Cliente")

# Inform users in Spanish about the virtual call
st.markdown("""
    **¡Bienvenido a nuestro Asistente de Llamada Virtual!**  
    Puedes usar el chat a continuación para interactuar con nuestro representante de atención al cliente.  
    No dudes en hacer cualquier pregunta relacionada con nuestros servicios.
""")

# Embedding Eleven Labs Virtual Call widget using st.components.v1.html
components.html("""
    <elevenlabs-convai agent-id="m5tRR9UgIevQCBy90gvh"></elevenlabs-convai>
    <script src="https://elevenlabs.io/convai-widget/index.js" async type="text/javascript"></script>
""", height=600)
