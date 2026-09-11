import streamlit as st
import os
import json
from google import genai
from google.genai import types

# --- 1. CHATGPT DARK THEME STYLE (CSS HACK) ---
st.set_page_config(page_title="ChatGPT - PowerWise SDG 7", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    /* Main Background & Chat Container */
    .stApp {
        background-color: #212121 !important;
        color: #ececec !important;
    }
    /* Input Box styling like ChatGPT */
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }
    .stChatInput div {
        background-color: #2f2f2f !important;
        border: 1px solid #424242 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
    }
    /* Headings & Text */
    h1, h2, h3, p, span, li {
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GET API KEY & INITIALIZE GEMINI ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please set it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 3. STRICT SDG 7 SYSTEM INSTRUCTION FOR RESPONSIBLE AI ---
SYSTEM_INSTRUCTION = (
    "You are 'PowerWise AI', a world-class Clean Energy Advisor designed exactly like ChatGPT, specialized in SDG 7: Affordable and Clean Energy. "
    "Provide very detailed, deeply informative, structured, and realistic advice on energy efficiency, renewable energy concepts (solar, wind), "
    "household conservation practices, and green buying choices. Use bullet points and paragraphs like a pro. "
    "CRITICAL RULE: If the user asks about unrelated topics (movies, sports, coding, politics), you MUST politely refuse and say: "
    "'I am a specialized SDG 7 Clean Energy Advisor. I can only assist with queries related to sustainable energy, electricity conservation, and clean technology.'"
)

# --- 4. BACKEND API FUNCTION FOR JUDGES (Using Gemini) ---
def run_api_backend(user_prompt, history_context=[]):
    try:
        contents = []
        # Build chat history for memory
        for msg in history_context:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
        
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]))
        
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
        )
        
        # Using standard robust production model to avoid 404/403 blocks
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=contents,
            config=config,
        )
        return {"status": "success", "response": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 5. DETECT IF JUDGES ARE QUERYING THE API VIA PARAMS ---
query_params = st.query_params
if "api_query" in query_params:
    input_query = query_params["api_query"]
    api_result = run_api_backend(input_query, [])
    st.text(json.dumps(api_result))
    st.stop()

# --- 6. CHATGPT BRANDED WEB UI INTERFACE ---
st.title("⚡ PowerWise AI")
st.markdown("*ChatGPT-powered Expert Advisor for SDG 7: Affordable & Clean Energy*")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history with custom avatars
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Message PowerWise AI..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    # Fast Response generation with loader
    with st.spinner("⚡ PowerWise AI is thinking..."):
        api_response = run_api_backend(prompt, st.session_state.messages)
        
    if api_response["status"] == "success":
        answer = api_response["response"]
    else:
        answer = f"Error generating response: {api_response['message']}"

    # Save to history to maintain correct memory state context
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 7. SHOW JURIES HOW TO USE THE API ---
st.sidebar.title("🛠️ Developer Panel")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Reachable REST API Endpoint")
st.sidebar.info(
    "To test the live backend API, append this parameter to your current browser URL:\n\n"
    "`?api_query=Your+Question`"
)
st.sidebar.markdown("---")
st.sidebar.caption("Next Gen Chatbot Arena © 2026")
