import streamlit as st
from openai import OpenAI
import base64
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import pygame

# Function to get API key
api_key = st.secrets.get("openai_api_key")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Function to generate a response (same as before)
def generate_response(prompt, response_type, conversation_history):
    # ... (keep the existing function as is)

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en-gb')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

# Function to play audio
def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

# Function to transcribe speech
def transcribe_speech():
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        st.write("Processing...")
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            st.error("Sorry, there was an error processing your speech.")
            return None

# Streamlit app
st.title("AI Interviewer with Speech Interaction")

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'follow_up_count' not in st.session_state:
    st.session_state.follow_up_count = 0
if 'ai_prompt' not in st.session_state:
    st.session_state.ai_prompt = interview_questions[0]

# Display current AI prompt
st.write("AI: " + st.session_state.ai_prompt)

# Text-to-speech for AI prompt
if st.button("Listen to the question"):
    audio_file = text_to_speech(st.session_state.ai_prompt)
    play_audio(audio_file)
    os.unlink(audio_file)

# Speech-to-text for user response
if st.button("Speak your answer"):
    user_response = transcribe_speech()
    if user_response:
        st.write("You said: " + user_response)
        
        # Add user response to conversation
        st.session_state.conversation.append({"role": "user", "content": user_response})
        
        # Generate AI response
        is_follow_up = st.session_state.follow_up_count < 2
        ai_response = generate_response(user_response, "follow_up" if is_follow_up else "next_question", st.session_state.conversation)
        
        if ai_response:
            st.session_state.conversation.append({"role": "assistant", "content": ai_response})
            
            if is_follow_up:
                st.session_state.follow_up_count += 1
                st.session_state.ai_prompt = ai_response
            else:
                st.session_state.current_question += 1
                st.session_state.follow_up_count = 0
                if st.session_state.current_question < len(interview_questions):
                    transition = generate_response(user_response, "next_question", st.session_state.conversation)
                    st.session_state.ai_prompt = f"{transition} {interview_questions[st.session_state.current_question]}"
                else:
                    st.session_state.ai_prompt = "Thank you for completing the interview! Do you have any final thoughts or questions?"
            
            st.experimental_rerun()

# Display conversation history
st.write("Conversation History:")
for message in st.session_state.conversation:
    st.write(f"{message['role'].capitalize()}: {message['content']}")

# Function to create a downloadable link for the conversation (same as before)
def get_conversation_download_link():
    # ... (keep the existing function as is)

# Add download button for the conversation
if st.session_state.conversation:
    st.markdown(get_conversation_download_link(), unsafe_allow_html=True)

# Main execution
if __name__ == "__main__":
    print("Streamlit app is ready to run. Use 'streamlit run ai_interviewer.py' to start the app.")