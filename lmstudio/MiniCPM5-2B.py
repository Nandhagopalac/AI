import argparse
import json
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen

from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_PATH = r"C:\AI\Models\MiniCPM5-2B"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
NOTES_FILE = "interview_notes.md"
SYSTEM_PROMPT = """You are a helpful local LLM assistant.
Answer the user's questions clearly and accurately.
Keep answers concise unless the user asks for more detail.
Do not show your internal reasoning or use <think> tags. Give only the final answer.
Always finish your sentences before stopping."""


def clean_response(response):
    response = re.sub(r"<think>.*?</think>\s*", "", response, flags=re.DOTALL | re.IGNORECASE)
    response = re.sub(r"<think>.*$", "", response, flags=re.DOTALL | re.IGNORECASE)
    return response.strip()


def generate_response(tokenizer, model, messages):
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=900,
        do_sample=False,
    )
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1] :],
        skip_special_tokens=True,
    )
    return clean_response(response)


class ChatHandler(BaseHTTPRequestHandler):
    tokenizer = None
    model = None

    def do_POST(self):
        if self.path != "/chat":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        request = json.loads(self.rfile.read(content_length))
        try:
            response = generate_response(self.tokenizer, self.model, request["messages"])
        except Exception as exc:
            payload = json.dumps({"error": str(exc)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        payload = json.dumps({"response": response}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format_string, *args):
        return


def run_server(host, port):
    print("Loading MiniCPM5-2B once...", flush=True)
    ChatHandler.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    ChatHandler.model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="auto",
        torch_dtype="auto",
    )
    print(f"Model loaded. Local server: http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), ChatHandler).serve_forever()


def request_response(messages, host, port):
    payload = json.dumps({"messages": messages}).encode("utf-8")
    request = Request(
        f"http://{host}:{port}/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as result:
        payload = json.loads(result.read())
        if "error" in payload:
            raise RuntimeError(payload["error"])
        return payload["response"]


def save_exchange(number, question, answer):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(NOTES_FILE, "a", encoding="utf-8") as notes:
        if notes.tell() == 0:
            notes.write("# English Interview Notes\n\n")
        notes.write(f"## Exchange {number} - {timestamp}\n\n")
        notes.write("### My Question\n\n")
        notes.write(f"{question.strip()}\n\n")
        notes.write("### LLM Answer\n\n")
        notes.write(f"{answer.strip()}\n\n")


def run_client(host, port):
    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT,
    }]
    exchange_number = 1
    while True:
        user_question = input("\nYou: ").strip()
        if user_question.lower() in {"exit", "quit", "q"}:
            break
        messages.append({
            "role": "user",
            "content": user_question,
        })
        try:
            response = request_response(messages, host, port)
        except Exception as exc:
            raise SystemExit(
                f"Cannot reach the local Qwen server at http://{host}:{port}.\n"
                "Start it in another terminal with:\n"
                "  python qwen27b.py --server\n"
                f"Details: {exc}"
            ) from exc

        print(f"\nQwen: {response}")
        save_exchange(exchange_number, user_question, response)
        print(f"Saved to {NOTES_FILE}")
        exchange_number += 1
        messages.append({
            "role": "assistant",
            "content": response,
        })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--model-path", default=MODEL_PATH)
    args = parser.parse_args()
    MODEL_PATH = args.model_path
    if args.server:
        run_server(args.host, args.port)
    else:
        run_client(args.host, args.port)
