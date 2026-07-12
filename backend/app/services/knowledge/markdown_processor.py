import logging
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger("markdown_processor")

def process_markdown(file_content: bytes, filename: str) -> tuple[str, str]:
    """
    Processes markdown file content.
    Returns a tuple of (original_markdown_str, cleaned_plain_text).
    """
    try:
        md_text = file_content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            md_text = file_content.decode("latin-1")
        except Exception as e:
            logger.error(f"Failed to decode markdown file {filename}: {e}")
            raise ValueError("Unable to decode file content as markdown. Please ensure it is UTF-8 encoded.")
            
    try:
        # Convert Markdown to HTML
        html = markdown.markdown(md_text)
        
        # Strip HTML tags using BeautifulSoup to get clean plain text
        soup = BeautifulSoup(html, "html.parser")
        plain_text = soup.get_text()
        
        # Clean extra whitespace
        cleaned_lines = [line.strip() for line in plain_text.splitlines()]
        cleaned_text = "\n".join(line for line in cleaned_lines if line)
        
        return md_text, cleaned_text
    except Exception as e:
        logger.error(f"Error parsing markdown file {filename}: {e}", exc_info=True)
        raise ValueError(f"Failed to parse Markdown document: {str(e)}")
