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
            deployment_token=st.secrets["ABACUS_DEPLOYMENT_TOKEN"],
            deployment_id=st.secrets["ABACUS_DEPLOYMENT_ID"],
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
    fg = client.describe_feature_group(st.secrets["PRICING_FEATURE_GROUP_ID"])
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

    # Savings Visualization
    st.write("Savings Comparison")
    fig = px.bar(filtered_df, x='plan_name', y='savings_percentage', title='Savings Percentage by Plan')
    st.plotly_chart(fig)

    # Best Value Plan
    best_value = filtered_df.loc[filtered_df['savings_percentage'].idxmax()]
    st.write(f"Best Value Plan: {best_value['plan_name']} with {best_value['savings_percentage']:.2f}% savings")

# Main app layout
st.title("ASISTENTE DE IA - Pasto Verde")

# Sidebar for language selection
with st.sidebar:
    st.session_state.language = st.radio("Select Language / Seleccione el idioma", ["English", "Español"])

# Main chat interface
st.subheader("Chat with Pasto Verde Assistant")

# Display conversation history
for message in st.session_state.conversation_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("How can I assist you today? / ¿Cómo puedo ayudarte hoy?")

if user_input:
    # Add user message to history
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get AI response
    response = execute_pasto_verde_assistant(user_input, st.session_state.language)
    
    if response:
        # Add AI response to history
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        
        # Display AI response
        with st.chat_message("assistant"):
            st.write(response)

# Display pricing information
if st.button("Show Pricing Information"):
    pricing_data = load_pricing_data()
    display_pricing_info(pricing_data)

# Clear conversation button
if st.button("Clear Conversation"):
    st.session_state.conversation_history = []
    st.experimental_rerun()
