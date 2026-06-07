import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data"

def load_json(relative_path):
    file_path = DATA_DIR / relative_path

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)