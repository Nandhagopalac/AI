import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# -------------------- CONFIG --------------------

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FILE = "chat_history.json"
system_input = "Limit the token usage to 50 and answer precisely."

st.set_page_config(page_title="Simple AI Chat", layout="centered")
st.title("💬 Simple AI Chat (Persistent)")

# -------------------- FILE FUNCTIONS --------------------

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat(messages):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

# -------------------- SESSION INIT --------------------

if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

# -------------------- DISPLAY HISTORY --------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"**{message['time']}**")
        st.markdown(message["content"])

# -------------------- USER INPUT --------------------

user_input = st.chat_input("Enter your prompt")

if user_input:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display user message
    st.chat_message("user").markdown(f"**{timestamp}**\n\n{user_input}")

    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "time": timestamp
    })

    # Prepare conversation for OpenAI (without timestamp)
    openai_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    response = client.responses.create(
        model="o4-mini",
        input=openai_messages,
        instructions=system_input
    )

    reply = response.output_text
    assistant_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display assistant reply
    st.chat_message("assistant").markdown(f"**{assistant_time}**\n\n{reply}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "time": assistant_time
    })

    # Save to JSON
    save_chat(st.session_state.messages)

# -------------------- CLEAR BUTTON --------------------

if st.button("🗑 Clear Chat"):
    st.session_state.messages = []
    save_chat([])
    st.success("Chat cleared successfully!")