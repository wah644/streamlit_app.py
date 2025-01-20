import streamlit as st
import requests

st.title("DxVar - Clinician Assistant Chatbot")

# Conversation storage
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

# User input
user_input = st.text_input(
    "User: Type your variant or question:", key="unique_user_input_key"
)

# Process user input
if user_input:
    # Append user input to conversation history
    st.session_state["conversation"].append({"role": "user", "content": user_input})

    # Variant detection (example logic)
    n_variants = user_input.count(">")  # Count the number of variants in the input
    if n_variants > 0:
        st.write(f"Detected {n_variants} variant(s).")
        # Handle variants (API or custom logic here)
    else:
        st.write("No variants detected.")

    # Simulate chatbot response
    assistant_response = f"Processing your query: {user_input}"
    st.session_state["conversation"].append(
        {"role": "assistant", "content": assistant_response}
    )

# Display conversation history
for message in st.session_state["conversation"]:
    role = message["role"].capitalize()
    content = message["content"]
    st.write(f"{role}: {content}")
