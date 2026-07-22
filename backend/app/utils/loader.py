import json
from pathlib import Path

# Resolve base directories safely across Windows, Linux, and Docker
BASE_DIR = Path(__file__).resolve().parents[3]

def get_data_dir() -> Path:
    candidates = [
        BASE_DIR / "data",
        BASE_DIR / "backend" / "data",
        Path("/app/data"),
        Path("/data"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return BASE_DIR / "data"

DATA_DIR = get_data_dir()

def load_json(relative_path: str):
    data_dir = get_data_dir()
    file_path = data_dir / relative_path

    if not file_path.exists():
        # Secondary fallback attempt if nested in backend/data
        alt_path = BASE_DIR / "backend" / "data" / relative_path
        if alt_path.exists():
            file_path = alt_path

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)