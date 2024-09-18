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
        fg_id = st.secrets["abacus"]["PRICING_FEATURE_GROUP_ID"]
        fg = client.describe_feature_group(fg_id)
        df = client.execute_feature_group_sql(f"SELECT * FROM {fg.table_name}")
        return df
    except Exception as e:
        st.error(f"Error loading pricing data: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Streamlit app
st.title("Pasto Verde Assistant")

# Sidebar for testing options
st.sidebar.title("Test Options")
show_pricing_data = st.sidebar.checkbox("Show Pricing Data")
show_errors = st.sidebar.checkbox("Show Errors", value=True)
show_warnings = st.sidebar.checkbox("Show Warnings", value=True)

# Language selection
user_language = st.selectbox("Select your language", ["en", "es", "fr"])  # Add more languages as needed

# Load and display pricing data if selected
if show_pricing_data:
    st.subheader("Pricing Data")
    pricing_df = load_pricing_data()
    if not pricing_df.empty:
        st.dataframe(pricing_df)
    else:
        st.warning("No pricing data available.")

# User input
user_input = st.text_input("How can I assist you today?")

if st.button("Submit Query"):
    if user_input:
        with st.spinner("Processing your request..."):
            # Translate user input to English if necessary
            if user_language != "en":
                translated_input = translate_text(user_input, "en")
            else:
                translated_input = user_input
            
            # Execute the AI assistant
            response = execute_pasto_verde_assistant(translated_input, "en")
            
            # Translate response back to user's language if necessary
            if user_language != "en":
                translated_response = translate_text(response, user_language)
            else:
                translated_response = response
            
            st.subheader("Assistant Response:")
            st.write(translated_response)
    else:
        st.warning("Please enter a query before submitting.")

# Error and warning display
if show_errors:
    st.subheader("Errors")
    error_placeholder = st.empty()
    if not error_placeholder.text:
        st.info("No errors to display.")

if show_warnings:
    st.subheader("Warnings")
    warning_placeholder = st.empty()
    if not warning_placeholder.text:
        st.info("No warnings to display.")

# Footer
st.markdown("---")
st.markdown("Pasto Verde Assistant ")
