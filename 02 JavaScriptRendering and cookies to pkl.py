import time
import random
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent


class CaptchaHandler:
    @staticmethod
    def get_captcha_options(captcha_type, custom_options=None):
        """Python version of the CAPTCHA options system"""
        default_options = {
            'timeout': 30000,
            'check_interval': 500,
            'wait_network_idle': 1000,
            'debug': False
        }

        captcha_selectors = {
            'DataDome': {'selector': '#datadome-captcha', 'success_selector': '#captcha-success'},
            'reCAPTCHA': {'selector': '.g-recaptcha', 'success_selector': '.recaptcha-success'},
            'hCaptcha': {'selector': '.h-captcha', 'success_selector': '.hcaptcha-success'},
            'CloudflareTurnstile': {'selector': '.cf-turnstile', 'success_selector': '.cf-success'},
        }

        options = default_options.copy()
        options.update(captcha_selectors.get(captcha_type, {}))
        if custom_options:
            options.update(custom_options)
        return options

    def detect_captcha_type(self, driver):
        """Auto-detect which CAPTCHA is present on the page"""
        captcha_types = [
            ('reCAPTCHA', '.g-recaptcha'),
            ('hCaptcha', '.h-captcha'),
            ('CloudflareTurnstile', '.cf-turnstile'),
            ('DataDome', '#datadome-captcha')
        ]

        for captcha_type, selector in captcha_types:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return captcha_type
        return None

    def solve_captcha(self, driver, captcha_type=None, custom_options=None):
        """Handle different CAPTCHA types with appropriate solutions"""
        if not captcha_type:
            captcha_type = self.detect_captcha_type(driver)
            if not captcha_type:
                return True  # No CAPTCHA found

        options = self.get_captcha_options(captcha_type, custom_options)

        try:
            if captcha_type == 'reCAPTCHA':
                return self.solve_recaptcha(driver, options)
            elif captcha_type == 'hCaptcha':
                return self.solve_hcaptcha(driver, options)
            elif captcha_type == 'CloudflareTurnstile':
                return self.solve_turnstile(driver, options)
            else:
                print(f"Unsupported CAPTCHA type: {captcha_type}")
                return False

        except Exception as e:
            print(f"CAPTCHA solve failed: {str(e)}")
            return False

    def solve_recaptcha(self, driver, options):
        """Handle reCAPTCHA challenges"""
        print("Solving reCAPTCHA...")
        # Switch to reCAPTCHA iframe
        WebDriverWait(driver, options['timeout'] / 1000).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[title*='reCAPTCHA']")
            )
        )

        # Click the checkbox
        checkbox = WebDriverWait(driver, options['timeout'] / 1000).until(
            EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
        )
        checkbox.click()

        # Switch back to main content
        driver.switch_to.default_content()

        # Wait for verification
        WebDriverWait(driver, options['timeout'] / 1000).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, options['success_selector']))
        )
        return True

    def solve_hcaptcha(self, driver, options):
        """Handle hCaptcha challenges"""
        print("Solving hCaptcha...")
        # Implementation would go here
        return False

    def solve_turnstile(self, driver, options):
        """Handle Cloudflare Turnstile"""
        print("Solving Cloudflare Turnstile...")
        # Implementation would go here
        return False


class EnhancedCloudflareBypasser:
    def __init__(self, headless=True):
        self.chrome_options = Options()
        self.ua = UserAgent()
        self.captcha_handler = CaptchaHandler()
        self.setup_browser(headless)

    def setup_browser(self, headless):
        """Configure Chrome with enhanced stealth options"""
        self.chrome_options.add_argument(f"user-agent={self.ua.random}")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)

        # Enhanced stealth options
        self.chrome_options.add_argument("--disable-webgl")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")

        if headless:
            self.chrome_options.add_argument("--headless=new")

        # Optimized content settings
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.javascript": 1,
            "profile.default_content_setting_values.cookies": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

    def bypass_protection(self, url, timeout=15):
        """Bypass Cloudflare with CAPTCHA handling"""
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )

        try:
            # Initial access
            driver.get(url)

            # Check for CAPTCHA first
            if not self.captcha_handler.solve_captcha(driver):
                raise Exception("CAPTCHA solve failed")

            # Rest of bypass logic
            if "cloudflare" not in driver.current_url.lower():
                return driver
            else:
                raise Exception("Bypass failed")

        except Exception as e:
            driver.quit()
            raise Exception(f"Bypass failed: {str(e)}")

    def save_session(self, driver, filename="cf_session.pkl"):
        """Persist cookies and local storage for future sessions"""
        try:
            # Get all cookies
            cookies = driver.get_cookies()

            # Get local storage
            local_storage = driver.execute_script("return Object.assign({}, window.localStorage);")

            # Save session data
            session_data = {
                'cookies': cookies,
                'local_storage': local_storage,
                'user_agent': self.ua.random
            }

            with open(filename, 'wb') as f:
                pickle.dump(session_data, f)

            print(f"\n[+] Session saved to {filename}")
            return True

        except Exception as e:
            print(f"[!] Failed to save session: {str(e)}")
            return False


# Example Usage
if __name__ == "__main__":
    try:
        bypasser = EnhancedCloudflareBypasser(headless=False)
        driver = bypasser.bypass_protection("https://www.scrapingcourse.com/javascript-rendering")

        if driver:
            print("Successfully accessed protected site")
            print("Page title:", driver.title)

            bypasser.save_session(driver)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()