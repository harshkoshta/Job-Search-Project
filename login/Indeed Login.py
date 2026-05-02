from playwright.sync_api import sync_playwright
from service.GmailOTPChecker import GmailOTPChecker
from playwright_stealth import  Stealth
from playwright.sync_api import sync_playwright

def login_and_get_cookies():

    with Stealth().use_sync(sync_playwright()) as p:
        # Launch browser in headless mode (no UI)
        browser = p.chromium.launch(headless=True)


        page = browser.new_page()

        context = browser.new_context()

        # Navigate to login page
        page.goto("https://www.simplyhired.co.in")
        page.wait_for_load_state("networkidle")
        # page.click("text=Sign in/Create account", timeout=5000)

        page.click("text=Sign In or Sign Up")
        page.wait_for_timeout(3000)
        email_selector="#ifl-InputFormField-\\:passport-ssr-Reaktala\\:"
        page.fill(email_selector, "koshta1999@gmail.com")
        page.wait_for_timeout(5000)
        page.click("#emailform > button")
        page.wait_for_timeout(5000)
        # print("verify you are human")
        #
        # #check human
        # page.check("#nqtI3 > div > label > input[type=checkbox]")
        # print("clicked verified you are human")
        # page.wait_for_timeout(5000)
        page.click("text=Sign in with a code instead")
        page.wait_for_timeout(5000)
        otp_checker = GmailOTPChecker("koshta1999@gmail.com", "smon pytr pkdp xqbh")
        otp_checker.login()
        otp = otp_checker.otpcheck()
        page.fill("#passcode-input", otp)




        # Wait until page fully loads
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000000)  # Wait for drawer animation

        # Extract cookies/session
        cookies = page.context.cookies()
        print(cookies)
        context.storage_state(path="storage.json")
        print("Login session saved to storage.json")
        browser.close()
        return cookies

cookies = login_and_get_cookies()


# def reuse_context():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         # Load saved state
#         context = browser.new_context(storage_state="storage.json")
#         page = context.new_page()
#
#         # Now you’re already logged in
#         page.goto("https://www.indeed.com")
#         print("Logged in automatically using saved context")
#
#         browser.close()
#
# reuse_context()