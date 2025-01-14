import streamlit as st
from transformers import pipeline

# Initialize the Llama model pipeline
pipe = pipeline('text-generation', model="meta-llama/Llama-2-7b-hf")

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

# Function to get variant information from the user
def get_variant_info():
    chr = st.text_input("Enter chromosome", "6")
    pos = st.text_input("Enter position", "160585140")
    ref = st.text_input("Enter reference base", "T")
    alt = st.text_input("Enter alternate base", "G")
    genome = "hg38"
    return chr, pos, ref, alt, genome

# Get variant information from the user
chr, pos, ref, alt, genome = get_variant_info()

# Define the API URL and parameters
url = "https://api.genebe.net/cloud/api-public/v1/variant"
params = {
    "chr": chr,
    "pos": pos,
    "ref": ref,
    "alt": alt,
    "genome": genome
}

# Set the headers
headers = {
    "Accept": "application/json"
}

# Make the GET request and display results
if st.button("Get Variant Info"):
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
            user_input = f"Tell me about the following variant and its possible diseases: Chromosome: {chr}, Position: {pos}, Reference Base: {ref}, Alternate Base: {alt}, ACMG Classification: {acmg_classification}, Effect: {effect}, Gene Symbol: {gene_symbol}, Gene HGNC ID: {gene_hgnc_id}"
            conversation_history += f"User: {user_input}\n"
            
        else:
            st.write("No variants found in response.")
    else:
        st.write("Error:", response.status_code, response.text)

    # After the variant information, continue conversation with the assistant
    user_input = st.text_input("User: Type your question or exit:", "")
    
    if user_input.lower() == "exit":
        st.write("Goodbye!")
    else:
        conversation_history += f"User: {user_input}\n"

        # Generate the assistant's response using the Llama model
        outputs = pipe(conversation_history, max_length=512, num_return_sequences=1)

        # Extract the assistant's response
        response = outputs[0]["generated_text"][len(conversation_history):].strip()

        # Display the assistant's response
        st.write(f"Assistant: {response}")

        # Add the assistant's response to the conversation history
        conversation_history += f"Assistant: {response}\n"
