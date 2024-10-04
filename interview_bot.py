import streamlit as st
from openai import OpenAI
import os
import base64

# Function to get API key (same as before)
api_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (same as before)
client = OpenAI(api_key=api_key)

# Function to generate a response
def generate_response(prompt, response_type):
    try:
        system_content = "You are an experienced and considerate interviewer in higher education, focusing on AI applications. "
        if response_type == "feedback":
            system_content += "Provide a brief, insightful feedback on the interviewee's response without asking a new question."
        elif response_type == "follow_up":
            system_content += "Provide a thoughtful follow-up question based on the interviewee's response. Do not repeat previous feedback or introduce a new topic."
        elif response_type == "next_question":
            system_content += "Provide a brief, natural transition to the next main question without repeating previous feedback."

        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
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
    "What is your particular interest in AI and its application in education?",
    "In what ways do you think AI can enhance the learning experience for students?",
    "Can you share any specific examples or case studies of successful AI implementation in your institution or others you're familiar with?",
    "What challenges do you foresee in adopting AI technologies in higher education, and how might these be addressed?",
    "What ethical considerations should be taken into account when implementing AI in education?",
    "What are your thoughts on the potential impact of AI on assessment and evaluation in higher education?",
    "Do you believe AI has the potential to transform higher education?"
]

# Initialize session state variables
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'follow_up_count' not in st.session_state:
    st.session_state.follow_up_count = 0
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'ai_prompt' not in st.session_state:
    st.session_state.ai_prompt = interview_questions[0]
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# Display current AI prompt
st.write("AI Interviewer:", st.session_state.ai_prompt)

# Get user input
user_response = st.text_area("Your response:", key=f"response_{st.session_state.current_question}_{st.session_state.follow_up_count}")

# Submit button
if st.button("Submit"):
    if user_response:
        # Add user response to conversation
        st.session_state.conversation.append({"role": "user", "content": user_response})
        
        # Generate AI feedback
        feedback = generate_response(user_response, "feedback")
        st.session_state.feedback = feedback
        st.session_state.conversation.append({"role": "assistant", "content": feedback})
        
        if st.session_state.follow_up_count < 3:
            # Generate follow-up question
            follow_up = generate_response(user_response + "\n\nPrevious feedback: " + feedback, "follow_up")
            st.session_state.ai_prompt = feedback + "\n\n" + follow_up
            st.session_state.follow_up_count += 1
        else:
            # Move to next main question
            st.session_state.current_question += 1
            st.session_state.follow_up_count = 0
            if st.session_state.current_question < len(interview_questions):
                transition = generate_response(user_response + "\n\nPrevious feedback: " + feedback, "next_question")
                next_question = interview_questions[st.session_state.current_question]
                st.session_state.ai_prompt = feedback + "\n\n" + transition + "\n\n" + next_question
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