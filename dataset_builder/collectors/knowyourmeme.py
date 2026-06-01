import urllib.parse
from playwright.sync_api import sync_playwright
from .base_collector import BaseCollector

class KnowYourMemeCollector(BaseCollector):
    def search_and_download(self, topic):
        url = f"https://knowyourmeme.com/search?q={urllib.parse.quote(topic)}"
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                )
                
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(3000)

                image_urls = set()
                stale_count = 0

                for i in range(10):
                    images = page.query_selector_all("img")
                    found_new = False
                    
                    for img in images:
                        src = img.get_attribute("data-src") or img.get_attribute("src")
                        if src and "knowyourmeme.com/photos" in src:
                            if src not in image_urls:
                                image_urls.add(src)
                                found_new = True

                    if not found_new and len(image_urls) > 0:
                        stale_count += 1
                        if stale_count >= 2:
                            break
                    else:
                        stale_count = 0

                    if len(image_urls) >= self.max_images:
                        break

                    page.evaluate("window.scrollBy(0, 1500)")
                    page.wait_for_timeout(1500)

                browser.close()

            for img_url in list(image_urls)[:self.max_images]:
                filepath = self.download_image(img_url, "knowyourmeme")
                if filepath:
                    yield filepath, img_url

        except Exception as e:
            print(f"Failed to load Know Your Meme for {topic}: {e}")
