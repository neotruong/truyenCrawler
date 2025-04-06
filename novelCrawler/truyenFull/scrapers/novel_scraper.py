"""
Scraper for novel details and chapters.
"""

import random
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import MAX_WORKERS_CHAPTERS, MAX_CHAPTERS_PER_NOVEL
from utils.http_utils import fetch_with_retry
from scrapers.chapter_scraper import fetch_chapter_content

def fetch_novel_details(novel_info, index, total, data_store):
    """
    Fetch detailed information for a single novel.
    
    Args:
        novel_info: Dictionary with basic novel information
        index: Current novel index (for progress reporting)
        total: Total number of novels (for progress reporting)
        data_store: DataStore instance for storing data
        
    Returns:
        Novel entry dictionary on success, None on failure
    """
    title = novel_info["title"]
    url = novel_info["link"]
    
    try:
        print(f"Fetching details for {title} ({index}/{total})...")
        
        # Random delay to avoid getting blocked
        time.sleep(random.uniform(0.3, 0.7))
        
        response = fetch_with_retry(
            url, 
            timeout=15, 
            error_msg=f"Error fetching details for novel {title}"
        )
        
        if not response or response.status_code != 200:
            print(f"Failed to fetch details for {title}: Status code {response.status_code if response else 'None'}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Get description
        desc_div = soup.find("div", class_="desc-text")
        description = desc_div.get_text(strip=True) if desc_div else ""
        
        # Get categories/genres
        genre_tags = soup.find_all("a", itemprop="genre")
        novel_categories = []
        
        for tag in genre_tags:
            category_name = tag.get_text(strip=True)
            category_id = data_store.get_category_id(category_name)
            novel_categories.append(category_id)
        
        # Get ratings/views/likes if available
        ratings_span = soup.find("span", itemprop="ratingValue")
        ratings = float(ratings_span.get_text(strip=True)) if ratings_span else 0
        
        # Views and likes would need specific selectors, using placeholders
        views = random.randint(100, 10000)  # Placeholder
        likes = random.randint(10, 1000)  # Placeholder
        
        # Status
        status_span = soup.find("span", class_="text-success")
        status = status_span.get_text(strip=True) if status_span else "Unknown"
        
        # Create novel entry
        timestamp = data_store.get_timestamp()
        novel_data = {
            "name": title,
            "description": description,
            "views": views,
            "likes": likes,
            "ratings": ratings,
            "status": status,
            "image": novel_info["image"],
            "author_id": novel_info["author_id"],
            "category_id": novel_categories[0] if novel_categories else None,
            "created_at": timestamp,
            "updated_at": timestamp,
            "deleted_at": None
        }
        
        novel_id = data_store.create_novel(novel_data)
        
        # Get chapter list
        chapter_list_div = soup.find("div", id="list-chapter")
        chapter_links = chapter_list_div.select("ul.list-chapter a") if chapter_list_div else []
        
        # Limit chapters to process
        chapter_links = chapter_links[:MAX_CHAPTERS_PER_NOVEL]
        
        # Create chapter entries
        chapter_data = []
        for idx, ch_link in enumerate(chapter_links):
            chapter_title = ch_link.get_text(strip=True)
            chapter_url = urljoin(url, ch_link["href"])
            
            # Create chapter entry
            chapter_info = {
                "name": chapter_title,
                "sort_order": float(idx + 1),  # Convert to float as per schema
                "novel_id": novel_id,
                "created_at": timestamp,
                "updated_at": timestamp,
                "deleted_at": None
            }
            
            chapter_id = data_store.create_chapter(chapter_info)
            
            # Create info for content fetching
            chapter_data.append({
                "id": chapter_id,
                "name": chapter_title,
                "url": chapter_url
            })
        
        # Fetch chapter contents in parallel
        chapter_futures = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_CHAPTERS) as executor:
            chapter_futures = {
                executor.submit(fetch_chapter_content, chapter, title, data_store): chapter["id"] 
                for chapter in chapter_data
            }
            
            for future in as_completed(chapter_futures):
                # Processing handled in fetch_chapter_content
                pass
        
        print(f"✅ Completed novel: {title} with {len(chapter_data)} chapters")
        return novel_data
    
    except Exception as e:
        print(f"❌ Error fetching details for {title}: {e}")
        return None