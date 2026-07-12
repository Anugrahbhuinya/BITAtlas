import json
import logging
import re
from typing import Any, Dict

# Keys containing sensitive personal data or secrets to scrub from all logs
SCRUB_KEYS = ["password", "token", "access_token", "refresh_token", "secret", "client_secret", "password_hash"]

class StructuredJsonFormatter(logging.Formatter):
    """
    Structured JSON log formatter for enterprise log parsing.
    Scrubs passwords, secrets, tokens, and personal credentials.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Build base JSON structure
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Include exception traceback if present
        if record.exc_info:
            log_data["traceback"] = self.formatException(record.exc_info)
            
        # Append correlation parameters if registered inside extra
        for key in ["request_id", "client_ip", "user_id", "method", "path", "status_code", "duration_s", "stage", "error"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
                
        # Scrub any potential secrets found in extra attributes
        log_data = self._scrub_dict(log_data)
        return json.dumps(log_data)

    def _scrub_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        scrubbed: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, dict):
                scrubbed[k] = self._scrub_dict(v)
            elif isinstance(v, str):
                # Apply key matching or general regex patterns
                if k.lower() in SCRUB_KEYS:
                    scrubbed[k] = "******"
                else:
                    # Strip out Bearer token strings
                    v_clean = re.sub(r"Bearer\s+[a-zA-Z0-9\._\-]+", "Bearer ******", v)
                    scrubbed[k] = v_clean
            else:
                scrubbed[k] = v
        return scrubbed

def setup_structured_logging(log_level: str = "INFO"):
    """
    Configures the root logging stream to utilize StructuredJsonFormatter.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        
    # Standard output stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(stream_handler)
