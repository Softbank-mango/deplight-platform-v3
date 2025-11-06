#!/usr/bin/env python3
import os
import sys

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv() -> None:  # fallback noop if python-dotenv isn't installed
        pass

from ai.llm_client import quick_ping


def main() -> int:
    load_dotenv()

    # Guardrails: ensure key present
    if not os.getenv("LETSUR_API_KEY"):
        print("error: LETSUR_API_KEY is not set. Export it or add to a .env file.")
        print("example: export LETSUR_API_KEY=sk-...\n")
        return 2

    prompt = "Give a 1-sentence motivational tip for a hackathon team."
    try:
        reply = quick_ping(prompt)
        print("Model reply:\n" + reply)
        return 0
    except Exception as e:
        print(f"LLM call failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

