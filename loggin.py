from playwright.sync_api import sync_playwright

def manual_login_and_save():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://twitter.com/login")
        input("🔐 Please log in to Twitter/X manually in the browser. Press Enter here after you're done...")

        context.storage_state(path="auth.json")
        browser.close()
        print("✅ Session saved to auth.json")

if __name__ == "__main__":
    manual_login_and_save()