import json
import os
import socket
import time
from datetime import datetime
from urllib.request import Request, urlopen

import streamlit as st


API_URL = os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:8000/chat")
CHAT_FILE = "chat_history.json"
NOTES_FILE = "interview_notes.md"
SYSTEM_PROMPT = (
    "You are a helpful local LLM assistant. Answer clearly and accurately. "
    "Keep answers concise, use Markdown when useful, and never show internal reasoning."
)


def server_is_ready():
    api_host = API_URL.split("//", 1)[-1].split("/", 1)[0]
    host, port_text = api_host.rsplit(":", 1)
    try:
        with socket.create_connection((host, int(port_text)), timeout=1):
            return True
    except (OSError, ValueError):
        return False

st.set_page_config(page_title="Local Desk", page_icon="✦", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root { --ink: #17211d; --muted: #6d7772; --paper: #f5f4ef; --line: #d9ddd6; --accent: #e76f51; --green: #31594f; }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 1120px; padding: 3rem 3rem 7rem; }
    h1, h2, h3, p, div, textarea, button { font-family: 'Manrope', sans-serif; }
    h1 { letter-spacing: 0; font-size: 2.8rem; line-height: 1.05; color: var(--ink); }
    .eyebrow { color: var(--accent); font: 500 .75rem 'DM Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
    .subtitle { color: var(--muted); font-size: 1rem; margin-top: -.8rem; }
    .status { border: 1px solid var(--line); background: #fbfaf6; padding: .75rem 1rem; border-radius: 8px; color: var(--green); font: 500 .78rem 'DM Mono', monospace; }
    .status.offline { color: #a34c3b; }
    .stChatMessage { border: 0; padding: 1rem 0; }
    [data-testid='stChatMessage'] { color: var(--ink) !important; }
    [data-testid='stChatMessageContent'] { color: var(--ink) !important; border-bottom: 1px solid var(--line); padding-bottom: 1.1rem; }
    [data-testid='stChatMessageContent'] * { color: var(--ink) !important; }
    [data-testid='stChatMessageContent'] code { color: #26483f !important; background: #e7ebe3 !important; }
    [data-testid='stChatMessageContent'] a { color: #b84f39 !important; }
    [data-testid='stChatMessageAvatar'] { background: var(--green); }
    .stChatInputContainer { background: transparent; }
    .stChatInputContainer, [data-testid='stChatInput'] { background: #ffffff !important; }
    .stChatInputContainer textarea, [data-testid='stChatInput'] textarea { min-height: 76px !important; border: 1px solid #aebbb2 !important; border-radius: 8px; background: #ffffff !important; color: #17211d !important; caret-color: #17211d !important; font-size: 1rem !important; padding: 1rem !important; }
    .stChatInputContainer textarea::placeholder, [data-testid='stChatInput'] textarea::placeholder { color: #66736c !important; opacity: 1; }
    .stMarkdown, .stMarkdown p, .stMarkdown li { color: var(--ink); }
    .response-meta { color: var(--muted); font: 500 .72rem 'DM Mono', monospace; margin-top: .75rem; }
    .stButton button { border: 1px solid var(--line); border-radius: 7px; color: var(--ink); background: #fbfaf6; }
    .stButton button:hover { border-color: var(--accent); color: var(--accent); }
    section[data-testid='stSidebar'] { background: #e7ebe3; border-right: 1px solid var(--line); }
    .metric { font: 500 .78rem 'DM Mono', monospace; color: var(--muted); border-top: 1px solid var(--line); padding-top: 1rem; margin-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_history():
    if not os.path.exists(CHAT_FILE):
        return []
    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as chat_file:
            return json.load(chat_file)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(messages):
    with open(CHAT_FILE, "w", encoding="utf-8") as chat_file:
        json.dump(messages, chat_file, indent=2, ensure_ascii=False)


def local_answer(messages):
    payload = json.dumps({"messages": messages}).encode("utf-8")
    request = Request(API_URL, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=600) as result:
        response = json.loads(result.read())
    if "error" in response:
        raise RuntimeError(response["error"])
    return response["response"]


def append_notes(question, answer, number, response_seconds):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(NOTES_FILE, "a", encoding="utf-8") as notes:
        if notes.tell() == 0:
            notes.write("# LLM Notes\n\n")
        notes.write(f"## Exchange {number} - {timestamp}\n\n")
        notes.write(f"### My Question\n\n{question.strip()}\n\n")
        notes.write(f"### LLM Answer\n\n{answer.strip()}\n\n")
        notes.write(f"_Response time: {response_seconds:.2f} seconds_\n\n")


if "messages" not in st.session_state:
    st.session_state.messages = load_history()

with st.sidebar:
    st.markdown("<div class='eyebrow'>Local workspace</div>", unsafe_allow_html=True)
    st.markdown("## Local Desk")
    st.caption("Private questions, answered on your machine.")
    st.markdown(f"<div class='metric'>{len(st.session_state.messages) // 2} exchanges saved</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric'>Notes → {NOTES_FILE}</div>", unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        save_history([])
        st.rerun()

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown("<div class='eyebrow'>A quiet interface for big questions</div>", unsafe_allow_html=True)
    st.title("Local Desk")
    st.markdown("<div class='subtitle'>Ask anything. Keep the useful answers.</div>", unsafe_allow_html=True)
with header_right:
    if not server_is_ready():
        st.markdown("<div class='status offline'>● server offline</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status'>● local model ready</div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "response_seconds" in message:
            st.markdown(
                f"<div class='response-meta'>answered in {message['response_seconds']:.2f} seconds</div>",
                unsafe_allow_html=True,
            )

user_input = st.chat_input("Ask your local model anything...")
if user_input:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": user_input, "time": timestamp})
    with st.chat_message("user"):
        st.markdown(user_input)

    model_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    model_messages.extend(
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.messages
    )
    try:
        with st.chat_message("assistant"):
            started_at = time.perf_counter()
            with st.spinner("Thinking..."):
                answer = local_answer(model_messages)
            response_seconds = time.perf_counter() - started_at
            st.markdown(answer)
            st.markdown(
                f"<div class='response-meta'>answered in {response_seconds:.2f} seconds</div>",
                unsafe_allow_html=True,
            )
    except Exception as error:
        st.error(f"The local model is unavailable: {error}")
        st.stop()

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "time": timestamp,
        "response_seconds": response_seconds,
    })
    save_history(st.session_state.messages)
    append_notes(user_input, answer, len(st.session_state.messages) // 2, response_seconds)
    st.rerun()
