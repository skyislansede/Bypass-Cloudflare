import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent


class CloudflareBypasser:
    def __init__(self, headless=False):
        self.chrome_options = Options()
        self.ua = UserAgent()
        self.setup_browser(headless)

    def setup_browser(self, headless):
        """Configure Chrome to avoid detection"""
        self.chrome_options.add_argument(f"user-agent={self.ua.random}")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)

        if headless:
            self.chrome_options.add_argument("--headless=new")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")

        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.chrome_options.add_experimental_option("prefs", prefs)

    def human_like_movement(self, element, driver):
        """Simulate human-like mouse movement"""
        action = ActionChains(driver)
        action.move_to_element(element).pause(random.uniform(0.5, 1.5))
        action.click().pause(random.uniform(0.2, 0.7))
        action.perform()

    def solve_cloudflare(self, driver, timeout=30):
        """Directly confront and solve Cloudflare challenge"""
        try:
            # Switch to challenge iframe
            WebDriverWait(driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[title*='Cloudflare']")
                )
            )

            # Wait for verify button
            verify_button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "input[value*='Verify'], .big-button.pow-button")
                )
            )

            # Human-like interaction
            self.human_like_movement(verify_button, driver)
            driver.switch_to.default_content()

            # Wait for redirect
            WebDriverWait(driver, timeout).until_not(
                EC.title_contains("Just a moment") |
                EC.title_contains("Verifying")
            )
            return True

        except Exception as e:
            print(f"Challenge solve failed: {str(e)}")
            return False

    def bypass_protection(self, url, timeout=30):
        """Main bypass method with fallback to challenge solving"""
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )

        try:
            # First attempt (bypass)
            print(f"Accessing {url}...")
            driver.get(url)
            time.sleep(random.uniform(2, 5))  # Natural delay

            # Verify
            if driver.current_url != url:
                print(f"Redirected to {driver.current_url}, checking for challenges...")

                # Check if challenge appeared
                if "cloudflare" in driver.page_source.lower():
                    print("Cloudflare detected - attempting to solve...")
                    if not self.solve_cloudflare(driver, timeout):
                        raise Exception("Failed to solve Cloudflare")
                else:
                    print("Unexpected redirect, but no Cloudflare detected")

            # Final verification
            if driver.current_url == url:
                print("Successfully reached target URL!")
                return driver
            else:
                raise Exception(f"Failed to reach target URL. Landed at: {driver.current_url}")

        except Exception as e:
            driver.quit()
            raise Exception(f"Bypass failed: {str(e)}")


# Usage Example
if __name__ == "__main__":
    bypasser = CloudflareBypasser(headless=False)

    try:
        target_url = "https://www.scrapingcourse.com/cloudflare-challenge"  #target url ***Sucessfully tested with https://www.researchgate.net/, https://www.cloudflare.com/, https://www.facebook.com/**
        driver = bypasser.bypass_protection(target_url, timeout=45)

        # Scrape the contents
        print("\nSuccess! Page details:")
        print("Title:", driver.title)
        print("URL:", driver.current_url)
        print("Page length:", len(driver.page_source), "characters")

        # Extract all links from the page
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\nFound {len(links)} links on the page")
        for link in links[:5]:  # Print first 5 links
            print(f"- {link.get_attribute('href')}")

    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit() #quit driver and finish the program