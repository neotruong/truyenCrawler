"""
Data store for managing scraped data with thread-safe access.
"""

import threading
from datetime import datetime

class DataStore:
    """Thread-safe data store for all scraped entities."""
    
    def __init__(self):
        # Data collections
        self.novels = []
        self.authors = []
        self.categories = []
        self.chapters = []
        self.chapter_contents = []
        self.deleted_images = []
        
        # Lookup dictionaries
        self.author_lookup = {}  # name -> id
        self.category_lookup = {}  # name -> id
        self.novel_lookup = {}  # name -> id
        
        # Thread locks for ID generation
        self.locks = {
            "author": threading.Lock(),
            "category": threading.Lock(),
            "novel": threading.Lock(),
            "chapter": threading.Lock()
        }
    
    def get_timestamp(self):
        """Get current timestamp in proper format for database."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_author_id(self, author_name):
        """Get or create author ID in a thread-safe manner."""
        with self.locks["author"]:
            if author_name not in self.author_lookup:
                author_id = len(self.authors) + 1
                self.author_lookup[author_name] = author_id
                self.authors.append({
                    "id": author_id,
                    "name": author_name,
                    "created_at": self.get_timestamp(),
                    "updated_at": self.get_timestamp(),
                    "deleted_at": None
                })
            return self.author_lookup[author_name]
    
    def get_category_id(self, category_name):
        """Get or create category ID in a thread-safe manner."""
        with self.locks["category"]:
            if category_name not in self.category_lookup:
                category_id = len(self.categories) + 1
                self.category_lookup[category_name] = category_id
                self.categories.append({
                    "id": category_id,
                    "name": category_name,
                    "icon": "",
                    "is_active": True,
                    "created_at": self.get_timestamp(),
                    "updated_at": self.get_timestamp(),
                    "deleted_at": None
                })
            return self.category_lookup[category_name]
    
    def create_novel(self, novel_data):
        """Create a novel entry in a thread-safe manner."""
        with self.locks["novel"]:
            novel_id = len(self.novels) + 1
            self.novel_lookup[novel_data["name"]] = novel_id
            
            novel_entry = {
                "id": novel_id,
                **novel_data
            }
            
            self.novels.append(novel_entry)
            return novel_id
    
    def create_chapter(self, chapter_data):
        """Create a chapter entry in a thread-safe manner."""
        with self.locks["chapter"]:
            chapter_id = len(self.chapters) + 1
            
            chapter_entry = {
                "id": chapter_id,
                **chapter_data
            }
            
            self.chapters.append(chapter_entry)
            return chapter_id
    
    def add_chapter_content(self, content_data):
        """Add chapter content."""
        self.chapter_contents.append(content_data)