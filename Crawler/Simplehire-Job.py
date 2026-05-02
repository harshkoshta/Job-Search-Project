from playwright.sync_api import sync_playwright
import json
import os
from datetime import datetime
import re


def scrape_without_clicking():
    os.makedirs("jobs", exist_ok=True)
    """Faster method: extract all data from cards without clicking each"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.simplyhired.co.in/search?q=java+developer&l=&t=7")
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

            for i in range(1, items.count() + 1):
                page.click(f"#job-list > li:nth-child({i})")
                print(i);
                page.wait_for_timeout(3000)
                content = page.locator("#__next > div > main > div > div.css-17iqsqz > div > div > div.css-1k5vmo0 > div > div > div > aside > div")
                print(content.text_content())
                print(page.url)
                title = page.locator(f"#job-list > li:nth-child({i}) > div > div.chakra-stack.css-1igwmid > h2 > a")
                print("Title:" + title.text_content())
                company = page.locator(f"#job-list > li:nth-child({i}) > div > p > span.css-lvyu5j > span")
                print("Company:" + company.text_content())
                location = page.locator(f"#job-list > li:nth-child({i}) > div > p > span.css-1t92pv")
                print("Location:" + title.text_content())
                save_job(title.text_content(),company.text_content(), location.text_content(), page.url, content.text_content())
                save_job_json(title.text_content(),company.text_content(), location.text_content(), page.url, content.text_content())
                # apply = page.locator(f"#__next > div > main > div > div.css-17iqsqz > div > div > div.css-1k5vmo0 > div > div > div > aside > header > div > div > div.css-1r85bh9 > ul.css-t8ypn1 > li:nth-child({i}) > a")
                # print(apply.get_attribute("href"))
                page.wait_for_timeout(3000)
                print("------------------------------------------------------")
            page_num = page_num + 1
            # Get the current page number text
            current_page = page.locator("ul[data-testid='pageNumberContainer'] span[aria-current='true']")
            current_text = current_page.inner_text()
            print("Currently on page:", current_text)

            # Calculate next page number
            next_number = str(int(current_text) + 1)

            # Try to find the next page link by its text
            next_page = page.locator(f"ul[data-testid='pageNumberContainer'] a:has-text('{next_number}')")

            if next_page.count() > 0:
                max_pages=max_pages+1
                print(f"Clicking page {next_number}")
                with page.expect_navigation():
                    next_page.click()
            else:
                print(f"No page {next_number} exists. Stopping.")
        browser.close()

        with open("../simplyhired_jobs.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)

        print(f"\n=== Total: {len(all_jobs)} jobs ===")
        return all_jobs


def save_job(title: str, company: str, location: str, link: str, content: str):
    with open("jobs.md", "a", encoding="utf-8") as f:
        f.write(f"## {title}\n\n")
        f.write(f"# {company}\n\n")
        f.write(f" {location}\n\n")
        f.write(f"[Job Link] {link}\n\n")
        f.write(f"[Description] {content}\n\n")
        f.write("---\n\n")

def save_job_json(title: str, company: str, location: str, link: str, content: str):
    job = {
        "title": title,
        "company": company,
        "location": location,
        "link": link,
        "content": content,
    }

    safe_title = re.sub(r'[\\/:*?"<>|]', '', title).strip()[:50]
    filename = f"jobs/{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(job, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    scrape_without_clicking()
