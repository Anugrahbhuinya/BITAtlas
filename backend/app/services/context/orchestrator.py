"""
Context Orchestrator.

The main coordinator of the Smart Context Engine. Serves as the single entrypoint
for chat.py, executing the context pipeline and returning legacy-compatible
PromptContext alongside execution diagnostics.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple, Any

from app.schemas.prompt_schema import PromptContext
from app.services.context.injector import ContextInjector
from app.services.context.models import ContextRequest, PipelineDiagnostics, ContextPackage
from app.services.context.pipeline import ContextPipeline

logger = logging.getLogger("context.orchestrator")


class ContextOrchestrator:
    """
    Coordinates context selection, retrieval, optimization, and injection.
    """

    def __init__(self) -> None:
        self.pipeline = ContextPipeline()
        self.injector = ContextInjector()

    async def build_context(
        self,
        query: str,
        routing_decision: Any,  # accepts app.services.llm.intent_router.RoutingDecision
        session_id: Optional[str] = None,
        current_student: Optional[dict] = None,
        nav_request_data: Optional[dict] = None,
    ) -> Tuple[PromptContext, PipelineDiagnostics, ContextPackage]:
        """
        Runs the context pipeline and returns the enriched PromptContext, diagnostics, and package.

        Args:
            query:            Raw user query.
            routing_decision: Intent routing output containing intent and resource requirements.
            session_id:       Active session ID (for history/memory).
            current_student:  Authenticated student dictionary (from JWT).
            nav_request_data: Navigation parameters (source, destination node IDs, accessibility).

        Returns:
            Tuple of (PromptContext, PipelineDiagnostics, ContextPackage).
        """
        logger.info(
            "Orchestrator building context: query='%s', intent='%s'",
            query,
            routing_decision.intent if routing_decision else "Unknown",
        )

        nav_data = nav_request_data or {}
        
        # Translate RoutingDecision into ContextRequest requirements
        requires_rag = routing_decision.requires_rag if routing_decision else False
        requires_navigation = routing_decision.requires_navigation if routing_decision else False
        requires_workspace = routing_decision.requires_workspace if routing_decision else False
        requires_conversation = routing_decision.requires_conversation_memory if routing_decision else True
        routing_confidence = routing_decision.confidence if routing_decision else 1.0
        intent = routing_decision.intent if routing_decision else "general"

        # Map to legacy intent string expected by selector
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
                "Unknown": "rag" if requires_rag else "general"
            }
            return mapping.get(intent_name, "general")


        legacy_intent = map_to_legacy_intent(intent)

        # Pre-fetch history if required to save redundant calls in conversation provider
        history_list = None
        if requires_conversation and session_id:
            try:
                from app.services.history_service import get_chat_history
                history_list = await get_chat_history(session_id)
            except Exception as e:
                logger.error("Failed to pre-fetch history: %s", e)

        request = ContextRequest(
            query=query,
            intent=legacy_intent,
            session_id=session_id,
            current_student=current_student,
            routing_confidence=routing_confidence,
            requires_rag=requires_rag,
            requires_navigation=requires_navigation,
            requires_workspace=requires_workspace,
            requires_conversation=requires_conversation,
            current_location_node_id=nav_data.get("currentLocationNodeId"),
            current_dest_node_id=nav_data.get("currentDestinationNodeId"),
            accessibility_mode=nav_data.get("accessibilityMode", False),
            history=history_list,
        )

        # Execute pipeline
        package, diagnostics = await self.pipeline.execute(request)

        # Inject package into PromptContext
        prompt_context = self.injector.inject(package, query)

        return prompt_context, diagnostics, package
