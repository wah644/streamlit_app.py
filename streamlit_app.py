import streamlit as st
import requests
from groq import Groq
import re  # For regex validation

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

# Function to parse and validate variant input
def parse_variant_input(variant_input):
    """
    Parse the variant string in the format 'chr6:160585140-T>G'
    and extract chromosome, position, reference base, and alternate base.
    """
    match = re.match(r"^chr(\d+|[XYM]):(\d+)-([ACGT])>([ACGT])$", variant_input)
    if match:
        chr, pos, ref, alt = match.groups()
        return chr, pos, ref, alt
    return None, None, None, None

# Input box for the variant string
variant_input = st.text_input("Enter the variant in the format 'chr6:160585140-T>G':", "")

# Define the API URL and parameters
url = "https://api.genebe.net/cloud/api-public/v1/variant"

# Make the GET request and display results
if st.button("Get Variant Info"):
    chr, pos, ref, alt = parse_variant_input(variant_input)
    
    if chr and pos and ref and alt:
        genome = "hg38"
        params = {
            "chr": chr,
            "pos": pos,
            "ref": ref,
            "alt": alt,
            "genome": genome,
        }
        
        headers = {
            "Accept": "application/json"
        }

        # API request
        response = requests.get(url, headers=headers, params=params)

        # Check the response status and extract relevant data
        if response.status_code == 200:
            data = response.json()

            if "variants" in data and len(data["variants"]) > 0:
                variant = data["variants"][0]  # Get the first variant
                acmg_classification = variant.get("acmg_classification", "Not Available")
                effect = variant.get("effect", "Not Available")
                gene_symbol = variant.get("gene_symbol", "Not Available")
                gene_hgnc_id = variant.get("gene_hgnc_id", "Not Available")

                # Display the results
                st.write("ACMG Classification:", acmg_classification)
                st.write("Effect:", effect)
                st.write("Gene Symbol:", gene_symbol)
                st.write("Gene HGNC ID:", gene_hgnc_id)

                # Add to conversation history
                user_input = (
                    f"Tell me about the following variant and its possible diseases: "
                    f"Chromosome: {chr}, Position: {pos}, Reference Base: {ref}, Alternate Base: {alt}, "
                    f"ACMG Classification: {acmg_classification}, Effect: {effect}, "
                    f"Gene Symbol: {gene_symbol}, Gene HGNC ID: {gene_hgnc_id}"
                )
                conversation_history += f"User: {user_input}\n"

                # Get and display the assistant's response
                assistant_response = get_assistant_response(user_input)
                st.write(f"Assistant: {assistant_response}")
                conversation_history += f"Assistant: {assistant_response}\n"
            else:
                st.write("No variants found in response.")
        else:
            st.write("Error:", response.status_code, response.text)
    else:
        st.write("Invalid input format. Please enter the variant in the format 'chr6:160585140-T>G'.")

# After the variant information, continue conversation with the assistant
user_input = st.text_input("User: Type your question or exit:", "")
if user_input:
    # Add user's input to the conversation history
    conversation_history += f"User: {user_input}\n"

    # Get and display the assistant's response
    assistant_response = get_assistant_response(user_input)
    st.write(f"Assistant: {assistant_response}")

    # Add the assistant's response to the conversation history
    conversation_history += f"Assistant: {assistant_response}\n"
