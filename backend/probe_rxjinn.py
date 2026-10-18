import asyncio
import nodriver as uc
import os

async def fetch_sitemap():
    print("Starting nodriver to fetch sitemap...")
    browser = await uc.start(headless=False, browser_args=["--window-size=1440,900"])
    
    print("Navigating to https://www.rxjinn.com/sitemap.xml or /browse-prescriptions/")
    # Browsing UI usually has all categories or pagination available directly
    # Let's try the browse url first as sitemaps can sometimes be huge and hard to parse from DOM
    page = await browser.get("https://www.rxjinn.com/sitemap.xml")
    
    print("Waiting 15 seconds for Cloudflare...")
    await asyncio.sleep(15)
    
    html = await page.get_content()
    
    with open("sitemap_dump.xml", "w", encoding="utf-8") as f:
        f.write(html)
    print("Done. Saved to sitemap_dump.xml")
    
    browser.stop()

if __name__ == "__main__":
    asyncio.run(fetch_sitemap())
