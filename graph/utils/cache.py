import os
import json

MEMORY_DIR = "memory"


def get_cache(key):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    cache_file = os.path.join(MEMORY_DIR, f"{key}_output.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def set_cache(key, value):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    cache_file = os.path.join(MEMORY_DIR, f"{key}_output.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
    print(f"[Cache] Saved output for node '{key}' to {cache_file}") 