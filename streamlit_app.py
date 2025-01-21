import streamlit as st

# Title of the app
st.title("DxVar - Clinician Assistant Chatbot")

# Initialize conversation storage
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

# User input widget
user_input = st.text_input(
    "User: Type your variant or question:", 
    key="unique_user_input_key"  # Ensure unique key
)

# Process user input
if user_input:
    # Append user input to conversation history
    st.session_state["conversation"].append({"role": "user", "content": user_input})

    # Generate assistant response (placeholder logic)
    assistant_response = f"You said: {user_input}. How can I assist further?"

    # Add assistant response to conversation history
    st.session_state["conversation"].append({"role": "assistant", "content": assistant_response})

# Display conversation history
for message in st.session_state["conversation"]:
    role = message["role"].capitalize()
    content = message["content"]
    st.write(f"{role}: {content}")
