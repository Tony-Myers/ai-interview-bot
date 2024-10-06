import streamlit as st
from openai import OpenAI
import pandas as pd
import io

# Function to generate a response
def generate_response(prompt, response_type="feedback", conversation_history=None):
    try:
        if conversation_history is None:
            conversation_history = []

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

        client = OpenAI(api_key=st.secrets["openai_api_key"])
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=120,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred in generate_response: {str(e)}"

# Function to create a downloadable link for the transcript
def get_transcript_download_link(conversation):
    df = pd.DataFrame(conversation)
    csv = df.to_csv(index=False)
    csv_bytes = csv.encode()
    b64 = base64.b64encode(csv_bytes).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="interview_transcript.csv">Download Interview Transcript</a>'
    return href

# Streamlit app
def main():
    st.title("AI in Education Interview Bot")

    # Check if API key is set in secrets
    if "openai_api_key" not in st.secrets:
        st.error("OpenAI API Key is not set in Streamlit secrets. Please add it to continue.")
        st.stop()

    # Initialize session state
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "consent_given" not in st.session_state:
        st.session_state.consent_given = False
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Consent radio button
    consent = st.radio(
        "I have read the information sheet and give my written informed consent for my interview data to be used.",
        ("No", "Yes")
    )
    st.session_state.consent_given = (consent == "Yes")

    if st.session_state.consent_given:
        # Main interview questions
        questions = [
            "Can you tell me about your background and interest in AI?",
            "What do you think are the most significant challenges in AI today?",
            "How do you envision AI impacting education in the next decade?",
            "Can you discuss an AI project you've worked on or find particularly interesting?",
            "What ethical considerations do you think are most important in AI development?",
        ]

        if st.session_state.question_index < len(questions):
            current_question = questions[st.session_state.question_index]
            
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
                    conversation_history = st.session_state.conversation
                    ai_prompt = f"Based on the following conversation, provide a thoughtful response and a follow-up question as an experienced interviewer:\
\
{conversation_history}\
\
Interviewer response:"
                    ai_response = generate_response(ai_prompt, "feedback", conversation_history)

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
            st.success("Interview completed! Thank you for your insights on AI in higher education.")

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

    else:
        st.warning("Please provide your consent to proceed with the interview.")

if __name__ == "__main__":
    main()

print("Updated Streamlit app code")
