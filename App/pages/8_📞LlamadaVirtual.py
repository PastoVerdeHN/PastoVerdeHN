import streamlit as st

def show_under_construction_banner():
    st.warning(
        "🚧 This page is under construction. Some features may not work as expected. 🚧",
        icon="🏗️"
    )

# Use this at the top of your Streamlit app
show_under_construction_banner()

# Your existing app code goes here
st.title("Llamada Virtual Atencion Al Cliente")
# ... rest of your app ...



import streamlit as st
from sqlalchemy.orm import sessionmaker
from models import SessionLocal, Order  # Import your models
import requests
import base64

# Function to send audio to Groq for transcription
def transcribe_audio_with_groq(audio_data):
  url = "https://api.groq.com/whisper/transcribe"  # Replace with your Groq endpoint
  headers = {
      "Authorization": "Bearer YOUR_API_KEY",  # Replace with your API key
      "Content-Type": "application/json"
  }
  
  # Send audio data to Groq
  response = requests.post(url, headers=headers, json={"audio": audio_data})
  return response.json()

# Streamlit app layout
st.title("Voice-Activated Order Management System")

# Create a new order
with st.form("order_form"):
  item_name = st.text_input("Item Name")
  quantity = st.number_input("Quantity", min_value=1)
  delivery_address = st.text_input("Delivery Address")
  submitted = st.form_submit_button("Submit Order")

  if submitted:
      session = SessionLocal()
      new_order = Order(item_name=item_name, quantity=quantity, delivery_address=delivery_address)
      session.add(new_order)
      session.commit()
      st.success("Order submitted successfully!")

# Microphone input for voice commands
st.markdown("""
  <script>
      async function recordAudio() {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          const mediaRecorder = new MediaRecorder(stream);
          const audioChunks = [];

          mediaRecorder.ondataavailable = event => {
              audioChunks.push(event.data);
          };

          mediaRecorder.onstop = async () => {
              const audioBlob = new Blob(audioChunks);
              const reader = new FileReader();
              reader.onloadend = async () => {
                  const base64Audio = reader.result.split(',')[1];  // Get base64 string
                  const response = await fetch('/transcribe', {
                      method: 'POST',
                      headers: {
                          'Content-Type': 'application/json'
                      },
                      body: JSON.stringify({ audio: base64Audio })
                  });
                  const result = await response.json();
                  document.getElementById('transcription').innerText = result.text;
              };
              reader.readAsDataURL(audioBlob);
          };

          mediaRecorder.start();
          setTimeout(() => {
              mediaRecorder.stop();
          }, 5000);  // Record for 5 seconds
      }
  </script>
""", unsafe_allow_html=True)

if st.button("Record Voice Command"):
  st.markdown("<script>recordAudio();</script>", unsafe_allow_html=True)

# Display transcription result
st.markdown("<div id='transcription'></div>", unsafe_allow_html=True)

# Handle audio transcription endpoint
if st.experimental_get_query_params().get("audio"):
  audio_data = st.experimental_get_query_params()["audio"]
  transcription = transcribe_audio_with_groq(audio_data)
  st.write("Transcription:", transcription.get("text", ""))
