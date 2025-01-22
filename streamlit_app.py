import streamlit as st
import requests
from groq import Groq
parts = []

# Set page configuration
st.set_page_config(page_title="DxVar", layout="centered")

st.markdown("""
    <style>
        .justified-text {
            text-align: justify;
        }
        .results-table {
            margin-left: auto;
            margin-right: auto;
        }
    </style>
""", unsafe_allow_html=True)


st.title("DxVar")

# Initialize Groq API client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Define the initial system message
initial_messages = [
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

messages = [
    {
        "role": "system",
        "content": (
            "You are a clinician assistant chatbot specializing in genomic research and variant analysis. "
            "Your task is to interpret user-provided genetic variant data, identify possible Mendelian diseases linked to genes."
        ),
    }
]

# Function to interact with Groq API for assistant responses
def get_assistant_response_initial(user_input):
    groq_messages = [{"role": "user", "content": user_input}]
    for message in initial_messages:
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
    try:
        parts = message.split(',')
        if len(parts) == 5 and parts[1].isdigit() and parts[4] == "hg38":
            st.write("Message matches the expected format!")
            return parts
        else:
            st.write("Message does not match the format.")
            return []
    except Exception as e:
        st.write(f"Error while parsing variant: {e}")
        return []

# Main Streamlit interaction loop
user_input = st.text_input("Enter a genetic variant or a question:")

if user_input:
    # Get assistant's response
    assistant_response = get_assistant_response_initial(user_input)
    st.write(f"Assistant: {assistant_response}")
    
    # Parse the variant if present
    parts = get_variant_info(assistant_response)

    if parts:
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

        # Make API request
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            
            if "variants" in data and len(data["variants"]) > 0:
                variant = data["variants"][0]  # Get the first variant
                acmg_classification = variant.get("acmg_classification", "Not Available")
                effect = variant.get("effect", "Not Available")
                gene_symbol = variant.get("gene_symbol", "Not Available")
                gene_hgnc_id = variant.get("gene_hgnc_id", "Not Available")

                # Display results in a table
                st.write("### ACMG Results")
                data = {
                        "Attribute": ["ACMG Classification", "Effect", "Gene Symbol", "Gene HGNC ID"],
                "GeneBe Results": [acmg_classification, effect, gene_symbol, gene_hgnc_id],
                }
                st.table(data)

            else:
                st.write("No variants found in the API response.")
        else:
            st.write("API Error:", response.status_code, response.text)
    else:
        st.write("Unable to parse the variant information. Please check your input.")

    # Non-variant input, handle as general question
    user_input = f"Tell me about the following genetic variant and its possible mendelian diseases: ACMG Classification: {acmg_classification}, Effect: {effect}, Gene Symbol: {gene_symbol}, Gene HGNC ID: {gene_hgnc_id}"
    assistant_response = get_assistant_response(user_input)
    st.markdown(
    f"""
    <div class="justified-text">
        Assistant: {assistant_response}
    </div>
    """,
    unsafe_allow_html=True,
)


