import streamlit as st
import requests
from groq import Groq

# Initialize Groq API client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
st.title("DxVar")

# Define the initial system message
system_message = {
    "role": "system",
    "content": (
        "You are a clinician assistant chatbot who helps identify Mendelian diseases linked with genetic variants. "
        "If a variant is entered (e.g., chr6:160585140-T>G or other format), then reply with the format: "
        "n = number of variants entered, followed by chromosome: position: reference base: alternate base: genome: "
        "for each variant in that exact order. If the genome is not specified, use hg38 by default."
    ),
}

# Initialize the conversation history
messages = [system_message]
conversation_history = f"System: {system_message['content']}\n"

# ACMG API URL
api_url = "https://api.genebe.net/cloud/api-public/v1/variant"

# Function to interact with Groq API
def get_assistant_response(user_input):
    groq_messages = messages + [{"role": "user", "content": user_input}]
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

# Function to query ACMG API for a variant
def query_acmg_api(chr, pos, ref, alt, genome="hg38"):
    params = {"chr": chr, "pos": pos, "ref": ref, "alt": alt, "genome": genome}
    headers = {"Accept": "application/json"}
    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

# Infinite chat loop
while True:
    # Get user input
    user_input = st.text_input("User: Type your variant or question:", "")
    if not user_input:
        continue
    
    # Add user input to conversation history
    messages.append({"role": "user", "content": user_input})
    conversation_history += f"User: {user_input}\n"

    # Check if the user input includes a variant or 'n'
    if "n" in user_input.lower():
        try:
            # Extract variants information and call ACMG API
            parts = user_input.split("-")
            chr = parts[0].split(":")[0]
            pos = parts[0].split(":")[1]
            ref, alt = parts[1].split(">")
            genome = "hg38" if "hg38" not in user_input else user_input.split("genome:")[1].strip()
            
            # Query the ACMG API
            acmg_data = query_acmg_api(chr, pos, ref, alt, genome)
            if "error" not in acmg_data:
                variants = acmg_data.get("variants", [])
                if variants:
                    for i, variant in enumerate(variants, start=1):
                        acmg_classification = variant.get("acmg_classification", "Not Available")
                        effect = variant.get("effect", "Not Available")
                        gene_symbol = variant.get("gene_symbol", "Not Available")
                        st.write(
                            f"Variant {i}:\n"
                            f"- ACMG Classification: {acmg_classification}\n"
                            f"- Effect: {effect}\n"
                            f"- Gene Symbol: {gene_symbol}"
                        )
                else:
                    st.write("No variants found.")
            else:
                st.write(f"Error querying ACMG API: {acmg_data['error']}")
        except Exception as e:
            st.write("Error processing the variant input:", str(e))
    else:
        # Get and display assistant's response
        assistant_response = get_assistant_response(user_input)
        st.write(f"Assistant: {assistant_response}")
        messages.append({"role": "assistant", "content": assistant_response})
        conversation_history += f"Assistant: {assistant_response}\n"
