import streamlit as st
from abacusai import ApiClient
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="ASISTENTE DE IA", page_icon="🤖", layout="wide")

# Initialize API client
client = ApiClient()

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Function to execute AI agent
def execute_pasto_verde_assistant(user_input, language):
    try:
        result = client.execute_agent(
            deployment_token="YOUR_DEPLOYMENT_TOKEN",  # Replace with actual token
            deployment_id="YOUR_DEPLOYMENT_ID",  # Replace with actual ID
            keyword_arguments={
                "user_input": user_input,
                "language": language
            }
        )
        return result.response
    except Exception as e:
        st.error(f"Error executing AI agent: {str(e)}")
        return None

# Function to load pricing data
@st.cache_data
def load_pricing_data():
    fg = client.describe_feature_group("127e54af20")
    df = client.execute_feature_group_sql(f"SELECT * FROM {fg.table_name}")
    return df

# Function to display pricing information
def display_pricing_info(df):
    st.subheader("Pricing Information")
    
    # Filter options
    sub_type = st.selectbox("Subscription Type", df['subscription_type'].unique())
    filtered_df = df[df['subscription_type'] == sub_type]

    # Display comparison table
    st.write("Plan Comparison")
    st.dataframe(filtered_df[['plan_name', 'price', 'effective_price', 'total_discount', 'savings_percentage', 'commitment_period', 'first_month_free', 'delivery']])

    # Savings visualization
    st.write("Savings Comparison")
    fig = px.bar(filtered_df, x='plan_name', y='savings_percentage', title='Savings Percentage by Plan')
    st.plotly_chart(fig)

    # Best value plan
    best_value = filtered_df.loc[filtered_df['savings_percentage'].idxmax()]
    st.info(f"Best Value Plan: {best_value['plan_name']} with {best_value['savings_percentage']:.2f}% savings")

# Main function
def main():
    st.title("Pasto Verde AI Assistant")

    # Sidebar for language selection
    st.sidebar.title("Settings")
    st.session_state.language = st.sidebar.radio("Select Language / Seleccione el idioma", ["English", "Español"])

    # User input
    user_input = st.text_input("How can I assist you today? / ¿Cómo puedo ayudarte hoy?", key="user_input")

    # Execute AI agent when user submits input
    if st.button("Submit / Enviar"):
        if user_input:
            with st.spinner("Processing..."):
                response = execute_pasto_verde_assistant(user_input, st.session_state.language)
            
            if response:
                # Add to conversation history
                st.session_state.conversation_history.append(("User", user_input))
                st.session_state.conversation_history.append(("Assistant", response))

                # Clear input
                st.session_state.user_input = ""

    # Display conversation history
    st.subheader("Conversation History")
    for role, message in st.session_state.conversation_history:
        if role == "User":
            st.text_input("You:", message, disabled=True)
        else:
            st.text_area("Assistant:", message, height=100, disabled=True)

    # Display pricing information
    if st.checkbox("Show Pricing Information"):
        df = load_pricing_data()
        display_pricing_info(df)

if __name__ == "__main__":
    main()
