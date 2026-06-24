from fastapi import APIRouter
import logging

from app.models.schemas import ChatRequest
from app.services.history_service import add_message_to_history, get_chat_history, format_chat_history
from app.services.rag.rag_service import query_rag
from app.services.rag.retriever import is_reasoning_query
from app.services.llm.intent_router import should_use_gemini
from app.services.llm.prompt_builder import build_prompt
from app.services.llm.gemini_service import generate_response
from app.services.llm.response_formatter import clean_gemini_response

router = APIRouter()
logger = logging.getLogger("chat_route")


@router.post("/chat")
async def chat(request: ChatRequest):

    try:
        import time
        start_time = time.time()
        
        query = request.message.strip()

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
        # QUERY RAG
        # ==========================================
        print("Calling query_rag()...")
        rag_start = time.time()
        rag_result = query_rag(query)
        rag_time = time.time() - rag_start

        # ==========================================
        # INTENT / CONFIDENCE ROUTING DECISION
        # ==========================================
        use_gemini = should_use_gemini(query, rag_result)
        
        from app.services.llm.intent_router import GEMINI_KEYWORDS
        intent_gemini = any(kw in query.lower() for kw in GEMINI_KEYWORDS)

        gemini_time = 0.0
        context_length = 0
        context_chunks = 0
        history_length = 0
        gemini_called = False

        if use_gemini:
            gemini_called = True
            gemini_start = time.time()
            
            # Gemini Context: top 7 chunks if reasoning query, else top 3 chunks
            context = ""
            if rag_result and "documents" in rag_result:
                reasoning = is_reasoning_query(query)
                limit = 7 if reasoning else 3
                chunks = rag_result["documents"][:limit]
                context_chunks = len(chunks)
                context = "\n\n".join(chunks)
                context_length = len(context)
                
                print("\n========== CONTEXT INJECTION ==========")
                print(f"Top Retrieved Chunks (Count: {context_chunks}):")
                for i, chunk in enumerate(chunks, 1):
                    print(f"--- Chunk {i} ---\n{chunk[:200]}...")

            # Conversation Memory: last 6 messages (excluding the query we just saved)
            history_text = ""
            if request.sessionId:
                history = await get_chat_history(request.sessionId)
                history_length = len(history)
                if len(history) > 1:
                    history_text = format_chat_history(history[:-1])

            # Build prompt
            prompt = build_prompt(question=query, context=context, history=history_text)

            # Generate response
            gemini_raw = generate_response(prompt)

            # Format/clean response
            answer = clean_gemini_response(gemini_raw)
            gemini_time = time.time() - gemini_start

            result = {
                "type": "gemini",
                "answer": answer
            }
        else:
            result = {
                "type": "rag",
                "answer": rag_result["answer"],
                "source": rag_result["source"],
                "confidence": rag_result["confidence"]
            }
            if rag_result and "documents" in rag_result:
                context_chunks = len(rag_result["documents"])
                context_length = sum(len(d) for d in rag_result["documents"])
            if request.sessionId:
                history = await get_chat_history(request.sessionId)
                history_length = len(history)

        # Total response time
        total_time = time.time() - start_time

        # Display debugging logs as requested
        print("\n========== QUERY ==========")
        print(query)

        print("\n========== RAG ==========")
        if rag_result:
            print(f"Source: {rag_result.get('source')}")
            print(f"Confidence: {rag_result.get('confidence')}")
        else:
            print("Source: None")
            print("Confidence: None")

        print("\n========== ROUTING ==========")
        print(f"Intent Gemini: {intent_gemini}")
        print(f"Using {'Gemini' if use_gemini else 'Direct RAG'}")
        print(f"Gemini Called: {gemini_called}")
        print(f"Context Length: {context_length} chars ({context_chunks} chunks)")
        print(f"History Length: {history_length} messages")

        print("\n========== PERFORMANCE ==========")
        print(f"Response Time: {total_time:.4f}s")
        print(f"RAG Time: {rag_time:.4f}s")
        print(f"Gemini Time: {gemini_time:.4f}s")
        print("=================================\n")

        # Reasoning retrieval diagnostics
        if is_reasoning_query(query):
            sent_docs = []
            if use_gemini:
                if rag_result and "documents" in rag_result:
                    limit = 7
                    sent_docs = rag_result["documents"][:limit]
            else:
                if rag_result and "documents" in rag_result:
                    sent_docs = rag_result["documents"]
            
            from app.services.rag.retriever import get_last_retrieval_sources
            raw_sources = get_last_retrieval_sources()
            unique_sources = []
            for i in range(len(sent_docs)):
                if i < len(raw_sources):
                    src = raw_sources[i]
                    if src and src not in unique_sources:
                        unique_sources.append(src)

            print("==================================================")
            print("\nREASONING RETRIEVAL\n")
            print("Query:")
            print(query)
            print("\nDocuments Sent:")
            print(len(sent_docs))
            print("\nSources Found:")
            for src in unique_sources:
                print(src)
            print("\n==================================================")

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