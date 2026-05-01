from playwright.sync_api import sync_playwright
import json

def scrape_without_clicking():
    """Faster method: extract all data from cards without clicking each"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.simplyhired.co.in/search?q=software+engineer&l=pune")
        page.wait_for_load_state("networkidle")

        all_jobs = []
        page_num = 1
        max_pages = 1

        while page_num <= max_pages:
            print(f"\n=== Page {page_num} ===")

            # Wait and get all cards
            page.wait_for_selector("#job-list > li:nth-child(1)", timeout=10000)
            print("Check either click or not")
            items = page.locator("ul#job-list > li")
            print("Number of job cards:", items.count())

            for i in range(1, items.count()+1):
                page.click(f"#job-list > li:nth-child({i})")
                print(i);
                page.wait_for_load_state("networkidle")
                content = page.locator("#__next > div > main > div > div.css-17iqsqz > div > div > div.css-1k5vmo0 > div > div > div > aside > div")
                print(content.text_content())
                print(page.url)
                # apply = page.locator(f"#__next > div > main > div > div.css-17iqsqz > div > div > div.css-1k5vmo0 > div > div > div > aside > header > div > div > div.css-1r85bh9 > ul.css-t8ypn1 > li:nth-child({i}) > a")
                # print(apply.get_attribute("href"))
                # page.wait_for_timeout(3000)
                print("------------------------------------------------------")
            page_num=page_num+1
        browser.close()

        with open("../simplyhired_jobs.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)

        print(f"\n=== Total: {len(all_jobs)} jobs ===")
        return all_jobs

if __name__ == "__main__":
    scrape_without_clicking()
