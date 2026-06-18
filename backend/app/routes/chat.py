from fastapi import APIRouter
from app.models.schemas import ChatRequest
from app.services.universal_search import universal_search
from app.services.history_service import add_message_to_history

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):

    try:

        query = request.message.strip()

        if not query:
            return {
                "type": "error",
                "answer": "Please enter a valid question."
            }

        # Save user message to history
        if request.sessionId:
            await add_message_to_history(request.sessionId, "user", query)

        result = universal_search(query)

        if not result:
            result = {
                "type": "fallback",
                "answer": (
                    "Sorry, I couldn't find any information related to your query."
                )
            }

        # Save bot response to history
        if request.sessionId and "answer" in result:
            await add_message_to_history(request.sessionId, "assistant", result["answer"])

        return result

    except Exception as e:

        return {
            "type": "error",
            "answer": f"Internal Server Error: {str(e)}"
        }

# Trigger reload for buildings.json and rapidfuzz processor update