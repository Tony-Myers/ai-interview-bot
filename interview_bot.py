import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Function to generate a response
def generate_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an experienced and considerate interviewer in higher education, focusing on AI applications. Provide thoughtful follow-up questions and comments based on the interviewee's responses."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# List of interview questions
interview_questions = [
    "Can you briefly introduce yourself and your role in higher education?",
    "How familiar are you with AI technologies and their applications in education?",
    "Do you believe AI has the potential to transform higher education? If so, how?",
    "In what ways do you think AI can enhance the learning experience for students?"
]

# Streamlit app
st.title("AI Interview: AI in Higher Education")

# Initialize session state for question index and conversation history
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Display current question
if st.session_state.question_index < len(interview_questions):
    current_question = interview_questions[st.session_state.question_index]
    st.write(f"Question {st.session_state.question_index + 1}: {current_question}")

    # User input
    user_answer = st.text_area("Your Answer:", height=150)

    if st.button("Submit Answer"):
        if user_answer:
            # Add user's answer to conversation history
            st.session_state.conversation.append(f"Q: {current_question}\nA: {user_answer}")

            # Generate AI response
            conversation_history = "\n\n".join(st.session_state.conversation)
            ai_prompt = f"Based on the following conversation, provide a thoughtful response and a follow-up question as an experienced interviewer:\n\n{conversation_history}\n\nInterviewer response:"
            ai_response = generate_response(ai_prompt)

            st.write("Interviewer's Response:")
            st.write(ai_response)

            # Add AI's response to conversation history
            st.session_state.conversation.append(f"Interviewer: {ai_response}")

            # Move to next question
            st.session_state.question_index += 1
        else:
            st.warning("Please provide an answer before submitting.")

    # Option to skip to the next question
    if st.button("Skip to Next Question"):
        st.session_state.question_index += 1
        st.experimental_rerun()

else:
    st.success("Interview completed! Thank you for your insights on AI in higher education.")

# Display conversation history
if st.checkbox("Show Interview Transcript"):
    st.write("Interview Transcript:")
    for entry in st.session_state.conversation:
        st.write(entry)
        st.write("---")

# Option to restart the interview
if st.button("Restart Interview"):
    st.session_state.question_index = 0
    st.session_state.conversation = []
    st.experimental_rerun()


