import json
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend.agent.loop import run_agent
from backend.agent.tool_registry import dispatch_tool

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory session store for V1 - {session_id: {"history": [...]}}
SESSIONS: dict[str, dict] = {}


class ChatRequest(BaseModel):
    vehicle_id: str
    message: str
    session_id: str | None = None


class ChatConfirmRequest(BaseModel):
    vehicle_id: str
    session_id: str
    confirm: bool


def _find_pending_confirmation(history: list[dict]) -> dict | None:
    """Scans history for the most recent tool response still awaiting confirmation,
    and pairs it with the tool_call's name/args from the preceding assistant message."""
    for i in range(len(history) - 1, -1, -1):
        msg = history[i]
        if msg.get("role") != "tool":
            continue
        try:
            content = json.loads(msg["content"])
        except (json.JSONDecodeError, TypeError):
            continue
        if content.get("status") != "needs_confirmation":
            continue

        tool_call_id = msg["tool_call_id"]
        for j in range(i - 1, -1, -1):
            prior = history[j]
            if prior.get("role") == "assistant" and prior.get("tool_calls"):
                for call in prior["tool_calls"]:
                    if call["id"] == tool_call_id:
                        return {
                            "tool_call_id": tool_call_id,
                            "history_index": i,
                            "name": content["proposed_action"],
                            "args": content["args"],
                        }
        return None
    return None


@router.post("")
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())
    session = SESSIONS.setdefault(session_id, {"history": []})

    reply, history = await run_agent(body.message, body.vehicle_id, conversation_state=session["history"])
    session["history"] = history

    pending = _find_pending_confirmation(history)
    return {
        "reply": reply,
        "needs_confirmation": pending is not None,
        "proposed_action": {"tool_name": pending["name"], "args": pending["args"]} if pending else None,
        "session_id": session_id,
    }


@router.post("/confirm")
async def confirm(body: ChatConfirmRequest):
    session = SESSIONS.get(body.session_id)
    if not session:
        return {"reply": "This session has expired - please start over.", "needs_confirmation": False,
                "proposed_action": None, "session_id": body.session_id}

    history = session["history"]
    pending = _find_pending_confirmation(history)

    if not pending:
        return {"reply": "There's no pending action to confirm.", "needs_confirmation": False,
                "proposed_action": None, "session_id": body.session_id}

    if not body.confirm:
        history[pending["history_index"]]["content"] = json.dumps({"status": "declined_by_user"})
        return {"reply": "Okay, I won't go ahead with that.", "needs_confirmation": False,
                "proposed_action": None, "session_id": body.session_id}

    result = dispatch_tool(pending["name"], {**pending["args"], "confirmed": True})
    history[pending["history_index"]]["content"] = json.dumps(result)

    reply, updated_history = await run_agent(
        "The action has been executed - please confirm the verified result to the user in one short message.",
        body.vehicle_id,
        conversation_state=history,
    )
    session["history"] = updated_history

    return {
        "reply": reply,
        "needs_confirmation": False,
        "proposed_action": None,
        "session_id": body.session_id,
    }
