import json
from openai import OpenAI

# config is imported first: it runs load_dotenv() before OpenAI() reads the API key
from coding_agent.config import MODEL, SYSTEM_PROMPT, setup_workspace
from coding_agent.tools import TOOL_FUNCTIONS
from coding_agent.schemas import TOOL_SCHEMAS

client = OpenAI()
setup_workspace()


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
