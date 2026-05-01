from playwright.sync_api import sync_playwright

def login_and_get_cookies():
    with sync_playwright() as p:
        # Launch browser in headless mode (no UI)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to login page
        page.goto("https://www.simplyhired.co.in")
        page.wait_for_load_state("networkidle")
        # page.click("text=Sign in/Create account", timeout=5000)

        page.click("text=Sign In or Sign Up", timeout=5000)





        # Wait until page fully loads
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(10000)  # Wait for drawer animation

        # Extract cookies/session
        cookies = page.context.cookies()
        print(cookies)

        browser.close()
        return cookies

cookies = login_and_get_cookies()
