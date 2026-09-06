import json
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend import db_access
from backend.agent.loop import run_agent
from backend.agent.tool_registry import dispatch_tool

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Synthetic follow-up sent to the model after a confirmed YELLOW action - not something
# the user actually typed, so get_history() below hides it from a resumed conversation.
_CONFIRM_FOLLOWUP_MESSAGE = (
    "The action has been executed - please confirm the verified result to the user in one short message."
)


class ChatRequest(BaseModel):
    vehicle_id: str
    message: str
    session_id: str | None = None


class ChatConfirmRequest(BaseModel):
    vehicle_id: str
    session_id: str
    confirm: bool


class ProposedAction(BaseModel):
    tool_name: str
    args: dict


class ChatResponse(BaseModel):
    reply: str
    needs_confirmation: bool = False
    proposed_action: ProposedAction | None = None
    session_id: str
    tool_calls: list[str] = []


class ChatHistoryMessage(BaseModel):
    kind: str  # "user" | "agent"
    text: str


def _find_pending_confirmation(history: list[dict]) -> dict | None:
    """Scans history for the most recent tool response still awaiting confirmation,
    and pairs it with the tool_call's name/args from the preceding assistant message.
    history_index doubles as the message's `seq` in chat_messages - both are the
    message's 0-based position, since append_chat_message assigns seq contiguously."""
    for i in range(len(history) - 1, -1, -1):
        msg = history[i]
        if msg.get("role") != "tool":
            continue
        try:
            content = json.loads(msg["content"])
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(content, dict) or content.get("status") != "needs_confirmation":
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


def _new_tool_call_names(old_len: int, history: list[dict]) -> list[str]:
    """Names of every tool the agent called during the newly-added tail of history -
    lets the UI show 'checking maintenance status...' style activity lines (Ch 10.3)."""
    names = []
    for m in history[old_len:]:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            names.extend(c["function"]["name"] for c in m["tool_calls"])
    return names


def _get_or_create_session(session_id: str | None, vehicle_id: str) -> tuple[str, list[dict]]:
    """Returns (session_id, history). Loads persisted history for a known session,
    or creates a fresh DB-backed session (covers missing id, and an id from a
    since-wiped DB, so the chat degrades to a fresh session instead of erroring)."""
    if session_id and db_access.get_chat_session(session_id):
        return session_id, db_access.get_chat_messages(session_id)

    new_session_id = session_id or str(uuid.uuid4())
    db_access.create_chat_session(new_session_id, vehicle_id)
    return new_session_id, []


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest):
    session_id, history = _get_or_create_session(body.session_id, body.vehicle_id)

    old_len = len(history)
    reply, updated_history = await run_agent(body.message, body.vehicle_id, conversation_state=history)

    for msg in updated_history[old_len:]:
        db_access.append_chat_message(session_id, msg)

    pending = _find_pending_confirmation(updated_history)
    return {
        "reply": reply,
        "needs_confirmation": pending is not None,
        "proposed_action": {"tool_name": pending["name"], "args": pending["args"]} if pending else None,
        "session_id": session_id,
        "tool_calls": _new_tool_call_names(old_len, updated_history),
    }


@router.post("/confirm", response_model=ChatResponse)
async def confirm(body: ChatConfirmRequest):
    session = db_access.get_chat_session(body.session_id)
    if not session:
        return {"reply": "This session has expired - please start over.", "needs_confirmation": False,
                "proposed_action": None, "session_id": body.session_id}

    history = db_access.get_chat_messages(body.session_id)
    pending = _find_pending_confirmation(history)

    if not pending:
        return {"reply": "There's no pending action to confirm.", "needs_confirmation": False,
                "proposed_action": None, "session_id": body.session_id}

    if not body.confirm:
        history[pending["history_index"]]["content"] = json.dumps({"status": "declined_by_user"})
        db_access.update_chat_message(body.session_id, pending["history_index"], history[pending["history_index"]])
        return {"reply": "Okay, I won't go ahead with that.", "needs_confirmation": False,
                "proposed_action": None, "session_id": body.session_id}

    result = dispatch_tool(pending["name"], {**pending["args"], "confirmed": True})
    history[pending["history_index"]]["content"] = json.dumps(result)
    db_access.update_chat_message(body.session_id, pending["history_index"], history[pending["history_index"]])

    old_len = len(history)
    reply, updated_history = await run_agent(
        _CONFIRM_FOLLOWUP_MESSAGE,
        body.vehicle_id,
        conversation_state=history,
    )
    for msg in updated_history[old_len:]:
        db_access.append_chat_message(body.session_id, msg)

    return {
        "reply": reply,
        "needs_confirmation": False,
        "proposed_action": None,
        "session_id": body.session_id,
        "tool_calls": _new_tool_call_names(old_len, updated_history),
    }


@router.get("/{session_id}/history", response_model=list[ChatHistoryMessage])
def get_history(session_id: str):
    """Returns just the user/agent text turns (tool call/result plumbing omitted) -
    enough for the frontend to redraw a resumed conversation after a page reload."""
    if not db_access.get_chat_session(session_id):
        return []

    messages = db_access.get_chat_messages(session_id)
    result = []
    for msg in messages:
        if msg.get("role") == "user" and msg.get("content") != _CONFIRM_FOLLOWUP_MESSAGE:
            result.append({"kind": "user", "text": msg["content"]})
        elif msg.get("role") == "assistant" and msg.get("content"):
            result.append({"kind": "agent", "text": msg["content"]})
    return result
