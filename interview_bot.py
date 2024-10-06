def generate_response(prompt, response_type="feedback", conversation_history=None):
    try:
        if conversation_history is None:
            conversation_history = []

        system_content = """You are an experienced and considerate interviewer in higher education, focusing on AI applications. Use British English in your responses, including spellings like 'democratised'. Ensure your responses are complete and not truncated. 
        After each user response, provide brief feedback and ask a relevant follow-up probing question based on their answer. Avoid duplicating topics from the main interview questions."""
        
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
            max_tokens=200,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred in generate_response: {str(e)}"

# In the main function, update the interview loop:

if st.session_state.consent_given:
    if st.session_state.question_index < len(interview_questions):
        st.subheader(f"Question {st.session_state.question_index + 1}")
        st.write(interview_questions[st.session_state.question_index])
        
        user_answer = st.text_area("Your response:", key=f"user_input_{st.session_state.question_index}")
        
        if st.button("Submit Answer"):
            if user_answer:
                # Add user's answer to conversation history
                st.session_state.conversation.append({"role": "user", "content": f"Q: {interview_questions[st.session_state.question_index]}\nA: {user_answer}"})

                # Generate AI response with feedback and follow-up question
                ai_prompt = f"The user responded to the question '{interview_questions[st.session_state.question_index]}' with: '{user_answer}'. Provide brief feedback on their response and ask a relevant follow-up probing question."
                ai_response = generate_response(ai_prompt, "feedback", st.session_state.conversation)

                # Display AI feedback and follow-up question
                st.write("AI Interviewer:")
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
