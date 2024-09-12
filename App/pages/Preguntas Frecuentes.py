import streamlit as st

def app():
    st.title("Preguntas Frecuentes")
    
    # Replace 'https://example.com' with your actual website URL
    website_url = "https://pastoverde.durablesites.com/faq?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="
    
    # Embed the website in an iframe
    st.components.v1.iframe(website_url, width=None, height=600, scrolling=True)

    if st.button("Inicio"):
        st.switch_page("App.py")

if __name__ == "__main__":
    app()
