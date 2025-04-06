#!/usr/bin/env python3
"""
Main entry point for the novel scraper.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    MAX_PAGES, MAX_WORKERS_PAGES, MAX_WORKERS_NOVELS, 
    OUTPUT_DIR
)
from data_store import DataStore
from scrapers.page_scraper import fetch_page
from scrapers.novel_scraper import fetch_novel_details
from utils.file_utils import save_data_to_json

def main():
    """Main function to scrape all novels and their details with enhanced parallelism."""
    # Initialize data store
    data_store = DataStore()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    start_time = time.time()
    print(f"Starting to scrape {MAX_PAGES} pages with parallel processing...")
    
    # Step 1: Fetch novel listings from all pages in parallel
    all_novels = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_PAGES) as executor:
        future_to_page = {executor.submit(fetch_page, page, data_store): page for page in range(1, MAX_PAGES + 1)}
        for future in as_completed(future_to_page):
            all_novels.extend(future.result())
    
    print(f"Found {len(all_novels)} novels across {MAX_PAGES} pages")
    
    # Step 2: Fetch details for each novel in parallel
    novel_sample = all_novels[:30]  # Sample size
    total_novels = len(novel_sample)
    
    print(f"Fetching details for {total_novels} novels in parallel...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_NOVELS) as executor:
        novel_futures = {
            executor.submit(fetch_novel_details, novel, idx, total_novels, data_store): idx 
            for idx, novel in enumerate(novel_sample, 1)
        }
        
        for future in as_completed(novel_futures):
            # Result processing handled within fetch_novel_details
            pass
    
    # Step 3: Save all data to JSON files
    save_data_to_json(data_store)
    
    elapsed_time = time.time() - start_time
    print(f"🎉 Scraping completed in {elapsed_time:.2f} seconds!")
    print(f"  - Novels: {len(data_store.novels)}")
    print(f"  - Authors: {len(data_store.authors)}")
    print(f"  - Categories: {len(data_store.categories)}")
    print(f"  - Chapters: {len(data_store.chapters)}")
    print(f"  - Chapter contents: {len(data_store.chapter_contents)}")

if __name__ == "__main__":
    main()