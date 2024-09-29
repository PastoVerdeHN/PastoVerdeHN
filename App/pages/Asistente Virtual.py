import streamlit as st

def app():
    # Configure the Streamlit page
    st.set_page_config(
        page_title="Asistente Virtual",
        page_icon="🤖",
        layout="wide"
    )

    # Load and display the sidebar image
    image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
    st.sidebar.image(image_url, use_column_width=True, caption="La Naturaleza A Los Pies De Tus Mascota")

    st.title("Asistente Virtual")

        # Add a submessage about the AI nature of the assistant
    st.markdown("""
    <div style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 20px;">
    <p style="font-style: italic; color: #4a4a4a;">
    Bienvenido a nuestro Asistente Virtual impulsado por IA. Estoy aquí para responder a cualquier pregunta que tengas sobre Pasto Verde, nuestros productos, o cuidado de mascotas. No dudes en preguntar lo que quieras - ¡estoy listo para ayudarte!
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Load the link from the secrets.toml file
    try:
        link = st.secrets["asistente_virtual_link"]["link"]
    except KeyError as e:
        st.error(f"Error accessing secret: {e}")
        st.stop()

    # Embed the link into the Streamlit app
    try:
        st.components.v1.iframe(
            src=link,
            height=600,  # Adjust the height as needed
            scrolling=True
        )
    except Exception as e:
        st.error(f"Error embedding iframe: {e}")
        st.write("Attempting to display link as text:")
        st.write(link)

    # Add a navigation button
    if st.button("Inicio"):
        st.switch_page("App.py")  # Ensure "App.py" is the correct target page name

if __name__ == "__main__":
    app()
