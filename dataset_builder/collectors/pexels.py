import time
from playwright.sync_api import sync_playwright
from .base_collector import BaseCollector

class PexelsCollector(BaseCollector):
    def search_and_download(self, topic):
        print(f"Starting Pexels collector for topic: {topic}")
        downloaded = 0
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            search_url = f"https://www.pexels.com/search/{topic.replace(' ', '%20')}/"
            try:
                page.goto(search_url, timeout=60000)
                page.wait_for_load_state('domcontentloaded')
                time.sleep(3)
                
                # HITL: Wait for manual CAPTCHA solving if Cloudflare intercepts
                for _ in range(30): # Wait up to 60 seconds
                    title = page.title().lower()
                    if "just a moment" in title or "attention required" in title or "security" in title or "cloudflare" in title:
                        print(f"[{topic}] CAPTCHA detected on Pexels! Please solve it in the popped-up browser window...")
                        time.sleep(2)
                    else:
                        break
                        
            except Exception as e:
                print(f"Failed to load Pexels for {topic}: {e}")
                browser.close()
                return

            image_urls = set()
            max_scrolls = max(20, self.max_images // 3)
            scroll_attempts = 0
            stale_count = 0
            while len(image_urls) < self.max_images and scroll_attempts < max_scrolls:
                prev_count = len(image_urls)
                images = page.query_selector_all('img')
                for img in images:
                    src = img.get_attribute('src') or ''
                    srcset = img.get_attribute('srcset') or ''
                    data_src = img.get_attribute('data-src') or ''
                    
                    # Pexels photo URLs contain images.pexels.com/photos
                    for candidate in [src, data_src]:
                        if 'images.pexels.com/photos' in candidate:
                            # Request high-res: set w=1260
                            base = candidate.split('?')[0]
                            clean_url = f"{base}?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
                            image_urls.add(clean_url)
                            break
                    
                    # Also check srcset for pexels URLs
                    if 'images.pexels.com/photos' in srcset:
                        parts = srcset.split(',')
                        for part in parts:
                            url_part = part.strip().split(' ')[0]
                            if 'images.pexels.com/photos' in url_part:
                                base = url_part.split('?')[0]
                                clean_url = f"{base}?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
                                image_urls.add(clean_url)
                                break
                        
                    if len(image_urls) >= self.max_images:
                        break

                if len(image_urls) > 0 and len(image_urls) == prev_count:
                    stale_count += 1
                    if stale_count >= 10:
                        print(f"  No new images found after {stale_count} scrolls, stopping.")
                        break
                elif len(image_urls) > prev_count:
                    stale_count = 0
                            
                page.evaluate("window.scrollBy(0, 1500)")
                time.sleep(1.5)
                scroll_attempts += 1
            
            browser.close()

        print(f"Found {len(image_urls)} image URLs on Pexels.")
        
        for url in list(image_urls)[:self.max_images]:
            filepath = self.download_image(url, "pexels")
            if filepath:
                downloaded += 1
                yield filepath, url

        print(f"Pexels collector finished. Downloaded {downloaded} images.")
