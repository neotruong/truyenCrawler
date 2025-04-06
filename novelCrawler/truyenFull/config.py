"""
Configuration settings for the novel scraper.
"""

# Base URL
BASE_URL = "https://truyenfull.vision/danh-sach/truyen-hot/trang-"

# HTTP Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Scraping limits
MAX_PAGES = 1  # Number of pages to scrape
MAX_WORKERS_PAGES = 10  # Workers for page scraping
MAX_WORKERS_NOVELS = 1  # Workers for novel details
MAX_WORKERS_CHAPTERS = 5  # Workers for chapter content
MAX_CHAPTERS_PER_NOVEL = 5  # Maximum chapters to scrape per novel

# Retry settings
MAX_RETRIES = 3  # Maximum number of retry attempts
RETRY_DELAY = 2  # Base delay between retries in seconds

# Output directory
OUTPUT_DIR = "scraped_data"