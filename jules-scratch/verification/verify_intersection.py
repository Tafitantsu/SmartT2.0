from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the application
            page.goto("http://localhost:5173", timeout=10000)

            # 2. Wait for a key element to be visible, indicating the app has loaded
            # and connected to the backend. The queue display is a good candidate.
            ns_queue_locator = page.locator(".queue-ns-top")
            expect(ns_queue_locator).to_be_visible(timeout=5000)

            # Check for initial state text
            expect(ns_queue_locator).to_contain_text("NS: 3")

            # 3. Take a screenshot for visual verification
            page.screenshot(path="jules-scratch/verification/verification.png")

            print("Successfully took screenshot of the initial state.")

        except Exception as e:
            print(f"An error occurred: {e}")
            # Take a screenshot even on failure for debugging
            page.screenshot(path="jules-scratch/verification/error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
