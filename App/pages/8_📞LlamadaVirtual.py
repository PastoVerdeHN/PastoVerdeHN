import streamlit as st
import streamlit.components.v1 as components

# Streamlit app layout
st.title("Llamada Virtual - Atención al Cliente")

# Inform users in Spanish about the virtual call
st.markdown("""
    **¡Bienvenido a nuestro Asistente de Llamada Virtual!**  
    Puedes usar el chat a continuación para interactuar con nuestro representante de atención al cliente.  
    No dudes en hacer cualquier pregunta relacionada con nuestros servicios.
""", unsafe_allow_html=True)

# Embed the Eleven Labs Virtual Call widget with JavaScript to position it at the top
components.html("""
    <script>
        window.onload = function() {
            setTimeout(function() {
                var widget = document.querySelector("elevenlabs-convai");
                if (widget) {
                    widget.style.position = "fixed";
                    widget.style.top = "0";
                    widget.style.left = "0";
                    widget.style.width = "100%";
                    widget.style.zIndex = "9999";
                }
            }, 500);  // Delay to ensure widget is loaded
        }
    </script>
    <elevenlabs-convai agent-id="m5tRR9UgIevQCBy90gvh"></elevenlabs-convai>
    <script src="https://elevenlabs.io/convai-widget/index.js" async type="text/javascript"></script>
""", height=600)
