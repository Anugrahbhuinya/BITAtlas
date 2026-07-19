import logging
import time
import requests
import asyncio
from app.core import config

logger = logging.getLogger("website_scraper")

_session = None

def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session

def _download_html_sync(url: str, timeout: int, max_retries: int, user_agent: str, original_url: str = None) -> str:
    # Check if brotli is available for Accept-Encoding
    try:
        import brotli
        accept_encoding = "gzip, deflate, br"
    except ImportError:
        accept_encoding = "gzip, deflate"
        
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": accept_encoding,
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1"
    }
    
    session = _get_session()
    
    last_err = None
    for attempt in range(max_retries + 1):
        response = None
        exact_failure_reason = "None"
        try:
            logger.info(f"Downloading HTML from {url} (Attempt {attempt + 1}/{max_retries + 1})")
            
            # session.get handles redirects and maintains connection pool
            response = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # Check for client errors that should not be retried
            if response.status_code in (400, 401, 403, 404):
                response.raise_for_status()
                
            response.raise_for_status()
            
            # Prevent downloading excessively large files
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > config.MAX_PAGE_SIZE:
                raise ValueError(f"Content length exceeds limit of {config.MAX_PAGE_SIZE} bytes")
                
            if len(response.content) > config.MAX_PAGE_SIZE:
                raise ValueError(f"Downloaded content exceeds limit of {config.MAX_PAGE_SIZE} bytes")
                
            # Log in development mode only
            if getattr(config, "IS_DEV_MODE", False):
                logger.info(
                    f"[DEV ONLY] Web Ingestion Debug Info:\n"
                    f"  Original URL: {original_url or url}\n"
                    f"  Normalized URL: {url}\n"
                    f"  Final URL: {response.url}\n"
                    f"  Request Headers: {dict(response.request.headers) if response.request is not None else headers}\n"
                    f"  Redirect Count: {len(response.history)}\n"
                    f"  HTTP Status: {response.status_code}\n"
                    f"  Content-Type: {response.headers.get('Content-Type')}\n"
                    f"  Retry Number: {attempt}\n"
                    f"  Failure Reason: {exact_failure_reason}"
                )
                
            return response.text
            
        except requests.HTTPError as e:
            last_err = e
            exact_failure_reason = str(e)
            status_code = e.response.status_code if e.response is not None else None
            
            # Log in development mode on failure
            if getattr(config, "IS_DEV_MODE", False):
                logger.info(
                    f"[DEV ONLY] Web Ingestion Debug Info (HTTPError):\n"
                    f"  Original URL: {original_url or url}\n"
                    f"  Normalized URL: {url}\n"
                    f"  Final URL: {response.url if response is not None else 'N/A'}\n"
                    f"  Request Headers: {dict(response.request.headers) if response is not None and response.request is not None else headers}\n"
                    f"  Redirect Count: {len(response.history) if response is not None else 0}\n"
                    f"  HTTP Status: {status_code if status_code is not None else 'N/A'}\n"
                    f"  Content-Type: {response.headers.get('Content-Type') if response is not None else 'N/A'}\n"
                    f"  Retry Number: {attempt}\n"
                    f"  Failure Reason: {exact_failure_reason}"
                )
                
            if status_code in (400, 401, 403, 404):
                logger.error(f"Client error {status_code} for {url}. Skipping retries.")
                raise e
                
            logger.warning(f"Attempt {attempt + 1} failed for {url} with HTTP {status_code}: {str(e)}")
            
        except requests.RequestException as e:
            last_err = e
            exact_failure_reason = str(e)
            
            # Log in development mode on failure
            if getattr(config, "IS_DEV_MODE", False):
                logger.info(
                    f"[DEV ONLY] Web Ingestion Debug Info (RequestException):\n"
                    f"  Original URL: {original_url or url}\n"
                    f"  Normalized URL: {url}\n"
                    f"  Final URL: N/A\n"
                    f"  Request Headers: {headers}\n"
                    f"  Redirect Count: 0\n"
                    f"  HTTP Status: N/A\n"
                    f"  Content-Type: N/A\n"
                    f"  Retry Number: {attempt}\n"
                    f"  Failure Reason: {exact_failure_reason}"
                )
                
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
            
        except Exception as e:
            last_err = e
            exact_failure_reason = str(e)
            
            # Log in development mode on failure
            if getattr(config, "IS_DEV_MODE", False):
                logger.info(
                    f"[DEV ONLY] Web Ingestion Debug Info (Exception):\n"
                    f"  Original URL: {original_url or url}\n"
                    f"  Normalized URL: {url}\n"
                    f"  Final URL: N/A\n"
                    f"  Request Headers: {headers}\n"
                    f"  Redirect Count: 0\n"
                    f"  HTTP Status: N/A\n"
                    f"  Content-Type: N/A\n"
                    f"  Retry Number: {attempt}\n"
                    f"  Failure Reason: {exact_failure_reason}"
                )
            raise e
            
        if attempt < max_retries:
            backoff_time = (2 ** attempt)
            logger.info(f"Retrying in {backoff_time}s...")
            time.sleep(backoff_time)
            
    raise last_err or requests.RequestException("Scraping failed after retries")

async def download_html(url: str, original_url: str = None) -> str:
    """
    Asynchronously downloads HTML content from a URL.
    Delegates block-based HTTP operations to a background worker thread.
    """
    timeout = getattr(config, "REQUEST_TIMEOUT", 10)
    max_retries = getattr(config, "MAX_RETRIES", 3)
    user_agent = getattr(config, "USER_AGENT", "Mozilla/5.0")
    
    return await asyncio.to_thread(
        _download_html_sync,
        url,
        timeout,
        max_retries,
        user_agent,
        original_url
    )
