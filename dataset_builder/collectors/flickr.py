from dataset_builder.collectors.base_collector import BaseCollector
from playwright.sync_api import sync_playwright
import time
import urllib.parse

class FlickrCollector(BaseCollector):
    def search_and_download(self, topic):
        encoded_topic = urllib.parse.quote(topic)
        search_url = f"https://www.flickr.com/search/?text={encoded_topic}"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            try:
                page.goto(search_url, timeout=60000, wait_until='load')
                time.sleep(3)
            except Exception as e:
                print(f"  Warning: Initial Flickr load failed or timed out: {e}")
            
            image_urls = set()
            max_scrolls = max(20, self.max_images // 3)
            scroll_attempts = 0
            stale_count = 0
            
            while len(image_urls) < self.max_images and scroll_attempts < max_scrolls:
                prev_count = len(image_urls)
                try:
                    images = page.query_selector_all('img')
                    for img in images:
                        src = img.get_attribute('src') or ''
                        if src and 'live.staticflickr.com' in src:
                            # Use the highest res format if possible. Usually removing size suffix like _m.jpg -> _b.jpg
                            # But raw src is usually enough for scraping.
                            image_urls.add(src)
                        
                        if len(image_urls) >= self.max_images:
                            break
                            
                except Exception as e:
                    print(f"  Warning: selector query failed (attempt {scroll_attempts}): {e}")
                    time.sleep(1)

                if len(image_urls) > 0 and len(image_urls) == prev_count:
                    stale_count += 1
                    if stale_count >= 10:
                        print(f"  No new images found after {stale_count} scrolls, stopping.")
                        break
                elif len(image_urls) > prev_count:
                    stale_count = 0
                            
                try:
                    page.evaluate("window.scrollBy(0, 1500)")
                except:
                    pass
                    
                time.sleep(1.5)
                scroll_attempts += 1

            browser.close()

        for url in list(image_urls)[:self.max_images]:
            filepath = self.download_image(url, "flickr")
            if filepath:
                yield filepath, url
