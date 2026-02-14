import streamlit as st
import json
import os
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import numpy as np
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Page Config
st.set_page_config(
    page_title="The Reframing Room",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Premium Aesthetic
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    .reframed-text {
        font-size: 1.2em;
        color: #A6E3A1;
        font-style: italic;
        background-color: #1E1E2E;
        padding: 15px;
        border-left: 5px solid #A6E3A1;
        border-radius: 5px;
    }
    .raw-text {
        font-size: 1.1em;
        color: #F38BA8;
        background-color: #1E1E2E;
        padding: 15px;
        border-left: 5px solid #F38BA8;
        border-radius: 5px;
    }
    h1, h2, h3 {
        font-weight: 700;
        color: #CDD6F4;
    }
</style>
""", unsafe_allow_html=True)

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

# Groq Setup
api_key = os.getenv("GROQ_API_KEY")
client = None
if api_key:
    client = Groq(api_key=api_key)

def generate_micro_date(love_language, conflict_context):
    if not client:
        return "Configure Groq API Key to generate real ideas."
    
    prompt = f"""
    Suggest a unique 'Micro-Date' (under 30 mins) for a couple to reconnect after a conflict.
    
    Constraint: One partner's Love Language is "{love_language}".
    Context of conflict: "{conflict_context}"
    
    The idea should be specific, actionable, and low-pressure.
    Output ONLY the idea in one sentence.
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return "Could not generate idea. (API Error)"

# Title and Header
st.title("🕊️ The Reframing Room")
st.markdown("### *Turning Conflict into Connection*")

# Tabs for Screens
tab1, tab2, tab3 = st.tabs(["The Translator", "Biometrics", "Peace Offering"])

# Auto-refresh logic
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Poll for changes
state = read_state()
messages = state.get("messages", [])
current_love_language = state.get("settings", {}).get("love_language", "Words of Affirmation")

# Sidebar for Settings
with st.sidebar:
    st.header("❤️ Relationship Settings")
    selected_language = st.selectbox(
        "Partner's Love Language",
        ["Words of Affirmation", "Acts of Service", "Receiving Gifts", "Quality Time", "Physical Touch"],
        index=["Words of Affirmation", "Acts of Service", "Receiving Gifts", "Quality Time", "Physical Touch"].index(current_love_language)
    )
    
    # Update state if changed
    if selected_language != current_love_language:
        state["settings"] = {"love_language": selected_language}
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
        st.rerun()

# Get latest message if available
latest_msg = messages[-1] if messages else None

with tab1:
    st.header("The Translator")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Vent (You said)")
        if latest_msg:
            st.markdown(f'<div class="raw-text">{latest_msg.get("original_text", "Waiting for input...")}</div>', unsafe_allow_html=True)
        else:
            st.info("Waiting for WhatsApp messages...")

    with col2:
        st.subheader("Reframed Connection (We heard)")
        if latest_msg:
            st.markdown(f'<div class="reframed-text">{latest_msg.get("reframed_text", "Waiting for reframing...")}</div>', unsafe_allow_html=True)
            st.caption(f"Reasoning: {latest_msg.get('hidden_need', 'connection')} | Mode: {current_love_language}")
        else:
            st.info(f"AI is listening... (Mode: {current_love_language})")

with tab2:
    st.header("Biometrics & Emotion")
    
    if latest_msg:
        conflict_score = latest_msg.get("conflict_score", 50)
        
        # Conflict Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = conflict_score,
            title = {'text': "Conflict Temperature"},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#F38BA8" if conflict_score > 60 else "#FAB387" if conflict_score > 30 else "#A6E3A1"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(166, 227, 161, 0.3)'},
                    {'range': [30, 70], 'color': 'rgba(250, 179, 135, 0.3)'},
                    {'range': [70, 100], 'color': 'rgba(243, 139, 168, 0.3)'}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Heartbeat Visualizer (Sine Wave Animation)
        st.subheader("Emotional Pulse")
        
        # Simulate a heartbeat based on conflict score
        # Higher conflict = faster frequency, higher amplitude
        freq = 1 + (conflict_score / 20)
        amp = 1 + (conflict_score / 50)
        
        x = np.linspace(0, 10, 100)
        y = amp * np.sin(freq * x)
        
        df_wave = pd.DataFrame({'Time': x, 'Pulse': y})
        fig_wave = px.line(df_wave, x='Time', y='Pulse', template="plotly_dark")
        fig_wave.update_traces(line_color='#89B4FA', line_width=3)
        fig_wave.update_layout(yaxis_range=[-4, 4], showlegend=False, xaxis_visible=False, yaxis_visible=False)
        st.plotly_chart(fig_wave, use_container_width=True)
        
    else:
        st.info("No biometric data yet.")

with tab3:
    st.header("The Peace Offering")
    if latest_msg:
        st.success(f"🕊️ Suggestion: {latest_msg.get('peace_offering', 'Take a breath.')}")
        
        st.markdown("### Why this works")
        st.write(f"This addresses the hidden need for **{latest_msg.get('hidden_need', 'connection')}** by creating a shared moment of safety.")
        
        if st.button("Generate New Micro-Date Idea"):
             idea = generate_micro_date(current_love_language, latest_msg.get('hidden_need', 'connection'))
             st.info(f"💡 {idea}")

    else:
        st.info("Waiting for conflict resolution...")

# Auto-rerun for real-time updates
time.sleep(2)
st.rerun()
