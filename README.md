# Coding Agent

A minimal AI coding agent built from scratch in Python, as a learning project.
It chats with you in the terminal and can explore, read, write files and run
shell commands to complete tasks — using the OpenAI API with tool calling.

## Features

- **Chat loop** in the terminal
- **Tool calling** — the model decides when to use a tool:
  | Tool | What it does |
  |---|---|
  | `list_files` | Lists files and folders (folders end with `/`) |
  | `read_file` | Reads a text file |
  | `write_file` | Creates or overwrites a file |
  | `run_command` | Runs a shell command **after you approve it (y/n)** |
- **Agent loop** — the model can call several tools in a row before answering
- **Error recovery** — tool errors are sent back to the model instead of crashing
- **Separate workspace** — everything the agent builds goes into `workspace/`

## How it works

```
You type a message
      │
      ▼
 ┌─────────────────────────────┐
 │ Send messages to the model  │◄──────────┐
 └─────────────────────────────┘           │
      │                                    │
      ▼                                    │
 Does it want a tool? ── yes ──► run tool, add result to messages
      │
      no
      ▼
 Print the answer, wait for the next message
```

There are two loops:

- **Outer loop** — waits for your input.
- **Inner loop** — keeps calling the model until it stops requesting tools.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An OpenAI API key

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

   or with pip:

   ```bash
   pip install -r requirement.txt
   ```

2. Copy `.env.example` to `.env` and add your API key:

   ```bash
   copy .env.example .env
   ```

   ```
   OPENAI_API_KEY=your-key-here
   ```

## Usage

```bash
uv run src/coding_agent/agent.py
```

Example session:

```
You: make folder name ken
[tool] run_command({'command': 'mkdir ken'})
Run this command? `mkdir ken` (y/n): y
AI: Created folder "ken".
```

Type `exit` to quit.

## Project structure

```
Coding_Agent/
├── src/coding_agent/
│   ├── __init__.py
│   └── agent.py        # the whole agent: tools, schemas, loops
├── workspace/          # projects created by the agent
├── pyproject.toml
├── requirement.txt
└── .env                # your API key (not committed)
```

## Safety notes

> ⚠️ This is a learning project, not a sandbox.

- `write_file` **overwrites files without asking**.
- `run_command` asks for approval, but runs anything you approve.
- The `workspace/` folder keeps things tidy, but the agent can still reach
  other paths (e.g. `..` or absolute paths).

Read each command before typing `y`.

## Ideas for next steps

- Ask for confirmation before `write_file` overwrites a file
- Limit tools to paths inside `workspace/`
- Truncate very large tool outputs
- Stream the model's responses
