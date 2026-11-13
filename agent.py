#!/usr/bin/env python3
"""A tiny local agent: model + tool + loop.

The model never searches by itself. It only *asks* for a search by writing
a small JSON message. Our code runs the search and hands the result back.
That back-and-forth is the whole idea of an agent.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

import ollama

# The model to talk to. Override with:  MODEL=llama3.2:1b python agent.py
MODEL = os.environ.get("MODEL", "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:Q4_K_M")
MAX_STEPS = 5  # safety limit so the loop can never run forever

SYSTEM_PROMPT = """You are a research assistant. You have ONE tool:

  search(query): look something up on Wikipedia.

Reply with ONLY a JSON object and nothing else. Two forms are allowed:

  {"action": "search", "query": "<what to look up>"}
  {"action": "answer", "text": "<your final answer>"}

Rules:
- For factual questions, search first.
- After you receive search results, answer using ONLY those results.
- If the results are empty or unhelpful, try one different search query.
"""


# ---------------------------------------------------------------- the tool --
def search(query: str) -> str:
    """Look something up on Wikipedia (free, no account or API key)."""
    params = urllib.parse.urlencode({
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrlimit": 3, "prop": "extracts", "exintro": 1, "explaintext": 1,
        "exlimit": "max", "format": "json",
    })
    request = urllib.request.Request(
        "https://en.wikipedia.org/w/api.php?" + params,
        headers={"User-Agent": "local-agent-workshop/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
    except Exception as error:  # no Wi-Fi, timeout, etc.
        return f"Search failed: {error}"

    pages = data.get("query", {}).get("pages", {}).values()
    pages = sorted(pages, key=lambda page: page.get("index", 0))
    if not pages:
        return "No results."
    return "\n\n".join(f"{p['title']}: {p.get('extract', '')[:500]}" for p in pages)


# ---------------------------------------------------------------- the loop --
def run_agent(question: str) -> None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(1, MAX_STEPS + 1):
        # 1. THINK: ask the model what to do next
        try:
            reply = ollama.chat(
                model=MODEL, messages=messages,
                format="json", options={"temperature": 0},
            )
        except Exception as error:
            print(f"\nCould not reach the model: {error}")
            print("Is Ollama running? Did you pull the model? (see README)")
            return

        text = reply["message"]["content"]
        messages.append({"role": "assistant", "content": text})

        try:
            action = json.loads(text)
        except json.JSONDecodeError:
            action = None
        if not isinstance(action, dict):
            print(f"[step {step}] model sent something unreadable, asking again")
            messages.append({"role": "user", "content": "Reply with valid JSON only."})
            continue

        # 2. ACT: run the tool, or finish
        if action.get("action") == "search":
            query = str(action.get("query", ""))
            print(f"[step {step}] searching for: {query}")
            result = search(query)
            print(f"[step {step}] got {len(result)} characters back")
            # 3. OBSERVE: give the result back to the model, then loop
            messages.append({
                "role": "user",
                "content": f"Search results:\n{result}\n\nNow answer, or search again.",
            })
        elif action.get("action") == "answer":
            print(f"\nANSWER: {action.get('text', '')}\n")
            return
        else:
            messages.append({"role": "user", "content": "Unknown action. Use search or answer."})

    print("\nStopped: the agent hit its step limit without answering.\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_agent(" ".join(sys.argv[1:]))
    else:
        print(f"Local agent using {MODEL}. Type a question, or press Enter to quit.")
        while True:
            question = input("\nAsk> ").strip()
            if not question:
                break
            run_agent(question)
