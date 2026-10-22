<div align="center">

# 🤖 Coding Agent

**A minimal AI coding agent built from scratch in Python.**
It chats in your terminal, explores files, writes code and runs commands,
powered by the OpenAI **Responses API** with tool calling.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-Responses_API-412991?logo=openai&logoColor=white)
![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9)
![Status](https://img.shields.io/badge/status-learning_project-F59E0B)

</div>

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 💬 | **Chat loop** | Talk to the agent in your terminal |
| 🛠️ | **Tool calling** | The model decides when to list, read, write or run |
| 🔁 | **Agent loop** | Chains several tool calls before answering |
| 🧠 | **Server-side memory** | Conversation is kept by OpenAI via `previous_response_id` |
| 🩹 | **Error recovery** | Tool errors go back to the model instead of crashing |
| 🛡️ | **Human approval** | Every shell command needs your `y/n` |
| 📁 | **Sandbox folder** | Everything the agent builds lands in `workspace/` |

---

## 🗺️ How it works

### The big picture

```mermaid
flowchart LR
    U(["🧑 You"]) -->|message| A["🤖 agent.py"]
    A -->|"input + previous_response_id"| O[("☁️ OpenAI<br/>Responses API")]
    O -->|"text or function_call"| A
    A -->|run| T["🛠️ tools.py"]
    T -->|result| A
    T <-->|"read / write / run"| W[("📁 workspace/")]
    A -->|answer| U

    classDef user fill:#0ea5e9,stroke:#0369a1,color:#fff
    classDef agent fill:#8b5cf6,stroke:#5b21b6,color:#fff
    classDef cloud fill:#10b981,stroke:#047857,color:#fff
    classDef tool fill:#f59e0b,stroke:#b45309,color:#fff
    classDef disk fill:#64748b,stroke:#334155,color:#fff
    class U user
    class A agent
    class O cloud
    class T tool
    class W disk
```

### The agent loop

Two loops are nested inside each other. The **outer loop** (`main`) waits for you.
The **inner loop** (`run_turn`) keeps calling the model until it stops asking for tools.

```mermaid
flowchart TD
    Start(["▶️ Start"]) --> Setup["setup_workspace()<br/>cd into workspace/"]
    Setup --> Input[/"⌨️ You: ..."/]
    Input --> Exit{"exit?"}
    Exit -- yes --> Stop(["⏹️ Bye"])
    Exit -- no --> Call["☁️ client.responses.create()<br/>instructions + tools + new input<br/>+ previous_response_id"]
    Call --> Save["💾 remember response.id"]
    Save --> Check{"🔧 function_call<br/>in output?"}
    Check -- no --> Print["💬 print output_text"]
    Print --> Input
    Check -- yes --> Run["🛠️ run_tool() for each call"]
    Run --> Approve{"run_command?"}
    Approve -- yes --> Ask{"🛡️ You approve? y/n"}
    Ask -- y --> Exec["⚙️ execute"]
    Ask -- n --> Deny["🚫 'User denied'"]
    Approve -- no --> Exec
    Exec --> Out["📦 function_call_output"]
    Deny --> Out
    Out -->|"send results back"| Call

    subgraph outer ["🔁 Outer loop · main()"]
        Input
        Exit
        Print
    end
    subgraph inner ["🔄 Inner loop · run_turn()"]
        Call
        Save
        Check
        Run
        Approve
        Ask
        Exec
        Deny
        Out
    end

    style outer fill:#0ea5e915,stroke:#0ea5e9,stroke-width:2px
    style inner fill:#8b5cf615,stroke:#8b5cf6,stroke-width:2px
```

### One turn, step by step

A real example: *"what's in calculator.py?"*

```mermaid
sequenceDiagram
    autonumber
    actor You as 🧑 You
    participant Agent as 🤖 agent.py
    participant API as ☁️ OpenAI
    participant Tools as 🛠️ tools.py

    You->>Agent: "what's in calculator.py?"
    Agent->>API: user message (no previous id)
    API-->>Agent: function_call list_files(".")
    Agent->>Tools: list_files(".")
    Tools-->>Agent: "calculator/"
    Agent->>API: function_call_output + previous_response_id
    API-->>Agent: function_call read_file("calculator/calculator.py")
    Agent->>Tools: read_file(...)
    Tools-->>Agent: file contents
    Agent->>API: function_call_output + previous_response_id
    API-->>Agent: final text answer
    Agent-->>You: "AI: It's a simple calculator that..."

    Note over Agent,API: Only NEW items are sent each time.<br/>OpenAI remembers the rest via previous_response_id.
```

### Module map

```mermaid
flowchart LR
    subgraph pkg ["📦 src/coding_agent"]
        direction TB
        agent["🤖 <b>agent.py</b><br/>client · run_turn · run_tool · main"]
        config["⚙️ <b>config.py</b><br/>MODEL · SYSTEM_PROMPT<br/>WORKSPACE · setup_workspace"]
        tools["🛠️ <b>tools.py</b><br/>list_files · read_file<br/>write_file · run_command"]
        schemas["📜 <b>schemas.py</b><br/>TOOL_SCHEMAS<br/>(JSON the model sees)"]
    end

    env[(".env<br/>OPENAI_API_KEY")] -.->|load_dotenv| config
    config --> agent
    tools -->|TOOL_FUNCTIONS| agent
    schemas -->|TOOL_SCHEMAS| agent

    style agent fill:#8b5cf6,stroke:#5b21b6,color:#fff
    style config fill:#0ea5e9,stroke:#0369a1,color:#fff
    style tools fill:#f59e0b,stroke:#b45309,color:#fff
    style schemas fill:#10b981,stroke:#047857,color:#fff
    style env fill:#64748b,stroke:#334155,color:#fff
    style pkg fill:#ffffff08,stroke:#94a3b8,stroke-dasharray:5 5
```

> [!TIP]
> **schemas.py** describes the tools *to the model*, and **tools.py** *is* the tools.
> The names must match: when the model calls `read_file`, the agent finds
> `TOOL_FUNCTIONS["read_file"]` and runs it.

---

## 🛠️ Tools

| Tool | What it does | Needs approval |
|---|---|:---:|
| `list_files` | Lists files and folders (folders end with `/`) | ❌ |
| `read_file` | Reads a text file | ❌ |
| `write_file` | Creates or overwrites a file | ❌ |
| `run_command` | Runs a shell command (30 s timeout) | ✅ |

---

## 🚀 Getting started

### Requirements

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An OpenAI API key

### Setup

```bash
# 1. Install dependencies
uv sync                          # or: pip install -r requirement.txt

# 2. Add your API key
copy .env.example .env           # then edit OPENAI_API_KEY in .env
```

### Run

```bash
uv run src/coding_agent/agent.py
```

### Example session

```text
You: make a folder called ken
[tool] run_command({'command': 'mkdir ken'})
Run this command? `mkdir ken` (y/n): y
AI: Created folder "ken".

You: exit
```

---

## 📂 Project structure

```text
Coding_Agent/
├── src/coding_agent/
│   ├── agent.py        🤖 OpenAI client + agent loops
│   ├── config.py       ⚙️ model, system prompt, workspace path
│   ├── tools.py        🛠️ the Python functions the agent can call
│   └── schemas.py      📜 tool descriptions sent to the model
├── workspace/          📁 projects created by the agent (not committed)
├── .env                🔑 your API key (not committed)
├── .env.example
├── pyproject.toml
└── requirement.txt
```

---

## ⚠️ Safety notes

> [!WARNING]
> This is a learning project, **not a sandbox**. Read every command before typing `y`.

- `write_file` **overwrites files without asking**.
- `run_command` asks for approval, but runs anything you approve.
- `workspace/` keeps things tidy, but the agent can still reach other paths (e.g. `..` or absolute paths).
- Conversations are stored on OpenAI's servers (`store=True` is the default) so that `previous_response_id` works.

---

## 🧭 Roadmap

- [x] Tool calling with an agent loop
- [x] Migrate to the Responses API with server-side conversation state
- [x] Split into `config` / `tools` / `schemas` / `agent` modules
- [ ] `edit_file` tool (replace a snippet instead of rewriting the whole file)
- [ ] Limit file tools to paths inside `workspace/`
- [ ] Stream the model's responses
- [ ] Max-iteration guard and API retry with backoff
- [ ] Tests with `pytest`
