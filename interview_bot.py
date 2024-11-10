import streamlit as st
import pandas as pd
import base64

# Debug output at the start to verify the app is loading
st.write("App has started loading. This is a diagnostic check.")

# List of interview topics (for demonstration)
interview_topics = [
    "Introduction, role in higher education, and interest in AI",
    "AI's impact on traditional classroom experience",
    "AI enhancing student learning experience",
    "Ethical considerations in implementing AI in education",
    "AI's potential to transform higher education"
]

def generate_response(prompt, conversation_history=None):
    """
    This function simulates generating an AI response.
    Replace with actual OpenAI API call after verifying basic app functionality.
    """
    try:
        # Here we simulate a response without an actual API call
        ai_response = "This is a placeholder response. Replace with OpenAI API call."
        return ai_response
    except Exception as e:
        st.error(f"An error occurred in generate_response: {str(e)}")
        return "An error occurred with the AI response generation."

def get_transcript_download_link(conversation):
    """
    Function to generate a download link for the interview transcript.
    """
    df = pd.DataFrame(conversation)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="interview_transcript.csv">Download Transcript</a>'
    return href

def main():
    # Debug output to confirm the main function is executing
    st.write("App is now executing the main function.")

    st.title("AI Interview Bot - Diagnostic Mode")
    st.write("If you see this, the basic app is loading correctly.")

    # Initialize session state variables
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = "Please introduce yourself and your interest in AI."

    consent = st.checkbox("I give my consent to participate in this interview.")
    
    if consent:
        st.write(st.session_state.current_question)
        user_answer = st.text_area("Your response:", key=f"user_input_{len(st.session_state.conversation)}")

        if st.button("Submit Answer"):
            if user_answer:
                # Add user's answer to conversation history
                st.session_state.conversation.append({"role": "user", "content": user_answer})
                
                # Simulate AI response without actual OpenAI API call
                ai_response = generate_response(user_answer, st.session_state.conversation)
                
                # Add AI's response to conversation history
                st.session_state.conversation.append({"role": "assistant", "content": ai_response})
                
                # Update the current question with AI's follow-up
                st.session_state.current_question = ai_response
                
                # Rerun to update UI
                st.experimental_rerun()
            else:
                st.warning("Please provide an answer before submitting.")

        # Display conversation history and download link
        st.write("Interview Transcript:")
        for entry in st.session_state.conversation:
            st.write(f"{entry['role'].capitalize()}: {entry['content']}")
            st.write("---")
            
        st.markdown(get_transcript_download_link(st.session_state.conversation), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
