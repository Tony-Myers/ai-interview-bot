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
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced and considerate interviewer in higher education, focusing on AI applications. Provide thoughtful follow-up questions and comments based on the interviewee's responses."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
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

st.write("Welcome to the AI Interviewer. This application simulates an interview about AI in higher education. Please respond to each question, and the AI will provide follow-up questions based on your answers.")

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Display current question
if st.session_state.current_question < len(interview_questions):
    st.write(f"Question {st.session_state.current_question + 1}:")
    st.write(interview_questions[st.session_state.current_question])
    
    # Get user input
    user_response = st.text_area("Your response:", key=f"response_{st.session_state.current_question}")
    
    if st.button("Submit"):
        # Add user response to conversation
        st.session_state.conversation.append({"role": "user", "content": user_response})
        
        # Generate AI response
        ai_response = generate_response(user_response)
        if ai_response:
            st.session_state.conversation.append({"role": "assistant", "content": ai_response})
            
            # Move to next question
            st.session_state.current_question += 1
            st.experimental_rerun()

# Display conversation history
st.write("Conversation History:")
for message in st.session_state.conversation:
    st.write(f"{message['role'].capitalize()}: {message['content']}")

# End of interview
if st.session_state.current_question >= len(interview_questions):
    st.write("Thank you for completing the interview!")

# Main execution
if __name__ == "__main__":
    print("Streamlit app is ready to run. Use 'streamlit run <filename>.py' to start the app.")