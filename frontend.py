# frontend.py

import streamlit as st
import requests
import os

# Define the backend API URL - use environment variable for Docker compatibility
API_URL = os.getenv("API_URL", "http://localhost:8000/chat/")

st.set_page_config(page_title="Helios Dynamics - Agent-Driven ERP", layout="wide")
st.title("💡 Helios Dynamics Agent-Driven ERP")
st.caption("A modular, agent-driven platform to streamline your business operations.")

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What can I help you with?"):
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send request to the backend API and get the response
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"prompt": prompt})
            response_json = response.json()
            agent_response = response_json["response"]
            agent_name = response_json["agent_used"]
            
            full_response = f"**Agent Used:** `{agent_name}`\n\n{agent_response}"

            # Add the agent's full response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Display the agent's response
            with st.chat_message("assistant"):
                st.markdown(full_response)

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the backend: {e}")
