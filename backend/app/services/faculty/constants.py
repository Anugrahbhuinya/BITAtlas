import re

# Similarity confidence thresholds (on 0-100 scale)
THRESHOLD_HIGH = 90.0
THRESHOLD_MEDIUM = 70.0
THRESHOLD_LOW = 50.0

# Tie-break delta (if best fuzzy match scores are within this delta, ask user to clarify)
TIE_BREAK_DELTA = 2.0

# Query Normalization Regexes
HONORIFIC_REGEX = re.compile(r"\b(?:dr|prof|professor)\b\.?", re.IGNORECASE)
PUNCTUATION_REGEX = re.compile(r"[^\w\s]")
