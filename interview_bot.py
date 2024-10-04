import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Function to generate a response
def generate_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an experienced and considerate interviewer in higher education, focusing on AI applications. Provide thoughtful follow-up questions and comments based on the interviewee's responses."
            },
            {"role": "user", "content": prompt}
        ]
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

# Function to display the conversation transcript with proper formatting
def display_transcript(conversation):
    st.markdown("### Interview Transcript")
    for entry in conversation:
        if entry['type'] == 'question':
            st.markdown(f"**Q{entry['number']}: {entry['content']}**")
        elif entry['type'] == 'answer':
            st.markdown(f"*A*: {entry['content']}")
        elif entry['type'] == 'interviewer':
            st.markdown(f"**Interviewer**: {entry['content']}")
        st.markdown("---")  # Separator for readability

# Display current question
if st.session_state.question_index < len(interview_questions):
    current_question = interview_questions[st.session_state.question_index]
    st.markdown(f"### Question {st.session_state.question_index + 1}:")
    st.markdown(f"**{current_question}**")

    # User input
    user_answer = st.text_area("Your Answer:", height=150)

    if st.button("Submit Answer"):
        if user_answer.strip():
            # Add user's answer to conversation history
            st.session_state.conversation.append({
                'type': 'question',
                'number': st.session_state.question_index + 1,
                'content': current_question
            })
            st.session_state.conversation.append({
                'type': 'answer',
                'content': user_answer.strip()
            })

            # Generate AI response
            conversation_history = ""
            for entry in st.session_state.conversation:
                if entry['type'] == 'question':
                    conversation_history += f"Q{entry['number']}: {entry['content']}\n"
                elif entry['type'] == 'answer':
                    conversation_history += f"A: {entry['content']}\n"
                elif entry['type'] == 'interviewer':
                    conversation_history += f"Interviewer: {entry['content']}\n"

            ai_prompt = (
                f"Based on the following conversation, provide a thoughtful response and a follow-up question as an experienced interviewer:\n\n"
                f"{conversation_history}\n"
                f"Interviewer response:"
            )
            ai_response = generate_response(ai_prompt)

            st.session_state.conversation.append({
                'type': 'interviewer',
                'content': ai_response
            })

            st.success("Answer submitted and response generated!")

            # Optionally display the AI response immediately
            st.markdown("**Interviewer Response:**")
            st.write(ai_response)
            st.markdown("---")

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
    display_transcript(st.session_state.conversation)

# Option to restart the interview
if st.button("Restart Interview"):
    st.session_state.question_index = 0
    st.session_state.conversation = []
    st.experimental_rerun()
