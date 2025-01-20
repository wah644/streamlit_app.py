import streamlit as st
import requests
from groq import Groq

# Initialize Groq API client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("DxVar - Mendelian Disease Identification")

# Define the initial system message and the user's first message
messages = [
    {
        "role": "system",
        "content": (
            "You are a clinician assistant chatbot who helps identify Mendelian diseases linked with genetic variants. "
            "Each response you provide should be concise and limited to a maximum of 150 words max."
        ),
    },
]

# Initialize the conversation history
conversation_history = ""
for message in messages:
    role = "System" if message["role"] == "system" else "User"
    conversation_history += f"{role}: {message['content']}\n"



    user_input = st.text_input("User: Type your question or exit:", "")
    
    if user_input.lower() == "exit":
        st.write("Goodbye!")
    else:
        conversation_history += f"User: {user_input}\n"

        # Generate the assistant's response using Groq API
        groq_messages = [{"role": "user", "content": user_input}]
        for message in messages:
            groq_messages.insert(0, {"role": message["role"], "content": message["content"]})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            temperature=1,
            max_completion_tokens=150,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Extract and display the assistant's response
        assistant_response = completion.choices[0].message.content

        st.write(f"Assistant: {assistant_response}")

        # Add the assistant's response to the conversation history
        conversation_history += f"Assistant: {assistant_response}\n"
