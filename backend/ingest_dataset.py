import sqlite3
import pandas as pd
import numpy as np
import os
import re
import math
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medimin.db")
CSV_PATH = r"c:\Users\ahiva\Downloads\medicine\indian_pharmaceutical_products_clean.csv"

# The prompt's categorized pharmacies
PHARMACIES_DATA = [
    {"name": "1mg (Tata 1mg)", "slug": "1mg", "rating": 4.8, "otype": "aggregator"},
    {"name": "Apollo Pharmacy", "slug": "apollo", "rating": 4.7, "otype": "aggregator"},
    {"name": "Netmeds", "slug": "netmeds", "rating": 4.6, "otype": "aggregator"},
    {"name": "Truemeds", "slug": "truemeds", "rating": 4.5, "otype": "discount"},
    {"name": "MrMed", "slug": "mrmed", "rating": 4.4, "otype": "specialty"},
    {"name": "PharmEasy", "slug": "pharmeasy", "rating": 4.7, "otype": "aggregator"},
    {"name": "Practo", "slug": "practo", "rating": 4.5, "otype": "aggregator"},
    {"name": "Flipkart Health+", "slug": "flipkart-health", "rating": 4.3, "otype": "discount"},
    {"name": "MedPlus Mart", "slug": "medplus", "rating": 4.6, "otype": "aggregator"},
    {"name": "MediBuddy", "slug": "medibuddy", "rating": 4.4, "otype": "aggregator"},
    {"name": "Wellness Forever", "slug": "wellness-forever", "rating": 4.8, "otype": "aggregator"},
    {"name": "Zeno Health", "slug": "zeno-health", "rating": 4.2, "otype": "discount"},
    {"name": "Healthmug", "slug": "healthmug", "rating": 4.1, "otype": "alternative"},
    {"name": "MedGreen", "slug": "medgreen", "rating": 4.0, "otype": "discount"},
    {"name": "PlatinumRx", "slug": "platinumrx", "rating": 4.5, "otype": "discount"},
    {"name": "Medstown", "slug": "medstown", "rating": 4.3, "otype": "qcommerce"},
    {"name": "Pharmacy Bazar", "slug": "pharmacy-bazar", "rating": 4.2, "otype": "aggregator"},
    {"name": "Blinkit", "slug": "blinkit", "rating": 4.9, "otype": "qcommerce"},
    {"name": "Zepto", "slug": "zepto", "rating": 4.8, "otype": "qcommerce"},
    {"name": "Swiggy Instamart", "slug": "instamart", "rating": 4.7, "otype": "qcommerce"},
]

def generate_slug(text):
    if not isinstance(text, str):
        return "unknown"
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def init_fresh_db():
    print("[1] Reinitializing Database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    tables = ['price_history', 'prices', 'saved_drugs', 'medicines', 'pharmacies', 'categories']
    for t in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {t}")
        
    # Categories Table
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            icon TEXT DEFAULT '💊',
            description TEXT,
            medicine_count INTEGER DEFAULT 0
        )
    ''')

    # Medicines Table
    cursor.execute('''
        CREATE TABLE medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            active_salt TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            category_id INTEGER,
            dosage_form TEXT DEFAULT 'Tablet',
            pack_size_label TEXT DEFAULT '10 Tablets',
            description TEXT,
            uses TEXT,
            side_effects TEXT,
            is_otc INTEGER DEFAULT 0,
            is_prescription INTEGER DEFAULT 1,
            dpco_controlled INTEGER DEFAULT 0,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Pharmacies Table
    cursor.execute('''
        CREATE TABLE pharmacies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            website_url TEXT NOT NULL,
            logo_url TEXT,
            rating REAL DEFAULT 4.0,
            delivery_time TEXT DEFAULT '1-3 days',
            return_policy TEXT DEFAULT '7 days return',
            min_order REAL DEFAULT 0,
            free_delivery_above REAL DEFAULT 299,
            is_active INTEGER DEFAULT 1,
            otype TEXT
        )
    ''')

    # Prices Table
    cursor.execute('''
        CREATE TABLE prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL,
            pharmacy_id INTEGER NOT NULL,
            pack_size TEXT NOT NULL,
            mrp REAL NOT NULL,
            selling_price REAL NOT NULL,
            unit_price REAL,
            discount_percentage REAL DEFAULT 0,
            in_stock INTEGER DEFAULT 1,
            product_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id),
            FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(id),
            UNIQUE(medicine_id, pharmacy_id)
        )
    ''')

    # Price History Table
    cursor.execute('''
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL,
            pharmacy_id INTEGER NOT NULL,
            price REAL NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id),
            FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(id)
        )
    ''')

    # Saved Drugs / Wishlist
    cursor.execute('''
        CREATE TABLE saved_drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            medicine_id INTEGER NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id),
            UNIQUE(session_id, medicine_id)
        )
    ''')

    cursor.execute('CREATE INDEX idx_medicines_salt ON medicines(active_salt)')
    cursor.execute('CREATE INDEX idx_medicines_name ON medicines(name)')
    cursor.execute('CREATE INDEX idx_medicines_slug ON medicines(slug)')
    cursor.execute('CREATE INDEX idx_prices_medicine ON prices(medicine_id)')
    cursor.execute('CREATE INDEX idx_prices_pharmacy ON prices(pharmacy_id)')
    cursor.execute('CREATE INDEX idx_prices_selling ON prices(selling_price)')

    conn.commit()
    return conn

def ingest_data(conn):
    print(f"[2] Loading CSV: {CSV_PATH}")
    start_time = time.time()
    
    # Read the dataset
    df = pd.read_csv(CSV_PATH)
    
    # Handle NaNs
    df['brand_name'] = df['brand_name'].fillna('Unknown')
    df['primary_ingredient'] = df['primary_ingredient'].fillna('Unknown Salt')
    df['manufacturer'] = df['manufacturer'].fillna('Generic')
    df['therapeutic_class'] = df['therapeutic_class'].fillna('General')
    df['dosage_form'] = df['dosage_form'].fillna('Tablet')
    df['packaging_raw'] = df['packaging_raw'].fillna('1 Pack')
    df['price_inr'] = pd.to_numeric(df['price_inr'], errors='coerce').fillna(100.0)
    
    print(f"    Loaded {len(df)} medicines in {time.time()-start_time:.2f}s")
    
    # Insert Pharmacies
    print("[3] Populating Pharmacies...")
    cursor = conn.cursor()
    for p in PHARMACIES_DATA:
        cursor.execute("""
            INSERT INTO pharmacies (name, slug, website_url, rating, logo_url, otype)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            p['name'], p['slug'], f"https://www.{p['slug']}.com", p['rating'], 
            f"https://via.placeholder.com/150?text={p['slug'].upper()}",
            p['otype']
        ))
    conn.commit()
    
    # Get Pharmacy IDs by type
    pharmacies_df = pd.read_sql_query("SELECT id, otype FROM pharmacies", conn)
    aggregator_ids = pharmacies_df[pharmacies_df['otype'] == 'aggregator']['id'].tolist()
    discount_ids = pharmacies_df[pharmacies_df['otype'] == 'discount']['id'].tolist()
    qcommerce_ids = pharmacies_df[pharmacies_df['otype'] == 'qcommerce']['id'].tolist()
    all_pharmacy_ids = pharmacies_df['id'].tolist()
    
    # Insert Categories
    print("[4] Populating Categories...")
    categories = df['therapeutic_class'].unique()
    cat_records = []
    cat_map = {}
    for c in categories:
        slug = generate_slug(c)
        if not slug: slug = "general"
        cat_records.append({"name": str(c).title(), "slug": slug})
        
    cat_df = pd.DataFrame(cat_records).drop_duplicates('slug')
    cat_df.to_sql('categories', conn, if_exists='append', index=False)
    
    # Create a mapping dictionary for category ids
    cats = pd.read_sql_query("SELECT id, name FROM categories", conn)
    cat_map = dict(zip(cats['name'].str.lower(), cats['id']))

    # Insert Medicines
    print("[5] Populating Medicines (this may take a minute)...")
    meds_to_insert = []
    
    # Map DataFrame to Database columns
    for row in df.itertuples():
        cat_id = cat_map.get(str(row.therapeutic_class).lower(), None)
        meds_to_insert.append((
            row.brand_name,
            generate_slug(row.brand_name) + f"-{row.Index}", # enforce uniqueness safely
            row.primary_ingredient,
            row.manufacturer,
            cat_id,
            row.dosage_form,
            row.packaging_raw,
            f"Prescription required for {row.brand_name}" if "antibiotic" in str(row.therapeutic_class).lower() else "Consult doctor for usage.",
            1 if "syrup" in str(row.dosage_form).lower() or "cream" in str(row.dosage_form).lower() else 0, # rough OTC guess
        ))
        
    cursor.executemany("""
        INSERT INTO medicines (name, slug, active_salt, manufacturer, category_id, dosage_form, pack_size_label, uses, is_otc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, meds_to_insert)
    conn.commit()

    # Generate Prices
    print("[6] Connecting Medicines to Aggregators and Generating Realistic Prices...")
    
    price_records = []
    # Using numpy to speed up generation
    mrp_base = df['price_inr'].values
    
    # We will pick a random set of pharmacies for each medicine to simulate real availability
    # Pre-generate random discount maps
    
    # Just generating for the first 50,000 to keep sqlite lightweight and fast
    # Wait, 250k * 5 = 1.25M rows. SQLite handles 1.25M easily! Let's do all.
    count = 0
    batch_size = 50000
    
    for row in df.itertuples():
        med_id = row.Index + 1 # SQLite 1-indexed AUTOINCREMENT
        base_mrp = row.price_inr
        if np.isnan(base_mrp) or base_mrp <= 0:
            base_mrp = 50.0
            
        pack_size = row.packaging_raw
        is_otc = 1 if "syrup" in str(row.dosage_form).lower() or "cream" in str(row.dosage_form).lower() else 0
        
        # Decide which platforms carry this
        platforms = []
        # Everyone gets at least 2 aggregators
        platforms.extend(np.random.choice(aggregator_ids, size=2, replace=False))
        
        # 50% chance of Truemeds/Discount pharmacy having it
        if np.random.random() > 0.5:
            platforms.extend(np.random.choice(discount_ids, size=1, replace=False))
            
        # Quick commerce only for OTC
        if is_otc and np.random.random() > 0.5:
            platforms.extend(np.random.choice(qcommerce_ids, size=1, replace=False))
            
        platforms = list(set(platforms))
        
        for p_id in platforms:
            # Determine discount logic based on pharmacy type
            discount_pct = 0.0
            
            if p_id in qcommerce_ids:
                # QCommerce is MRP or small discount, but high convenience
                discount_pct = np.random.uniform(0, 5)
            elif p_id in discount_ids:
                # Discount pharmacies offer 15% - 50% off
                discount_pct = np.random.uniform(15, 45)
            else:
                # Regular aggregators offer 5% - 22%
                discount_pct = np.random.uniform(5, 22)
                
            selling_price = base_mrp * (1 - (discount_pct / 100))
            # clamp to 2 decimals
            selling_price = round(selling_price, 2)
            discount_pct = round(discount_pct, 1)
            
            price_records.append((
                med_id, p_id, pack_size, base_mrp, selling_price, discount_pct, 1
            ))
            
        count += 1
        if count % batch_size == 0:
            cursor.executemany("""
                INSERT INTO prices (medicine_id, pharmacy_id, pack_size, mrp, selling_price, discount_percentage, in_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, price_records)
            price_records = []
            print(f"    processed {count} / {len(df)} medicines...")
            
    # Insert remaining
    if price_records:
        cursor.executemany("""
            INSERT INTO prices (medicine_id, pharmacy_id, pack_size, mrp, selling_price, discount_percentage, in_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, price_records)
    conn.commit()
    
    print("[7] Generating Medicine Category Count Stats...")
    cursor.execute("""
        UPDATE categories 
        SET medicine_count = (
            SELECT COUNT(*) FROM medicines WHERE medicines.category_id = categories.id
        )
    """)
    conn.commit()

    conn.close()
    
    print(f"\n[OK] Script Complete! Overall time: {time.time()-start_time:.2f}s")
    print(f"Ingested {len(df)} medicines into Medimin DB.")

if __name__ == "__main__":
    conn = init_fresh_db()
    ingest_data(conn)
