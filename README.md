# Local LLM Workspace

A self-hosted local LLM setup using Transformers, MiniCPM5-2B, a lightweight Python model server, and a Streamlit chat interface.

## Requirements

- Windows
- Python 3.14 or compatible Python version
- The repository virtual environment at `.venv`
- MiniCPM5-2B downloaded to `C:\AI\Models\MiniCPM5-2B`

The model server loads the model once and keeps it in memory. The chat client and Streamlit UI reuse that server, so the model is not loaded for every question.

## Setup

From the repository root:

```powershell
& .\.venv\Scripts\Activate.ps1
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `requirements.txt` is not present yet, install the main packages directly:

```powershell
& .\.venv\Scripts\python.exe -m pip install transformers torch torchvision pillow accelerate streamlit
```

## Run the local model server

Open Terminal 1 and leave it running:

```powershell
& .\.venv\Scripts\python.exe .\lmstudio\qwen27b.py --server
```

Wait until you see:

```text
Model loaded. Local server: http://127.0.0.1:8000
```

Only start one server process on port `8000`.

## Run the terminal chat client

Open Terminal 2:

```powershell
& .\.venv\Scripts\python.exe .\lmstudio\qwen27b.py
```

Type any question. Use `exit`, `quit`, or `q` to close the client.

## Run the Streamlit UI

Keep the model server running, then start Streamlit in another terminal:

```powershell
& .\.venv\Scripts\python.exe -m streamlit run .\chatbot_streamlitIntegration\streamlit_app.py --server.port 8501
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

The UI provides:

- Local model status
- Persistent conversation history
- Response time for each answer
- Clear conversation control
- Markdown-formatted answers

## Saved files

- `interview_notes.md`: question, answer, timestamp, and response time
- `chat_history.json`: Streamlit conversation history

These runtime files are ignored by Git where appropriate. Do not commit model weights, virtual environments, API keys, or other large local artifacts.

## Troubleshooting

### Connection refused on port 8000

Start the model server first and wait for `Model loaded` before starting the client or Streamlit.

### Port 8000 is already in use

Find the process:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Stop a stale Python process only after confirming it belongs to this project:

```powershell
Stop-Process -Id <PID> -Force
```

### Model loading is slow

The first server startup loads the model weights. Keep the server terminal open and reuse it for multiple questions.
