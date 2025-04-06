"""
Scraper for chapter content.
"""

import random
import time
from bs4 import BeautifulSoup

from utils.http_utils import fetch_with_retry

def fetch_chapter_content(chapter_info, novel_name, data_store):
    """
    Fetch content for a single chapter.
    
    Args:
        chapter_info: Dictionary with chapter information
        novel_name: Novel name (for logging)
        data_store: DataStore instance for storing data
        
    Returns:
        Chapter content dictionary on success, None on failure
    """
    chapter_id = chapter_info["id"]
    chapter_url = chapter_info["url"]
    chapter_title = chapter_info["name"]
    
    try:
        # Add small random delay
        time.sleep(random.uniform(0.2, 0.5))
        
        response = fetch_with_retry(
            chapter_url, 
            timeout=10, 
            error_msg=f"Error fetching chapter {chapter_title}"
        )
        
        if not response or response.status_code != 200:
            print(f"  ✗ Failed to fetch chapter: {chapter_title} - Status: {response.status_code if response else 'None'}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", id="chapter-c")
        content = content_div.get_text(strip=True) if content_div else "Content not available"
        
        chapter_content = {
            "chap_id": chapter_id,
            "content": content[:50000]  # Limit content size for demo
        }
        
        data_store.add_chapter_content(chapter_content)
        
        print(f"  ✓ Fetched chapter: {chapter_title} for {novel_name}")
        return chapter_content
    
    except Exception as e:
        print(f"  ✗ Error fetching chapter {chapter_title}: {e}")
        return None