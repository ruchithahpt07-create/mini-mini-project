import gradio as gr
import requests

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b"


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content) if content is not None else ""


def _build_messages(message: str, history: list) -> list[dict]:
    messages = []
    for item in history:
        if isinstance(item, dict):
            role = item.get("role")
            text = _extract_text(item.get("content"))
            if role and text:
                messages.append({"role": role, "content": text})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            user_text = _extract_text(item[0])
            assistant_text = _extract_text(item[1])
            if user_text:
                messages.append({"role": "user", "content": user_text})
            if assistant_text:
                messages.append({"role": "assistant", "content": assistant_text})
    messages.append({"role": "user", "content": message})
    return messages


def chat(message: str, history: list) -> str:
    messages = _build_messages(message, history)
    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )
        if response.status_code != 200:
            return f"HTTP {response.status_code}: {response.text}"
        result = response.json()
        return result.get("message", {}).get("content", "")
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running (ollama serve)."
    except Exception as e:
        return f"Error: {str(e)}"


demo = gr.ChatInterface(
    fn=chat,
    title="Llama 3.2 Chatbot",
    description="Chat with your local Ollama LLM (llama3.2:1b)",
)

if _name_ == "_main_":
    demo.launch()


On Wed, Nov 25, 2026 at 4:18 PM R.PALLAVI REDDY <rpallavireddy304@gmail.com> wrote:
import gradio as gr
import requests


def chat(message, history):
    url = "http://localhost:11434/api/chat"

    # Convert Gradio history into Ollama message format
    messages = []
    for item in history:
        # Handles both Gradio dict format and older tuple/list format safely
        if isinstance(item, dict):
            messages.append({"role": item["role"], "content": item["content"]})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            messages.append({"role": "user", "content": item[0]})
            if item[1]:
                messages.append({"role": "assistant", "content": item[1]})

    # Add current user message
    messages.append({"role": "user", "content": message})

    try:
        response = requests.post(
            url,
            json={
                "model": "llama3.2:latest",
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        return result["message"]["content"]

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running (ollama serve)."
    except Exception as e:
        return f"Error: {str(e)}"


demo = gr.ChatInterface(
    fn=chat,
    title="Llama 3.2 Chatbot",
    description="Chat with your local Ollama LLM",
)

if _name_ == "_main_":
    demo.