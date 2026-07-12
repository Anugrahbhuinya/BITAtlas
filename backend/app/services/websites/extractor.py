import logging
import os
import uuid
from typing import List, Tuple
from bs4 import BeautifulSoup, Comment

logger = logging.getLogger("website_extractor")

def extract_clean_text(html_content: str) -> str:
    """
    Extracts semantic content from raw HTML source code.
    1. Removes only boilerplate tags (script, style, noscript, svg, iframe).
    2. Tries to extract text blocks from semantic containers (article, main, section).
    3. Falls back to body if semantic containers are empty or missing.
    4. Filters duplicate consecutive lines and lines shorter than 3 chars (unless headings).
    5. Logs metrics and writes debug files on failure.
    """
    if not html_content or not html_content.strip():
        return ""

    # 1. Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    dom_elements_count = len(soup.find_all(True))
    html_size = len(html_content)

    # 2. Strip comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    # Remove ONLY true boilerplate elements
    boilerplate_tags = ["script", "style", "noscript", "svg", "iframe"]
    for tag in soup.find_all(boilerplate_tags):
        tag.extract()

    # Recursive element walking utility
    def walk(node, lines):
        if node.name is None:
            # Text Node (NavigableString)
            text = node.strip()
            if text:
                lines.append((text, False))
            return

        # Handle headings (always kept)
        if node.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            text = node.get_text(strip=True)
            if text:
                lines.append((text, True))
            return  # Prevent nested/duplicate child traversal

        # Handle other standard semantic elements
        if node.name in ("p", "li", "td", "th"):
            text = node.get_text(strip=True)
            if text:
                lines.append((text, False))
            return  # Prevent nested/duplicate child traversal

        # Handle table rows for formatting
        if node.name == "tr":
            cells = [c.get_text(strip=True) for c in node.find_all(["td", "th"], recursive=False)]
            if cells:
                text = " | ".join(c for c in cells if c)
                if text:
                    lines.append((text, False))
            return  # Prevent nested child traversal

        # Handle divs: extract if no block children, otherwise recurse
        if node.name == "div":
            has_block_children = any(
                child.name in ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "div")
                for child in node.descendants if child.name is not None
            )
            if not has_block_children:
                text = node.get_text(strip=True)
                if text:
                    lines.append((text, False))
                return
            else:
                for child in node.children:
                    walk(child, lines)
                return

        # Recurse for structural container wrappers (body, main, section, article, table, tr, span, formatting)
        for child in node.children:
            walk(child, lines)

    # 3. Locate top-level semantic containers: article, main, section
    all_containers = soup.find_all(["article", "main", "section"])
    top_containers = []
    for c in all_containers:
        # Keep only containers that do not have parents in the same containers list (no nested duplication)
        has_ancestor = False
        parent = c.parent
        while parent is not None:
            if parent in all_containers:
                has_ancestor = True
                break
            parent = parent.parent
        if not has_ancestor:
            top_containers.append(c)

    raw_lines: List[Tuple[str, str]] = []
    if top_containers:
        logger.info(f"Found {len(top_containers)} top-level semantic containers. Extracting.")
        for container in top_containers:
            walk(container, raw_lines)

    # Check if we successfully extracted text from containers
    container_text = "".join(t for t, _ in raw_lines).strip()

    # 4. Fall back to entire body if no text is in semantic containers
    if not top_containers or not container_text:
        logger.info("Semantic containers empty or absent. Falling back to body.")
        raw_lines = []
        body_node = soup.body or soup
        walk(body_node, raw_lines)

    # 5. Clean, normalize, and filter lines
    cleaned_lines = []
    last_line = None
    for text, is_heading in raw_lines:
        # Normalize internal whitespace
        normalized = " ".join(text.split())
        
        # Skip empty lines
        if not normalized:
            continue
            
        # Ignore lines shorter than 3 characters unless they are headings
        if not is_heading and len(normalized) < 3:
            continue
            
        # Remove duplicate consecutive lines
        if normalized == last_line:
            continue

        cleaned_lines.append(normalized)
        last_line = normalized

    final_text = "\n".join(cleaned_lines).strip()
    
    # Calculate word count of final output text
    words = final_text.split()
    word_count = len(words)

    # Log required telemetry stats
    logger.info(
        f"HTML Ingestion Inbound Stats: "
        f"HTML size={html_size} chars, "
        f"DOM elements scanned={dom_elements_count}, "
        f"Extracted text blocks={len(cleaned_lines)}, "
        f"Final word count={word_count}"
    )

    # 6. Save debug file before returning empty text
    if not final_text:
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            debug_dir = os.path.join(backend_dir, "debug_extraction")
            os.makedirs(debug_dir, exist_ok=True)
            debug_file = os.path.join(debug_dir, f"extract_debug_empty_{uuid.uuid4().hex[:8]}.txt")
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write("=== RAW HTML CONTENT ===\n")
                f.write(html_content)
                f.write("\n\n=== EXTRACTED RAW LINES ===\n")
                f.write("\n".join(f"[Heading={is_h}] {t}" for t, is_h in raw_lines))
            logger.warning(f"No extractable body text found. Saved extraction debug file to: {debug_file}")
        except Exception as e:
            logger.error(f"Failed to write extraction debug file: {e}")

    return final_text
