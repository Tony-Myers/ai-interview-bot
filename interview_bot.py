import streamlit as st
from openai import OpenAI
import pandas as pd
import base64

# List of interview questions
interview_questions = [
    "Can you tell me about your background and interest in AI?",
    "What do you think are the most significant challenges in AI today?",
    "How do you envision AI impacting education in the next decade?",
    "Can you discuss an AI project you've worked on or find particularly interesting?",
    "What ethical considerations do you think are most important in AI development?"
]

def generate_response(prompt, response_type="feedback", conversation_history=None):
    try:
        if conversation_history is None:
            conversation_history = []

        system_content = "You are an experienced and considerate interviewer in AI and education. Provide thoughtful feedback and follow-up questions based on the interviewee's responses."
        
        messages = [
            {"role": "system", "content": system_content},
            *conversation_history[-4:],  # Include the last 4 exchanges for context
            {"role": "user", "content": prompt}
        ]

        client = OpenAI(api_key=st.secrets["openai_api_key"])
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred in generate_response: {str(e)}"

def get_transcript_download_link(conversation):
    df = pd.DataFrame(conversation)
    csv = df.to_csv(index=False)
    csv_bytes = csv.encode()
    b64 = base64.b64encode(csv_bytes).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="interview_transcript.csv">Download Interview Transcript</a>'

def main():
    st.title("AI in Education Interview Bot")

    if "openai_api_key" not in st.secrets:
        st.error("OpenAI API Key is not set in Streamlit secrets. Please add it to continue.")
        st.stop()

    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    if st.session_state.question_index < len(interview_questions):
        current_question = interview_questions[st.session_state.question_index]
        
        # Display AI feedback above the user input box
        if st.session_state.conversation and st.session_state.conversation[-1]["role"] == "assistant":
            st.write("Interviewer's Feedback:")
            st.write(st.session_state.conversation[-1]["content"])
            st.write("---")
        
        st.write(f"Question {st.session_state.question_index + 1}: {current_question}")

        # User input
        user_answer = st.text_area("Your Answer:", value=st.session_state.user_input, height=150, key="user_input")

        if st.button("Submit Answer"):
            if user_answer:
                # Add user's answer to conversation history
                st.session_state.conversation.append({"role": "user", "content": f"Q: {current_question}\
A: {user_answer}"})

                # Generate AI response
                ai_prompt = f"Based on the following conversation, provide thoughtful feedback and a follow-up question:\
\
{st.session_state.conversation}\
\
Interviewer response:"
                ai_response = generate_response(ai_prompt, "feedback", st.session_state.conversation)

                # Add AI's response to conversation history
                st.session_state.conversation.append({"role": "assistant", "content": ai_response})

                # Move to next question and clear user input
                st.session_state.question_index += 1
                st.session_state.user_input = ""
                st.experimental_rerun()
            else:
                st.warning("Please provide an answer before submitting.")

        # Option to skip to the next question
        if st.button("Skip to Next Question"):
            st.session_state.question_index += 1
            st.session_state.user_input = ""
            st.experimental_rerun()

    else:
        st.success("Interview completed! Thank you for your insights on AI in education.")

    # Display conversation history and download link
    if st.checkbox("Show Interview Transcript"):
        st.write("Interview Transcript:")
        for entry in st.session_state.conversation:
            st.write(f"{entry['role'].capitalize()}: {entry['content']}")
            st.write("---")
        
        st.markdown(get_transcript_download_link(st.session_state.conversation), unsafe_allow_html=True)

    # Option to restart the interview
    if st.button("Restart Interview"):
        st.session_state.question_index = 0
        st.session_state.conversation = []
        st.session_state.user_input = ""
        st.experimental_rerun()

if __name__ == "__main__":
    main()

print("Updated app.py with original structure and new interview questions")
