import asyncio
import argparse
import warnings
import sys
from io import StringIO
from contextlib import redirect_stderr
from agents.agent_core import app

# Color codes for terminal output
class Colors:
    USER = '\033[94m'      # Blue for user input
    SYSTEM = '\033[92m'    # Green for system output
    LOG = '\033[90m'       # Gray for logs
    RESET = '\033[0m'      # Reset color
    BOLD = '\033[1m'       # Bold text

async def chat_once(user_message: str):
    # Streams LLM + tool output to stdout
    # Capture and suppress warnings
    with redirect_stderr(StringIO()):
        async for event in app.async_stream_query(user_id="local_cli", message=user_message):
            content = event.get("content", {})
            for part in content.get("parts", []):
                if "text" in part:
                    print(f"{Colors.SYSTEM}{part['text']}{Colors.RESET}", end="", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Chat locally with the ADK RAG agent.")
    parser.add_argument("message", nargs="*", help="Message to send. If empty, enters REPL.")
    args = parser.parse_args()
    msg = " ".join(args.message).strip()

    if msg:
        print(f"{Colors.USER}You: {msg}{Colors.RESET}")
        asyncio.run(chat_once(msg))
        print()
        return

    print(f"{Colors.BOLD}🏢 CymbalBot - Internal Knowledge Assistant{Colors.RESET}")
    print(f"{Colors.LOG}Ask me about company policies, benefits, IT resources, and more!{Colors.RESET}")
    print(f"{Colors.LOG}Type 'help' for guidance or Ctrl+C to exit{Colors.RESET}")
    try:
        while True:
            try:
                q = input(f"{Colors.USER}You: {Colors.RESET}")
                asyncio.run(chat_once(q))
                print()
            except EOFError:
                # Handle piped input ending gracefully
                print(f"\n{Colors.LOG}Input ended. Goodbye!{Colors.RESET}")
                break
    except KeyboardInterrupt:
        print(f"\n{Colors.LOG}bye{Colors.RESET}")

if __name__ == "__main__":
    main()
