import streamlit as st
import os
from google import genai
from google.genai import types

# Page Title & Visual Anchor
st.set_page_config(page_title="PowerWise AI - SDG 7", page_icon="⚡", layout="centered")
st.title("⚡ PowerWise AI - SDG 7 Clean Energy Advisor")
st.caption("Silver Oak University - Next Gen Chatbot Arena")

# 1. Initialize Gemini Client safely using Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please set it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 2. Strict SDG 7 System Instructions
SYSTEM_INSTRUCTION = (
    "You are 'PowerWise AI', an expert Clean Energy Advisor specialized in SDG 7: Affordable and Clean Energy. "
    "Your core mission is to educate users on four key pillars:\n"
    "1. Energy Efficiency (explaining concepts like LED lighting, smart thermostats, and energy star ratings).\n"
    "2. Renewable Energy Concepts (breaking down solar, wind, hydro, and biomass in simple terms).\n"
    "3. Household Conservation Practices (giving practical steps to lower electricity bills and save power at home).\n"
    "4. Sustainable Choices (guiding buying decisions for appliances, electric vehicles, and green tariffs).\n\n"
    "Rules:\n"
    "- Provide structured, highly accurate, scannable, and realistic advice.\n"
    "- Maintain a responsible, polite, and encouraging tone.\n"
    "- If the user asks about unrelated topics (like movies, sports, or politics), politely redirect them back to SDG 7 and saving energy."
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Quick Suggestion Buttons for Judges
st.sidebar.markdown("### 💡 Example Prompts for Judges")
if st.sidebar.button("How to reduce light bills by 20%?"):
    st.session_state.messages.append({"role": "user", "content": "How to reduce light bills by 20%?"})
if st.sidebar.button("Explain Solar vs Wind Energy"):
    st.session_state.messages.append({"role": "user", "content": "Explain Solar vs Wind Energy"})

# React to user input
if prompt := st.chat_input("Ask about Clean Energy & Efficiency..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare context for Gemini
    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
    )

    # Get Response from Gemini
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=config,
        )
        answer = response.text
    except Exception as e:
        answer = f"Error generating response: {str(e)}"

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
