"""
Scraper for novel listing pages.
"""

import random
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import BASE_URL
from utils.http_utils import fetch_with_retry

def fetch_page(page, data_store):
    """
    Fetch and parse a single page of novel listings.
    
    Args:
        page: Page number to fetch
        data_store: DataStore instance for storing data
        
    Returns:
        List of novel information dictionaries
    """
    url = f"{BASE_URL}{page}/"
    try:
        response = fetch_with_retry(
            url, 
            timeout=10, 
            error_msg=f"Error fetching page {page}"
        )
        
        if not response or response.status_code != 200:
            print(f"Failed to fetch page {page}: Status code {response.status_code if response else 'None'}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        book_items = soup.find_all("div", class_="row", itemscope=True)
        page_novels = []

        for book in book_items:
            title_tag = book.find("h3", class_="truyen-title")
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            link_tag = title_tag.find("a") if title_tag else None
            link = urljoin(url, link_tag["href"]) if link_tag else ""
            
            # Extract author information
            author_tag = book.find("span", class_="author")
            author_name = author_tag.get_text(strip=True).replace("✎ ", "") if author_tag else "Unknown"
            
            # Get or create author
            author_id = data_store.get_author_id(author_name)
            
            # Extract image url
            lazyimg_div = book.find("div", class_="lazyimg")
            image_url = lazyimg_div["data-image"] if lazyimg_div and lazyimg_div.has_attr("data-image") else ""
            
            # Add to page novels for detailed processing
            page_novels.append({
                "title": title,
                "link": link,
                "author_name": author_name,
                "author_id": author_id,
                "image": image_url
            })

        print(f"✅ Page {page} done. {len(page_novels)} books found.")
        
        # Add a small delay to avoid overwhelming the server
        time.sleep(random.uniform(0.1, 0.5))
        
        return page_novels
    
    except Exception as e:
        print(f"❌ Error fetching page {page}: {e}")
        return []