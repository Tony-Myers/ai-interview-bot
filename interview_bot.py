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

# ... (keep the generate_response and get_transcript_download_link functions as they were)

def main():
    st.title("AI in Education Interview Bot")

    # Initialize session state variables
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Display consent information and get user consent
    st.write("""
    Before we begin, please read the information sheet provided and understand that by ticking yes, 
    you will be giving your written informed consent for your responses to be used for research purposes 
    and may be anonymously quoted in publications. 
    
    You can choose to end the interview at any time and 
    request your data be removed by emailing tony.myers@staff.ac.uk. This interview will be conducted by 
    an AI assistant who, along with asking set questions, will ask additional probing questions depending on your response.
    """)

    consent = st.radio("Do you consent to participate in this interview?", ("No", "Yes"))
    
    if consent == "Yes":
        st.session_state.consent_given = True
    else:
        st.session_state.consent_given = False
        st.write("You must consent to participate in the interview. If you do not wish to participate, you may close this window.")
        return

    if st.session_state.consent_given:
        if st.session_state.question_index < len(interview_questions):
            st.subheader(f"Question {st.session_state.question_index + 1}")
            st.write(interview_questions[st.session_state.question_index])
            
            user_answer = st.text_area("Your response:", key=f"user_input_{st.session_state.question_index}")
            
            if st.button("Submit Answer"):
                if user_answer:
                    # Add user's answer to conversation history
                    st.session_state.conversation.append({"role": "user", "content": f"Q{st.session_state.question_index + 1}: {user_answer}"})
                    
                    # Generate AI response (feedback and follow-up question)
                    ai_prompt = f"Provide feedback on the following answer and ask a follow-up probing question:\n\nUser's answer: {user_answer}"
                    ai_response = generate_response(ai_prompt, "feedback", st.session_state.conversation)
                    
                    # Display AI's feedback and follow-up question
                    st.write("AI Feedback and Follow-up:")
                    st.write(ai_response)
                    
                    # Add AI's response to conversation history
                    st.session_state.conversation.append({"role": "assistant", "content": ai_response})

                    # Wait for user's response to the follow-up question
                    follow_up_answer = st.text_area("Your response to the follow-up:", key=f"follow_up_{st.session_state.question_index}")
                    
                    if st.button("Submit Follow-up Answer"):
                        if follow_up_answer:
                            # Add user's follow-up answer to conversation history
                            st.session_state.conversation.append({"role": "user", "content": f"Follow-up A: {follow_up_answer}"})
                            
                            # Move to next question
                            st.session_state.question_index += 1
                            st.rerun()
                        else:
                            st.warning("Please provide an answer to the follow-up question before submitting.")
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
