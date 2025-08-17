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


class ScrapingCourseLogin:
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
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.javascript": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

    def extract_csrf_token(self, driver):
        """Extract CSRF token from scrapingcourse.com specific implementation"""
        try:
            # First try to get the token from the form input
            token = driver.find_element(By.CSS_SELECTOR, "input[name='csrf_token']").get_attribute("value")
            if token:
                return token

            # If not found, check for meta tags
            token = driver.find_element(By.CSS_SELECTOR, "meta[name='csrf-token']").get_attribute("content")
            if token:
                return token

            # For scrapingcourse.com specifically, check the JavaScript variable
            token = driver.execute_script("return window.csrfToken;")
            if token:
                return token

            raise Exception("No CSRF token found in any expected location")
        except Exception as e:
            print("Debug: Page source for inspection:")
            print(driver.page_source[:2000])  # Print first 2000 chars of page source
            raise Exception(f"CSRF token extraction failed: {str(e)}")

    def human_like_interaction(self, element, driver):
        """Simulate human-like behavior"""
        action = ActionChains(driver)
        action.move_to_element_with_offset(element, random.randint(-5, 5), random.randint(-5, 5))
        action.pause(random.uniform(0.1, 0.3))
        action.move_to_element(element)
        action.pause(random.uniform(0.2, 0.5))
        action.click()
        action.pause(random.uniform(0.5, 1.2))
        action.perform()

    def login(self, username, password):
        """Perform login to scrapingcourse.com with CSRF protection"""
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )

        try:
            # 1. Access login page
            print("Navigating to login page...")
            driver.get("https://www.scrapingcourse.com/login/csrf")
            time.sleep(random.uniform(2, 4))

            # 2. Extract CSRF token with multiple fallbacks
            print("Extracting CSRF token...")
            csrf_token = self.extract_csrf_token(driver)
            print(f"Extracted CSRF token: {csrf_token}")

            # 3. Find form elements
            print("Locating form elements...")
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            # 4. Human-like form filling
            print("Filling in credentials...")
            self.human_like_interaction(username_field, driver)
            username_field.send_keys(username)

            time.sleep(random.uniform(0.5, 1.5))

            self.human_like_interaction(password_field, driver)
            password_field.send_keys(password)

            time.sleep(random.uniform(0.3, 0.8))

            # 5. Submit form
            print("Submitting form...")
            self.human_like_interaction(submit_button, driver)

            # 6. Verify login success
            print("Verifying login...")
            WebDriverWait(driver, 10).until(
                lambda d: "login" not in d.current_url  # Wait for URL to change from login page
            )

            print("\nLogin successful!")
            print("Current URL:", driver.current_url)
            print("Page Title:", driver.title)

            return driver

        except Exception as e:
            print(f"\nLogin failed: {str(e)}")
            driver.save_screenshot("login_failure.png")
            print("Saved screenshot as 'login_failure.png'")
            return None


# Example Usage
if __name__ == "__main__":
    USERNAME = "admin@example.com"
    PASSWORD = "password"

    # Initialize login handler
    login_handler = ScrapingCourseLogin(headless=False)  # Set to True for production

    # Perform login
    print("\nStarting login process...")
    driver = login_handler.login(USERNAME, PASSWORD)

    if driver:
        # Successful login actions
        try:
            content = driver.find_element(By.TAG_NAME, 'body').text
            print("\nProtected Content Sample:")
            print(content[:500] + "...")  # Print first 500 characters


        finally:
            # close the driver
            driver.quit()
    else:
        print("\nLogin failed. Check the screenshot for details.")