from datetime import datetime, timezone
from app.core.database import get_database

async def add_message_to_history(session_id: str, role: str, content: str):
    if not session_id:
        return
    db = get_database()
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc)
    }
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
        return []
    return doc.get("messages", [])

async def delete_chat_history(session_id: str) -> bool:
    if not session_id:
        return False
    db = get_database()
    result = await db.sessions.delete_one({"sessionId": session_id})
    return result.deleted_count > 0
