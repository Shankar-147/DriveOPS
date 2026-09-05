import json

from backend.agent.llm_client import call_llm
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.tool_registry import ALL_TOOL_SCHEMAS, dispatch_tool, is_yellow_tier

MAX_TOOL_ITERATIONS = 8


async def run_agent(user_message, vehicle_id, conversation_state=None, tools=None):
    """Runs the tool-calling loop for one user turn.

    conversation_state: prior message list (without the system prompt - it is
    prepended fresh each call so prompt edits take effect immediately).
    Returns (reply_text, updated_messages).
    """
    tools = tools if tools is not None else ALL_TOOL_SCHEMAS
    history = conversation_state or []

    system_msg = {
        "role": "system",
        "content": f"{SYSTEM_PROMPT}\n\nThe active vehicle_id for this conversation is: {vehicle_id}",
    }
    messages = [system_msg] + history + [{"role": "user", "content": user_message}]

    for _ in range(MAX_TOOL_ITERATIONS):
        response = await call_llm(messages, tools=tools)
        choice = response["choices"][0]["message"]

        if choice.get("tool_calls"):
            messages.append(choice)
            for call in choice["tool_calls"]:
                name = call["function"]["name"]
                try:
                    args = json.loads(call["function"]["arguments"] or "{}")
                except json.JSONDecodeError:
                    args = {}

                if is_yellow_tier(name) and not args.get("confirmed"):
                    result = {
                        "status": "needs_confirmation",
                        "proposed_action": name,
                        "args": args,
                    }
                else:
                    result = dispatch_tool(name, args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(result),
                })
            continue

        return choice["content"], messages[1:]  # drop system message from stored history

    return "I wasn't able to finish reasoning about that within the tool-call budget - please try rephrasing.", messages[1:]
