TOOL_SCHEMAS = [
    {
        "type": "function",
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
    },
    {
        "type": "function",
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
    },
    {
        "type": "function",
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
    },
    {
        "type": "function",
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
]