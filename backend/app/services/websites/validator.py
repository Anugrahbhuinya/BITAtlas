import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Validates if a URL is well-formed and has HTTP/HTTPS protocol.
    """
    if not url:
        return False
    try:
        parsed = urlparse(url.strip())
        # Scheme must be http or https
        if parsed.scheme not in ("http", "https"):
            return False
        # Netloc (domain/host) must be present
        if not parsed.netloc:
            return False
        # Basic check for domain names (no spaces or invalid characters)
        host = parsed.netloc.split(':')[0]
        if not host or not re.match(r'^[a-zA-Z0-9.-]+$', host):
            return False
        return True
    except Exception:
        return False

def normalize_url(url: str) -> str:
    """
    Normalizes a URL to ensure consistency (e.g. lowercasing scheme/host,
    stripping trailing slashes from path, etc.).
    """
    if not url:
        return ""
    parsed = urlparse(url.strip())
    
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    
    # Strip trailing slash from path, unless path is empty or just "/"
    if path.endswith('/') and len(path) > 1:
        path = path.rstrip('/')
    elif not path:
        path = '/'
        
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    
    return f"{scheme}://{netloc}{path}{query}{fragment}"
