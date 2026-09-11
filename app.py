import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai  # Purana standard library

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Clean Energy Advisor 🌱", page_icon="🌱")

# Title and caption
st.title("Clean Energy Advisor 🌱")
st.caption("Your AI guide for clean energy and sustainable choices.")

# Initialize Gemini Client (Purana stable tarika)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please configure GEMINI_API_KEY in your Streamlit Secrets / .env file.")
    st.stop()

# Configure the API key
genai.configure(api_key=api_key)

# User input
user_question = st.chat_input("Ask a question about clean energy...")

if user_question:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_question)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Stable free-tier model call
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=(
                        "You are Clean Energy Advisor, an expert AI guide dedicated to renewable energy, "
                        "energy efficiency, energy conservation, and sustainable choices. "
                        "Answer questions clearly, accurately, and helpfully."
                    )
                )
                response = model.generate_content(user_question)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating response: {e}")
