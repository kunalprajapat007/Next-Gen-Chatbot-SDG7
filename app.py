import streamlit as st
import json

# --- 1. SET UP THE PAGE ---
st.set_page_config(page_title="PowerWise AI - SDG 7", page_icon="⚡", layout="centered")

# --- 2. SDG 7 EXPERT KNOWLEDGE BASE (Rule-Based System) ---
KNOWLEDGE_BASE = {
    "hi": "Hello! I am 'PowerWise AI', your SDG 7 Clean Energy Advisor. How can I help you save energy today?",
    "hy": "Hello! I am 'PowerWise AI', your SDG 7 Clean Energy Advisor. How can I help you save energy today?",
    "hello": "Hello! I am 'PowerWise AI', your SDG 7 Clean Energy Advisor. How can I help you save energy today?",
    "what is sdg 7": "**SDG 7** stands for **Affordable and Clean Energy**. Its main goal is to ensure access to affordable, reliable, sustainable, and modern energy for all people by 2030.",
    "solar energy": "**Solar Energy** is clean, renewable power harnessed from the sun using photovoltaic (PV) panels. Benefits include zero emissions, reduced electricity bills, and low maintenance costs.",
    "renewable energy": "**Renewable Energy** is clean energy that comes from natural resources that rewrite themselves naturally, such as Solar, Wind, Hydro, and Biomass power. It reduces climate impact significantly.",
    "electricity bill": "Here are 3 ways to reduce your household electricity bill by 20%:\n1. **Switch to LEDs:** Replace old bulbs with Energy Star-rated LED lights.\n2. **Unplug Idle Devices:** Turn off appliances from the plug point to avoid 'phantom load'.\n3. **Smart Thermostats:** Use smart heating/cooling settings to maximize efficiency.",
    "energy efficiency": "**Energy Efficiency** means using less energy to perform the same task (e.g., using an LED bulb instead of a regular bulb). It saves money and protects the planet.",
    "conservation": "**Energy Conservation** means changing behaviors to save power altogether (e.g., turning off a fan when leaving a room). It costs zero rupees to implement!"
}

DEFAULT_RESPONSIBLE_RESPONSE = (
    "I am 'PowerWise AI', an expert Clean Energy Advisor specialized in SDG 7. "
    "I can only provide accurate and responsible advice on energy efficiency, renewable energy, and sustainable household habits. "
    "Please ask me anything related to saving electricity or solar/wind power!"
)

# --- 3. HARDCODED INSTANT API BACKEND ---
def run_api_backend(user_prompt):
    clean_prompt = user_prompt.lower().strip("?.! ")
    
    # Check knowledge base first
    for key in KNOWLEDGE_BASE:
        if key in clean_prompt:
            return {"status": "success", "response": KNOWLEDGE_BASE[key]}
            
    # Responsible AI filter fallback
    return {"status": "success", "response": DEFAULT_RESPONSIBLE_RESPONSE}

# --- 4. DETECT IF JUDGES ARE QUERYING THE API VIA PARAMS ---
query_params = st.query_params
if "api_query" in query_params:
    input_query = query_params["api_query"]
    api_result = run_api_backend(input_query)
    st.text(json.dumps(api_result))
    st.stop()

# --- 5. STANDARD WEB UI INTERFACE ---
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

    # Instant calculation from backend
    api_response = run_api_backend(prompt)
    answer = api_response["response"]

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 6. SHOW JURIES HOW TO USE THE API ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Evaluation API Endpoint")
st.sidebar.info(
    "To test the reachable API endpoint, add `?api_query=YOUR_QUESTION` to the end of this web URL."
)
