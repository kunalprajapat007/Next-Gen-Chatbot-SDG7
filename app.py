import os
import sys
import gradio as gr
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Initialize Gemini Client
try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini Client: {e}")
    sys.exit(1)

# 2. Strict SDG 7 System Instructions for Responsible AI
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

def predict(message, history):
    contents = []
    for human, ai in history:
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=human)]))
        contents.append(types.Content(role="model", parts=[types.Part.from_text(text=ai)]))
    
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=config,
        )
        return response.text
    except APIError as e:
        if e.code == 429:
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=contents,
                    config=config,
                )
                return response.text + "\n\n*(Served via backup model due to high traffic)*"
            except Exception as fallback_error:
                return f"Rate limit reached. Please retry in a moment. Error: {str(fallback_error)}"
        else:
            return f"API Error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# 3. Build Web Interface
demo = gr.ChatInterface(
    fn=predict,
    title="⚡ PowerWise AI - SDG 7 Clean Energy Advisor",
    description=(
        "Welcome! I am your AI guide for SDG 7 (Affordable & Clean Energy). "
        "Ask me about solar power, cutting electricity bills, or energy-efficient choices!"
    ),
    examples=[
        "How can I cut down my household electricity bill by 20%?",
        "Explain the difference between energy efficiency and conservation.",
        "What are the benefits of switching to solar energy at home?",
        "What should I look for when buying an energy-efficient appliance?"
    ],
    theme="soft",
    type="messages"
)

if __name__ == "__main__":
    demo.launch()
