# localagents
Run a Local AI Agent

You will install Ollama, download a tiny 1B model, and run an agent that looks things up on the web. Everything except the web lookup runs on your laptop.

Agent = model + tool + loop. The model decides, our code acts, the result goes back to the model, repeat.

Step 1: Install Ollama (~3 min)
Your computer	Do this
Go to https://ollama.com/download and copy the curl command for your operating system Mac / Windows / Linux
Example: Linux	curl -fsSL https://ollama.com/install.sh | sh

Open a terminal (Mac: Terminal app. Windows: PowerShell) and run curl command. 

Then check it worked by running:

ollama --version

✅ Checkpoint 1: you see a version number.

Step 2: Download the model

A 1B-parameter Llama 3.2 from Hugging Face (Q4_K_M, roughly 0.8 GB), you can check it out https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF

pull model:

ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:Q4_K_M

Try it out:

ollama run hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:Q4_K_M

Type hello, watch it reply, then type /bye to leave.

✅ Checkpoint: the model says hello back. yay!

Step 3: Get the agent code 
git clone <YOUR-REPO-URL>
cd <YOUR-REPO-FOLDER>

No git? Use the green Code → Download ZIP button, unzip, and open a terminal in that folder.

Step 4: Install the one dependency (~1 min)

Check Python first: python3 --version (Windows: python --version). You need 3.9 or newer.

Create a private environment and install:

# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

✅ Checkpoint: your prompt starts with (.venv) and pip finished without errors.

Step 5: Run the agent (~1 min)
python agent.py "How tall is the Eiffel Tower?"

(Windows: python agent.py ...)

You will see the loop happen:

[step 1] searching for: Eiffel Tower height
[step 1] got 1473 characters back
ANSWER: ...

Or run it interactively: python agent.py

To use a different model:

# Mac / Linux
MODEL=llama3.2:1b python agent.py "your question"

# Windows (PowerShell)
$env:MODEL="llama3.2:1b"; python agent.py "your question"

✅ Checkpoint: you saw at least one searching for: line followed by an ANSWER:.

Things to try
Who wrote Pride and Prejudice?
What is the capital of Australia?
What is photosynthesis?
Something the model can't know on its own: Who won the most recent Nobel Prize in Physics?
Expect it to be imperfect

A 1B model is tiny. Sometimes it picks a strange search query, ignores the results, or answers wrongly. That is normal and is part of the lesson: the loop works, but model quality matters. Compare the [step] lines to the answer and see where it went wrong.

Troubleshooting
Problem	Fix
ollama: command not found	Close and reopen the terminal. Still missing? Re-run the installer.
Could not reach the model	Ollama isn't running. Mac/Windows: open the Ollama app. Linux: run ollama serve in another terminal.
model ... not found	Run the Step 2 ollama pull command again and let it finish.
python: command not found	Try python3. If neither works, ask a helper.
Search failed: ...	Wi-Fi problem. The agent still runs but can't look things up.
Garbled or looping output	Normal for tiny models. Press Ctrl+C and rephrase the question.
Files
agent.py: the whole agent, about 100 lines. Read the three comments THINK, ACT, OBSERVE.
requirements.txt: the one dependency (ollama, the Python client).
