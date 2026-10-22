import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-5-mini"

# The agent works inside <project root>/workspace so its projects stay separate
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE = os.path.join(PROJECT_ROOT, "workspace")

SYSTEM_PROMPT = """You are a coding agent working inside the user's project folder.

- Explore with the tools before acting; never guess file paths or contents.
- Read a file before editing it, and write back the complete new content.
- If a tool returns an error, read it and try a different approach.
- If the user denies a command, don't retry it; suggest an alternative.
- Don't ask the user for permission in chat before using a tool. The app already
  asks the user to approve every command automatically, so just call the tool.
- The user is on Windows, so use Windows commands (e.g. dir, not ls).
- Keep answers short."""


def setup_workspace():
    """Create the workspace folder if needed and make it the working directory."""
    os.makedirs(WORKSPACE, exist_ok=True)
    os.chdir(WORKSPACE)
