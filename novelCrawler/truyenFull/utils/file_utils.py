"""
File utilities for saving data.
"""

import os
import json
from config import OUTPUT_DIR

def save_data_to_json(data_store):
    """Save all data structures to JSON files."""
    data_files = {
        "novels.json": data_store.novels,
        "authors.json": data_store.authors,
        "categories.json": data_store.categories,
        "chapters.json": data_store.chapters,
        "chapter_contents.json": data_store.chapter_contents
    }
    
    for filename, data in data_files.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {filepath}")