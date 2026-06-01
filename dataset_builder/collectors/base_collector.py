from abc import ABC, abstractmethod
import os
import requests
import uuid
import time
from urllib.parse import urlparse

class BaseCollector(ABC):
    def __init__(self, target_folder, max_images=100):
        self.target_folder = target_folder
        self.max_images = max_images
        
        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)

    @abstractmethod
    def search_and_download(self, topic):
        """
        Search for the given topic and download images.
        Should yield tuples of (filepath, source_url) for each downloaded image
        to be used by the metadata logger.
        """
        pass

    def download_image(self, url, source_name):
        """Helper to download a direct image URL."""
        try:
            # Handle headers to prevent basic blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code == 200:
                # Get extension from URL or fallback to jpg
                ext = '.jpg'
                parsed = urlparse(url)
                if '.' in parsed.path.split('/')[-1]:
                    ext = '.' + parsed.path.split('/')[-1].split('.')[-1]
                
                filename = f"{source_name}_{uuid.uuid4().hex[:8]}{ext}"
                filepath = os.path.join(self.target_folder, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return filepath
        except Exception as e:
            print(f"Failed to download {url}: {e}")
        return None
