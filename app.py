import streamlit as st
import json
import google.generativeai as genai

# --- 1. CLEAN STANDARD LAYOUT (FIXES INPUT BOX VISIBILITY) ---
st.set_page_config(page_title="PowerWise SDG 7", page_icon="⚡", layout="centered")

# Minimal CSS to avoid blocking Streamlit's default components
st.markdown("""
    <style>
    h1 {
        background: linear-gradient(90deg, #00ffcc, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 0px !important;
    }
    .unique-tagline {
        color: #00ffcc !important;
        font-style: italic;
        font-size: 14px;
        margin-top: 5px !important;
        margin-bottom: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. INITIALIZE GEMINI LLM FOR ALL-ROUND QUESTIONS ---
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip() != "":
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.warning("⚠️ Please configure 'GEMINI_API_KEY' in Streamlit Secrets for full AI capabilities.")

def run_api_backend(user_prompt, history_context=[]):
    clean_prompt = user_prompt.lower().strip("?.! ")
    
    # --- PERSISTENT MEMORY CONTEXTUAL LOGIC ---
    for msg in history_context:
        if msg["role"] == "user" and "my name is" in msg["content"].lower():
            name_part = msg["content"].lower().split("my name is")[-1].strip().title()
            if "name" in clean_prompt:
                return {"status": "success", "response": f"Your name is **{name_part}**. I remember our conversation! How else can I assist you today?"}

    if "my name is" in clean_prompt:
        name = user_prompt.lower().split("is")[-1].strip().title()
        return {"status": "success", "response": f"Nice to meet you, **{name}**! 🤝 I am PowerWise AI. I can answer any question you have, with a special expertise in SDG 7 (Clean Energy). What's on your mind?"}

    # --- MAIN AI ENGINE (UPDATED TO GEMINI 3.6 FLASH) ---
    try:
        # UPDATED: Google ke naye model name 'gemini-3.6-flash' ka use kiya hai
        model = genai.GenerativeModel(
            model_name="gemini-3.6-flash"
        )
        
        full_prompt = (
            "You are PowerWise AI, an all-purpose AI assistant themed around SDG 7 (Affordable and Clean Energy). "
            "You must answer ALL types of questions asked by the user including coding, poems, history, recipes, etc. "
            f"User Question: {user_prompt}"
        )
        
        response = model.generate_content(full_prompt)
        return {"status": "success", "response": response.text}
        
    except Exception as e:
        return {"status": "error", "response": f"Sorry, I faced an issue connecting to the AI. Ensure your API Key is correct. (Details: {str(e)})"}

# --- 3. DETECT IF JUDGES ARE QUERYING THE API VIA PARAMS ---
query_params = st.query_params
if "api_query" in query_params:
    input_query = query_params["api_query"]
    api_result = run_api_backend(input_query, st.session_state.get("messages", []))
    st.text(json.dumps(api_result))
    st.stop()

# --- 4. INITIALIZE PERSISTENT CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. SIDEBAR OPTIONS HUB ---
st.sidebar.markdown("## ⚡ PowerWise Control Panel")
st.sidebar.markdown("---")

st.sidebar.markdown("### 💡 Sample Queries")
if st.sidebar.button("🌍 What is SDG 7 Goal?"):
    st.session_state.messages.append({"role": "user", "content": "What is SDG 7?"})
    api_res = run_api_backend("What is SDG 7?", st.session_state.messages[:-1])
    st.session_state.messages.append({"role": "assistant", "content": api_res["response"]})

if st.sidebar.button("💻 Write a Python Function"):
    st.session_state.messages.append({"role": "user", "content": "Write a python function to check prime numbers."})
    api_res = run_api_backend("Write a python function to check prime numbers.", st.session_state.messages[:-1])
    st.session_state.messages.append({"role": "assistant", "content": api_res["response"]})

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Core UN Focus Targets")
st.sidebar.caption("• Target 7.1: Universal Access")
st.sidebar.caption("• Target 7.2: Increase Clean Share")
st.sidebar.caption("• Target 7.3: Double Efficiency")

# --- 6. MAIN CHAT AREA ---
st.title("⚡ PowerWise AI")
st.markdown("<p class='unique-tagline'>✨ Fueling the Future, One Clean Prompt at a Time</p>", unsafe_allow_html=True)
st.markdown("---")

# Render previous chat blocks correctly
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# COMPLETED NATIVE STREAMLIT INPUT BOX LOGIC WITH ST.RERUN() FOR ACCURATE RESPONSES
if prompt := st.chat_input("Ask PowerWise AI absolutely anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate Response immediately
    api_res = run_api_backend(prompt, st.session_state.messages[:-1])
    st.session_state.messages.append({"role": "assistant", "content": api_res["response"]})
    st.rerun()
