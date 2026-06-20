from fastapi import APIRouter

from app.models.schemas import ChatRequest
from app.services.universal_search import universal_search
from app.services.history_service import add_message_to_history
from app.services.rag.rag_service import query_rag

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):

    try:

        query = request.message.strip()

        print("\n========================")
        print("CHAT REQUEST RECEIVED")
        print("QUERY:", query)
        print("========================\n")

        if not query:
            return {
                "type": "error",
                "answer": "Please enter a valid question."
            }

        # ==========================================
        # SAVE USER MESSAGE
        # ==========================================

        if request.sessionId:

            print("Saving user message...")

            await add_message_to_history(
                request.sessionId,
                "user",
                query
            )

        # ==========================================
        # TEST RAG
        # ==========================================

        print("Calling query_rag()...")

        rag_result = query_rag(query)

        print("RAG RESULT:")
        print(rag_result)

        if rag_result:

            print(
                f"Using RAG | Source: {rag_result['source']}"
            )

            result = {
                "type": "rag",
                "answer": rag_result["answer"],
                "source": rag_result["source"],
                "confidence": rag_result["confidence"]
            }

        else:

            print("RAG returned None")
            print("Using Universal Search")

            result = universal_search(query)

            print("Universal Search Result:")
            print(result)

            if not result:

                result = {
                    "type": "fallback",
                    "answer": (
                        "Sorry, I couldn't find any information related to your query."
                    )
                }

        # ==========================================
        # SAVE BOT RESPONSE
        # ==========================================

        if (
            request.sessionId
            and "answer" in result
        ):

            print("Saving assistant response...")

            await add_message_to_history(
                request.sessionId,
                "assistant",
                result["answer"]
            )

        print("Returning response successfully")

        return result

    except Exception as e:

        print("\n========================")
        print("CHAT ERROR")
        print(type(e))
        print(str(e))
        print("========================\n")

        return {
            "type": "error",
            "answer": f"{type(e).__name__}: {str(e)}"
        }