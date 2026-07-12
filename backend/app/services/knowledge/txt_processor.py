import logging

logger = logging.getLogger("txt_processor")

def process_txt(file_content: bytes, filename: str) -> str:
    """
    Decodes plain text file content, performs cleanups, and returns plain text.
    """
    try:
        # Try UTF-8 first
        text = file_content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1
            text = file_content.decode("latin-1")
        except Exception as e:
            logger.error(f"Failed to decode TXT file {filename}: {e}")
            raise ValueError("Unable to decode file content as text. Please ensure it is UTF-8 encoded.")
            
    # Clean whitespace and trailing space
    cleaned_lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in cleaned_lines if line)
