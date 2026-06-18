from fastapi import APIRouter, HTTPException
from app.models.schemas import HistoryResponse, MessageSchema
from app.services.history_service import get_chat_history, delete_chat_history

router = APIRouter(
    prefix="/chat/history",
    tags=["Chat History"]
)

@router.get("/{sessionId}", response_model=HistoryResponse)
async def get_history(sessionId: str):
    try:
        messages = await get_chat_history(sessionId)
        formatted_messages = [
            MessageSchema(role=msg["role"], content=msg["content"])
            for msg in messages
        ]
        return HistoryResponse(sessionId=sessionId, messages=formatted_messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")

@router.delete("/{sessionId}")
async def delete_history(sessionId: str):
    try:
        deleted = await delete_chat_history(sessionId)
        if not deleted:
            return {"status": "success", "message": "No chat history found or cleared"}
        return {"status": "success", "message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")
