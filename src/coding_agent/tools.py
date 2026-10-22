import os
import subprocess

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