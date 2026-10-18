import asyncio
import random
import sqlite3
from datetime import datetime
from .nlp_matcher import normalize_price

# Configuration of available networks (Slugs match the DB)
PHARMACY_NETWORKS = [
    {"slug": "1mg", "name": "1mg"},
    {"slug": "pharmeasy", "name": "PharmEasy"},
    {"slug": "netmeds", "name": "Netmeds"},
    {"slug": "apollo", "name": "Apollo Pharmacy"},
    {"slug": "truemeds", "name": "Truemeds"}
]

async def simulate_live_fetch(pharmacy_slug: str, query: str) -> list:
    """
    Simulated Scraper Node. 
    In a real production environment, this would use aiohttp + proxies 
    or a browser pool (Playwright) to visit the network's search page.
    """
    # Simulate realistic network jitter (0.8s - 3.5s)
    await asyncio.sleep(random.uniform(0.8, 3.5))
    
    # Mock data generation based on search seed
    # This simulates finding 1-2 items per pharmacy
    base_price = random.uniform(20.0, 50.0)
    
    results = []
    # Primary match
    results.append({
        "name": f"{query}", # Exact match
        "pack": "strip of 15",
        "price": round(base_price, 2)
    })
    
    # Random variation/alternative match
    if random.random() > 0.5:
        results.append({
            "name": f"{query} Double Strength",
            "pack": "strip of 10",
            "price": round(base_price * 1.8, 2)
        })
        
    return {"slug": pharmacy_slug, "items": results}

async def refresh_live_prices(db_path: str, medicine_id: int):
    """
    The core background task engine.
    1. Fetches the medicine name from DB.
    2. Fans out requests to all pharmacies.
    3. Normalizes and updates the prices table.
    """
    start_time = datetime.now()
    print(f"[{start_time}] Starting Live Aggregator Refresh for Medicine ID: {medicine_id}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        med = conn.execute("SELECT name FROM medicines WHERE id = ?", (medicine_id,)).fetchone()
        if not med:
            print(f"Medicine {medicine_id} not found. Aborting refresh.")
            return
            
        medicine_name = med["name"]
        
        # Dispatch parallel tasks
        tasks = [simulate_live_fetch(p["slug"], medicine_name) for p in PHARMACY_NETWORKS]
        results = await asyncio.gather(*tasks)
        
        # Process and update DB
        cursor = conn.cursor()
        for res in results:
            pharm_slug = res["slug"]
            pharm = cursor.execute("SELECT id FROM pharmacies WHERE slug = ?", (pharm_slug,)).fetchone()
            if not pharm: continue
            
            pharm_id = pharm["id"]
            
            for item in res["items"]:
                norm = normalize_price(medicine_name, item["name"], item["pack"], item["price"])
                
                if norm["is_exact_match"] or norm["is_similar"]:
                    # Update or Insert price
                    cursor.execute('''
                        INSERT INTO prices (medicine_id, pharmacy_id, pack_size, mrp, selling_price, unit_price, in_stock)
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                        ON CONFLICT(medicine_id, pharmacy_id) DO UPDATE SET
                            pack_size = excluded.pack_size,
                            selling_price = excluded.selling_price,
                            unit_price = excluded.unit_price,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (
                        medicine_id, pharm_id, item["pack"], 
                        norm["selling_price"] * 1.2, # Mock MRP 20% higher
                        norm["selling_price"], norm["unit_price"]
                    ))
                    
                    # Log to price history to enable trends
                    cursor.execute('''
                        INSERT INTO price_history (medicine_id, pharmacy_id, price)
                        VALUES (?, ?, ?)
                    ''', (medicine_id, pharm_id, norm["selling_price"]))
        
        conn.commit()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[{end_time}] Live Aggregator Refresh Complete in {duration}s")
        
    except Exception as e:
        print(f"Aggregator Error: {str(e)}")
    finally:
        conn.close()
