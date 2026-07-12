"""
Context Compressor.

Applies adaptive compression to the ContextPackage based on the desired
compression level (LOW, MEDIUM, HIGH, AUTO) or token budget pressure.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from app.services.context.configs.context_config import (
    COMPRESSION_AUTO_THRESHOLD_LOW,
    COMPRESSION_AUTO_THRESHOLD_MEDIUM,
    COMPRESSION_AUTO_THRESHOLD_HIGH,
    COMPRESSION_CONVERSATION_TURNS_HIGH,
    COMPRESSION_CONVERSATION_TURNS_LOW,
    COMPRESSION_CONVERSATION_TURNS_MEDIUM,
    COMPRESSION_RAG_CHUNKS_HIGH,
    COMPRESSION_RAG_CHUNKS_LOW,
    COMPRESSION_RAG_CHUNKS_MEDIUM,
    TOTAL_CONTEXT_TOKEN_LIMIT,
)
from app.services.context.models import (
    CompressionLevel,
    CompressionResult,
    ContextPackage,
)
from app.services.context.utils.tokenizer import estimate_tokens

logger = logging.getLogger("context.compression")


class ContextCompressor:
    """
    Applies text compression strategies to sections of the ContextPackage.
    
    Strategies:
    - Trim conversation history turns.
    - Reduce the number of RAG chunks.
    - Never trims system section.
    """

    def compress(
        self,
        package: ContextPackage,
        requested_level: CompressionLevel = CompressionLevel.AUTO,
    ) -> CompressionResult:
        """
        Compresses the package in-place and returns details.

        Args:
            package: ContextPackage to compress.
            requested_level: Compression level to apply.

        Returns:
            CompressionResult mapping the before/after statistics.
        """
        original_tokens = package.total_tokens
        
        # Determine the target level if AUTO is requested
        level = requested_level
        if requested_level == CompressionLevel.AUTO:
            level = self._determine_auto_level(original_tokens)
            
        logger.info(
            "Compressing context package. Original tokens: %d, Level requested: %s, Applied: %s",
            original_tokens,
            requested_level,
            level,
        )

        if level == CompressionLevel.NONE:
            result = CompressionResult(
                original_tokens=original_tokens,
                final_tokens=original_tokens,
                compression_ratio=1.0,
                level_applied=level,
                sections_affected=[],
            )
            package.compression_level = level
            return result

        sections_affected: List[str] = []

        # 1. Compress Conversation Section
        conv_section = package.get_section("conversation")
        if conv_section and conv_section.items:
            # Determine how many turns to keep
            if level == CompressionLevel.LOW:
                turns_to_keep = COMPRESSION_CONVERSATION_TURNS_LOW
            elif level == CompressionLevel.MEDIUM:
                turns_to_keep = COMPRESSION_CONVERSATION_TURNS_MEDIUM
            else:  # HIGH
                turns_to_keep = COMPRESSION_CONVERSATION_TURNS_HIGH
                
            item = conv_section.items[0]
            raw_messages = item.metadata.get("messages")
            is_navigation = item.metadata.get("is_navigation", False)
            
            if raw_messages:
                # Re-format history with reduced turns
                from app.services.context.providers.conversation_provider import (
                    _format_general_history,
                    _format_navigation_history,
                )
                if is_navigation:
                    new_content = _format_navigation_history(raw_messages, turns_to_keep)
                else:
                    new_content = _format_general_history(raw_messages, turns_to_keep)
                
                if new_content != item.content:
                    item.content = new_content
                    item.token_count = estimate_tokens(new_content)
                    conv_section.total_tokens = sum(i.token_count for i in conv_section.items)
                    sections_affected.append("conversation")
                    logger.debug(
                        "Compressed conversation turns to %d. New token count: %d",
                        turns_to_keep,
                        conv_section.total_tokens,
                    )

        # 2. Compress RAG Section
        rag_section = package.get_section("rag")
        if rag_section and rag_section.items:
            if level == CompressionLevel.LOW:
                chunks_to_keep = COMPRESSION_RAG_CHUNKS_LOW
            elif level == CompressionLevel.MEDIUM:
                chunks_to_keep = COMPRESSION_RAG_CHUNKS_MEDIUM
            else:  # HIGH
                chunks_to_keep = COMPRESSION_RAG_CHUNKS_HIGH

            if len(rag_section.items) > chunks_to_keep:
                # Keep top-N chunks
                original_chunk_count = len(rag_section.items)
                rag_section.items = rag_section.items[:chunks_to_keep]
                rag_section.total_tokens = sum(i.token_count for i in rag_section.items)
                sections_affected.append("rag")
                logger.debug(
                    "Compressed RAG chunks from %d to %d. New token count: %d",
                    original_chunk_count,
                    chunks_to_keep,
                    rag_section.total_tokens,
                )

        # Update package totals
        package.total_tokens = sum(s.total_tokens for s in package.sections)
        package.compression_level = level
        
        final_tokens = package.total_tokens
        ratio = final_tokens / original_tokens if original_tokens > 0 else 1.0

        logger.info(
            "Compression finished. Final tokens: %d, Ratio: %.2f",
            final_tokens,
            ratio,
        )

        return CompressionResult(
            original_tokens=original_tokens,
            final_tokens=final_tokens,
            compression_ratio=ratio,
            level_applied=level,
            sections_affected=sections_affected,
        )

    def _determine_auto_level(self, total_tokens: int) -> CompressionLevel:
        """Determines the appropriate compression level based on token usage."""
        limit = TOTAL_CONTEXT_TOKEN_LIMIT
        if limit <= 0:
            return CompressionLevel.NONE
            
        ratio = total_tokens / limit
        
        if ratio < COMPRESSION_AUTO_THRESHOLD_LOW:
            return CompressionLevel.NONE
        elif ratio < COMPRESSION_AUTO_THRESHOLD_MEDIUM:
            return CompressionLevel.LOW
        elif ratio < COMPRESSION_AUTO_THRESHOLD_HIGH:
            return CompressionLevel.MEDIUM
        else:
            return CompressionLevel.HIGH
