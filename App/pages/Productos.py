import streamlit as st

def app():
    
    st.set_page_config(
    page_title="Productos",
    page_icon="🌿",
    layout="wide"
)
    
    # Replace 'https://example.com' with your actual website URL
    website_url = "https://pastoverde.durablesites.com/productos?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="
    
    # Embed the website in an iframe
    st.components.v1.iframe(website_url, width=None, height=600, scrolling=True)

    if st.button("Inicio"):
        st.switch_page("App.py")

if __name__ == "__main__":
    app()
