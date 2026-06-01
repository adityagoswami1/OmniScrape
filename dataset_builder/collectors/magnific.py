import urllib.parse
from playwright.sync_api import sync_playwright
from .base_collector import BaseCollector

class MagnificCollector(BaseCollector):
    def search_and_download(self, topic):
        url = f"https://www.magnific.com/free-photos-vectors/{urllib.parse.quote(topic.replace(' ', '-'))}"
        
        try:
            with sync_playwright() as p:
                # Magnific has strict anti-bot protections. 
                # Setting headless=False might occasionally bypass it if run locally.
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                )
                
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(4000)

                image_urls = set()
                stale_count = 0

                for i in range(10):
                    images = page.query_selector_all("img")
                    found_new = False
                    
                    for img in images:
                        src = img.get_attribute("src")
                        if src and src.startswith("http") and "media.magnific.com" in src:
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
                    page.wait_for_timeout(2000)

                browser.close()

            for img_url in list(image_urls)[:self.max_images]:
                filepath = self.download_image(img_url, "magnific")
                if filepath:
                    yield filepath, img_url

        except Exception as e:
            print(f"Failed to load Magnific for {topic}: {e}")
