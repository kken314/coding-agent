import os
import json
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
MODEL = "gpt-5-mini"

# The agent works inside <project root>/workspace so its projects stay separate
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE = os.path.join(PROJECT_ROOT, "workspace")
os.makedirs(WORKSPACE, exist_ok=True)
os.chdir(WORKSPACE)
SYSTEM_PROMPT = """You are a coding agent working inside the user's project folder.

- Explore with the tools before acting; never guess file paths or contents.
- Read a file before editing it, and write back the complete new content.
- If a tool returns an error, read it and try a different approach.
- If the user denies a command, don't retry it; suggest an alternative.
- Don't ask the user for permission in chat before using a tool. The app already
  asks the user to approve every command automatically, so just call the tool.
- The user is on Windows, so use Windows commands (e.g. dir, not ls).
- Keep answers short."""

#Tools
def list_files(path="."):
    """List the files and folders inside a directory.

    Args:
        path: Directory to list. Defaults to the current directory.

    Returns:
        One name per line. Folder names end with "/".
    """
    names = []
    for name in os.listdir(path):
        if os.path.isdir(os.path.join(path, name)):
            name += "/"
        names.append(name)
    return "\n".join(names)

def read_file(path):
    """Read a text file.

    Args:
        path: Path of the file to read.

    Returns:
        The full contents of the file as a string.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    """Write text to a file, creating it or overwriting it.

    Does not create missing folders; the folder in `path` must already exist.

    Args:
        path: Path of the file to write.
        content: The full text to put in the file.

    Returns:
        A short message saying how many characters were written.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} characters to {path}"

def run_command(command):
    """Run a shell command after the user approves it.

    Args:
        command: The shell command to run.

    Returns:
        The exit code, stdout and stderr as one string, or a message
        saying the user denied the command.
    """
    # Ask the human before running anything
    answer = input(f"Run this command? `{command}` (y/n): ")
    if answer.lower() != "y":
        return "User denied running this command."

    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    return f"exit code: {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"

TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files and folders inside a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list. Defaults to the current directory."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the text contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file to read."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text to a file. Creates the file if missing and overwrites it if it exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file to write."
                    },
                    "content": {
                        "type": "string",
                        "description": "The full text to put in the file."
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command and return its exit code, stdout and stderr. The user must approve it first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run."
                    }
                },
                "required": ["command"]
            }
        }
    }
]

# The Responses API expects function tool fields at the top level (no nested "function" key)
TOOL_SCHEMAS = [{"type": "function", **schema["function"]} for schema in TOOL_SCHEMAS]

# The server keeps the conversation; we only chain responses by id
previous_response_id = None

while True:
    user_input = input("You: ")

    if user_input == "exit":
        break

    # Only the new items for this call (user message first, tool results later)
    next_input = [{
        "role": "user",
        "content": user_input
    }]

    # Inner loop: keep talking to the model until it stops asking for tools
    while True:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            input=next_input,
            previous_response_id=previous_response_id
        )
        previous_response_id = response.id
        next_input = []

        tool_calls = [item for item in response.output if item.type == "function_call"]

        # No tool needed -> show the answer and go back to the user
        if not tool_calls:
            print(f"AI: {response.output_text}")
            break

        # Tool needed -> run each one and send the result back
        for tool_call in tool_calls:
            try:
                func = TOOL_FUNCTIONS[tool_call.name]
                args = json.loads(tool_call.arguments)
                print(f"[tool] {tool_call.name}({args})")
                result = func(**args)
            except Exception as e:
                result = f"Error: {e}"

            next_input.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(result)
            })
        # loop again so the model can read the tool results
