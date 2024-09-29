import streamlit as st

def app():
    # Configure the Streamlit page
    st.set_page_config(
        page_title="Asistente Virtual",
        page_icon="",
        layout="wide"
    )

    # Load the link from the secrets.toml file
    link = st.secrets["asistente_virtual_link"]

    # Embed the link into the Streamlit app
    st.components.v1.iframe(
        src=link,
        height=600,  # Adjust the height as needed
        scrolling=False
    )

if __name__ == "__main__":
    app()
