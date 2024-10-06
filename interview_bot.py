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
        st.error("OpenAI API Key is not set in the app's secrets.")
        return

    if "consent_given" not in st.session_state:
        st.session_state.consent_given = False

    if "question_index" not in st.session_state:
        st.session_state.question_index = 0

    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display consent information
    st.write("""
    Before we begin, please read the information sheet provided and understand that by ticking yes, 
    you will be giving your written informed consent for your responses to be used for research purposes 
    and may be anonymously quoted in publications. You can choose to end the interview at any time and 
    request your data be removed by emailing tony.myers@staff.newman.ac.uk. This interview will be conducted by 
    an AI assistant who, along with asking set questions, will ask additional probing questions depending on your response.
    """)

    # Consent radio button
    consent = st.radio("Do you consent to participate in this interview?", ("No", "Yes"))
    st.session_state.consent_given = (consent == "Yes")

    if st.session_state.consent_given:
        if st.session_state.question_index < len(interview_questions):
            current_question = interview_questions[st.session_state.question_index]
            st.write(f"Question {st.session_state.question_index + 1}: {current_question}")

            # User input
            user_answer = st.text_area("Your answer:", key=f"user_input_{st.session_state.question_index}")

            if st.button("Submit Answer"):
                if user_answer.strip():
                    # Add user's answer to conversation history
                    st.session_state.conversation.append({"role": "user", "content": f"Q: {current_question}\nA: {user_answer}"})

                    # Generate AI response
                    ai_prompt = f"Based on the following conversation, provide thoughtful feedback and a follow-up question:\n\n{st.session_state.conversation}\n\nInterviewer response:"
                    ai_response = generate_response(ai_prompt, "feedback", st.session_state.conversation)

                    # Add AI's response to conversation history
                    st.session_state.conversation.append({"role": "assistant", "content": ai_response})

                    # Move to next question
                    st.session_state.question_index += 1
                    st.rerun()
                else:
                    st.warning("Please provide an answer before submitting.")

            # Option to skip to the next question
            if st.button("Skip to Next Question"):
                st.session_state.question_index += 1
                st.rerun()

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
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
