import json
from openai import OpenAI

# config is imported first: it runs load_dotenv() before OpenAI() reads the API key
from coding_agent.config import MODEL, SYSTEM_PROMPT, setup_workspace
from coding_agent.tools import TOOL_FUNCTIONS
from coding_agent.schemas import TOOL_SCHEMAS

client = OpenAI()

def run_tool(tool_call):
    """Run one tool call and return the function_call_output item for it."""
    try:
        func = TOOL_FUNCTIONS[tool_call.name]
        args = json.loads(tool_call.arguments)
        print(f"[tool] {tool_call.name}({args})")
        result = func(**args)
    except Exception as e:
        result = f"Error: {e}"

    return {
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": str(result)
    }

def run_turn(user_input, previous_response_id):
    """Handle one user message. Returns the id of the last response."""
    # Only the new items for this call (user message first, tool results later)
    next_input = [{
        "role": "user",
        "content": user_input
    }]

    # Keep talking to the model until it stops asking for tools
    while True:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            input=next_input,
            previous_response_id=previous_response_id
        )
        previous_response_id = response.id

        tool_calls = [item for item in response.output if item.type == "function_call"]

        # No tool needed -> show the answer and go back to the user
        if not tool_calls:
            print(f"AI: {response.output_text}")
            return previous_response_id

        # Tool needed -> run each one and send the results back
        next_input = [run_tool(tool_call) for tool_call in tool_calls]

def main():
    setup_workspace()

    # The server keeps the conversation; we only chain responses by id
    previous_response_id = None

    while True:
        user_input = input("You: ")

        if user_input == "exit":
            break

        previous_response_id = run_turn(user_input, previous_response_id)

if __name__ == "__main__":
    main()
