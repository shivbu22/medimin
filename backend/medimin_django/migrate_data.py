import os
import sqlite3
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Category, Medicine, Pharmacy, Price, PriceHistory, AnalyticsClick

OLD_DB = '../medimin.db'

def migrate():
    if not os.path.exists(OLD_DB):
        print(f"Error: {OLD_DB} not found.")
        return

    conn = sqlite3.connect(OLD_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("Migrating Categories...")
    cursor.execute("SELECT * FROM categories")
    for row in cursor.fetchall():
        Category.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
            icon=row['icon'],
            description=row['description'],
            medicine_count=row['medicine_count']
        )

    print("Migrating Pharmacies...")
    cursor.execute("SELECT * FROM pharmacies")
    for row in cursor.fetchall():
        Pharmacy.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
            website_url=row['website_url'],
            logo_url=row['logo_url'],
            rating=row['rating'],
            delivery_time=row['delivery_time'],
            return_policy=row['return_policy'],
            min_order=row['min_order'],
            free_delivery_above=row['free_delivery_above'],
            is_active=bool(row['is_active'])
        )

    print("Migrating Medicines...")
    cursor.execute("SELECT * FROM medicines")
    for row in cursor.fetchall():
        # Get category object
        category = None
        if row['category_id']:
            category = Category.objects.filter(id=row['category_id']).first()
            
        Medicine.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
            active_salt=row['active_salt'],
            manufacturer=row['manufacturer'],
            category=category,
            dosage_form=row['dosage_form'],
            pack_size_label=row['pack_size_label'],
            description=row['description'],
            uses=row['uses'],
            side_effects=row['side_effects'],
            is_otc=bool(row['is_otc']),
            is_prescription=bool(row['is_prescription']),
            dpco_controlled=bool(row['dpco_controlled']),
            image_url=row['image_url']
        )

    print("Migrating Prices...")
    cursor.execute("SELECT * FROM prices")
    for row in cursor.fetchall():
        try:
            medicine = Medicine.objects.get(id=row['medicine_id'])
            pharmacy = Pharmacy.objects.get(id=row['pharmacy_id'])
            Price.objects.get_or_create(
                id=row['id'],
                medicine=medicine,
                pharmacy=pharmacy,
                pack_size=row['pack_size'],
                mrp=row['mrp'],
                selling_price=row['selling_price'],
                unit_price=row['unit_price'],
                discount_percentage=row['discount_percentage'],
                in_stock=bool(row['in_stock']),
                product_url=row['product_url']
            )
        except Medicine.DoesNotExist:
            print(f"Skipping price {row['id']} - Medicine {row['medicine_id']} not found")
        except Pharmacy.DoesNotExist:
            print(f"Skipping price {row['id']} - Pharmacy {row['pharmacy_id']} not found")

    print("Data migration complete!")
    conn.close()

if __name__ == "__main__":
    migrate()
