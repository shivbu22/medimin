"""
Fast bulk migration from medimin.db → Django SQLite using bulk_create.
Inserts in batches of 2000 rows — 50-100x faster than row-by-row.
"""
import os
import sys
import sqlite3
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction, connection
from api.models import Category, Medicine, Pharmacy, Price

OLD_DB = os.path.join(os.path.dirname(__file__), '..', 'medimin.db')
BATCH_SIZE = 2000


def truncate_tables():
    """Clear existing data so we can do a clean re-import."""
    print("Clearing existing data...")
    with transaction.atomic():
        Price.objects.all().delete()
        Medicine.objects.all().delete()
        Pharmacy.objects.all().delete()
        Category.objects.all().delete()
    print("Done. Tables cleared.")


def migrate_categories(cursor):
    print("\n[1/4] Migrating Categories...")
    cursor.execute("SELECT id, name, slug, icon, description, medicine_count FROM categories")
    rows = cursor.fetchall()
    objs = [
        Category(
            id=r['id'], name=r['name'], slug=r['slug'],
            icon=r['icon'] or '💊',
            description=r['description'],
            medicine_count=r['medicine_count'] or 0
        )
        for r in rows
    ]
    Category.objects.bulk_create(objs, ignore_conflicts=True)
    print(f"  -> {len(objs)} categories migrated.")


def migrate_pharmacies(cursor):
    print("\n[2/4] Migrating Pharmacies...")
    cursor.execute("SELECT id, name, slug, website_url, logo_url, rating, delivery_time, return_policy, min_order, free_delivery_above, is_active FROM pharmacies")
    rows = cursor.fetchall()
    objs = [
        Pharmacy(
            id=r['id'], name=r['name'], slug=r['slug'],
            website_url=r['website_url'] or '',
            logo_url=r['logo_url'],
            rating=r['rating'] or 4.0,
            delivery_time=r['delivery_time'] or '1-3 days',
            return_policy=r['return_policy'] or '7 days return',
            min_order=r['min_order'] or 0.0,
            free_delivery_above=r['free_delivery_above'] or 299.0,
            is_active=bool(r['is_active'])
        )
        for r in rows
    ]
    Pharmacy.objects.bulk_create(objs, ignore_conflicts=True)
    print(f"  -> {len(objs)} pharmacies migrated.")


def migrate_medicines(cursor):
    print("\n[3/4] Migrating Medicines (253k rows, will take ~1-2 min)...")
    cursor.execute("SELECT id, name, slug, active_salt, manufacturer, category_id, dosage_form, pack_size_label, description, uses, side_effects, is_otc, is_prescription, dpco_controlled, image_url FROM medicines")
    
    # Load all category IDs into memory for fast lookup
    cat_ids = set(Category.objects.values_list('id', flat=True))
    
    batch = []
    total = 0
    start = time.time()

    for r in cursor:
        slug = (r['slug'] or '').strip()
        if not slug:
            slug = f"medicine-{r['id']}"
        
        cat_id = r['category_id'] if r['category_id'] in cat_ids else None

        batch.append(Medicine(
            id=r['id'],
            name=r['name'] or 'Unknown',
            slug=slug,
            active_salt=r['active_salt'] or '',
            manufacturer=r['manufacturer'] or '',
            category_id=cat_id,
            dosage_form=r['dosage_form'] or 'Tablet',
            pack_size_label=r['pack_size_label'] or '10 Tablets',
            description=r['description'],
            uses=r['uses'],
            side_effects=r['side_effects'],
            is_otc=bool(r['is_otc']),
            is_prescription=bool(r['is_prescription']),
            dpco_controlled=bool(r['dpco_controlled']),
            image_url=r['image_url']
        ))

        if len(batch) >= BATCH_SIZE:
            Medicine.objects.bulk_create(batch, ignore_conflicts=True)
            total += len(batch)
            elapsed = time.time() - start
            print(f"  -> {total:,} medicines inserted... ({elapsed:.0f}s)")
            batch = []

    if batch:
        Medicine.objects.bulk_create(batch, ignore_conflicts=True)
        total += len(batch)

    print(f"  -> DONE: {total:,} medicines in {time.time()-start:.1f}s")


def migrate_prices(cursor):
    print("\n[4/4] Migrating Prices (645k rows, will take ~2-3 min)...")
    cursor.execute("SELECT id, medicine_id, pharmacy_id, pack_size, mrp, selling_price, unit_price, discount_percentage, in_stock, product_url FROM prices")

    # Pre-load all valid IDs
    med_ids = set(Medicine.objects.values_list('id', flat=True))
    pharm_ids = set(Pharmacy.objects.values_list('id', flat=True))

    batch = []
    total = 0
    skipped = 0
    start = time.time()

    for r in cursor:
        if r['medicine_id'] not in med_ids or r['pharmacy_id'] not in pharm_ids:
            skipped += 1
            continue

        batch.append(Price(
            id=r['id'],
            medicine_id=r['medicine_id'],
            pharmacy_id=r['pharmacy_id'],
            pack_size=r['pack_size'] or '10 Tablets',
            mrp=r['mrp'] or 0.0,
            selling_price=r['selling_price'] or 0.0,
            unit_price=r['unit_price'],
            discount_percentage=r['discount_percentage'] or 0.0,
            in_stock=bool(r['in_stock']),
            product_url=r['product_url']
        ))

        if len(batch) >= BATCH_SIZE:
            Price.objects.bulk_create(batch, ignore_conflicts=True)
            total += len(batch)
            elapsed = time.time() - start
            print(f"  -> {total:,} prices inserted... ({elapsed:.0f}s)")
            batch = []

    if batch:
        Price.objects.bulk_create(batch, ignore_conflicts=True)
        total += len(batch)

    print(f"  -> DONE: {total:,} prices, {skipped} skipped in {time.time()-start:.1f}s")


def main():
    t0 = time.time()
    print(f"Starting FAST bulk migration from {OLD_DB}")
    
    if not os.path.exists(OLD_DB):
        print(f"ERROR: {OLD_DB} not found! Make sure you run from medimin_django/")
        sys.exit(1)

    conn = sqlite3.connect(OLD_DB)
    conn.row_factory = sqlite3.Row
    # Enable WAL for faster reading
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    cursor = conn.cursor()

    truncate_tables()
    migrate_categories(cursor)
    migrate_pharmacies(cursor)
    migrate_medicines(cursor)
    migrate_prices(cursor)

    conn.close()
    print(f"\n[SUCCESS] Full migration complete in {time.time()-t0:.1f}s")
    print(f"   Categories: {Category.objects.count()}")
    print(f"   Pharmacies: {Pharmacy.objects.count()}")
    print(f"   Medicines:  {Medicine.objects.count():,}")
    print(f"   Prices:     {Price.objects.count():,}")


if __name__ == '__main__':
    main()
