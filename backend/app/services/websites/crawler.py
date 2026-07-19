import logging
from app.services.websites.scraper import download_html
from app.services.websites.validator import validate_url, normalize_url

logger = logging.getLogger("website_crawler")

async def crawl_single_page(url: str, original_url: str = None) -> str:
    """
    Crawls a single URL (depth = 0).
    Validates, normalizes, and downloads the raw HTML contents.
    """
    if not validate_url(url):
        raise ValueError(f"Invalid URL schema: {url}")
        
    normalized = normalize_url(url)
    logger.info(f"Initiating single page crawl for: {normalized}")
    
    html = await download_html(normalized, original_url=original_url)
    return html
