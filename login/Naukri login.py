from playwright.sync_api import sync_playwright

def login_and_get_cookies():
    with sync_playwright() as p:
        # Launch browser in headless mode (no UI)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to login page
        page.goto("https://www.naukri.com")

        # Click "Login" to open the JS drawer/modal
        page.click("text=Login", timeout=5000)
        page.wait_for_timeout(1000)  # Wait for drawer animation

        # Fill email using your selector (finds input inside the div)
        email_selector = "#root > div.nI-gNb-header > div.nI-gNb-header__wrapper > div > div > div.drawer-wrapper input[type='text']"
        page.fill(email_selector, "koshta1999@gmail.com")

        # Fill password - usually next to email
        password_selector = "#root > div.nI-gNb-header > div.nI-gNb-header__wrapper > div > div > div.drawer-wrapper input[type='password']"
        page.fill(password_selector, "Mandla66@")

        # Click login button in drawer
        page.click("#root > div.nI-gNb-header button[type='submit'], .drawer-wrapper button:has-text('Login')")

        # Wait until page fully loads
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(10000)  # Wait for drawer animation

        # Extract cookies/session
        cookies = page.context.cookies()
        print(cookies)

        browser.close()
        return cookies

cookies = login_and_get_cookies()
