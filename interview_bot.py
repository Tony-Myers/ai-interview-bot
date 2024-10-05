import streamlit as st
from openai import OpenAI
import base64
from gtts import gTTS
import tempfile
import os
import speech_recognition as sr
import pygame

# Function to get API key
api_key = st.secrets.get("openai_api_key")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Function to generate a response
def generate_response(prompt, response_type, conversation_history):
    try:
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

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while generating the response: {str(e)}")
        return None

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
    recognizer = sr.Recognizer()
    
    # List available microphones
    print("Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}")
    
    # You can change this index if needed
    mic_index = None  # None means default microphone
    
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("Adjusting for ambient noise. Please wait...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now.")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            print("Speech captured. Transcribing...")
        
        text = recognizer.recognize_google(audio)
        print(f"Transcribed text: {text}")
        return text
    except sr.WaitTimeoutError:
        print("No speech detected within the timeout period.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return ""
    except Exception as e:
        print(f"An error occurred during speech recognition: {e}")
        return ""
    
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
    st.session_state.ai_prompt = None

# List of interview questions
interview_questions = [
    "Can you tell me about your background and interest in AI?",
    "What do you think are the most significant challenges in AI today?",
    "How do you envision AI impacting education in the next decade?",
    "Can you discuss an AI project you've worked on or find particularly interesting?",
    "What ethical considerations do you think are most important in AI development?"
]

# Main interview loop
if st.session_state.current_question < len(interview_questions):
    if st.session_state.ai_prompt is None:
        st.session_state.ai_prompt = interview_questions[st.session_state.current_question]

    st.write("AI: " + st.session_state.ai_prompt)

    # Text-to-speech button
    if st.button("Listen to the question"):
        audio_file = text_to_speech(st.session_state.ai_prompt)
        play_audio(audio_file)
        os.unlink(audio_file)

    # Speech-to-text button
    if st.button("Speak your answer"):
        user_response = transcribe_speech()
        if user_response:
            st.write("You: " + user_response)
            st.session_state.conversation.append({"role": "user", "content": user_response})

    # Text input as fallback
    user_response = st.text_input("Or type your answer here:")
    if user_response:
        st.session_state.conversation.append({"role": "user", "content": user_response})

    if st.button("Submit"):
        if st.session_state.follow_up_count < 2:
            ai_response = generate_response(user_response, "follow_up", st.session_state.conversation)
            st.session_state.follow_up_count += 1
        else:
            ai_response = generate_response(user_response, "next_question", st.session_state.conversation)
            st.session_state.current_question += 1
            st.session_state.follow_up_count = 0
            if st.session_state.current_question < len(interview_questions):
                ai_response += f"\n\nNext question: {interview_questions[st.session_state.current_question]}"
        
        st.session_state.conversation.append({"role": "assistant", "content": ai_response})
        st.session_state.ai_prompt = ai_response
        st.experimental_rerun()

else:
    ai_response = "Thank you for completing the interview! Do you have any final thoughts or questions?"

    st.session_state.conversation.append({"role": "assistant", "content": ai_response})
    st.session_state.ai_prompt = ai_response
    st.experimental_rerun()

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
    print("Streamlit app is ready to run. Use 'streamlit run interview_bot.py' to start the app.")