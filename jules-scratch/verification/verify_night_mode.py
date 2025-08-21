from playwright.sync_api import sync_playwright, expect

def verify_night_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto("http://localhost:5173/")

        # Click the night mode button
        night_mode_button = page.get_by_role("button", name="Mode Nuit Désactivé")
        night_mode_button.click()

        # Wait for the button text to change
        expect(page.get_by_role("button", name="Mode Nuit Activé")).to_be_visible()

        # Wait for the intersection to be in night mode
        intersection = page.locator(".intersection")
        expect(intersection).to_have_class("intersection night-mode")

        # There are 4 traffic lights, and in night mode they are all yellow and flashing
        # Let's check the two main traffic lights

        # Traffic light F2 (top-right, EW)
        # The yellow light is the second .light element in the traffic-light div
        ew_traffic_light = page.locator(".corner.top-right .traffic-light .light:nth-child(3)")
        expect(ew_traffic_light).to_have_class("light yellow flashing")

        # Traffic light F1 (top-left, NS)
        ns_traffic_light = page.locator(".corner.top-left .traffic-light .light:nth-child(3)")
        expect(ns_traffic_light).to_have_class("light yellow flashing")

        page.screenshot(path="jules-scratch/verification/verification.png")

        browser.close()

if __name__ == "__main__":
    verify_night_mode()
