import streamlit as st
import requests
from groq import Groq
parts = []

# App title and description
st.set_page_config(page_title="DxVar", layout="centered")
st.title("DxVar")

# Initialize Groq API client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Define the initial system message
messages = [
    {
        "role": "system",
        "content": (
            "You are a clinician assistant chatbot specializing in genomic research and variant analysis. "
            "Your task is to interpret user-provided genetic variant data, identify possible Mendelian diseases linked to genes, "
            "and provide concise responses. If the user enters variants, you are to respond in a CSV format as such: "
            "chromosome,position,ref base,alt base,and if no genome is provided, assume hg38. Example: "
            "User input: chr6:160585140-T>G. You respond: 6,160585140,T,G,hg38. This response should be standalone with no extra texts. "
            "Remember bases can be multiple letters (e.g., chr6:160585140-T>GG). If the user has additional requests with the message "
            "including the variant (e.g., 'tell me about diseases linked with the variant: chr6:160585140-T>G'), "
            "ask them to enter only the variant first. They can ask follow-up questions afterward. "
            "The user can enter the variant in any format, but it should be the variant alone with no follow-up questions."
        ),
    }
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
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return completion.choices[0].message.content

# Function to parse variant information
def get_variant_info(message):
    parts = message.split(',')
    if len(parts) == 5 and parts[1].isdigit() and parts[4] == "hg38":
        print("Message matches the expected format!")
    else:
        print("Message does not match the format.")

# Main Streamlit interaction loop
conversation_history = ""
user_input = st.text_input("Enter a genetic variant or a question:")


# Parse the variant if present
assistant_response = get_assistant_response(user_input)
st.write(f"Assistant: {assistant_response}")
get_variant_info(assistant_response)

# Define the API URL and parameters
url = "https://api.genebe.net/cloud/api-public/v1/variant"
params = {
    "chr": parts[0],
    "pos": parts[1],
    "ref": parts[2],
    "alt": parts[3],
    "genome": parts[4]
}

# Set the headers
headers = {
    "Accept": "application/json"
}


response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    
    if "variants" in data and len(data["variants"]) > 0:
        variant = data["variants"][0]  # Get the first variant
        acmg_classification = variant.get("acmg_classification", "Not Available")
        effect = variant.get("effect", "Not Available")
        gene_symbol = variant.get("gene_symbol", "Not Available")
        gene_hgnc_id = variant.get("gene_hgnc_id", "Not Available")

                # Display results
        st.write("### Variant Analysis Results")
        st.write("ACMG Classification:", acmg_classification)
        st.write("Effect:", effect)
        st.write("Gene Symbol:", gene_symbol)
        st.write("Gene HGNC ID:", gene_hgnc_id)

                # Add to conversation history
        user_request = f"Chromosome: {variant_info['chr']}, Position: {variant_info['pos']}, Reference Base: {variant_info['ref']}, Alternate Base: {variant_info['alt']}, ACMG Classification: {acmg_classification}, Effect: {effect}, Gene Symbol: {gene_symbol}, Gene HGNC ID: {gene_hgnc_id}"
        conversation_history += f"User: {user_request}\n"

                # Get assistant's response
        assistant_response = get_assistant_response(user_request)
        st.write(f"Assistant: {assistant_response}")
        conversation_history += f"Assistant: {assistant_response}\n"
    else:
        st.write("No variants found in the API response.")
else:
    st.write("API Error:", response.status_code, response.text)
    
        # Non-variant input, handle as general question
assistant_response = get_assistant_response(user_input)
st.write(f"Assistant: {assistant_response}")
conversation_history += f"User: {user_input}\nAssistant: {assistant_response}\n"
