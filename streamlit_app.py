import streamlit as st
from openai import OpenAI

# Set up Streamlit page layout
st.set_page_config(page_title="GPT-powered Chatbot", layout="wide")

# Sidebar setup for configuration and session management
st.sidebar.title("Chatbot Settings")
st.sidebar.subheader("API Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.secrets["openai_api_key"])

model_options = ["gpt-3.5-turbo", "gpt-4", "davinci-codex", "text-davinci-003"]
selected_model = st.sidebar.selectbox("Choose your model", model_options)

st.sidebar.subheader("Session Management")
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'current_session' not in st.session_state:
    st.session_state.current_session = None

# Create a new session
new_session_name = st.sidebar.text_input("Create new session")
if st.sidebar.button("Create"):
    if new_session_name:
        st.session_state.sessions[new_session_name] = []
        st.session_state.current_session = new_session_name

# Session selector
session_names = list(st.session_state.sessions.keys())
if session_names:
    st.session_state.current_session = st.sidebar.selectbox("Select a session", options=session_names, index=session_names.index(st.session_state.current_session))

# Clear current session's chat history
if st.sidebar.button('Clear Current Chat History'):
    if st.session_state.current_session:
        st.session_state.sessions[st.session_state.current_session] = []

st.title("💬 Chatbot")

if not api_key:
    st.sidebar.error("Please add your OpenAI API key in the secrets to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=api_key)

    # Display and interact within the selected session
    if st.session_state.current_session:
        messages = st.session_state.sessions[st.session_state.current_session]
        
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What is up?"):
            messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the selected model and OpenAI API
            stream = client.chat.completions.create(
                model=selected_model,
                messages=messages,
                stream=True,
            )

            # Stream and store the response
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            messages.append({"role": "assistant", "content": response})
            st.session_state.sessions[st.session_state.current_session] = messages
