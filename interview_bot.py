import streamlit as st
from openai import OpenAI
import pandas as pd
import base64

# List of interview topics (instead of fixed questions)
interview_topics = [
    "Introduction, role in higher education, and interest in AI",
    "AI's impact on traditional classroom experience",
    "AI enhancing student learning experience",
    "Ethical considerations in implementing AI in education",
    "AI's potential to transform higher education"
]

def generate_response(prompt, conversation_history=None):
    try:
        if conversation_history is None:
            conversation_history = []

        system_content = """You are an experienced and considerate interviewer in higher education, focusing on AI applications. Use British English in your responses, including spellings like 'democratised'. Ensure your responses are complete and not truncated. 
        After each user response, provide brief feedback and ask a relevant follow-up question based on their answer. Tailor your questions to the user's previous responses, avoiding repetition and exploring areas they haven't covered. Be adaptive and create a natural flow of conversation."""
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "system", "content": f"Interview topics: {interview_topics}"},
            *conversation_history[-6:],  # Include the last 6 exchanges for more context
            {"role": "user", "content": prompt}
        ]

        client = OpenAI(api_key=st.secrets["openai_api_key"])
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages,
            max_tokens=250,
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
    href = f'<a href="data:file/csv;base64,{b64}" download="interview_transcript.csv">Download Interview Transcript</a>'
    return href

def main():
    st.title("AI in Education Interview Bot")

    # Initialize session state variables
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = "Can you briefly introduce yourself, your role in higher education, and your interest in AI?"

    # Display consent information and get user consent
    st.write("""
    Before we begin, please read the information sheet provided and understand that by ticking yes, 
    you will be giving your written informed consent for your responses to be used for research purposes 
    and may be anonymously quoted in publications. 

    You can choose to end the interview at any time and request your data be removed by emailing tony.myers@staff.ac.uk. 
    This interview will be conducted by an AI assistant who, along with asking set questions, 
    will ask additional probing questions depending on your response.
    """)

    consent = st.radio("Do you consent to participate in this interview?", ("No", "Yes"))
    
    if consent == "Yes":
        st.session_state.consent_given = True
    else:
        st.session_state.consent_given = False
        st.write("You must consent to participate in the interview.")
        return

    if st.session_state.consent_given:
        # Display the current question
        st.write(st.session_state.current_question)

        # Get user input
        user_answer = st.text_area("Your response:", key="user_input")
        
        if st.button("Submit Answer"):
            if user_answer:
                # Add user's answer to conversation history
                st.session_state.conversation.append({"role": "user", "content": user_answer})
                
                # Generate AI response
                ai_prompt = f"User's answer: {user_answer}\nProvide feedback and ask a follow-up question."
                ai_response = generate_response(ai_prompt, st.session_state.conversation)
                
                # Add AI's response to conversation history
                st.session_state.conversation.append({"role": "assistant", "content": ai_response})
                
                # Update current question with AI's follow-up
                st.session_state.current_question = ai_response
                
                # Attempt to clear the user input (this may not work due to Streamlit limitations)
                st.session_state.user_input = ""
                
                st.experimental_rerun()
            else:
                st.warning("Please provide an answer before submitting.")

        # Option to end the interview
        if st.button("End Interview"):
            st.success("Interview completed! Thank you for your insights on AI in education.")
            st.session_state.current_question = "Interview ended"

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
            st.experimental_rerun()

if __name__ == "__main__":
    main()
