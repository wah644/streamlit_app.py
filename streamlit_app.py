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

# Function to parse the variant input
def parse_variant_input(variant):
    try:
        # Parse the input string in the format chr6:160585140-T>G
        chr_pos, ref_alt = variant.split(":")
        chr = chr_pos.strip("chr")
        pos = ref_alt.split("-")[0]
        ref, alt = ref_alt.split(">")[1].split("-")
        genome = "hg38"
        return chr, pos, ref, alt, genome
    except Exception as e:
        st.error("Invalid input format. Please use 'chr6:160585140-T>G'")
        return None, None, None, None, None

# Get the variant input from the user
variant_input = st.text_input("Enter variant (e.g., chr6:160585140-T>G)", "")
chr, pos, ref, alt, genome = parse_variant_input(variant_input)

# Define the API URL
url = "https://api.genebe.net/cloud/api-public/v1/variant"

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

# Make the GET request and display results
if st.button("Get Variant Info") and chr and pos and ref and alt:
    params = {
        "chr": chr,
        "pos": pos,
        "ref": ref,
        "alt": alt,
        "genome": genome
    }
    headers = {
        "Accept": "application/json"
    }

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
            
            # Add the initial variant information to the conversation history
            user_input = (
                f"Tell me about the following variant and its possible diseases: "
                f"Chromosome: {chr}, Position: {pos}, Reference Base: {ref}, Alternate Base: {alt}, "
                f"ACMG Classification: {acmg_classification}, Effect: {effect}, Gene Symbol: {gene_symbol}, "
                f"Gene HGNC ID: {gene_hgnc_id}"
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
