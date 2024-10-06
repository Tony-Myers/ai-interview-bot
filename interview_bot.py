import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Function to generate a response
def generate_response(prompt, response_type, conversation_history):
    try:
        system_content = "You are an experienced and considerate interviewer in higher education, focusing on AI applications. Use British English in your responses, including spellings like 'democratised'. Ensure your responses are complete and not truncated. "
        if response_type == "feedback":
            system_content += "Provide a brief, insightful feedback on the interviewee's response without asking a new question or repeating information. Be concise and avoid pleasantries that might be redundant."
        elif response_type == "follow_up":
            system_content += "Provide a thoughtful follow-up question based on the interviewee's response. Do not repeat previous questions, information, or introduce topics from upcoming main questions. Avoid redundant pleasantries."
        elif response_type == "next_question":
            system_content += "Provide a brief, natural transition to the next main question, considering the context of previous questions and responses. Avoid repeating information or using redundant pleasantries."

        messages = [
            {"role": "system", "content": system_content},
            *conversation_history[-4:],  # Only include the last 4 exchanges for context
            {"role": "user", "content": prompt}
        ]

        # Try the newer API first
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=120,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except AttributeError:
            # If the newer API fails, fall back to the older API
            response = client.completions.create(
                model="gpt-4",
                prompt="\n".join([f"{msg['role']}: {msg['content']}" for msg in messages]),
                max_tokens=120,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].text.strip()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I apologize, but I encountered an error. Could you please rephrase your response or try again?"

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


