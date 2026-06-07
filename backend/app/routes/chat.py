from fastapi import APIRouter
from app.models.schemas import ChatRequest
from app.services.universal_search import universal_search

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):

    try:

        query = request.message.strip()

        if not query:
            return {
                "type": "error",
                "answer": "Please enter a valid question."
            }

        result = universal_search(query)

        if result:
            return result

        return {
            "type": "fallback",
            "answer": (
                "Sorry, I couldn't find any information related to your query."
            )
        }

    except Exception as e:

        return {
            "type": "error",
            "answer": f"Internal Server Error: {str(e)}"
        }