import streamlit as st
from openai import OpenAI
import os
import base64

# Function to get API key (same as before)
api_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (same as before)
client = OpenAI(api_key=api_key)

# Function to generate a response (same as before)
def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced and considerate interviewer in higher education, focusing on AI applications. Provide thoughtful follow-up questions and comments based on the interviewee's responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while generating the response: {str(e)}")
        return None

# List of interview questions (same as before)
interview_questions = [
    "Can you briefly introduce yourself and your role in higher education?",
    # ... (other questions)
]

# Initialize session state variables
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'ai_prompt' not in st.session_state:
    st.session_state.ai_prompt = interview_questions[0]

# Display current AI prompt
st.write("AI Interviewer:", st.session_state.ai_prompt)

# Get user input with a unique key
user_response = st.text_area("Your response:", key=f"response_{st.session_state.current_question}")

# Submit button
if st.button("Submit"):
    if user_response:
        # Add user response to conversation
        st.session_state.conversation.append({"role": "user", "content": user_response})
        
        # Generate AI response
        ai_response = generate_response(user_response)
        if ai_response:
            st.session_state.conversation.append({"role": "assistant", "content": ai_response})
            
            # Move to next question or use AI response as prompt
            st.session_state.current_question += 1
            if st.session_state.current_question < len(interview_questions):
                st.session_state.ai_prompt = ai_response
            else:
                st.session_state.ai_prompt = "Thank you for completing the interview! Do you have any final thoughts or questions?"
            
            st.rerun()
    else:
        st.warning("Please provide a response before submitting.")

# Display conversation history
st.write("Conversation History:")
for message in st.session_state.conversation:
    st.write(f"{message['role'].capitalize()}: {message['content']}")

# Function to create a downloadable link for the conversation
def get_conversation_download_link():
    conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.conversation])
    b64 = base64.b64encode(conversation_text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="interview_conversation.txt">Download Conversation</a>'

# Add download button for the conversation
if st.session_state.conversation:
    st.markdown(get_conversation_download_link(), unsafe_allow_html=True)

# Main execution
if __name__ == "__main__":
    print("Streamlit app is ready to run. Use 'streamlit run ai_interviewer.py' to start the app.")