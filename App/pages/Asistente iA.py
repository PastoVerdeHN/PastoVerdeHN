import streamlit as st
from abacusai import ApiClient
import pandas as pd
import traceback
from googletrans import Translator

# Initialize the API client and translator
client = ApiClient()
translator = Translator()

def translate_text(text, target_language):
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails

def execute_pasto_verde_assistant(user_input, language):
    try:
        # Make the API call to the agent
        result = client.execute_agent(
            deployment_token=st.secrets["abacus"]["ABACUS_DEPLOYMENT_TOKEN"],
            deployment_id=st.secrets["abacus"]["ABACUS_DEPLOYMENT_ID"],
            keyword_arguments={
                "user_input": user_input,
                "language": language
            }
        )
        
        # Check if the response contains the expected fields
        if isinstance(result.response, dict) and 'response' in result.response:
            return result.response['response']
        else:
            st.warning("Unexpected response format from the AI agent.")
            return "I'm sorry, but I received an unexpected response format. Please try again."

    except Exception as e:
        st.error(f"Error executing AI agent: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return "I'm sorry, but I encountered an error while processing your request. Please try again later."

def load_pricing_data():
    try:
        fg_id = st.secrets['abacus']['PRICING_FEATURE_GROUP_ID']
        fg = client.describe_feature_group(fg_id)
        df = client.execute_feature_group_sql(f"SELECT * FROM {fg.table_name}")
        return df
    except Exception as e:
        st.error(f"Error loading pricing data: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Streamlit app
st.title("Pasto Verde Assistant - Test Page")

# Display pricing data (optional, for testing purposes)
st.subheader("Pricing Data")
pricing_df = load_pricing_data()
if not pricing_df.empty:
    st.dataframe(pricing_df)
else:
    st.warning("Unable to load pricing data.")

# Language selection
user_language = st.selectbox("Select Language / Seleccione el idioma", ["en", "es"])

# User input
user_input = st.text_input("How can I assist you today? / ¿Cómo puedo ayudarte hoy?")

if user_input:
    # Translate user input to English if necessary
    if user_language != "en":
        user_input = translate_text(user_input, "en")
    
    # Execute the AI agent
    response = execute_pasto_verde_assistant(user_input, "en")
    
    # Translate response back to user's language if necessary
    if user_language != "en":
        response = translate_text(response, user_language)
    
    st.write("Assistant:", response)

# Error and warning display (optional, for testing purposes)
if st.session_state.get('errors'):
    st.subheader("Errors")
    for error in st.session_state.errors:
        st.error(error)

if st.session_state.get('warnings'):
    st.subheader("Warnings")
    for warning in st.session_state.warnings:
        st.warning(warning)
