import streamlit as st
from openai import OpenAI
import os
import base64

# Function to get API key (same as before)
api_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (same as before)
client = OpenAI(api_key=api_key)

# Function to generate a response
def generate_response(prompt, response_type, conversation_history):
    try:
        system_content = "You are an experienced and considerate interviewer in higher education, focusing on AI applications. Use British English in your responses. "
        if response_type == "feedback":
            system_content += "Provide a brief, insightful feedback on the interviewee's response before asking a thoughtful follow-up question based on the interviewee's responsea. Be concise and avoid pleasantries that might be redundant."
            system_content += "Do not repeat previous questions, information, or introduce topics from upcoming main questions. Avoid redundant pleasantries."
        elif response_type == "next_question":
            system_content += "Provide a brief, natural transition to the next main question, considering the context of previous questions and responses. Avoid repeating information or using redundant pleasantries."

        messages = [
            {"role": "system", "content": system_content},
            *conversation_history[-4:],  # Only include the last 4 exchanges for context
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            max_tokens=100,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while generating the response: {str(e)}")
        return None

# List of interview questions (same as before, but in British English)
interview_questions = [
    "Could you briefly introduce yourself and your role in higher education?",
    "what is your particular interest with AI technologies and their applications in education?",
    "In what ways do you think AI can enhance the learning experience for students?",
    "What impact do you think AI will have on assessment methods in higher education?"
    "What ethical considerations should be taken into account when implementing AI in education?",
    "What challenges do you foresee in adopting AI technologies in higher education, and how might these be addressed?",
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
        feedback = generate_response(user_response, "feedback", st.session_state.conversation)
        st.session_state.conversation.append({"role": "assistant", "content": feedback})
        
        # Determine next action
        if st.session_state.follow_up_count < 2:
            # Generate follow-up question
            follow_up = generate_response(user_response, "follow_up", st.session_state.conversation)
            st.session_state.conversation.append({"role": "assistant", "content": follow_up})
            st.session_state.ai_prompt = follow_up
            st.session_state.follow_up_count += 1
        else:
            # Move to next main question
            st.session_state.current_question += 1
            st.session_state.follow_up_count = 0
            if st.session_state.current_question < len(interview_questions):
                next_question = interview_questions[st.session_state.current_question]
                transition = generate_response(next_question, "next_question", st.session_state.conversation)
                st.session_state.ai_prompt = f"{transition} {next_question}"
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