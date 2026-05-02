from playwright.sync_api import sync_playwright
import json
import os
from datetime import datetime
import re
import random


def scrape_without_clicking():
    os.makedirs("jobs", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # keep False until bot-detection is fully bypassed
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()
        page.goto("https://www.simplyhired.co.in/search?q=java+developer&l=&t=1")
        page.wait_for_load_state("networkidle")

        try:
            page.wait_for_selector("ul#job-list > li", timeout=15000)
        except Exception:
            print("❌ Job list did not load.")
            browser.close()
            return []

        all_jobs = []
        page_num = 1
        max_pages = 1

        while page_num <= max_pages:
            print(f"\n=== Page {page_num} ===")
            items = page.locator("ul#job-list > li")
            count = items.count()
            print("Number of job cards:", count)

            if count == 0:
                print("No cards found. Stopping.")
                break

            for i in range(1, count + 1):
                try:
                    page.click(f"#job-list > li:nth-child({i})")
                    print(f"Clicked card {i}")

                    # ✅ FIX 1: Wait for the aside panel using a semantic/role selector
                    # instead of fragile auto-generated CSS class chains
                    detail_panel = page.locator("aside").last
                    detail_panel.wait_for(state="visible", timeout=10000)

                    # ✅ FIX 2: Try multiple fallback selectors for the content area
                    content_text = get_detail_content(page)

                    # Card-level fields — these selectors are more stable
                    card = page.locator(f"#job-list > li:nth-child({i})")
                    title = card.locator("h2 a").text_content(timeout=5000)
                    company = card.locator("[data-testid='companyName'], .css-lvyu5j span, [class*='company']").first.text_content(timeout=5000)
                    location_el = card.locator("[data-testid='searchSerpJobLocation'], [class*='location'], .css-1t92pv").first
                    location = location_el.text_content(timeout=5000) if location_el.count() > 0 else "N/A"

                    print(f"Title: {title}")
                    print(f"Company: {company}")
                    print(f"Location: {location}")
                    print(f"Content (first 100 chars): {content_text[:100]}")

                    job_data = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location.strip(),
                        "link": page.url,
                        "content": content_text.strip(),
                    }
                    all_jobs.append(job_data)
                    save_job_json(**job_data)

                    page.wait_for_timeout(random.randint(1500, 2500))
                    print("---")

                except Exception as e:
                    print(f"⚠️  Skipping card {i}: {e}")
                    continue

            # Pagination
            page_num += 1
            current_page = page.locator("ul[data-testid='pageNumberContainer'] span[aria-current='true']")
            if current_page.count() == 0:
                print("No pagination found. Stopping.")
                break

            current_text = current_page.inner_text()
            next_number = str(int(current_text) + 1)
            next_page = page.locator(f"ul[data-testid='pageNumberContainer'] a:has-text('{next_number}')")

            if next_page.count() > 0:
                max_pages += 1
                print(f"Going to page {next_number}")
                with page.expect_navigation():
                    next_page.click()
                page.wait_for_load_state("networkidle")
                try:
                    page.wait_for_selector("ul#job-list > li", timeout=15000)
                except Exception:
                    print("Next page did not load. Stopping.")
                    break
            else:
                print("No more pages.")
                break

        browser.close()

        with open("simplyhired_jobs.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)

        print(f"\n=== Total: {len(all_jobs)} jobs saved ===")
        return all_jobs


def get_detail_content(page) -> str:
    """
    ✅ FIX 3: Try selectors from most semantic → least,
    so one broken class name doesn't crash everything.
    """
    candidates = [
        # Semantic: job description section inside aside
        "aside [data-testid='jobDescription']",
        "aside [class*='jobDescription']",
        "aside [class*='description']",
        # Role-based
        "aside section",
        # Broad fallback: entire aside text
        "aside",
    ]

    for selector in candidates:
        try:
            el = page.locator(selector).first
            if el.count() > 0:
                el.wait_for(state="visible", timeout=5000)
                text = el.text_content(timeout=5000)
                if text and len(text.strip()) > 20:
                    return text
        except Exception:
            continue

    return "Content not found"


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