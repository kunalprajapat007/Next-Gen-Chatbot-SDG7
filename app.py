import streamlit as st
import os
import json
from google import genai
from google.genai import types

# --- 1. SET UP THE PAGE ---
st.set_page_config(page_title="PowerWise AI - SDG 7", page_icon="⚡", layout="centered")

# --- 2. GET API KEY & INITIALIZE GEMINI ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please set it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 3. STRICT SDG 7 SYSTEM INSTRUCTION ---
SYSTEM_INSTRUCTION = (
    "You are 'PowerWise AI', an expert Clean Energy Advisor specialized in SDG 7: Affordable and Clean Energy. "
    "Your core mission is to educate users on: Energy Efficiency, Renewable Energy, Household Conservation, and Sustainable Choices. "
    "Rules: Provide structured, highly accurate advice. If asked about unrelated topics, politely redirect back to SDG 7."
)

# --- 4. BACKEND API FUNCTION FOR JUDGES (Using Latest Gemini 3.6 Model) ---
def run_api_backend(user_prompt):
    try:
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
        )
        response = client.models.generate_content(
            model='gemini-3.6-flash',  # Updated to the latest 2026 model
            contents=user_prompt,
            config=config,
        )
        return {"status": "success", "response": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 5. DETECT IF JUDGES ARE QUERYING THE API VIA PARAMS ---
query_params = st.query_params
if "api_query" in query_params:
    input_query = query_params["api_query"]
    api_result = run_api_backend(input_query)
    st.text(json.dumps(api_result))
    st.stop()

# --- 6. STANDARD WEB UI INTERFACE ---
st.title("⚡ PowerWise AI - SDG 7 Clean Energy Advisor")
st.caption("Silver Oak University - Next Gen Chatbot Arena")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about Clean Energy & Efficiency..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.7)

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',  # Updated to the latest 2026 model
            contents=contents,
            config=config,
        )
        answer = response.text
    except Exception as e:
        answer = f"Error: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 7. SHOW JURIES HOW TO USE THE API ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Evaluation API Endpoint")
st.sidebar.info(
    "To test the reachable API endpoint, add `?api_query=YOUR_QUESTION` to the end of this web URL."
)
