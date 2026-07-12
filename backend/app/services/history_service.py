from datetime import datetime, timezone
from app.core.database import get_database

async def add_message_to_history(session_id: str, role: str, content: str, message_type: str = "text", metadata: dict | None = None):
    if not session_id:
        return
    db = get_database()
    message = {
        "role": role,
        "content": content,
        "messageType": message_type,
        "metadata": metadata,
        "timestamp": datetime.now(timezone.utc)
    }
    print(f"MongoDB Saving -> {role.capitalize()} Message: '{content[:60]}...'")
    await db.sessions.update_one(
        {"sessionId": session_id},
        {
            "$push": {"messages": message},
            "$set": {"updatedAt": datetime.now(timezone.utc)},
            "$setOnInsert": {"createdAt": datetime.now(timezone.utc)}
        },
        upsert=True
    )

async def get_chat_history(session_id: str) -> list:
    if not session_id:
        return []
    db = get_database()
    doc = await db.sessions.find_one({"sessionId": session_id})
    if not doc:
        print("\n========== HISTORY SERVICE ==========")
        print("History Loaded")
        print("Messages Count:\n0")
        return []
    messages = doc.get("messages", [])
    print("\n========== HISTORY SERVICE ==========")
    print("History Loaded")
    print(f"Messages Count:\n{len(messages)}")
    return messages

async def delete_chat_history(session_id: str) -> bool:
    if not session_id:
        return False
    db = get_database()
    result = await db.sessions.delete_one({"sessionId": session_id})
    return result.deleted_count > 0

def format_chat_history(messages: list) -> str:
    """
    Formats the last 6 messages into a single text representation:
    user: ...
    assistant: ...
    """
    if not messages:
        return ""
        
    last_messages = messages[-6:]
    formatted = []
    for msg in last_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted.append(f"{role}: {content}")
        
    return "\n".join(formatted)
