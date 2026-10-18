import asyncio
import nodriver as uc
import os
import sys
import django
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medimin_django.config.settings')
# Add the django project directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'medimin_django'))
django.setup()

from api.models import Medicine, Pharmacy, Price

async def fetch_medicine_live(query_name: str):
    """
    Automated crawler pipeline using nodriver and Django ORM.
    Visits RxJinn, bypassing Cloudflare, fetches the medicine data,
    and stores it in our database (SQLite or Cloud Postgres).
    """
    print(f"[1/4] Starting stealth browser for query: {query_name}...")
    browser = await uc.start(
        headless=False, 
        browser_args=["--window-size=1440,900"]
    )

    try:
        search_query = quote_plus(query_name)
        target_url = f"https://www.rxjinn.com/search?q={search_query}"
        
        print(f"[2/4] Navigating to {target_url}...")
        page = await browser.get(target_url)

        # Allow Cloudflare 5-second JS challenge to pass
        print("Waiting 15 seconds for Cloudflare challenge...")
        await asyncio.sleep(15)

        print("[3/4] Extracting content...")
        html_content = await page.get_content()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        page_title = soup.title.string if soup.title else "No Title"
        print(f"    -> Page Title: {page_title}")

    try:
        # ... logic for navigating ...
        
        # Reset is_syncing flag at the start of ingestion if medicine exists
        med_query = Medicine.objects.filter(name__iexact=query_name).first() or Medicine.objects.filter(slug__iexact=query_name).first()
        if med_query:
            med_query.is_syncing = True
            med_query.save()

        # Parse pharmacy data
        pharmacy_containers = soup.find_all('div', class_='price-card') # Adjust based on actual RxJinn DOM
        print(f"    -> Found {len(pharmacy_containers)} potential pharmacy matches.")

        for container in pharmacy_containers:
            try:
                pharmacy_name = container.find('p', class_='pharmacy-name').text.strip()
                selling_price_str = container.find('p', class_='price-value').text.replace('₹', '').replace(',', '').strip()
                product_url = container.find('a')['href']
                
                pharmacy, _ = Pharmacy.objects.get_or_create(
                    name=pharmacy_name,
                    defaults={'slug': pharmacy_name.lower().replace(" ", "-"), 'website_url': f"https://{pharmacy_name.lower()}.com"}
                )
                
                Price.objects.update_or_create(
                    medicine=medicine,
                    pharmacy=pharmacy,
                    defaults={
                        'selling_price': float(selling_price_str),
                        'product_url': product_url,
                        'in_stock': True
                    }
                )
            except Exception as inner_e:
                print(f"        -> Skip card due to parse error: {inner_e}")

        # Finalize
        if med_query:
            med_query.is_syncing = False
            med_query.save()
            print(f"    -> Reset is_syncing for {med_query.name}")

    except Exception as e:
        # ... logic for error ...
        if med_query:
            med_query.is_syncing = False
            med_query.save()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python live_crawler.py <medicine_name>")
        sys.exit(1)
        
    query = sys.argv[1]
    asyncio.run(fetch_medicine_live(query))
