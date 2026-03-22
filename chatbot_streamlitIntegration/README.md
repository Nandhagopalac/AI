A persistent AI chat application built with Streamlit and OpenAI o4-mini. Chat history is saved locally as JSON, so your conversations survive page refreshes and restarts.

✨ Features

🧠 Powered by OpenAI o4-mini
💾 Persistent chat history saved to chat_history.json
🕐 Timestamps on every message
🗑️ Clear chat button to reset history
⚡ Concise responses (token limit: 50)
🖥️ Clean, centered Streamlit UI


🗂️ Project Structure
AI/
└── nandha_chat_streamlit/
    ├── app.py                # Main Streamlit app
    ├── chat_history.json     # Auto-generated chat log (do NOT commit)
    ├── .env                  # API key (do NOT commit)
    ├── .env.example          # API key template
    ├── requirements.txt
    └── README.md

⚙️ Setup
1. Navigate to the project
bashcd AI/nandha_chat_streamlit
2. Activate your environment
bash# Windows (uvv env)
C:\Users\Acnan\AI\.venv\Scripts\activate
3. Install dependencies
bashpip install streamlit openai python-dotenv
4. Configure API key
Create a .env file:
OPENAI_API_KEY=your_openai_api_key_here

🚀 Usage
bashstreamlit run app.py
Then open your browser at:
http://localhost:8501

🖼️ How It Works
User types prompt
       ↓
Timestamp added + displayed
       ↓
Full conversation history sent to OpenAI o4-mini
       ↓
Assistant reply displayed with timestamp
       ↓
Both messages saved to chat_history.json
       ↓
History reloaded on next app start

💾 Chat History Format
Messages are stored in chat_history.json like this:
json[
    {
        "role": "user",
        "content": "What is Python?",
        "time": "2025-01-15 10:30:00"
    },
    {
        "role": "assistant",
        "content": "Python is a high-level programming language.",
        "time": "2025-01-15 10:30:01"
    }
]

📦 Requirements
streamlit
openai
python-dotenv
Generate via:
bashpip freeze > requirements.txt

🔒 .gitignore
Make sure these are ignored:
.env
chat_history.json
__pycache__/
*.pyc
.venv/

📁 .env.example
OPENAI_API_KEY=your_openai_api_key_here

📊 Roadmap

 Basic CLI chat — nandha_chat.py
 Streamlit UI with persistent history — app.py
 Export chat history as PDF/CSV
 Multiple chat sessions support
 Model selector (gpt-4.1-mini / o4-mini)


📄 License
MIT