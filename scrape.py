from playwright.sync_api import sync_playwright
from tqdm import tqdm
import time
import csv
from datetime import datetime, timedelta
import re
import os

HASHTAGS = ["nifty50", "sensex", "intraday", "banknifty"]

TWEET_LIMIT = 500
OUTPUT_FILE = "tweets.csv"
since_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

def extract_tweet_data(tweet):
    try:
        username_elem = tweet.query_selector('div[dir="ltr"] span')
        timestamp_elem = tweet.query_selector('time')

        username = username_elem.inner_text() if username_elem else "N/A"
        timestamp = timestamp_elem.get_attribute('datetime') if timestamp_elem else "N/A"
        content = tweet.inner_text()

        mentions = re.findall(r'@\w+', content)
        hashtags = re.findall(r'#\w+', content)

        return {
            "username": username,
            "timestamp": timestamp,
            "content": content,
            "mentions": ', '.join(mentions),
            "hashtags": ', '.join(hashtags)
        }
    except Exception as e:
        print(f"[!] Error extracting tweet: {e}")
        return None

def init_csv():
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["username", "timestamp", "content", "mentions", "hashtags"])
            writer.writeheader()

def append_to_csv(tweet_data):
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=tweet_data.keys())
        writer.writerow(tweet_data)

def scroll_and_collect(page, tag):
    search_url = f"https://twitter.com/search?q=%23{tag}%20since%3A{since_date}&src=typed_query&f=live"
    print(f"[+] Navigating to {search_url}")
    page.goto(search_url)

    try:
        page.wait_for_selector("article", timeout=15000)
        print("✅ Tweets are loading...")
    except:
        print("❌ Could not find tweets. Saving screenshot...")
        page.screenshot(path=f"screenshot_{tag}.png")
        return 0

    collected = 0
    seen = set()
    scroll_attempts = 0
    max_scroll_attempts = 10

    with tqdm(total=TWEET_LIMIT, desc=f"Scraping #{tag}", unit="tweets") as pbar:
        while collected < TWEET_LIMIT and scroll_attempts < max_scroll_attempts:
            tweets = page.query_selector_all('article')

            new_found = 0
            for tweet in tweets:
                identifier = tweet.inner_text()[:50]
                if identifier in seen:
                    continue
                seen.add(identifier)

                tweet_data = extract_tweet_data(tweet)
                if tweet_data:
                    append_to_csv(tweet_data)  # ⬅️ Save immediately
                    collected += 1
                    new_found += 1
                    pbar.update(1)

                if collected >= TWEET_LIMIT:
                    break

            if new_found == 0:
                scroll_attempts += 1
                print(f"🔁 No new tweets, scrolling again... ({scroll_attempts}/{max_scroll_attempts})")
            else:
                scroll_attempts = 0

            page.mouse.wheel(0, 3000)
            time.sleep(2.5)

    return collected

def main():
    init_csv()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        total_collected = 0
        for tag in HASHTAGS:
            count = scroll_and_collect(page, tag)
            total_collected += count

        print(f"[✓] Total tweets collected and saved: {total_collected}")
        browser.close()

if __name__ == "__main__":
    main()
