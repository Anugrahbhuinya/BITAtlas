"""
Smart Context Engine.

Designed to select, organize, optimize, and inject context for the prompt builder.
"""

from app.services.context.models import ContextPackage, PipelineDiagnostics
from app.services.context.orchestrator import ContextOrchestrator

__all__ = [
    "ContextOrchestrator",
    "ContextPackage",
    "PipelineDiagnostics",
]
