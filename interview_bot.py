import streamlit as st
from openai import OpenAI

import streamlit as st
from openai import OpenAI

def get_openai_api_key():
    st.write("Available secret keys:", list(st.secrets.keys()))
    
    api_key = st.secrets.get("openai_api_key", None)
    if api_key is None:
        st.error("OpenAI API key not found in Streamlit secrets.")
        st.stop()
    else:
        st.success("API key found in secrets!")
        st.write(f"API Key (first 5 chars): {api_key[:5]}...")
    return api_key

openai_api_key = get_openai_api_key()

# Rest of your code...

st.write("End of script reached.")

# You can add more Streamlit elements here if needed

st.write("End of script reached.")
# Function to get the OpenAI API key from Streamlit's secrets
def get_openai_api_key():
    api_key = st.secrets.get("openai_api_key", None)
    if api_key is None:
        st.error("OpenAI API key not found in Streamlit secrets.")
        st.stop()
    return api_key

# Get the OpenAI API key
openai_api_key = get_openai_api_key()

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize session state variables
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Define the interview questions
interview_questions = [
    "Can you briefly introduce yourself and your role in higher education?",
    "How familiar are you with AI technologies and their applications in education?",
    "Do you believe AI has the potential to transform higher education? If so, how?"
]

def generate_ai_prompt(user_input):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an insightful interviewer. Based on the following response, provide a thoughtful follow-up question."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=60,
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return ""

def submit_response():
    user_response = st.session_state.user_response
    if user_response.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_response})
        ai_prompt = generate_ai_prompt(user_response)
        if ai_prompt:
            st.session_state.chat_history.append({"role": "assistant", "content": ai_prompt})
        st.session_state.question_index += 1
        st.session_state.user_response = ""
    else:
        st.warning("Please enter a response before submitting.")

st.title("AI-Enhanced Interview")

if st.session_state.question_index < len(interview_questions):
    current_question = interview_questions[st.session_state.question_index]
    st.subheader(f"Question {st.session_state.question_index + 1}")
    st.write(current_question)
    st.text_area("Your Response", key="user_response")
    st.button("Submit Response", on_click=submit_response)
else:
    st.success("Interview completed. Thank you!")

st.subheader("Chat History")
for message in st.session_state.chat_history:
    st.write(f"**{message['role'].capitalize()}:** {message['content']}")