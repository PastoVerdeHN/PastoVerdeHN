import streamlit as st


def home_page():
       st.write(f"Bienvenido/a Pasto Verde, {st.session_state.user.name}! 🌿")
       st.write("¡Llevando pasto fresco a tus mascotas, una caja a la vez!")
       
       st.subheader("Conozca Pasto Verde")
       
       video_url = "https://github.com/PastoVerdeHN/PastoVerdeHN/raw/main/PASTO%20VERDE%20AD%20FINAL.mp4"
       st.video(video_url)
