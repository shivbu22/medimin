"""
RxJinn HTML/Screenshot Capture — Uses nodriver to bypass Cloudflare and capture UI.
"""
import asyncio
import nodriver as uc
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rxjinn_capture")
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def capture_rxjinn():
    print("[1/3] Launching undetected Chrome browser...")
    # headless=True might get detected by CF, but let's try headless=False to be safe
    browser = await uc.start(
        headless=False,
        browser_args=["--window-size=1440,900"]
    )

    print("[2/3] Navigating to RxJinn homepage...")
    page = await browser.get("https://www.rxjinn.com/")

    # Wait for Cloudflare to resolve
    print("Waiting for Cloudflare challenge to resolve (up to 20s)...")
    await asyncio.sleep(20)

    # Save homepage HTML
    html_content = await page.get_content()
    with open(os.path.join(OUTPUT_DIR, "homepage.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("    -> Saved homepage HTML")

    # Try to navigate to a medicine detail page
    print("[3/3] Navigating to Dolo 650 page...")
    page2 = await browser.get("https://www.rxjinn.com/prescription/Dolo+650+Tablet/")
    await asyncio.sleep(15)

    dolo_html = await page2.get_content()
    with open(os.path.join(OUTPUT_DIR, "dolo650.html"), "w", encoding="utf-8") as f:
        f.write(dolo_html)
    print("    -> Saved Dolo 650 HTML")

    print("\n[DONE] Capture complete!")
    browser.stop()

if __name__ == "__main__":
    asyncio.run(capture_rxjinn())
