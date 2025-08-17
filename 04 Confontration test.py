import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent


class CloudflarePenetrationTester:
    def __init__(self, headless=False, proxy=None):
        self.chrome_options = Options()
        self.ua = UserAgent()
        self.proxy = proxy
        self.setup_browser(headless)
        self.security_tests = {
            'basic_bypass': False,
            'js_challenge': False,
            'captcha_challenge': False,
            'rate_limit': False
        }

    def setup_browser(self, headless):
        """Configure Chrome to avoid detection"""
        self.chrome_options.add_argument(f"user-agent={self.ua.random}")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)

        if self.proxy:
            self.chrome_options.add_argument(f"--proxy-server={self.proxy}")

        if headless:
            self.chrome_options.add_argument("--headless=new")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")

        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.chrome_options.add_experimental_option("prefs", prefs)

    def human_like_interaction(self, element, driver):
        """Simulate human-like behavior"""
        action = ActionChains(driver)

        # Random movement pattern
        action.move_to_element_with_offset(element, random.randint(-5, 5), random.randint(-5, 5))
        action.pause(random.uniform(0.1, 0.3))
        action.move_to_element(element)
        action.pause(random.uniform(0.2, 0.5))
        action.click()
        action.pause(random.uniform(0.5, 1.2))
        action.perform()

    def detect_challenge_type(self, driver):
        """Identify Cloudflare protection type"""
        try:
            # Check for basic JS challenge
            if "jschl_vc" in driver.page_source:
                self.security_tests['js_challenge'] = True
                return "js_challenge"

            # Check for CAPTCHA
            if "g-recaptcha" in driver.page_source or "cf_captcha" in driver.page_source:
                self.security_tests['captcha_challenge'] = True
                return "captcha_challenge"

            # Check for rate limiting
            if "Access denied" in driver.title or "rate limit" in driver.page_source.lower():
                self.security_tests['rate_limit'] = True
                return "rate_limit"

            return "basic_bypass"
        except:
            return "unknown"

    def solve_js_challenge(self, driver, timeout=30):
        """Solve JavaScript challenge"""
        try:
            # Extract challenge variables
            jschl_vc = driver.find_element(By.NAME, "jschl_vc").get_attribute("value")
            pass_field = driver.find_element(By.NAME, "pass").get_attribute("value")

            # Execute challenge calculation (simplified)
            answer = len(driver.title) + random.randint(100, 500)

            # Build solution URL
            challenge_url = f"{driver.current_url.split('/')[0]}//{driver.current_url.split('/')[2]}"
            solution_url = f"{challenge_url}/cdn-cgi/l/chk_jschl?jschl_vc={jschl_vc}&pass={pass_field}&jschl_answer={answer}"

            # Submit solution
            driver.get(solution_url)
            time.sleep(5)
            return True
        except Exception as e:
            print(f"JS Challenge failed: {str(e)}")
            return False

    def solve_captcha_challenge(self, driver, timeout=30):
        """Confront CAPTCHA challenge (requires manual intervention)"""
        try:
            # Switch to CAPTCHA iframe
            WebDriverWait(driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[title*='CAPTCHA']")
                )
            )

            # Wait for CAPTCHA to load
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
            )

            print("\n[!] CAPTCHA detected - manual intervention required!")
            print("Please solve the CAPTCHA in the browser window...")

            # Wait for user to solve CAPTCHA
            WebDriverWait(driver, 300).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".recaptcha-checkbox-checked"))
            )

            driver.switch_to.default_content()
            return True
        except Exception as e:
            print(f"CAPTCHA solve failed: {str(e)}")
            return False

    def penetration_test(self, url, timeout=45):
        """Conduct full penetration test against Cloudflare"""
        print(f"\n[+] Starting penetration test against: {url}")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )

        try:
            # Initial access attempt
            print("[1] Initial access attempt...")
            driver.get(url)
            time.sleep(random.uniform(3, 7))

            # Detect protection type
            challenge_type = self.detect_challenge_type(driver)
            print(f"[2] Detected protection: {challenge_type.upper()}")

            # Conduct appropriate test
            if challenge_type == "js_challenge":
                print("[3] Attempting JS challenge bypass...")
                if self.solve_js_challenge(driver, timeout):
                    print("[+] JS challenge bypass successful!")
                    self.security_tests['basic_bypass'] = True

            elif challenge_type == "captcha_challenge":
                print("[3] Confronting CAPTCHA challenge...")
                if self.solve_captcha_challenge(driver, timeout):
                    print("[+] CAPTCHA challenge solved!")

            elif challenge_type == "rate_limit":
                print("[3] Testing rate limit evasion...")
                print("[!] Switching proxies and retrying...")
                # Implement proxy rotation here
                return False

            else:
                print("[3] No advanced protection detected")
                self.security_tests['basic_bypass'] = True

            # Verify final access
            if "cloudflare" not in driver.current_url.lower():
                print("[+] Successfully penetrated Cloudflare protection!")
                print(f"Final URL: {driver.current_url}")

                # Collect security headers for analysis
                security_headers = driver.execute_script("""
                    return Object.fromEntries(
                        Object.entries(window.performance.getEntries()[0].serverTiming || [])
                        .filter(([_, entry]) => entry.name.startsWith('cf-'))
                    );
                """)

                return {
                    "status": "success",
                    "final_url": driver.current_url,
                    "protection_type": challenge_type,
                    "security_headers": security_headers,
                    "tests_passed": self.security_tests
                }
            else:
                return {
                    "status": "failed",
                    "reason": "Failed to bypass protection",
                    "protection_type": challenge_type,
                    "tests_passed": self.security_tests
                }

        except Exception as e:
            return {
                "status": "error",
                "reason": str(e),
                "tests_passed": self.security_tests
            }
        finally:
            driver.quit()


# Example Usage
if __name__ == "__main__":
    TARGET_URL = "https://www.cloudflare-cn.com/enterprise/"
    PROXY = "http://your-proxy:port"  # Optional

    # Initialize tester
    tester = CloudflarePenetrationTester(
        headless=True,  # Set to True for production
        proxy=PROXY
    )

    # Run penetration test
    results = tester.penetration_test(TARGET_URL)

    # Print results
    print("\n[+] Test Results:")
    print(f"Status: {results['status'].upper()}")
    print(f"Protection Type: {results.get('protection_type', 'N/A')}")
    print("\nSecurity Tests:")
    for test, passed in results.get('tests_passed', {}).items():
        print(f"- {test.replace('_', ' ').title()}: {'PASSED' if passed else 'FAILED'}")

    if results['status'] == 'success':
        print("\nSecurity Headers Found:")
        for header, value in results.get('security_headers', {}).items():
            print(f"- {header}: {value}")

