"""
HTTP utilities with retry mechanism.
"""

import time
import random
import requests
from config import HEADERS, MAX_RETRIES, RETRY_DELAY

def fetch_with_retry(url, timeout=10, error_msg="Failed to fetch"):
    """
    Fetch URL with automatic retry on failure.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        error_msg: Base error message for logging
        
    Returns:
        Response object on success, None on failure
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            
            # If we get a 503 or other error status, retry
            if response.status_code >= 500:
                wait_time = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
                print(f"{error_msg}: Status code {response.status_code}, retrying in {wait_time:.2f}s (attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait_time)
                continue
                
            # For other status codes, return the response
            return response
            
        except requests.RequestException as e:
            # Exponential backoff
            wait_time = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
            print(f"{error_msg}: {str(e)}, retrying in {wait_time:.2f}s (attempt {attempt+1}/{MAX_RETRIES})")
            time.sleep(wait_time)
    
    # If we've exhausted all retries
    print(f"{error_msg}: All retry attempts failed")
    return None