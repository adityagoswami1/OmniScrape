import time
from playwright.sync_api import sync_playwright
from .base_collector import BaseCollector

class UnsplashCollector(BaseCollector):
    def search_and_download(self, topic):
        print(f"Starting Unsplash collector for topic: {topic}")
        downloaded = 0
        image_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            search_url = f"https://unsplash.com/s/photos/{topic.replace(' ', '-')}"
            try:
                page.goto(search_url, timeout=60000, wait_until='load')
                # Wait extra for any redirects to settle
                time.sleep(5)
                # Re-confirm we're on a stable page
                page.wait_for_load_state('domcontentloaded')
                
                # HITL: Wait for manual CAPTCHA solving if Cloudflare intercepts
                for _ in range(30): # Wait up to 60 seconds
                    title = page.title().lower()
                    if "just a moment" in title or "attention required" in title or "security" in title or "cloudflare" in title:
                        print(f"[{topic}] CAPTCHA detected on Unsplash! Please solve it in the popped-up browser window...")
                        time.sleep(2)
                    else:
                        break
                        
            except Exception as e:
                print(f"Failed to load Unsplash for {topic}: {e}")
                browser.close()
                return

            max_scrolls = max(20, self.max_images // 3)  # ~3 images per scroll
            scroll_attempts = 0
            stale_count = 0  # Track consecutive scrolls with no new images
            while len(image_urls) < self.max_images and scroll_attempts < max_scrolls:
                prev_count = len(image_urls)
                try:
                    images = page.query_selector_all('img')
                    for img in images:
                        try:
                            src = img.get_attribute('src') or ''
                            srcset = img.get_attribute('srcset') or ''
                        except Exception:
                            continue
                        
                        # Look for unsplash image URLs
                        if 'images.unsplash.com/photo' in src:
                            base = src.split('?')[0]
                            clean_url = f"{base}?w=1080&q=80&fm=jpg"
                            image_urls.add(clean_url)
                        elif 'images.unsplash.com/photo' in srcset:
                            first_url = srcset.split(',')[0].strip().split(' ')[0]
                            base = first_url.split('?')[0]
                            clean_url = f"{base}?w=1080&q=80&fm=jpg"
                            image_urls.add(clean_url)
                            
                        if len(image_urls) >= self.max_images:
                            break
                except Exception as e:
                    print(f"  Warning: selector query failed (attempt {scroll_attempts}): {e}")
                    time.sleep(1)

                # Stale detection: stop if 10 consecutive scrolls yield nothing new
                if len(image_urls) > 0 and len(image_urls) == prev_count:
                    stale_count += 1
                    if stale_count >= 10:
                        print(f"  No new images found after {stale_count} scrolls, stopping.")
                        break
                elif len(image_urls) > prev_count:
                    stale_count = 0
                            
                try:
                    page.evaluate("window.scrollBy(0, 1500)")
                except Exception:
                    pass
                time.sleep(1.5)
                scroll_attempts += 1
            
            browser.close()

        print(f"Found {len(image_urls)} image URLs on Unsplash.")
        
        for url in list(image_urls)[:self.max_images]:
            filepath = self.download_image(url, "unsplash")
            if filepath:
                downloaded += 1
                yield filepath, url

        print(f"Unsplash collector finished. Downloaded {downloaded} images.")
