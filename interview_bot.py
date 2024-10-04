import streamlit as st
from openai import OpenAI

# Initialize OpenAI client with API key from Streamlit secrets
try:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
except KeyError:
    st.error("OpenAI API key not found in Streamlit secrets. Please check your configuration.")
    st.stop()

# Function to generate a response
def generate_response(prompt):
    try:
        response = client.completions.create(
            model="gtp-4",  # Using a text completion model
            prompt=f"You are an experienced and considerate interviewer in higher education, focusing on AI applications. Provide a thoughtful follow-up question or comment based on the interviewee's response: {prompt}",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"An error occurred while generating the response: {str(e)}")
        return None

# List of interview questions
interview_questions = [
    "Can you briefly introduce yourself and your role in higher education?",
    "How familiar are you with AI technologies and their applications in education?",
    "Do you believe AI has the potential to transform higher education? If so, how?",
    "In what ways do you think AI can enhance the learning experience for students?",
    "What ethical considerations should be taken into account when implementing AI in education?",
    "How do you envision the role of educators evolving with the integration of AI in higher education?",
    "Can you share any specific examples or case studies of successful AI implementation in your institution or others you're familiar with?",
    "What challenges do you foresee in adopting AI technologies in higher education, and how might these be addressed?",
    "How do you think AI can be used to personalize learning experiences for students?",
    "What skills do you think educators and students need to develop to effectively work alongside AI in education?"
]

# Streamlit app
st.title("AI Interviewer for Higher Education")

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'ai_prompt' not in st.session_state:
    st.session_state.ai_prompt = interview_questions[0]

# Display current AI prompt
st.write(st.session_state.ai_prompt)

# Get user input
user_response = st.text_area("Your response:", key=f"response_{st.session_state.current_question}")

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

# Main execution
if __name__ == "__main__":
    print("Streamlit app is ready to run. Use 'streamlit run <filename>.py' to start the app.")