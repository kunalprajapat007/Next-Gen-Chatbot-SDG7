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

# --- 2. INITIALIZE GEMINI LLM WITH FORWARD COMPATIBILITY ---
api_key_configured = False
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip() != "":
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"].strip())
        api_key_configured = True
    except Exception:
        api_key_configured = False

# Optimized backend function supporting streaming
def get_ai_stream(user_prompt, history_context=[]):
    clean_prompt = user_prompt.lower().strip("?.! ")
    
    # --- PERSISTENT MEMORY CONTEXTUAL LOGIC ---
    for msg in history_context:
        if msg["role"] == "user" and "my name is" in msg["content"].lower():
            name_part = msg["content"].lower().split("my name is")[-1].strip().title()
            if "name" in clean_prompt:
                yield f"Your name is **{name_part}**. I remember our conversation! How else can I assist you today?"
                return

    if "my name is" in clean_prompt:
        name = user_prompt.lower().split("is")[-1].strip().title()
        yield f"Nice to meet you, **{name}**! 🤝 I am PowerWise AI. I can answer any question you have, with a special expertise in SDG 7 (Clean Energy). What's on your mind?"
        return

    # --- MAIN AI ENGINE WITH STREAMING ---
    if api_key_configured:
        try:
            model = genai.GenerativeModel(model_name="gemini-3.6-flash")
            context_string = ""
            for msg in history_context[-6:]:
                context_string += f"{msg['role'].upper()}: {msg['content']}\n"
                
            full_prompt = (
                "You are PowerWise AI, an all-purpose AI assistant themed around SDG 7 (Affordable and Clean Energy). "
                "CRITICAL: You must answer ALL types of questions asked by the user including coding, poems, history, recipes, general chat, etc. Never say no. "
                f"Conversation History:\n{context_string}"
                f"User Question: {user_prompt}"
            )
            # generate_content_stream se response tukdo mein fast aata hai
            response = model.generate_content(full_prompt, stream=True)
            for chunk in response:
                yield chunk.text
            return
        except Exception:
            pass

    # --- SMART LOCAL BACKUP MODE ---
    if clean_prompt in ["hi", "hy", "hello", "hey"]:
        yield "Hello! 👋 I am **PowerWise AI**. Ask me absolutely anything today!"
    elif "energy" in clean_prompt or "clean energy" in clean_prompt:
        yield "### ⚡ Clean Energy Overview\nClean energy is energy that comes from renewable, zero-emission sources. The motto of SDG 7 is to *ensure access to affordable, reliable, sustainable and modern energy for all by 2030*."
    elif "coding" in clean_prompt or "code" in clean_prompt or "python" in clean_prompt:
        yield "### 💻 Python Code Example\nHere is a simple example to print text:\n```python\nprint('Hello World!')\n```"
    else:
        yield f"I received your question: *'{user_prompt}'*.\n\n(Tip: Active live brain requires a valid `GEMINI_API_KEY` inside Streamlit Cloud secrets.)"

# --- 3. INITIALIZE PERSISTENT CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SIDEBAR OPTIONS HUB & HISTORY MANAGEMENT ---
st.sidebar.markdown("## ⚡ PowerWise Control Panel")
st.sidebar.markdown("---")

st.sidebar.markdown("### ⚙️ Chat Settings")
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.success("Chat history cleared locally!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Sample Queries")
if st.sidebar.button("🌍 What is SDG 7 Goal?"):
    st.session_state.messages.append({"role": "user", "content": "What is SDG 7?"})
    st.rerun()

if st.sidebar.button("💻 Write a Python Function"):
    st.session_state.messages.append({"role": "user", "content": "Write a python function."})
    st.rerun()

# --- 5. MAIN CHAT AREA ---
st.title("⚡ PowerWise AI")
st.markdown("<p class='unique-tagline'>✨ Fueling the Future, One Clean Prompt at a Time</p>", unsafe_allow_html=True)
st.markdown("---")

# Render historical messages
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Check if last message needs an AI response (Fixes delay & triggers instant stream)
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant", avatar="🤖"):
        # st.write_stream se text fast aur dynamic generate hoga
        response_placeholder = st.write_stream(get_ai_stream(last_prompt, st.session_state.messages[:-1]))
    st.session_state.messages.append({"role": "assistant", "content": response_placeholder})
    st.rerun()

# NATIVE STREAMLIT INPUT BOX LOGIC
if prompt := st.chat_input("Ask PowerWise AI absolutely anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
