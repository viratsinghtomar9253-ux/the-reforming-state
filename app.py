import os
import json
import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Logging
logging.basicConfig(level=logging.INFO)

# Configure Groq
api_key = os.getenv("GROQ_API_KEY")
client = None
if not api_key:
    logging.warning("GROQ_API_KEY not set. AI features will mock responses.")
else:
    client = Groq(api_key=api_key)

# Shared State File
STATE_FILE = "state.json"

def read_state():
    if not os.path.exists(STATE_FILE):
        return {"messages": []}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"messages": []}

def write_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def analyze_text(text):
    """
    Sends text to Groq to get JSON analysis:
    {
      "reframed_text": "...",
        "conflict_score": 0-100,
        "hidden_need": "...",
        "peace_offering": "..."
    }
    """
    # Read current settings
    state = read_state()
    love_language = state.get("settings", {}).get("love_language", "Words of Affirmation")

    if not client:
        # Mock response if no key
        return {
            "reframed_text": f"[Mock Reframed]: {text}",
            "conflict_score": 50,
            "hidden_need": "To be heard",
            "peace_offering": "Share a quiet moment together."
        }

    system_prompt = f"""
    You are an expert Relationship Psychologist. Your goal is to de-escalate conflict and uncover hidden emotional needs.
    Analyze the submitted message from a partner in a conflict.
    
    Reframing Constraint: The user's partner responds best to the Love Language: "{love_language}". 
    Ensure the 'reframed_text' and 'peace_offering' align with this value.
    
    Tasks:
    1. Reframe the message: Convert "You" statements to "I" statements. Remove insults. Preserve the core emotional truth. 
       - If "{love_language}" is Acts of Service, suggest helping or doing.
       - If "{love_language}" is Words of Affirmation, use validating and appreciative language.
       - If "{love_language}" is Quality Time, suggest time together.
    2. estimate a 'conflict_score' from 0 (peaceful) to 100 (high conflict).
    3. Identify the 'hidden_need' (e.g., validation, safety, connection).
    4. Suggest a 'peace_offering' (a micro-date or connection act).
    
    Output strictly valid JSON with keys: 'reframed_text', 'conflict_score', 'hidden_need', 'peace_offering'.
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        response_content = completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        logging.error(f"Groq Error: {e}")
        return {
            "reframed_text": "I'm feeling overwhelmed and need a moment.",
            "conflict_score": 75,
            "hidden_need": "Emotional safety",
            "peace_offering": "Take a deep breath and ask for a hug."
        }

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    logging.info(f"Received message from {sender}: {incoming_msg}")

    # analysis
    analysis = analyze_text(incoming_msg)
    
    # store state
    state = read_state()
    record = {
        "timestamp": datetime.now().isoformat(),
        "original_text": incoming_msg,
        "sender": sender,
        **analysis
    }
    state["messages"].append(record)
    write_state(state)

    # Respond via WhatsApp
    resp = MessagingResponse()
    reply_text = f"✨ Reframed: {analysis['reframed_text']}\n\n🌡️ Conflict Level: {analysis['conflict_score']}/100"
    resp.message(reply_text)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
