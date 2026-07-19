import re
from app.services.faculty.constants import HONORIFIC_REGEX, PUNCTUATION_REGEX

def normalize_name(name: str) -> str:
    """
    Normalizes a name string by converting to lowercase, removing punctuation,
    stripping common honorifics, and collapsing multiple spaces.
    """
    if not name:
        return ""
    # Lowercase
    n = name.lower()
    # Remove honorifics
    n = HONORIFIC_REGEX.sub(" ", n)
    # Remove punctuation
    n = PUNCTUATION_REGEX.sub(" ", n)
    # Collapse multiple spaces
    n = " ".join(n.split())
    return n
