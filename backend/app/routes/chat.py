from fastapi import APIRouter, Depends, Request
from typing import Optional, Any, Dict
import logging
import asyncio
import time

from app.security.rate_limit.rate_limiter import rate_limit_chat
from app.security.sanitizers.ai_guard import validate_chat_query

from app.models.schemas import ChatRequest
from app.services.history_service import add_message_to_history, get_chat_history, format_chat_history
from app.services.rag.rag_service import query_rag
from app.services.rag.retriever import is_reasoning_query
import app.services.rag.retriever as retriever
from app.services.llm.intent_router import should_use_gemini, is_greeting, classify_intent, ROUTING_TABLE, make_routing_decision, RoutingDecision
from app.core.config import IS_DEV_MODE, DEBUG_RAG
from app.services.rag.debug_logger import init_debug_store, get_debug_store
from app.services.llm.gemini_service import generate_response, get_circuit_breaker_status, get_last_retry_count, get_last_llm_usage
from app.services.ai.cache import get_cached_response, set_cached_response
from app.services.llm.response_formatter import clean_gemini_response
from app.services.ai.prompt import PromptOrchestrator
from app.schemas.prompt_schema import PromptContext, PromptMetadata

prompt_orchestrator = PromptOrchestrator()

router = APIRouter()
logger = logging.getLogger("chat_route")

def get_diagnostics_payload(
    total_time: float,
    auth_time: float,
    history_time: float,
    rag_time: float,
    academic_time: float,
    nav_time: float,
    prompt_gen_duration: float,
    gemini_time: float,
    prompt_length: int,
    estimated_tokens: int,
    context_chunks: int,
    history_length: int,
    context_length: int,
    intent: str,
    circuit_breaker_status: str = "CLOSED",
    gemini_called: bool = False,
    fallback_used: bool = False,
    retry_count: int = 0,
    cache_hit: bool = False,
    routing_decision: str = "Gemini",
    # New stabilization / refinement diagnostics
    detected_intent: str = "Unknown",
    selected_service: str = "Gemini",
    fallback_service: str = "Direct RAG Fallback",
    routing_reason: str = "Default",
    gemini_required: bool = True,
    rag_required: bool = True,
    navigation_required: bool = False,
    workspace_required: bool = False,
    confidence: float = 1.0,
    rejected_retrievals: list | None = None,
    # Extended routing diagnostics flags
    intent_confidence: float = 1.0,
    gemini_called_flag: bool = False,
    rag_called_flag: bool = False,
    navigation_called_flag: bool = False,
    workspace_called_flag: bool = False,
    rejected_retrieval_count: int = 0,
    response_strategy: str = "Gemini",
    **kwargs  # absorb any unknown future params gracefully
) -> dict:
    doc_cache_hits = getattr(retriever, "_docs_cache_hits", 0)
    doc_cache_misses = getattr(retriever, "_docs_cache_misses", 0)
    template_hits = prompt_orchestrator.template_loader.hits
    template_misses = prompt_orchestrator.template_loader.misses
    db_latency = history_time + academic_time + nav_time
    
    return {
        "total_response_time_seconds": round(total_time, 4),
        "stages": {
            "auth_time_seconds": round(auth_time, 4),
            "history_retrieval_time_seconds": round(history_time, 4),
            "rag_retrieval_time_seconds": round(rag_time, 4),
            "academic_context_time_seconds": round(academic_time, 4),
            "nav_resolution_time_seconds": round(nav_time, 4),
            "prompt_assembly_time_seconds": round(prompt_gen_duration, 4),
            "gemini_latency_time_seconds": round(gemini_time, 4)
        },
        "prompt_size_characters": prompt_length,
        "estimated_prompt_tokens": estimated_tokens,
        "retrieved_rag_chunk_count": context_chunks,
        "memory_messages_count": history_length,
        "context_size_characters": context_length,
        "gemini_response_latency_seconds": round(gemini_time, 4),
        "database_latency_seconds": round(db_latency, 4),
        "cache_status": {
            "document_cache": f"hits: {doc_cache_hits}, misses: {doc_cache_misses}",
            "template_cache": f"hits: {template_hits}, misses: {template_misses}",
            "response_cache": "HIT" if cache_hit else "MISS"
        },
        "overall_api_latency_seconds": round(total_time, 4),
        "circuit_breaker_status": circuit_breaker_status,
        "gemini_called": gemini_called,
        "fallback_used": fallback_used,
        "retry_count": retry_count,
        "cache_hit": cache_hit,
        "routing_decision": routing_decision,
        # Refinement Details
        "intent_refinement": {
            "detected_intent": detected_intent,
            "selected_service": selected_service,
            "fallback_service": fallback_service,
            "routing_reason": routing_reason,
            "intent_confidence": intent_confidence,
            "gemini_required": gemini_required,
            "rag_required": rag_required,
            "navigation_required": navigation_required,
            "workspace_required": workspace_required,
            "confidence": confidence,
            "rejected_retrievals": rejected_retrievals or [],
            "rejected_retrieval_count": rejected_retrieval_count,
            "service_calls": {
                "gemini_called": gemini_called_flag,
                "rag_called": rag_called_flag,
                "navigation_called": navigation_called_flag,
                "workspace_called": workspace_called_flag
            },
            "response_strategy": response_strategy
        },
        "context_engine_diagnostics": kwargs.get("context_engine_diagnostics")
    }

async def get_optional_current_student(request: Request) -> Optional[dict]:
    """Helper to decode student payload optionally if Bearer token is provided."""
    import time
    start_time = time.time()
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        if request and hasattr(request, "state"):
            request.state.auth_time = time.time() - start_time
        return None
    token = auth_header.split(" ")[1]
    try:
        from app.auth.jwt_service import JWTService
        from app.core.database import get_database
        from app.student.repository import StudentRepository
        db = get_database()
        payload = JWTService.decode_token(token)
        sub = payload.get("sub")
        role = payload.get("role")
        if role == "student" and sub:
            student_repo = StudentRepository(db)
            student = await student_repo.get_by_id(sub)
            if student and student.get("status") == "active":
                student["_id"] = str(student["_id"])
                if request and hasattr(request, "state"):
                    request.state.auth_time = time.time() - start_time
                return student
    except Exception:
        pass
    if request and hasattr(request, "state"):
        request.state.auth_time = time.time() - start_time
    return None

def format_navigation_chat_history(messages: list) -> str:
    """
    Cleans history messages: removes messages containing failure keywords,
    and formats only previous successful destination/source routes.
    """
    cleaned = []
    failure_keywords = [
        "could not find", 
        "does not exist", 
        "multiple locations match", 
        "which one did you mean", 
        "no route found",
        "invalid",
        "error"
    ]
    for msg in messages:
        content = msg.get("content", "")
        content_lower = content.lower()
        if any(kw in content_lower for kw in failure_keywords):
            continue
        role = msg.get("role", "user")
        cleaned.append(f"{role}: {content}")
    # Return formatted text representing previous successful routing context (last 2 messages)
    return "\n".join(cleaned[-2:])

def generate_grounded_structured_block(nav_ctx) -> str:
    directions_str = "\n".join(f"{i+1}. {d}" for i, d in enumerate(nav_ctx.directions))
    landmarks_str = ", ".join(nav_ctx.landmarks) if nav_ctx.landmarks else "None"
    
    minutes = round(nav_ctx.estimated_time, 1) if nav_ctx.estimated_time else 0
    distance = round(nav_ctx.walking_distance, 1) if nav_ctx.walking_distance else 0
    
    return f"""### Destination
{nav_ctx.destination}

### Walking Time
~{minutes} minutes (distance {distance}m)

### Directions
{directions_str}

### Landmarks
{landmarks_str}"""

def split_mixed_query(query: str) -> tuple[Optional[str], Optional[str]]:
    import re
    # Split query by punctuation and conjunctions
    parts = re.split(r'[.;?]+|\b(?:and|also|as\s+well\s+as)\b', query, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]
    
    fac_part = None
    other_part = None
    
    for part in parts:
        part_intent = classify_intent(part)
        if part_intent == "FacultyDirectory":
            if fac_part:
                fac_part += " and " + part
            else:
                fac_part = part
        else:
            if other_part:
                other_part += " and " + part
            else:
                other_part = part
                
    return fac_part, other_part

@router.post("/chat", dependencies=[Depends(rate_limit_chat)])
async def chat(
    request: ChatRequest,
    raw_request: Request = None,  # type: ignore[assignment]
    current_student: Optional[dict] = Depends(get_optional_current_student)
):
    start_time = time.time()
    try:
        result = await _chat_impl(request, raw_request, current_student)
        
        debug_store = get_debug_store()
        if debug_store and isinstance(result, dict):
            total_time_ms = (time.time() - start_time) * 1000.0
            debug_store.total_time_ms = total_time_ms
            
            other_stages = (
                debug_store.embedding_time_ms +
                debug_store.vector_search_time_ms +
                debug_store.metadata_filtering_time_ms +
                debug_store.cross_encoder_time_ms +
                debug_store.prompt_builder_time_ms +
                debug_store.llm_time_ms
            )
            debug_store.formatting_time_ms = max(0.0, total_time_ms - other_stages)
            
            debug_store.final_answer = result.get("answer") or ""
            
            raw_score = 0.0
            if debug_store.candidates:
                raw_score = debug_store.candidates[0].get("raw_score", 0.0)
            debug_store.confidence = result.get("confidence") or max(0.0, min(1.0, 1.0 - raw_score))
            debug_store.sources_used = list(set(c["source_type"] for c in debug_store.candidates[:3])) if debug_store.candidates else []
            debug_store.fallback_used = "fallback" in str(result.get("type", "")).lower() or result.get("type") == "rag_fallback"
            debug_store.hallucination_warning = debug_store.fallback_used or (not debug_store.candidates)
            
            # Log report
            debug_store.log_report()
            
            # Inject debug payload into diagnostics
            if "diagnostics" not in result or result["diagnostics"] is None:
                result["diagnostics"] = {}
            result["diagnostics"]["debug_rag"] = debug_store.to_dict()
            
            # Save telemetry to database
            try:
                from app.services.telemetry_service import log_ai_request
                student_username = current_student.get("email") if current_student else "Guest"
                await log_ai_request(
                    query=request.message,
                    response=result.get("answer") or "",
                    username=student_username,
                    debug_store=debug_store,
                    status="success"
                )
            except Exception as tel_err:
                logger.error(f"Failed to log telemetry: {tel_err}")
            
        return result
    except Exception as e:
        logger.error(f"Error in chat wrapper: {e}", exc_info=True)
        try:
            from app.services.telemetry_service import log_ai_request
            debug_store = get_debug_store()
            student_username = current_student.get("email") if current_student else "Guest"
            await log_ai_request(
                query=request.message,
                response=str(e),
                username=student_username,
                debug_store=debug_store,
                status="failure",
                error_message=str(e)
            )
        except Exception as tel_err:
            logger.error(f"Failed to log failure telemetry: {tel_err}")
        raise e

async def _chat_impl(
    request: ChatRequest,
    raw_request: Request = None,  # type: ignore[assignment]
    current_student: Optional[dict] = None
):

    try:
        import uuid
        start_time = time.time()
        
        # Get or generate request ID (Requirement 7)
        request_id = None
        if raw_request:
            request_id = raw_request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
            
        result: dict[str, Any] = {}
        metadata: dict[str, Any] | None = None
        prompt_gen_duration = 0.0
        query = request.message.strip()
        original_query = query
        
        # Conversation Context Reference Resolution
        from app.services.context_resolver.resolver import ConversationContextResolver
        resolver = ConversationContextResolver()
        resolved_query, clarification_needed = await resolver.resolve_references(query, request.sessionId)
        
        if clarification_needed:
            result = {
                "type": "text",
                "answer": resolved_query,
                "metadata": {}
            }
            if request.sessionId:
                await add_message_to_history(
                    request.sessionId,
                    "user",
                    original_query
                )
                await add_message_to_history(
                    request.sessionId,
                    "assistant",
                    resolved_query,
                    metadata=result["metadata"]
                )
            set_cached_response(original_query, result)
            return result

        query = resolved_query

        if IS_DEV_MODE:
            logger.info(f"[DEV DEBUG] RAG Trace: Request received with query: '{request.message}'")
            logger.info(f"[DEV DEBUG] RAG Trace: Query normalized: '{query}'")
        validate_chat_query(query)

        # Telemetry Store initialization
        debug_store = init_debug_store()
        if debug_store:
            debug_store.original_query = query

        if not query:
            return {
                "type": "error",
                "answer": "Please enter a valid question."
            }

        auth_time = getattr(raw_request.state if raw_request and hasattr(raw_request, "state") else None, "auth_time", 0.0)

        # Check response cache first
        cached = get_cached_response(original_query)
        if cached:
            if request.sessionId:
                await add_message_to_history(request.sessionId, "user", original_query)
                await add_message_to_history(
                    request.sessionId,
                    "assistant",
                    cached["answer"],
                    message_type=cached.get("type", "text"),
                    metadata=cached.get("metadata")
                )
            cached_response = dict(cached)
            if IS_DEV_MODE:
                cached_response["diagnostics"] = get_diagnostics_payload(
                    total_time=time.time() - start_time,
                    auth_time=auth_time,
                    history_time=0.0,
                    rag_time=0.0,
                    academic_time=0.0,
                    nav_time=0.0,
                    prompt_gen_duration=0.0,
                    gemini_time=0.0,
                    prompt_length=0,
                    estimated_tokens=0,
                    context_chunks=0,
                    history_length=0,
                    context_length=0,
                    intent="cached",
                    circuit_breaker_status="CLOSED",
                    gemini_called=False,
                    fallback_used=False,
                    retry_count=0,
                    cache_hit=True,
                    routing_decision="Cache"
                )
            return cached_response

        # Initialize timing and payload tracking variables
        prompt_length = 0
        estimated_tokens = 0
        prompt_gen_duration = 0.0
        gemini_time = 0.0
        context_chunks = 0
        context_length = 0
        history_length = 0
        nav_time = 0.0
        prompt = ""

        # ==========================================
        # SAVE USER MESSAGE
        # ==========================================
        if request.sessionId:
            print("Saving user message...")
            await add_message_to_history(
                request.sessionId,
                "user",
                original_query
            )

        # Check for mixed-intent queries
        fac_part, other_part = split_mixed_query(query)
        is_mixed = False
        faculty_prefix = ""
        faculty_ids = []
        if fac_part and other_part:
            is_mixed = True
            import re
            # Process the faculty portion first
            stop_words = {
                "who", "teaches", "teaching", "is", "the", "of", "in", "on", 
                "interested", "working", "faculty", "professor", "prof", "dr", 
                "show", "give", "me", "find", "email", "phone", "number", "contact", 
                "xyz", "abc", "about", "list", "members", "member", "department", 
                "works", "here", "are", "look", "for", "search", "details", "info", 
                "information", "please", "can", "you", "tell", "get", "address", 
                "office", "hours", "website", "designation"
            }
            
            # Extract words from fac_part
            fac_part_clean = re.sub(r"[^\w\s]", " ", fac_part)
            fac_words = [w.lower() for w in fac_part_clean.split() if w.lower() not in stop_words]
            
            # Resolve department names/acronyms to normalized names
            DEPT_ACRONYMS = {
                "cse": "Computer Science & Engineering",
                "ece": "Electronics & Communication Engineering",
                "eee": "Electrical & Electronics Engineering",
                "mechanical": "Mechanical Engineering",
                "civil": "Civil & Environmental Engineering",
                "chemical": "Chemical Engineering",
                "chemistry": "Chemistry",
                "physics": "Physics",
                "math": "Mathematics",
                "mathematics": "Mathematics",
                "architecture": "Architecture & Planning",
                "management": "Management",
                "pharmaceutical": "Pharmaceutical Sciences & Technology",
                "production": "Production & Industrial Engineering",
                "biotechnology": "Bioengineering & Biotechnology",
                "quantitative economics": "Center for Quantitative Economics and Data Science",
                "remote sensing": "Remote Sensing",
                "space engineering": "Space Engineering & Rocketry",
                "humanities": "Humanities & Social Sciences"
            }
            
            fac_search_query = " ".join(fac_words).strip()
            
            fac_dept_filter = None
            fac_dept_acronym_matched = None
            for word in fac_part.lower().split():
                clean_w = re.sub(r"[^\w]", "", word)
                if clean_w in DEPT_ACRONYMS:
                    fac_dept_filter = DEPT_ACRONYMS[clean_w]
                    fac_dept_acronym_matched = clean_w
                    break
            
            from app.services.faculty_service import FacultyService
            matching_faculty = []
            
            try:
                # Expand acronyms for search
                fac_search_terms = [fac_search_query] if fac_search_query else [fac_part]
                if fac_search_query.lower() == "nlp":
                    fac_search_terms.append("natural language processing")
                elif fac_search_query.lower() == "ai":
                    fac_search_terms.append("artificial intelligence")
                elif fac_search_query.lower() == "ml":
                    fac_search_terms.append("machine learning")
                elif fac_search_query.lower() == "cv":
                    fac_search_terms.append("computer vision")
                elif fac_search_query.lower() == "dl":
                    fac_search_terms.append("deep learning")
                elif fac_search_query.lower() == "iot":
                    fac_search_terms.append("internet of things")
                
                from app.services.faculty.resolver import FacultyNameResolver
                resolution = FacultyNameResolver.resolve(fac_part, fac_dept_filter, fac_dept_acronym_matched)
                matching_faculty = resolution.get("candidates", [])
                if resolution.get("message"):
                    faculty_prefix = resolution["message"]
            except Exception as e:
                logger.error(f"Error querying FacultyNameResolver in mixed query: {e}")
                matching_faculty = []
            
            # Format Faculty Response
            limit = 5
            if faculty_prefix:
                pass
            elif not matching_faculty:
                faculty_prefix = "I couldn't find any faculty member matching your request."
            else:
                subject = fac_dept_filter or fac_search_query or "your request"
                faculty_prefix = f"I found the following faculty members related to {subject}:\n\n"
                for member in matching_faculty[:limit]:
                    faculty_prefix += f"• **{member['name']}**\n"
                    faculty_prefix += f"  * Designation: {member.get('designation') or 'Faculty Member'}\n"
                    faculty_prefix += f"  * Department: {member.get('department')}\n"
                    if member.get('research_interests'):
                        faculty_prefix += f"  * Research Interests: {', '.join(member['research_interests'])}\n"
                    faculty_prefix += f"  * Email: {member.get('email')}\n"
                    if member.get('phone'):
                        faculty_prefix += f"  * Phone: {member['phone']}\n"
                    if member.get('office'):
                        faculty_prefix += f"  * Office: {member['office']}\n"
                    if member.get('building'):
                        faculty_prefix += f"  * Building: {member['building']}\n"
                    faculty_prefix += "\n"
                
                if len(matching_faculty) > limit:
                    faculty_prefix += f"Showing first {limit} of {len(matching_faculty)} matching faculty members. Let me know if you would like to see more!\n"
            
            faculty_ids = [m["id"] for m in matching_faculty] if matching_faculty else []
            
            # Swap query with other_part for RAG execution
            query = other_part

        # ==========================================
        # INTENT / CONFIDENCE ROUTING DECISION
        # ==========================================
        # Determine intent early
        detected_intent = classify_intent(query)
        selected_service = ROUTING_TABLE.get(detected_intent, "Gemini")
        routing_reason = f"Intent '{detected_intent}' mapped to service '{selected_service}'"
        
        requires_rag = (selected_service in ["Hybrid RAG", "Website Knowledge", "Hybrid Strategy", "Calendar Service", "Workspace Service"]) or (detected_intent in ["AI / ML Concept", "AI / ML Concepts", "Programming Help", "Engineering Concept", "Explanation", "Reasoning", "Comparison", "Summarization"])

        # Legacy intent mapping for selector compatibility
        def map_to_legacy_intent(intent_name: str) -> str:
            mapping = {
                "Navigation": "navigation",
                "Academic Calendar": "academic",
                "Student Dashboard": "academic",
                "Student Workspace": "student_workspace",
                "Workspace": "student_workspace",
                "Greeting": "general",
                "Conversation Follow-up": "general",
                "Campus Information": "rag" if requires_rag else "general",
                "Notice Retrieval": "general",
                "Uploaded Document QA": "rag" if requires_rag else "general",
                "Website QA": "rag" if requires_rag else "general",
                # Educational / conceptual intents → dedicated educational template
                "AI / ML Concept": "educational",
                "AI / ML Concepts": "educational",
                "Programming Help": "educational",
                "Engineering Concept": "educational",
                "Reasoning": "educational",
                "Comparison": "educational",
                "Summarization": "educational",
                "Explanation": "educational",
                "General Academic Concept": "educational",
                "Conversation": "general",
                "Document Question": "general",
                "Website Question": "general",
                "Follow-up Question": "general",
                "FacultyDirectory": "faculty",
                "Unknown": "rag" if requires_rag else "general"
            }
            return mapping.get(intent_name, "general")
            
        intent = map_to_legacy_intent(detected_intent)


        if debug_store:
            debug_store.detected_intent = detected_intent
            debug_store.normalized_query = query.lower()
            from app.services.rag.retriever import detect_intent, get_query_expansions
            debug_store.query_category = detect_intent(query) or "General"
            debug_store.synonyms_expanded = get_query_expansions(query.lower())

        # Gating flags
        gemini_required = (selected_service == "Gemini")
        rag_required = (selected_service in ["Hybrid RAG", "Website Knowledge", "Hybrid Strategy"]) or (detected_intent in ["AI / ML Concept", "AI / ML Concepts", "Programming Help", "Engineering Concept", "Explanation", "Reasoning", "Comparison", "Summarization"])

        navigation_required = (detected_intent == "Navigation")
        workspace_required = (detected_intent in ["Workspace", "Student Dashboard"])
        confidence = 1.0
        rejected_retrievals: list[Any] = []

        # Concurrently fetch and optimize all context using the ContextOrchestrator
        from app.services.context.orchestrator import ContextOrchestrator
        context_orchestrator = ContextOrchestrator()
        
        # We construct an initial routing decision to guide the selector
        from app.services.llm.intent_router import RoutingDecision
        initial_decision = RoutingDecision(
            intent=detected_intent,
            primary_service=selected_service,
            fallback_service="Gemini",
            confidence=1.0,
            reason="Initial classification",
            requires_rag=(selected_service in ["Hybrid RAG", "Website Knowledge", "Hybrid Strategy", "Calendar Service", "Workspace Service"]),
            requires_gemini=(selected_service == "Gemini") or (selected_service in ["Hybrid RAG", "Website Knowledge", "Hybrid Strategy"]),
            requires_navigation=(detected_intent == "Navigation"),
            requires_workspace=(detected_intent in ["Workspace", "Student Dashboard", "Student Workspace"]),
            requires_conversation_memory=True
        )

        nav_req_data = {
            "currentLocationNodeId": request.currentLocationNodeId,
            "currentDestinationNodeId": request.currentDestinationNodeId,
            "accessibilityMode": request.accessibilityMode or False
        }
        
        prompt_context, ctx_diagnostics, package = await context_orchestrator.build_context(
            query=query,
            routing_decision=initial_decision,
            session_id=request.sessionId,
            current_student=current_student,
            nav_request_data=nav_req_data
        )
        if IS_DEV_MODE:
            context_chunks = len(prompt_context.retrieved_chunks)
            context_length = len(prompt_context.context)
            logger.info(f"[DEV DEBUG] RAG Trace: Context built: length={context_length} chars, chunks={context_chunks}.")

        # Extract timing values from diagnostics
        history_time = 0.0
        rag_time = 0.0
        academic_time = 0.0
        nav_time = 0.0
        
        for pd in ctx_diagnostics.provider_diagnostics:
            if pd.provider_id == "conversation":
                history_time = pd.execution_time_s
            elif pd.provider_id == "rag":
                rag_time = pd.execution_time_s
            elif pd.provider_id == "workspace":
                academic_time = pd.execution_time_s
            elif pd.provider_id == "navigation":
                nav_time = pd.execution_time_s

        # Reconstruct rag_result and history list for legacy checks
        rag_result = None
        rag_section = package.get_section("rag")
        if rag_section:
            rag_result = rag_section.metadata.get("rag_result_dict")

        if debug_store:
            debug_store.selected_chunks = prompt_context.retrieved_chunks
            debug_store.duplicate_removal_count = ctx_diagnostics.duplicates_removed
            debug_store.token_count = ctx_diagnostics.total_tokens_after
            debug_store.context_length = len(prompt_context.context)
            if rag_result:
                debug_store.rejected_chunks = rag_result.get("rejected_documents", [])

        history = []
        conversation_section = package.get_section("conversation")
        if conversation_section and conversation_section.items:
            history = conversation_section.items[0].metadata.get("messages", [])
        history_length = len(history)

        nav_ctx = None
        navigation_section = package.get_section("navigation")
        if navigation_section and navigation_section.items:
            from app.schemas.prompt_schema import NavigationContext
            nav_ctx_dict = navigation_section.items[0].metadata.get("nav_ctx_dict")
            if nav_ctx_dict:
                nav_ctx = NavigationContext(**nav_ctx_dict)
        elif package.navigation_data:
            from app.schemas.prompt_schema import NavigationContext
            nav_ctx = NavigationContext(**package.navigation_data)

        # Navigation AI early exit resolution
        if nav_ctx and nav_ctx.validation_status != "valid":
            validation_status = nav_ctx.validation_status
            if validation_status == "ambiguous":
                ambigs = nav_ctx.building_metadata.get("ambiguities", [])
                ans = f"Multiple locations match your query: {', '.join(ambigs)}. Which one did you mean?"
                result_type = "navigation_clarification"
            elif validation_status == "invalid_destination":
                ans = "The destination you requested does not exist on the BIT Mesra campus. If you are looking for academic lectures, check the Lecture Hall Complex (LHC) or department buildings."
                result_type = "navigation_invalid"
            else:
                error_msg = f"Navigation failed: {validation_status.replace('_', ' ')}."
                if validation_status == "no_path":
                    error_msg = f"No pathway exists between {nav_ctx.source} and {nav_ctx.destination} on the campus graph."
                elif validation_status == "invalid_source":
                    error_msg = f"The source location could not be identified."
                ans = error_msg
                result_type = "navigation_error"

            result = {
                "type": result_type,
                "answer": ans
            }
            if validation_status not in ["ambiguous", "invalid_destination"]:
                result["validation_status"] = validation_status

            if request.sessionId:
                await add_message_to_history(request.sessionId, "assistant", ans)
            if IS_DEV_MODE:
                result["diagnostics"] = get_diagnostics_payload(
                    total_time=time.time() - start_time,
                    auth_time=auth_time,
                    history_time=history_time,
                    rag_time=rag_time,
                    academic_time=academic_time,
                    nav_time=nav_time,
                    prompt_gen_duration=0.0,
                    gemini_time=0.0,
                    prompt_length=0,
                    estimated_tokens=0,
                    context_chunks=0,
                    history_length=len(history),
                    context_length=0,
                    intent=intent,
                    context_engine_diagnostics=ctx_diagnostics.dict(),
                )
            return result

        # Resolve the final structured RoutingDecision
        routing_decision = make_routing_decision(query, rag_result, history)
        
        # Initialize tracking variables (must be defined before any early-return bypass)
        fallback_used = False
        retry_count = 0
        gemini_called = False
        circuit_breaker_status = "CLOSED"
        
        # Legacy intent mapping for selector compatibility
        intent = map_to_legacy_intent(routing_decision.intent)
        routing_reason = routing_decision.reason
        gemini_required = routing_decision.requires_gemini
        navigation_required = routing_decision.requires_navigation
        workspace_required = routing_decision.requires_workspace
        confidence = routing_decision.confidence
        rejected_retrievals = []
        if rag_result:
            rejected_retrievals = rag_result.get("rejected_documents", [])
            
        routing_decision_str = "Gemini" if routing_decision.requires_gemini else ("Direct RAG" if routing_decision.primary_service in ["Hybrid RAG", "Website Knowledge", "Calendar Service", "Workspace Service"] else routing_decision.primary_service)

        # Check for Greeting Bypass
        if routing_decision.intent == "Greeting":
            routing_decision_str = "Local Route (Greeting)"
            greeting_ans = "Hello! I am BITATLAS. How can I help you today?"
            result = {
                "type": "greeting",
                "answer": greeting_ans
            }
            if request.sessionId:
                await add_message_to_history(request.sessionId, "assistant", greeting_ans)
            set_cached_response(query, result)
            
            if IS_DEV_MODE:
                result["diagnostics"] = get_diagnostics_payload(
                    total_time=time.time() - start_time,
                    auth_time=auth_time,
                    history_time=history_time,
                    rag_time=rag_time,
                    academic_time=academic_time,
                    nav_time=nav_time,
                    prompt_gen_duration=0.0,
                    gemini_time=0.0,
                    prompt_length=0,
                    estimated_tokens=0,
                    context_chunks=0,
                    history_length=history_length,
                    context_length=0,
                    intent=intent,
                    circuit_breaker_status="CLOSED",
                    gemini_called=False,
                    fallback_used=False,
                    retry_count=0,
                    cache_hit=False,
                    routing_decision=routing_decision_str,
                    detected_intent=routing_decision.intent,
                    selected_service=routing_decision.primary_service,
                    routing_reason=routing_decision.reason,
                    gemini_required=routing_decision.requires_gemini,
                    rag_required=rag_required,
                    navigation_required=routing_decision.requires_navigation,
                    workspace_required=routing_decision.requires_workspace,
                    confidence=routing_decision.confidence,
                    rejected_retrievals=rejected_retrievals,
                    intent_confidence=1.0,
                    fallback_service=routing_decision.fallback_service,
                    gemini_called_flag=False,
                    rag_called_flag=rag_required,
                    navigation_called_flag=False,
                    workspace_called_flag=False,
                    rejected_retrieval_count=len(rejected_retrievals),
                    response_strategy="Local",
                    context_engine_diagnostics=ctx_diagnostics.dict()
                )
            return result

        # Check for Faculty Directory Bypass
        is_faculty_intent = (routing_decision.intent == "FacultyDirectory")
        is_faculty_followup = False
        previous_faculty_ids = []
        last_assistant_msg = None

        if history:
            # Find the last assistant message
            last_assistant_msg = None
            for msg in reversed(history):
                if msg.get("role") == "assistant":
                    last_assistant_msg = msg
                    break
            if last_assistant_msg and last_assistant_msg.get("metadata") and "faculty_ids" in last_assistant_msg["metadata"]:
                previous_faculty_ids = last_assistant_msg["metadata"]["faculty_ids"]
                last_assistant_text = last_assistant_msg.get("content", "")
                is_suggestion = "did you mean" in last_assistant_text.lower() or "which one did you mean" in last_assistant_text.lower()
                is_short_response = len(query.strip().split()) <= 3
                if (routing_decision.intent in ["FacultyDirectory", "Conversation Follow-up"] or
                    (is_suggestion and (is_short_response or routing_decision.intent == "Unknown"))):
                    is_faculty_followup = True
        
        if is_faculty_intent or is_faculty_followup:
            routing_decision_str = "Local Route (Faculty Directory)"
            
            # Start timer
            fac_start_time = time.time()
            
            from app.services.routing.router import FacultyQueryRouter
            router = FacultyQueryRouter()
            res = await router.route_query(
                query=query,
                previous_faculty_ids=previous_faculty_ids,
                last_assistant_msg=last_assistant_msg
            )
            
            answer = res["answer"]
            matching_faculty_ids = res.get("faculty_ids") or []
            
            result = {
                "type": "text",
                "answer": answer,
                "metadata": {
                    "faculty_ids": matching_faculty_ids
                }
            }
            
            if request.sessionId:
                await add_message_to_history(
                    request.sessionId,
                    "assistant",
                    answer,
                    metadata=result["metadata"]
                )
            
            set_cached_response(original_query, result)
            
            fac_duration = time.time() - fac_start_time
            if IS_DEV_MODE:
                result["diagnostics"] = get_diagnostics_payload(
                    total_time=time.time() - start_time,
                    auth_time=auth_time,
                    history_time=history_time,
                    rag_time=rag_time,
                    academic_time=fac_duration,
                    nav_time=nav_time,
                    prompt_gen_duration=0.0,
                    gemini_time=0.0,
                    prompt_length=0,
                    estimated_tokens=0,
                    context_chunks=0,
                    history_length=history_length,
                    context_length=0,
                    intent=intent,
                    circuit_breaker_status="CLOSED",
                    gemini_called=False,
                    fallback_used=False,
                    retry_count=0,
                    cache_hit=False,
                    routing_decision=routing_decision_str,
                    detected_intent=routing_decision.intent,
                    selected_service=routing_decision.primary_service,
                    routing_reason=routing_decision.reason,
                    gemini_required=False,
                    rag_required=False,
                    navigation_required=False,
                    workspace_required=False,
                    confidence=1.0,
                    rejected_retrievals=[],
                    intent_confidence=1.0,
                    fallback_service="Gemini",
                    gemini_called_flag=False,
                    rag_called_flag=False,
                    navigation_called_flag=False,
                    workspace_called_flag=False,
                    rejected_retrieval_count=0,
                    response_strategy="Local",
                    context_engine_diagnostics=ctx_diagnostics.dict()
                )
            return result

        # Check for Campus Navigation Bypass
        if routing_decision.requires_navigation and nav_ctx and nav_ctx.validation_status == "valid" and not is_reasoning_query(query):
            routing_decision_str = "Local Route (Navigation)"
            structured_block = generate_grounded_structured_block(nav_ctx)
            ans = f"Here is the route to {nav_ctx.destination}:\n\n{structured_block}"
            if is_mixed:
                ans = faculty_prefix + "\n\n" + ans
            result = {
                "type": "navigation",
                "answer": ans,
                "navigation_context": nav_ctx.dict() if nav_ctx else None
            }
            if is_mixed:
                result["metadata"] = {"faculty_ids": faculty_ids}
            if request.sessionId:
                metadata = {
                    "cardType": "route" if nav_ctx.source else "place",
                    "title": f"Route to {nav_ctx.destination}" if nav_ctx.source else nav_ctx.destination,
                    "source": nav_ctx.source,
                    "destination": nav_ctx.destination,
                    "distance": nav_ctx.walking_distance,
                    "time": nav_ctx.estimated_time,
                    "directions": nav_ctx.directions or [],
                    "landmarks": nav_ctx.landmarks or [],
                    "actions": ["start_navigation"] if nav_ctx.source else ["navigate"],
                    "navigation_context": nav_ctx.dict()
                }
                if is_mixed:
                    metadata["faculty_ids"] = faculty_ids
                await add_message_to_history(
                    request.sessionId,
                    "assistant",
                    ans,
                    message_type="navigation",
                    metadata=metadata
                )
            set_cached_response(original_query, result)
            
            if IS_DEV_MODE:
                result["diagnostics"] = get_diagnostics_payload(
                    total_time=time.time() - start_time,
                    auth_time=auth_time,
                    history_time=history_time,
                    rag_time=rag_time,
                    academic_time=academic_time,
                    nav_time=nav_time,
                    prompt_gen_duration=0.0,
                    gemini_time=0.0,
                    prompt_length=0,
                    estimated_tokens=0,
                    context_chunks=0,
                    history_length=history_length,
                    context_length=0,
                    intent=intent,
                    circuit_breaker_status="CLOSED",
                    gemini_called=False,
                    fallback_used=False,
                    retry_count=0,
                    cache_hit=False,
                    routing_decision=routing_decision_str,
                    detected_intent=routing_decision.intent,
                    selected_service=routing_decision.primary_service,
                    routing_reason=routing_decision.reason,
                    gemini_required=routing_decision.requires_gemini,
                    rag_required=rag_required,
                    navigation_required=routing_decision.requires_navigation,
                    workspace_required=routing_decision.requires_workspace,
                    confidence=routing_decision.confidence,
                    rejected_retrievals=rejected_retrievals,
                    intent_confidence=1.0,
                    fallback_service=routing_decision.fallback_service,
                    gemini_called_flag=False,
                    rag_called_flag=rag_required,
                    navigation_called_flag=True,
                    workspace_called_flag=False,
                    rejected_retrieval_count=len(rejected_retrievals),
                    response_strategy="Local",
                    context_engine_diagnostics=ctx_diagnostics.dict()
                )
            return result

        # Check for Direct RAG / Local DB Bypasses
        if not routing_decision.requires_gemini:
            routing_decision_str = "Direct RAG"
            ans_content = rag_result["answer"] if rag_result else "I could not find that information in the BITATLAS knowledge base."
            
            from app.services.llm.response_formatter import append_citations_to_response
            from app.services.rag.retriever import get_last_retrieved_docs
            retrieved_docs = get_last_retrieved_docs()
            ans_content = append_citations_to_response(ans_content, retrieved_docs)
            
            if is_mixed:
                ans_content = faculty_prefix + "\n\n" + ans_content
                
            result = {
                "type": "rag",
                "answer": ans_content,
                "source": rag_result.get("source", "rag") if rag_result else "rag",
                "confidence": routing_decision.confidence,
                "navigation_context": nav_ctx.dict() if 'nav_ctx' in locals() and nav_ctx else None
            }
            if is_mixed:
                result["metadata"] = {"faculty_ids": faculty_ids}
            if request.sessionId:
                meta = {"faculty_ids": faculty_ids} if is_mixed else None
                await add_message_to_history(
                    request.sessionId,
                    "assistant",
                    ans_content,
                    metadata=meta
                )
            
            set_cached_response(original_query, result)
            
            if IS_DEV_MODE:
                if rag_result and "documents" in rag_result:
                    context_chunks = len(rag_result["documents"])
                    context_length = sum(len(d) for d in rag_result["documents"])
                result["diagnostics"] = get_diagnostics_payload(
                    total_time=time.time() - start_time,
                    auth_time=auth_time,
                    history_time=history_time,
                    rag_time=rag_time,
                    academic_time=academic_time,
                    nav_time=nav_time,
                    prompt_gen_duration=0.0,
                    gemini_time=0.0,
                    prompt_length=0,
                    estimated_tokens=0,
                    context_chunks=context_chunks,
                    history_length=history_length,
                    context_length=context_length,
                    intent=intent,
                    circuit_breaker_status="CLOSED",
                    gemini_called=False,
                    fallback_used=False,
                    retry_count=0,
                    cache_hit=False,
                    routing_decision=routing_decision_str,
                    detected_intent=routing_decision.intent,
                    selected_service=routing_decision.primary_service,
                    routing_reason=routing_decision.reason,
                    gemini_required=routing_decision.requires_gemini,
                    rag_required=rag_required,
                    navigation_required=routing_decision.requires_navigation,
                    workspace_required=routing_decision.requires_workspace,
                    confidence=routing_decision.confidence,
                    rejected_retrievals=rejected_retrievals,
                    intent_confidence=1.0,
                    fallback_service=routing_decision.fallback_service,
                    gemini_called_flag=False,
                    rag_called_flag=rag_required,
                    navigation_called_flag=False,
                    workspace_called_flag=False,
                    rejected_retrieval_count=len(rejected_retrievals),
                    response_strategy="RAG",
                    context_engine_diagnostics=ctx_diagnostics.dict()
                )
            return result

        # Gemini Context Construction (already built and optimized by the ContextOrchestrator)
        chunks = prompt_context.retrieved_chunks
        context_chunks = len(chunks)
        context_length = len(prompt_context.context)
        history_length = len(history)
        
        prompt_metadata = PromptMetadata(
            intent=intent,
            persona="bit_mesra_assistant",
            version="v1",
            compression_enabled=True,
            hallucination_guard_enabled=True
        )

        # Build orchestrated prompt
        try:
            prompt_assemble_start = time.time()
            orchestrated_schema = prompt_orchestrator.assemble_prompt(prompt_context, prompt_metadata)
            prompt = orchestrated_schema.final_prompt
            if IS_DEV_MODE:
                logger.info(f"[DEV DEBUG] RAG Trace: Prompt built: length={len(prompt)} chars.")
            prompt_gen_duration = time.time() - prompt_assemble_start
            if debug_store:
                debug_store.prompt_builder_time_ms = prompt_gen_duration * 1000.0
                debug_store.system_prompt = orchestrated_schema.final_prompt.split("=== RETRIEVED KNOWLEDGE ===")[0] if "=== RETRIEVED KNOWLEDGE ===" in orchestrated_schema.final_prompt else orchestrated_schema.final_prompt
                debug_store.retrieved_context = prompt_context.context or ""
                debug_store.conversation_memory = "\n".join(f"{msg.get('role')}: {msg.get('content')}" for msg in history)
                debug_store.knowledge_sources = list(set(d.metadata.get("source", "rag") for d in package.get_section("rag").items)) if package.get_section("rag") else []
                debug_store.prompt_length = len(prompt)
                debug_store.estimated_tokens = len(prompt) // 4
        except Exception as orch_exc:
            logger.error(f"Prompt Orchestrator failure: {orch_exc}", exc_info=True)
            from app.services.rag.rag_service import extract_fallback_answer
            answer = extract_fallback_answer(query, chunks)
            
            from app.services.llm.response_formatter import append_citations_to_response
            from app.services.rag.retriever import get_last_retrieved_docs
            retrieved_docs = get_last_retrieved_docs()
            answer = append_citations_to_response(answer, retrieved_docs)
            
            fallback_used = True
            result = {
                "type": "rag_fallback",
                "answer": answer,
                "navigation_context": nav_ctx.dict() if 'nav_ctx' in locals() and nav_ctx else None
            }
            if request.sessionId:
                await add_message_to_history(request.sessionId, "assistant", answer)
            return result

        # Check Circuit Breaker
        circuit_breaker_status = get_circuit_breaker_status()
        
        if circuit_breaker_status == "OPEN":
            logger.warning("Circuit Breaker is OPEN. Executing immediate local fallback.")
            fallback_used = True
            routing_decision_str = "Circuit Breaker OPEN (Local Fallback)"
            from app.services.rag.rag_service import extract_fallback_answer
            answer = extract_fallback_answer(query, chunks)
            
            from app.services.llm.response_formatter import append_citations_to_response
            from app.services.rag.retriever import get_last_retrieved_docs
            retrieved_docs = get_last_retrieved_docs()
            answer = append_citations_to_response(answer, retrieved_docs)
            
            result = {
                "type": "rag_fallback",
                "answer": answer,
                "navigation_context": nav_ctx.dict() if 'nav_ctx' in locals() and nav_ctx else None
            }
            # Message will be saved once at the end of the handler
            pass
        else:
            # Circuit is CLOSED. Call Gemini.
            gemini_called = True
            routing_decision_str = "Gemini"
            gemini_start = time.time()
            try:
                if IS_DEV_MODE:
                    logger.info("[DEV DEBUG] RAG Trace: Gemini called.")
                gemini_raw = generate_response(prompt)
                retry_count = get_last_retry_count()
                answer = clean_gemini_response(gemini_raw)
                
                if IS_DEV_MODE:
                    model_name, usage = get_last_llm_usage()
                    p_tok = usage.prompt_token_count if usage else 0
                    c_tok = usage.candidates_token_count if usage else 0
                    k_sources = list(set(d.metadata.get("source", "rag") for d in package.get_section("rag").items)) if package.get_section("rag") else []
                    logger.info(
                        f"[DEV DEBUG] RAG Trace:\n"
                        f"  Prompt tokens: {p_tok}\n"
                        f"  Completion tokens: {c_tok}\n"
                        f"  Knowledge sources: {k_sources}"
                    )
                
                if debug_store:
                    gemini_time = (time.time() - gemini_start) * 1000.0
                    debug_store.llm_time_ms = gemini_time
                    model_name, usage = get_last_llm_usage()
                    debug_store.llm_model = model_name or "gemini-2.5-flash"
                    debug_store.llm_response_time_ms = gemini_time
                    if usage:
                        debug_store.prompt_tokens = usage.prompt_token_count
                        debug_store.completion_tokens = usage.candidates_token_count
                        debug_store.total_tokens = usage.total_token_count
                    debug_store.generation_latency_ms = gemini_time
                
                # Enforce Grounded Response Fact Checker
                if intent == "navigation" and nav_ctx and nav_ctx.validation_status == "valid":
                    structured_block = generate_grounded_structured_block(nav_ctx)
                    if "### Destination" in answer:
                        parts = answer.split("### Destination")
                        intro = parts[0].strip()
                        answer = f"{intro}\n\n{structured_block}"
                    else:
                        answer = f"{answer.strip()}\n\n{structured_block}"
                        
                from app.services.llm.response_formatter import append_citations_to_response
                from app.services.rag.retriever import get_last_retrieved_docs
                retrieved_docs = get_last_retrieved_docs()
                answer = append_citations_to_response(answer, retrieved_docs)
                
                result = {
                    "type": "gemini",
                    "answer": answer,
                    "navigation_context": nav_ctx.dict() if 'nav_ctx' in locals() and nav_ctx else None
                }
                # Message will be saved once at the end of the handler
                pass
                
                # Cache response
                set_cached_response(original_query, result)
            except Exception as gemini_exc:
                logger.error(f"Gemini API failure, executing local Direct RAG extraction fallback: {gemini_exc}", exc_info=True)
                fallback_used = True
                retry_count = get_last_retry_count()
                from app.services.rag.rag_service import extract_fallback_answer
                # Use intent-aware fallback message so conceptual questions don't get RAG-style error
                _rd = routing_decision if 'routing_decision' in locals() and hasattr(routing_decision, 'intent') else None
                _intent = _rd.intent if _rd else "Unknown"
                _gemini_intents = {"Comparison", "AI / ML Concept", "Engineering Concept", "Programming Help",
                                   "Explanation", "Reasoning", "Summarization", "General Academic Concept"}
                if _intent in _gemini_intents or (chunks is None or len(chunks) == 0):
                    answer = ("I'm currently having trouble reaching the AI service. "
                              "Please try again in a few moments, or rephrase your question.")
                else:
                    answer = extract_fallback_answer(query, chunks)
                    
                from app.services.llm.response_formatter import append_citations_to_response
                from app.services.rag.retriever import get_last_retrieved_docs
                retrieved_docs = get_last_retrieved_docs()
                answer = append_citations_to_response(answer, retrieved_docs)
                
                result = {
                    "type": "rag_fallback",
                    "answer": answer,
                    "navigation_context": nav_ctx.dict() if 'nav_ctx' in locals() and nav_ctx else None
                }
                # Message will be saved once at the end of the handler
                pass
                    
            gemini_time = time.time() - gemini_start

        # Total response time
        total_time = time.time() - start_time
        # Display debugging logs as requested safely
        try:
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
            print(f"Routing Decision: {routing_decision_str}")
            print(f"Gemini Called: {gemini_called}")
            print(f"Context Length: {context_length} chars ({context_chunks} chunks)")
            print(f"History Length: {history_length} messages")

            print("\n========== PERFORMANCE ==========")
            print(f"Response Time: {total_time:.4f}s")
            print(f"RAG Time: {rag_time:.4f}s")
            print(f"Gemini Time: {gemini_time:.4f}s")
            print("=================================\n")

            # Developer Debug Logging to Console (Requirement 6 / Timing diagnostics)
            if IS_DEV_MODE:
                db_latency = history_time + academic_time + nav_time
                print("\n" + "="*50)
                print("DEVELOPER TIMING DIAGNOSTICS")
                print("="*50)
                print(f"Total API Latency:             {total_time:.4f}s")
                print(f"  - Authentication Stage:      {auth_time:.4f}s")
                print(f"  - Chat History Retrieval:    {history_time:.4f}s")
                print(f"  - RAG Context Retrieval:     {rag_time:.4f}s")
                print(f"  - Academic Context Stage:    {academic_time:.4f}s")
                print(f"  - Navigation Resolution:     {nav_time:.4f}s")
                print(f"  - Prompt Assembly Stage:     {prompt_gen_duration:.4f}s")
                print(f"  - Gemini API Latency:        {gemini_time:.4f}s")
                print(f"Cumulative DB Latency:         {db_latency:.4f}s")
                print("-"*50)
                print(f"Prompt Size (chars):           {prompt_length}")
                print(f"Estimated Prompt Tokens:       {estimated_tokens}")
                print(f"Retrieved RAG Chunk Count:     {context_chunks}")
                print(f"Memory Message Count:          {history_length}")
                print(f"Injected Context Size (chars): {context_length}")
                doc_hits = getattr(retriever, "_docs_cache_hits", 0)
                doc_misses = getattr(retriever, "_docs_cache_misses", 0)
                t_hits = prompt_orchestrator.template_loader.hits
                t_misses = prompt_orchestrator.template_loader.misses
                print(f"Chroma Doc Cache Status:       hits={doc_hits}, misses={doc_misses}")
                print(f"Template Cache Status:         hits={t_hits}, misses={t_misses}")
                print("="*50 + "\n")

                # Temporary Debug Logging for RAG
                print("\n" + "="*50)
                print("TEMPORARY RAG PIPELINE TRACE")
                print("="*50)
                print("1. Retrieved Chunks:")
                if 'chunks' in locals() and chunks:
                    for idx, c in enumerate(chunks):
                        print(f"  Chunk {idx+1}: {str(c)[:120]}...")
                elif 'rag_result' in locals() and rag_result and "documents" in rag_result:
                    for idx, c in enumerate(rag_result["documents"]):
                        print(f"  Chunk {idx+1}: {str(c)[:120]}...")
                else:
                    print("  None")
                    
                print("2. Selected Chunks:")
                if 'prompt_context' in locals() and prompt_context and prompt_context.retrieved_chunks:
                    for idx, c in enumerate(prompt_context.retrieved_chunks):
                        print(f"  Selected Chunk {idx+1}: {str(c)[:120]}...")
                else:
                    print("  None")
                    
                print(f"3. Context Length: {context_length} chars")
                print(f"4. Prompt Length: {prompt_length} chars")
                
                print("5. Prompt Preview:")
                if 'prompt' in locals() and prompt:
                    print(prompt[:300] + "\n...")
                else:
                    print("  None")
                    
                print("6. Gemini Request:")
                if 'prompt' in locals() and prompt:
                    print(prompt)
                else:
                    print("  None")
                    
                print("7. Gemini Response:")
                if 'gemini_raw' in locals() and gemini_raw:
                    print(gemini_raw)
                else:
                    print("  None")
                    
                print("8. Parsed Response:")
                if 'answer' in locals() and answer:
                    print(answer)
                else:
                    print("  None")
                    
                print("9. Final Response:")
                if 'result' in locals() and result and "answer" in result:
                    print(result["answer"])
                else:
                    print("  None")
                print("="*50 + "\n")


                print("\n" + "="*50)
                print("INTENT ROUTING DIAGNOSTICS")
                print("="*50)
                print(f"Detected Intent:               {detected_intent}")
                print(f"Selected Service:              {selected_service}")
                print(f"Routing Reason:                {routing_reason}")
                print(f"Gemini Required:               {gemini_required}")
                print(f"RAG Required:                  {rag_required}")
                print(f"Navigation Required:           {navigation_required}")
                print(f"Workspace Required:            {workspace_required}")
                print(f"Confidence:                    {confidence}")
                print(f"Fallback Used:                 {fallback_used}")
                print(f"Rejected Retrievals:           {rejected_retrievals}")
                print("="*50 + "\n")

            # Navigation specific logs (ISSUE 13)
            from app.core.config import ENABLE_NAVIGATION_DEBUG
            if intent == "navigation" and ENABLE_NAVIGATION_DEBUG and 'nav_ctx' in locals() and nav_ctx:
                print("\n==================================================")
                print("NAVIGATION AI DEBUG")
                print("==================================================")
                print(f"Navigation Intent: {'route' if nav_ctx.source else 'search'}")
                print("Entity Extraction:")
                print(f"  Source: {nav_ctx.source or 'None'}")
                print(f"  Destination: {nav_ctx.destination}")
                print("Route Validation:")
                print(f"  Graph Nodes: {nav_ctx.validation_status == 'valid'}")
                print(f"  Distance: {nav_ctx.walking_distance} meters")
                print(f"  Walking Time: {nav_ctx.estimated_time} minutes")
                print(f"Prompt Validation: {orchestrated_schema.validation.is_valid if 'orchestrated_schema' in locals() else 'Passed'}")
                print(f"Prompt Compression: {round(orchestrated_schema.compression_ratio, 2) if 'orchestrated_schema' in locals() else '1.0'}")
                print(f"Navigation Context Validation: {nav_ctx.validation_status}")
                print(f"Gemini Prompt Tokens: {len(prompt) // 4 if 'prompt' in locals() else 0}")
                print(f"Gemini Response Time: {gemini_time:.4f}s")
                print("Prompt Version: v1")
                print("Navigation Template Version: v1")
                print("==================================================\n")

            # Reasoning retrieval diagnostics
            if is_reasoning_query(query):
                sent_docs = []
                _use_gemini = routing_decision.requires_gemini if 'routing_decision' in locals() and hasattr(routing_decision, 'requires_gemini') else True
                if _use_gemini:
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
        except Exception as print_exc:
            logger.warning(f"Failed to print debug output logs in chat handler: {print_exc}")


        if is_mixed and "answer" in result:
            result["answer"] = faculty_prefix + "\n\n" + result["answer"]

        # ==========================================
        # SAVE BOT RESPONSE
        # ==========================================
        if (
            request.sessionId
            and "answer" in result
        ):
            print("Saving assistant response...")
            msg_type = "text"
            metadata = None
            if intent == "navigation" and nav_ctx and nav_ctx.validation_status == "valid":
                msg_type = "navigation"
                if nav_ctx.source:
                    metadata = {
                        "cardType": "route",
                        "title": f"Route to {nav_ctx.destination}",
                        "source": nav_ctx.source,
                        "destination": nav_ctx.destination,
                        "distance": nav_ctx.walking_distance,
                        "time": nav_ctx.estimated_time,
                        "directions": nav_ctx.directions or [],
                        "landmarks": nav_ctx.landmarks or [],
                        "actions": ["start_navigation"],
                        "navigation_context": nav_ctx.dict()
                    }
                else:
                    metadata = {
                        "cardType": "place",
                        "title": nav_ctx.destination,
                        "building": nav_ctx.building_metadata.get("description", "") if nav_ctx.building_metadata else "",  # pylint: disable=no-member
                        "landmarks": nav_ctx.landmarks or [],
                        "facilities": nav_ctx.nearby_facilities or [],
                        "actions": ["navigate"],
                        "navigation_context": nav_ctx.dict()
                    }
            if is_mixed:
                if metadata is None:
                    metadata = {}
                metadata["faculty_ids"] = faculty_ids

            await add_message_to_history(
                request.sessionId,
                "assistant",
                result["answer"],
                message_type=msg_type,
                metadata=metadata
            )

        # Structured Backend Logging (Requirement 7)
        prompt_length = len(prompt) if 'prompt' in locals() and prompt else 0
        estimated_tokens = prompt_length // 4
        prompt_template = intent
        
        logger.info(
            f"[PROMPT LOG] RequestID: {request_id} | UserQuery: '{query}' | "
            f"TemplateSelected: {prompt_template} | PromptGenDuration: {prompt_gen_duration:.4f}s | "
            f"TotalPromptLength: {prompt_length} chars | TokenEstimate: {estimated_tokens} | "
            f"ModelResponseTime: {gemini_time:.4f}s | OverallLatency: {total_time:.4f}s"
        )
        
        # Developer Debug Logging (Requirement 6)
        from app.core.prompt_config import ENABLE_PROMPT_DEBUG
        from app.core.config import GEMINI_MODEL
        if ENABLE_PROMPT_DEBUG and 'prompt' in locals() and prompt:
            context_sources = []
            if rag_result and "documents" in rag_result:
                context_sources = rag_result.get("sources", ["rag"])
            
            import re
            injected_sections = re.findall(r"=== (.*?) ===", prompt)
            
            logger.info(
                f"[PROMPT DEBUG] === DEVELOPER DEBUG MODE ENABLED ===\n"
                f"Selected Prompt Template: {prompt_template}\n"
                f"Injected Prompt Sections: {injected_sections}\n"
                f"Context Sources: {context_sources}\n"
                f"Estimated Prompt Tokens: {estimated_tokens}\n"
                f"Prompt Size: {prompt_length} characters\n"
                f"Generation Time (LLM): {gemini_time:.4f}s\n"
                f"Model Used: {GEMINI_MODEL or 'gemini-3.5-flash'}\n"
                f"=================================================="
            )

        if IS_DEV_MODE:
            result["diagnostics"] = get_diagnostics_payload(
                total_time=total_time,
                auth_time=auth_time,
                history_time=history_time,
                rag_time=rag_time,
                academic_time=academic_time,
                nav_time=nav_time,
                prompt_gen_duration=prompt_gen_duration,
                gemini_time=gemini_time,
                prompt_length=prompt_length,
                estimated_tokens=estimated_tokens,
                context_chunks=context_chunks,
                history_length=history_length,
                context_length=context_length,
                intent=intent,
                circuit_breaker_status=circuit_breaker_status,
                gemini_called=gemini_called,
                fallback_used=fallback_used,
                retry_count=retry_count,
                cache_hit=False,
                routing_decision=routing_decision,
                detected_intent=detected_intent,
                selected_service=selected_service,
                routing_reason=routing_reason,
                gemini_required=gemini_required,
                rag_required=rag_required,
                navigation_required=navigation_required,
                workspace_required=workspace_required,
                confidence=confidence,
                rejected_retrievals=rejected_retrievals,
                context_engine_diagnostics=ctx_diagnostics.dict()
            )

        if is_mixed:
            if "metadata" not in result or result["metadata"] is None:
                result["metadata"] = {}
            result["metadata"]["faculty_ids"] = faculty_ids

        if IS_DEV_MODE:
            logger.info(f"[DEV DEBUG] RAG Trace: Response returned (type={result.get('type')})")
        print("Returning response successfully")
        return result

    except Exception as e:
        logger.error(f"Internal error in chat endpoint: {e}", exc_info=True)
        return {
            "type": "rag_fallback",
            "answer": "I am experiencing temporary technical difficulties. Please try again or ask another question.",
            "diagnostics": {
                "error": type(e).__name__,
                "message": "Internal request processing error occurred"
            } if IS_DEV_MODE else None
        }