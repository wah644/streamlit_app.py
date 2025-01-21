import streamlit as st
import requests

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

    # Variant analysis using the Groq API
    try:
        # Replace with your actual API endpoint and API key
        GROQ_API_URL = "https://api.groq.com/variant-analysis"
        API_KEY = "your_groq_api_key_here"
        
        # Make API request
        response = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"query": user_input}
        )
        response_data = response.json()

        if response.status_code == 200:
            # Extract response content
            detected_variants = response_data.get("detected_variants", [])
            assistant_response = response_data.get("message", "No detailed response provided.")
            n_variants = len(detected_variants)

            # Show results
            if n_variants > 0:
                st.write(f"Detected {n_variants} variant(s):")
                for variant in detected_variants:
                    st.write(f"- {variant}")
            else:
                st.write("No variants detected.")

        else:
            assistant_response = (
                f"Error processing your query: {response_data.get('error', 'Unknown error')}"
            )
    except Exception as e:
        assistant_response = f"An error occurred: {e}"

    # Add assistant response to conversation history
    st.session_state["conversation"].append({"role": "assistant", "content": assistant_response})

# Display conversation history
for message in st.session_state["conversation"]:
    role = message["role"].capitalize()
    content = message["content"]
    st.write(f"{role}: {content}")
