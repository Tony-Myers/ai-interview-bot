import streamlit as st
from openai import OpenAI
import pandas as pd
import base64

# List of interview questions
interview_questions = [
    "Can you briefly introduce yourself, your role in higher education and interest in AI?",
    "How do you see AI transforming the traditional classroom experience?",
    "In what ways do you think AI can enhance the learning experience for students?",
    "What ethical considerations should be taken into account when implementing AI in education?",
    "Do you believe AI has the potential to transform higher education?"
]

def generate_response(prompt, response_type="feedback", conversation_history=None):
    try:
        if conversation_history is None:
            conversation_history = []

        system_content = "You are an experienced and considerate interviewer in higher education, focusing on AI applications. Use British English in your responses, including spellings like 'democratised'. Ensure your responses are complete and not truncated. Be aware of the full list of interview questions to avoid duplicating topics in follow-up questions."
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "system", "content": f"Full list of interview questions: {interview_questions}"},
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
    if "consent_given" not in st.session_state:
        st.session_state.consent_given = False

    # Consent form
    if not st.session_state.consent_given:
        st.write("Before we begin, please read and agree to the following:")
        st.write("This interview will be conducted by an AI assistant. Your responses will be used for research purposes and may be anonymously quoted in publications. You can choose to end the interview at any time.")
        consent = st.radio("Do you agree to participate in this interview?", ("Yes", "No"))
        if consent == "Yes":
            st.session_state.consent_given = True
        elif consent == "No":
            st.write("Thank you for your time. The interview will not proceed without your consent.")
            return

    if st.session_state.consent_given and st.session_state.question_index < len(interview_questions):
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
                st.session_state.conversation.append({"role": "user", "content": f"Q: {current_question}\nA: {user_answer}"})

                # Generate AI response
                ai_prompt = f"Based on the following conversation, provide thoughtful feedback and a follow-up question that doesn't duplicate topics from the main interview questions:\n\n{st.session_state.conversation}\n\nInterviewer response:"
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

    elif st.session_state.consent_given:
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
        st.session_state.consent_given = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
