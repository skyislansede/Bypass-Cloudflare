# Cloudflare Bypassing Toolkit

This toolkit contains four specialized scripts for bypassing Cloudflare protections and handling various web scraping challenges. Each script serves a specific purpose in the scraping workflow.
***Headless Mode: Use headless=True for production to reduce resource usage, but note that some CAPTCHAs require a visible browser for manual solving.

## Script Overview

### 1. 01 Bypass CloudFlare Basic.py
Purpose: Basic Cloudflare challenge bypass  
**Features**:
- Solves simple Cloudflare JavaScript challenges
- Handles the "Verify you are human" checkbox
- Simulates human-like mouse movements
- Preserves natural browsing patterns with random delays

###2. 02_JavaScriptRendering_and_cookies_to_pkl.py
Purpose: Bypasses Cloudflare protections with enhanced stealth features, handles CAPTCHAs, and saves session data to a pickle file.
**Features**:
-Configures Chrome with advanced stealth options (disables WebGL, extensions, GPU).
-Auto-detects and attempts to solve CAPTCHAs (reCAPTCHA, hCaptcha, Cloudflare Turnstile, DataDome).
-Saves cookies and local storage to a .pkl file for session persistence.
-Optimized for JavaScript-heavy websites requiring dynamic content rendering.



###3. 03_CSRF_test.py
Purpose: Automates login to websites protected by CSRF tokens.
**Features**:
-Extracts CSRF tokens from form inputs, meta tags, or JavaScript variables.
-Simulates human-like interactions for filling and submitting login forms.
-Verifies login success and extracts protected content.
-Saves screenshots (login_failure.png) on login failure for debugging.

###4. 04_Confrontation_test.py
Purpose: Conducts penetration tests against Cloudflare-protected websites to evaluate security measures.
**Features**:
Detects Cloudflare protection types (JS challenge, CAPTCHA, rate limiting).
Attempts to bypass JS challenges and prompts for manual CAPTCHA solving.
Supports proxy rotation for rate limit evasion (requires proxy configuration).
Collects security headers and provides detailed test results.
