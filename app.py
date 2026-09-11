import streamlit as st
import os
import json
from google import genai
from google.genai import types

# --- 1. CHATGPT DARK THEME LAYOUT ---
st.set_page_config(page_title="ChatGPT - PowerWise SDG 7", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #212121 !important; color: #ececec !important; }
    .stChatInputContainer { padding-bottom: 20px !important; }
    .stChatInput div { background-color: #2f2f2f !important; border: 1px solid #424242 !important; color: #ffffff !important; border-radius: 12px !important; }
    h1, h2, h3, p, span, li, label { color: #ffffff !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    section[data-testid="stSidebar"] { background-color: #171717 !important; }
    div[data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GET API KEY & INITIALIZE 2026 GENAI CLIENT ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please set it in Streamlit Secrets.")
    st.stop()

# Correct Modern SDK initialization
client = genai.Client(api_key=api_key)

# --- 3. STRICT SDG 7 SYSTEM INSTRUCTION ---
SYSTEM_INSTRUCTION = (
    "You are 'PowerWise AI', a world-class Clean Energy Advisor designed exactly like ChatGPT, specialized in SDG 7: Affordable and Clean Energy. "
    "Provide very detailed, deeply informative, structured, and realistic advice on energy efficiency, renewable energy concepts (solar, wind), "
    "household conservation practices, and green buying choices. Use bullet points and paragraphs like a pro. "
    "CRITICAL RULE: If the user asks about unrelated topics (movies, sports, coding, politics), you MUST politely refuse and say: "
    "'I am a specialized SDG 7 Clean Energy Advisor. I can only assist with queries related to sustainable energy, electricity conservation, and clean technology.'"
)

# --- 4. BACKEND API FUNCTION FOR JUDGES (Using Latest Stable 3.5 Model) ---
def run_api_backend(user_prompt, history_context=[]):
    try:
        contents = []
        for msg in history_context:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
        
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]))
        
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
        )
        
        # Using the certified stable 2026 production model to bypass 404s
        response = client.models.generate_content(
            model='gemini-3.5-flash',
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

# --- 6. INTERACTIVE INTERFACE: SDG 7 SAVINGS CALCULATOR ---
st.title("⚡ PowerWise AI Dash")
st.markdown("### 📊 Interactive SDG 7 Energy & Carbon Savings Tool")
st.markdown("Use this calculator to see how household changes affect your footprint, then discuss outcomes with the chatbot below!")

col1, col2 = st.columns(2)
with col1:
    current_bill = st.slider("Your Monthly Electricity Bill (in ₹)", 500, 15000, 3000, step=100)
    led_switch = st.checkbox("Switched all household lights to Smart LEDs?")
    solar_installed = st.checkbox("Have or plan to install Solar Rooftops?")

# Logic calculations for the interactive section
potential_savings = 0
if led_switch:
    potential_savings += 0.15 # 15% savings from LED
if solar_installed:
    potential_savings += 0.60 # 60% savings from Solar

total_saved_money = current_bill * potential_savings
co2_prevented = (total_saved_money * 0.82) / 10 # Rough carbon offset scale

with col2:
    st.metric(label="Estimated Monthly Money Saved", value=f"₹{total_saved_money:,.2f}")
    st.metric(label="CO2 Emissions Prevented Monthly", value=f"{co2_prevented:.1f} kg")

st.markdown("---")

# --- 7. CHATGPT BRANDED WEB UI INTERFACE ---
st.markdown("### 🤖 Chat with PowerWise AI Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Message PowerWise AI..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    with st.spinner("⚡ PowerWise AI is thinking..."):
        api_response = run_api_backend(prompt, st.session_state.messages)
        
    if api_response["status"] == "success":
        answer = api_response["response"]
    else:
        answer = f"Error generating response: {api_response['message']}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 8. DEVELOPER PANEL FOR JURIES ---
st.sidebar.title("🛠️ Developer Panel")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Reachable REST API Endpoint")
st.sidebar.info(
    "To test the live backend API, append this parameter to your current browser URL:\n\n"
    "`?api_query=Your+Question`"
)
st.sidebar.markdown("---")
st.sidebar.caption("Next Gen Chatbot Arena © 2026")
