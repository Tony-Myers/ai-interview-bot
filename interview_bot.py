import streamlit as st
from openai import OpenAI

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

    # Consent radio button
    consent = st.radio(
        "I have read the information sheet and give my written informed consent for my interview data to be used.",
        ("No", "Yes")
    )
    st.session_state.consent_given = (consent == "Yes")

    if st.session_state.consent_given:
        # Main interview questions
        questions = [
            "What do you think are the main benefits of using AI in higher education?",
            "What potential challenges or risks do you foresee with the integration of AI in education?",
            "How do you think AI might change the role of educators in the future?",
            "What ethical considerations should be taken into account when implementing AI in education?",
            "How might AI impact the assessment and evaluation of students' work?",
        ]

        if st.session_state.question_index < len(questions):
            current_question = questions[st.session_state.question_index]
            st.write(f"Question {st.session_state.question_index + 1}: {current_question}")

            # User input
            user_answer = st.text_area("Your Answer:", height=150)

            if st.button("Submit Answer"):
                if user_answer:
                    # Add user's answer to conversation history
                    st.session_state.conversation.append({"role": "user", "content": f"Q: {current_question}\nA: {user_answer}"})

                    # Generate AI response
                    conversation_history = st.session_state.conversation
                    ai_prompt = f"Based on the following conversation, provide a thoughtful response and a follow-up question as an experienced interviewer:\n\n{conversation_history}\n\nInterviewer response:"
                    ai_response = generate_response(ai_prompt, "feedback", conversation_history)

                    st.write("Interviewer's Response:")
                    st.write(ai_response)

                    # Add AI's response to conversation history
                    st.session_state.conversation.append({"role": "assistant", "content": ai_response})

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
                st.write(f"{entry['role'].capitalize()}: {entry['content']}")
                st.write("---")

        # Option to restart the interview
        if st.button("Restart Interview"):
            st.session_state.question_index = 0
            st.session_state.conversation = []
            st.experimental_rerun()

    else:
        st.warning("Please provide your consent to proceed with the interview.")

if __name__ == "__main__":
    main()
