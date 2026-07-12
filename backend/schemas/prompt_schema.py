from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class NavigationContext(BaseModel):
    source: Optional[str] = None
    destination: str
    walking_distance: Optional[float] = None
    estimated_time: Optional[float] = None
    directions: List[str] = Field(default_factory=list)
    landmarks: List[str] = Field(default_factory=list)
    nearby_facilities: List[str] = Field(default_factory=list)
    graph_path: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    accessibility_mode: bool = False
    building_metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_status: str = "valid"  # "valid", "invalid_source", "invalid_destination", "no_path", etc.

class PromptContext(BaseModel):
    """
    Structured context for compiling prompt templates.
    Contains user inputs, student info, RAG documents, memories, etc.
    """
    question: str
    context: Optional[str] = ""  # Concatenated RAG content
    history: Optional[str] = ""  # Formatted chat history
    academic_context: Optional[str] = ""  # Structured academic/location details
    student_name: Optional[str] = "Student"
    department: Optional[str] = ""
    semester: Optional[str] = ""
    cgpa: Optional[str] = ""
    attendance: Optional[str] = ""
    today: Optional[str] = ""
    retrieved_chunks: List[str] = Field(default_factory=list)
    conversation_summary: Optional[str] = ""
    additional_variables: Dict[str, Any] = Field(default_factory=dict)
    navigation_context: Optional[NavigationContext] = None

class PromptMetadata(BaseModel):
    """
    Metadata config for selecting and optimizing the prompt templates.
    """
    intent: str = "general"
    persona: str = "bit_mesra_assistant"
    version: str = "v1"
    compression_enabled: bool = True
    hallucination_guard_enabled: bool = True

class PromptValidationResult(BaseModel):
    """
    Validation results checking prompt structure and token usage constraints.
    """
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class PromptSchema(BaseModel):
    """
    The final assembled output returned by the PromptOrchestrator.
    Consumed by Gemini or any downstream LLM service.
    """
    final_prompt: str
    context: PromptContext
    metadata: PromptMetadata
    validation: PromptValidationResult
    original_length: int = 0
    final_length: int = 0
    compression_ratio: float = 1.0
