import streamlit as st
import requests
import json

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

# Streamlit UI for variant input
st.title("DxVar: Mendelian Diseases Assistant")
st.write("I am here to help you find Mendelian diseases linked to genetic variants.")

chr = st.text_input("Enter chromosome (e.g., 1, X, Y):")
pos = st.text_input("Enter position:")
ref = st.text_input("Enter reference base:")
alt = st.text_input("Enter alternate base:")

# Function to fetch variant information
def get_variant_info(chr, pos, ref, alt):
    genome = "hg38"
    url = "https://api.genebe.net/cloud/api-public/v1/variant"
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
    return response

# Fetch variant information on button press
if st.button("Get Variant Information"):
    if chr and pos and ref and alt:
        response = get_variant_info(chr, pos, ref, alt)

        if response.status_code == 200:
            data = response.json()

            if "variants" in data and len(data["variants"]) > 0:
                variant = data["variants"][0]
                acmg_classification = variant.get("acmg_classification", "Not Available")
                effect = variant.get("effect", "Not Available")
                gene_symbol = variant.get("gene_symbol", "Not Available")
                gene_hgnc_id = variant.get("gene_hgnc_id", "Not Available")

                # Update conversation history
                user_input = f"Tell me about the following variant and its possible diseases: Chromosome: {chr}, Position: {pos}, Reference Base: {ref}, Alternate Base: {alt}, ACMG Classification: {acmg_classification}, Effect: {effect}, Gene Symbol: {gene_symbol}, Gene HGNC ID: {gene_hgnc_id}"
                conversation_history += f"User: {user_input}\n"

                # Display the results in Streamlit
                st.subheader("Variant Information")
                st.write(f"ACMG Classification: {acmg_classification}")
                st.write(f"Effect: {effect}")
                st.write(f"Gene Symbol: {gene_symbol}")
                st.write(f"Gene HGNC ID: {gene_hgnc_id}")
                
                # Handle assistant responses
                assistant_response = f"The variant you entered has the following information. Possible diseases can be linked to this variant based on clinical knowledge. You can proceed with further analysis using relevant resources."
                conversation_history += f"Assistant: {assistant_response}\n"
                st.write(assistant_response)

            else:
                st.write("No variants found for the provided information.")
        else:
            st.write(f"Error fetching data: {response.status_code}")
    else:
        st.write("Please fill in all fields.")
    
# Ongoing conversation for user interaction
user_message = st.text_area("Ask a question about this variant:")
if user_message:
    conversation_history += f"User: {user_message}\n"

    # Simulate assistant's response (this part can be replaced with model calls or other systems)
    assistant_response = "The variant you provided might have some potential links to certain diseases. Further clinical interpretation is necessary."

    conversation_history += f"Assistant: {assistant_response}\n"
    st.write(assistant_response)
