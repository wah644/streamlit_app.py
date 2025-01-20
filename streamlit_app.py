import streamlit as st
import requests
from groq import Groq

# Initialize Groq API client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
st.title("DxVar")

# Define the initial system message and the user's first message
messages = [
    {
        "role": "system",
        "content": (
            "You are a clinician assistant chatbot who helps identify Mendelian diseases linked with genetic variants. "
            "If a variant is entered (ie.chr6:160585140-T>G or other format), then reply with format n = number of variants entered and chromosome: position: reference base: alternate base: genome: for each in that exact order and format. "
            "If genome is not specified, write hg38 by default."
        ),
    },
]

# Function to interact with Groq API for assistant responses
def get_assistant_response(user_input):
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

    return completion.choices[0].message.content

# Infinite chatbot loop
conversation_history = ""
while True:
    # User input
    user_input = st.text_input(
        "User: Type your variant or question:", key="user_input"
    )
    
    if user_input:
        # Add user's input to the conversation history
        conversation_history += f"User: {user_input}\n"
        
        # Check for variants in input
        n_variants = user_input.count(">")  # Simple logic to estimate variants in input
        if n_variants > 0:
            st.write(f"Detected {n_variants} variant(s).")

            # Call ACMG API for each variant (simplified example)
            variant_info = user_input.split()
            for variant in variant_info:
                try:
                    chr, pos, ref_alt = variant.split(":")
                    ref, alt = ref_alt.split(">")
                    genome = "hg38"  # Default genome if not specified

                    url = "https://api.genebe.net/cloud/api-public/v1/variant"
                    params = {"chr": chr, "pos": pos, "ref": ref, "alt": alt, "genome": genome}
                    headers = {"Accept": "application/json"}

                    response = requests.get(url, headers=headers, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        st.write("Variant Data:", data)
                    else:
                        st.write("Error retrieving variant info:", response.text)
                except ValueError:
                    st.write(f"Invalid format for variant: {variant}")
        
        # Get assistant response
        assistant_response = get_assistant_response(user_input)
        st.write(f"Assistant: {assistant_response}")

        # Add the assistant's response to the conversation history
        conversation_history += f"Assistant: {assistant_response}\n"
