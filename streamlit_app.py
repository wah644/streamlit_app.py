import streamlit as st
import requests
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Groq API client
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("Groq API key not found! Please set GROQ_API_KEY in your environment.")
    st.stop()
client = Groq(api_key=API_KEY)

# App title and description
st.set_page_config(page_title="DxVar: Mendelian Disease Identification")
st.title("DxVar - Mendelian Disease Identification")

# Hide Streamlit branding
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Define the initial system message and the assistant role
messages = [
    {
        "role": "system",
        "content": (
            "You are a clinician assistant chatbot specializing in identifying Mendelian diseases linked to genetic variants. "
            "Your responses should be concise, clear, and limited to 150 words."
        ),
    }
]

# Function to get variant information from the user
def get_variant_info():
    chr = st.text_input("Enter chromosome", "6")
    pos = st.text_input("Enter position", "160585140")
    ref = st.text_input("Enter reference base", "T")
    alt = st.text_input("Enter alternate base", "G")
    genome = "hg38"
    return chr, pos, ref, alt, genome

# Collect variant details
chr, pos, ref, alt, genome = get_variant_info()

# Define API URL and parameters for variant analysis
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

# Function to get assistant response using Groq API
def get_assistant_response(user_input):
    groq_messages = [{"role": "user", "content": user_input}]
    for message in messages:
        groq_messages.insert(0, {"role": message["role"], "content": message["content"]})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            temperature=1,
            max_completion_tokens=150,
            top_p=1,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Fetch and display variant information
if st.button("Get Variant Info"):
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if "variants" in data and len(data["variants"]) > 0:
            variant = data["variants"][0]  #
