import streamlit as st
import os

st.title("Interview Bot Debugger")

# Display current working directory and list files
st.write("Current working directory:", os.getcwd())
st.write("Files in current directory:", os.listdir())

# Try to import OpenAI
try:
    from openai import OpenAI
    st.success("Successfully imported OpenAI")
except ImportError as e:
    st.error(f"Error importing OpenAI: {str(e)}")

# Display Streamlit version
st.write("Streamlit version:", st.__version__)

# Print all available secrets
st.write("All available secrets:")
for key in st.secrets:
    st.write(f"- {key}: {'*' * len(str(st.secrets[key]))}")

# Try to access the OpenAI API key
api_key = st.secrets.get("openai_api_key")
if api_key:
    st.success("Successfully accessed OpenAI API key from secrets")
    st.write("API key (first 5 chars):", api_key[:5])
else:
    st.error("OpenAI API key not found in secrets")

# Try to initialize OpenAI client
if api_key:
    try:
        client = OpenAI(api_key=api_key)
        models = client.models.list()
        st.success("Successfully initialized OpenAI client and listed models")
        st.write("Available models:", [model.id for model in models.data[:5]])
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")
else:
    st.error("Cannot initialize OpenAI client without API key")

st.write("Debug information complete")