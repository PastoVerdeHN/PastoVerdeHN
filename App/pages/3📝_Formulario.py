import streamlit as st

# --- SHARED ON ALL PAGES ---
st.logo("https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/refs/heads/main/menu_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.png")

def generate_iframe_html(url, container_height, hide_top_pct, hide_bottom_pct):
    hide_pixels_top = container_height * hide_top_pct / 100
    hide_pixels_bottom = container_height * hide_bottom_pct / 100
    iframe_height = container_height + hide_pixels_top + hide_pixels_bottom

    iframe_html = f"""
    <div class="iframe-container" style="height: {iframe_height}px; overflow: hidden;">
        <iframe src="{url}" scrolling="no" style="height: {iframe_height}px; width: 100%; border: none; transform: translateY(-{hide_pixels_top}px);"></iframe>
    </div>
    """
    return iframe_html

def app():
    st.set_page_config(
        page_title="Ordena Hoy",
        page_icon="🌿",
        layout="wide"
    )

    image_url = "https://raw.githubusercontent.com/PastoVerdeHN/PastoVerdeHN/main/STREAMLIT%20PAGE%20ICON.png"
    st.sidebar.image(image_url, use_column_width=True, caption="© La Naturaleza A Los Pies De Tus Mascota")

    website_url = "https://pastoverde.durablesites.com/contact?pt=NjZjZmZiNmQzMzBjMWZmZWVjOWY4OWRhOjE3MjQ5MTgwODYuOTQ1OnByZXZpZXc="
    container_height = 600
    hide_percentage_top = 20
    hide_percentage_bottom = 7.2

    iframe_html = generate_iframe_html(
        url=website_url,
        container_height=container_height,
        hide_top_pct=hide_percentage_top,
        hide_bottom_pct=hide_percentage_bottom
    )

    st.components.v1.html(
        iframe_html,
        height=container_height,
        scrolling=False
    )

    # Add a navigation button (optional)
    if st.button("Inicio"):
        st.switch_page("App.py")  # Ensure "App.py" is the correct target page name

if __name__ == "__main__":
    app()
