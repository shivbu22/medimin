"""
Medimin Seed Data — Realistic medicine price data across 6 pharmacy platforms.
50+ medicines across 9 categories with realistic price variations (15-45%).
"""

import sqlite3
import os
import random
from database import DB_PATH, init_db

random.seed(42)  # Reproducible data

# ═══════════════════════════════════════════
# PHARMACY PLATFORMS
# ═══════════════════════════════════════════
PHARMACIES = [
    {
        "name": "Tata 1mg",
        "slug": "tata-1mg",
        "website_url": "https://www.1mg.com",
        "logo_url": "/logos/1mg.svg",
        "rating": 4.4,
        "delivery_time": "1-2 days",
        "return_policy": "15 days return",
        "free_delivery_above": 149
    },
    {
        "name": "Apollo Pharmacy",
        "slug": "apollo-pharmacy",
        "website_url": "https://www.apollopharmacy.in",
        "logo_url": "/logos/apollo.svg",
        "rating": 4.3,
        "delivery_time": "1-3 days",
        "return_policy": "7 days return",
        "free_delivery_above": 199
    },
    {
        "name": "PharmEasy",
        "slug": "pharmeasy",
        "website_url": "https://www.pharmeasy.in",
        "logo_url": "/logos/pharmeasy.svg",
        "rating": 4.2,
        "delivery_time": "1-2 days",
        "return_policy": "15 days return",
        "free_delivery_above": 199
    },
    {
        "name": "Netmeds",
        "slug": "netmeds",
        "website_url": "https://www.netmeds.com",
        "logo_url": "/logos/netmeds.svg",
        "rating": 4.1,
        "delivery_time": "2-4 days",
        "return_policy": "7 days return",
        "free_delivery_above": 249
    },
    {
        "name": "Truemeds",
        "slug": "truemeds",
        "website_url": "https://www.truemeds.in",
        "logo_url": "/logos/truemeds.svg",
        "rating": 4.0,
        "delivery_time": "2-3 days",
        "return_policy": "30 days return",
        "free_delivery_above": 299
    },
    {
        "name": "MedPlusmart",
        "slug": "medplusmart",
        "website_url": "https://www.medplusmart.com",
        "logo_url": "/logos/medplus.svg",
        "rating": 4.1,
        "delivery_time": "1-3 days",
        "return_policy": "10 days return",
        "free_delivery_above": 199
    }
]

# ═══════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════
CATEGORIES = [
    {"name": "Pain & Fever", "slug": "pain-fever", "icon": "🔥", "description": "Pain relievers, anti-inflammatory and fever medication"},
    {"name": "Diabetes", "slug": "diabetes", "icon": "🩸", "description": "Insulin, metformin, and glucose management drugs"},
    {"name": "Heart & BP", "slug": "heart-bp", "icon": "❤️", "description": "Blood pressure, cholesterol and cardiac medication"},
    {"name": "Thyroid", "slug": "thyroid", "icon": "🦋", "description": "Thyroid hormone regulation medicines"},
    {"name": "Antibiotics", "slug": "antibiotics", "icon": "🦠", "description": "Antibacterial and anti-infective medicines"},
    {"name": "Gastric & Liver", "slug": "gastric-liver", "icon": "🫁", "description": "Antacids, PPI, and digestive health drugs"},
    {"name": "Vitamins & Supplements", "slug": "vitamins", "icon": "💪", "description": "Essential vitamins, minerals and health supplements"},
    {"name": "Respiratory", "slug": "respiratory", "icon": "🌬️", "description": "Asthma, allergy, and respiratory medicines"},
    {"name": "Skin & Allergy", "slug": "skin-allergy", "icon": "🧴", "description": "Antihistamines, derma creams, and allergy relief"},
]

# ═══════════════════════════════════════════
# MEDICINES (50+ across 9 categories)
# ═══════════════════════════════════════════
MEDICINES = [
    # --- Pain & Fever (8) ---
    {"name": "Dolo 650 Tablet", "slug": "dolo-650-tablet", "salt": "Paracetamol (650mg)", "mfr": "Micro Labs Ltd", "cat": "Pain & Fever", "form": "Tablet", "pack": "15 Tablets", "mrp": 33.28,
     "desc": "Dolo 650 is used to relieve pain including headache, migraine, toothache, period pain, and to reduce fever.",
     "uses": "Fever, Headache, Body ache, Toothache, Period pain",
     "side_effects": "Nausea, Allergic reaction, Liver damage (rare)"},

    {"name": "Crocin 650 Tablet", "slug": "crocin-650-tablet", "salt": "Paracetamol (650mg)", "mfr": "GSK Consumer Healthcare", "cat": "Pain & Fever", "form": "Tablet", "pack": "15 Tablets", "mrp": 35.00,
     "desc": "Crocin 650 is a paracetamol-based analgesic and antipyretic used for mild to moderate pain and fever.",
     "uses": "Fever, Pain relief, Cold & Flu symptoms",
     "side_effects": "Nausea, Skin rash (rare)"},

    {"name": "Combiflam Tablet", "slug": "combiflam-tablet", "salt": "Ibuprofen (400mg) + Paracetamol (325mg)", "mfr": "Sanofi India", "cat": "Pain & Fever", "form": "Tablet", "pack": "20 Tablets", "mrp": 42.80,
     "desc": "Combiflam is used to reduce fever and relieve pain from conditions like headache, dental pain, arthritis, and period pain.",
     "uses": "Headache, Toothache, Arthritis pain, Body ache, Period pain",
     "side_effects": "Stomach upset, Nausea, Dizziness"},

    {"name": "Saridon Tablet", "slug": "saridon-tablet", "salt": "Propyphenazone (150mg) + Paracetamol (250mg) + Caffeine (50mg)", "mfr": "Bayer Zydus Pharma", "cat": "Pain & Fever", "form": "Tablet", "pack": "10 Tablets", "mrp": 28.00,
     "desc": "Saridon is a triple-action headache relief tablet that works fast against headache, body ache, and toothache.",
     "uses": "Headache, Body ache, Toothache",
     "side_effects": "Dizziness, Nausea, Sleep disturbance"},

    {"name": "Disprin Tablet", "slug": "disprin-tablet", "salt": "Aspirin (350mg)", "mfr": "Reckitt Benckiser", "cat": "Pain & Fever", "form": "Dispersible Tablet", "pack": "10 Tablets", "mrp": 11.68,
     "desc": "Disprin is a dispersible aspirin tablet used for quick relief from headache, cold, and body pain.",
     "uses": "Headache, Body pain, Cold & Flu, Mild fever",
     "side_effects": "Stomach irritation, Nausea"},

    {"name": "Brufen 400 Tablet", "slug": "brufen-400-tablet", "salt": "Ibuprofen (400mg)", "mfr": "Abbott India", "cat": "Pain & Fever", "form": "Tablet", "pack": "15 Tablets", "mrp": 35.73,
     "desc": "Brufen 400 is a nonsteroidal anti-inflammatory drug (NSAID) used for pain relief and reducing inflammation.",
     "uses": "Joint pain, Toothache, Headache, Muscle pain, Period pain",
     "side_effects": "Stomach pain, Nausea, Diarrhea"},

    {"name": "Voveran SR 100 Tablet", "slug": "voveran-sr-100-tablet", "salt": "Diclofenac (100mg)", "mfr": "Novartis India", "cat": "Pain & Fever", "form": "Tablet", "pack": "10 Tablets", "mrp": 47.00,
     "desc": "Voveran SR 100 is used to relieve pain, inflammation and swelling in conditions like arthritis and acute injury.",
     "uses": "Arthritis, Joint pain, Muscle pain, Post-surgery pain",
     "side_effects": "Stomach upset, Dizziness, Headache"},

    {"name": "Sumo Tablet", "slug": "sumo-tablet", "salt": "Nimesulide (100mg) + Paracetamol (325mg)", "mfr": "Alkem Laboratories", "cat": "Pain & Fever", "form": "Tablet", "pack": "10 Tablets", "mrp": 44.00,
     "desc": "Sumo tablet is used for quick relief from pain and inflammation associated with various conditions.",
     "uses": "Fever, Pain, Inflammation, Headache",
     "side_effects": "Nausea, Diarrhea, Dizziness, Liver issues (rare)"},

    # --- Diabetes (7) ---
    {"name": "Glycomet GP 2 Tablet", "slug": "glycomet-gp-2-tablet", "salt": "Metformin (500mg) + Glimepiride (2mg)", "mfr": "USV Pvt Ltd", "cat": "Diabetes", "form": "Tablet", "pack": "10 Tablets", "mrp": 131.00,
     "desc": "Glycomet GP 2 is used to treat type 2 diabetes mellitus by controlling blood sugar levels.",
     "uses": "Type 2 Diabetes, Blood sugar control",
     "side_effects": "Nausea, Diarrhea, Hypoglycemia, Stomach pain"},

    {"name": "Glucophage 500 Tablet", "slug": "glucophage-500-tablet", "salt": "Metformin (500mg)", "mfr": "Franco-Indian Pharmaceuticals", "cat": "Diabetes", "form": "Tablet", "pack": "20 Tablets", "mrp": 26.78,
     "desc": "Glucophage 500 is a first-choice medicine for type 2 diabetes, reducing blood glucose levels.",
     "uses": "Type 2 Diabetes, Insulin resistance, PCOS",
     "side_effects": "Nausea, Diarrhea, Metallic taste, Stomach upset"},

    {"name": "Januvia 100mg Tablet", "slug": "januvia-100mg-tablet", "salt": "Sitagliptin (100mg)", "mfr": "MSD Pharmaceuticals", "cat": "Diabetes", "form": "Tablet", "pack": "7 Tablets", "mrp": 520.00,
     "desc": "Januvia 100mg is used to control blood sugar levels in adults with type 2 diabetes.",
     "uses": "Type 2 Diabetes",
     "side_effects": "Headache, Runny nose, Sore throat, Stomach pain"},

    {"name": "Galvus 50mg Tablet", "slug": "galvus-50mg-tablet", "salt": "Vildagliptin (50mg)", "mfr": "Novartis India", "cat": "Diabetes", "form": "Tablet", "pack": "14 Tablets", "mrp": 452.00,
     "desc": "Galvus 50mg is used to improve blood sugar control in patients with type 2 diabetes.",
     "uses": "Type 2 Diabetes",
     "side_effects": "Headache, Dizziness, Tremor, Nausea"},

    {"name": "Amaryl M 2mg Tablet", "slug": "amaryl-m-2mg-tablet", "salt": "Glimepiride (2mg) + Metformin (500mg)", "mfr": "Sanofi India", "cat": "Diabetes", "form": "Tablet", "pack": "10 Tablets", "mrp": 120.00,
     "desc": "Amaryl M is used in the treatment of type 2 diabetes mellitus.",
     "uses": "Type 2 Diabetes, Blood sugar control",
     "side_effects": "Hypoglycemia, Nausea, Headache"},

    {"name": "Trajenta 5mg Tablet", "slug": "trajenta-5mg-tablet", "salt": "Linagliptin (5mg)", "mfr": "Boehringer Ingelheim", "cat": "Diabetes", "form": "Tablet", "pack": "10 Tablets", "mrp": 490.00,
     "desc": "Trajenta 5mg is used to lower blood sugar levels in adults with type 2 diabetes.",
     "uses": "Type 2 Diabetes",
     "side_effects": "Runny nose, Cough, Headache"},

    {"name": "Gluformin G1 Tablet", "slug": "gluformin-g1-tablet", "salt": "Metformin (500mg) + Glimepiride (1mg)", "mfr": "Mankind Pharma", "cat": "Diabetes", "form": "Tablet", "pack": "10 Tablets", "mrp": 85.00,
     "desc": "Gluformin G1 is used to treat type 2 diabetes by controlling blood sugar levels.",
     "uses": "Type 2 Diabetes",
     "side_effects": "Nausea, Diarrhea, Hypoglycemia"},

    # --- Heart & BP (7) ---
    {"name": "Telmikind 40 Tablet", "slug": "telmikind-40-tablet", "salt": "Telmisartan (40mg)", "mfr": "Mankind Pharma", "cat": "Heart & BP", "form": "Tablet", "pack": "10 Tablets", "mrp": 95.00,
     "desc": "Telmikind 40 is used to treat high blood pressure (hypertension) and reduce the risk of heart attack and stroke.",
     "uses": "Hypertension, Heart failure prevention",
     "side_effects": "Dizziness, Diarrhea, Back pain"},

    {"name": "Amlokind 5 Tablet", "slug": "amlokind-5-tablet", "salt": "Amlodipine (5mg)", "mfr": "Mankind Pharma", "cat": "Heart & BP", "form": "Tablet", "pack": "15 Tablets", "mrp": 57.35,
     "desc": "Amlokind 5 is used to treat high blood pressure and chest pain (angina).",
     "uses": "Hypertension, Angina",
     "side_effects": "Swelling, Headache, Dizziness, Flushing"},

    {"name": "Ecosprin 75 Tablet", "slug": "ecosprin-75-tablet", "salt": "Aspirin (75mg)", "mfr": "USV Pvt Ltd", "cat": "Heart & BP", "form": "Tablet", "pack": "14 Tablets", "mrp": 7.72,
     "desc": "Ecosprin 75 is a blood-thinning medicine used to prevent heart attacks and strokes.",
     "uses": "Heart attack prevention, Stroke prevention, Blood thinning",
     "side_effects": "Stomach upset, Bleeding risk"},

    {"name": "Atorva 10 Tablet", "slug": "atorva-10-tablet", "salt": "Atorvastatin (10mg)", "mfr": "Zydus Lifesciences", "cat": "Heart & BP", "form": "Tablet", "pack": "15 Tablets", "mrp": 102.00,
     "desc": "Atorva 10 is a statin used to lower cholesterol and reduce the risk of heart disease.",
     "uses": "High cholesterol, Heart disease prevention",
     "side_effects": "Muscle pain, Headache, Nausea"},

    {"name": "Ramistar 5 Tablet", "slug": "ramistar-5-tablet", "salt": "Ramipril (5mg)", "mfr": "Lupin Ltd", "cat": "Heart & BP", "form": "Tablet", "pack": "15 Tablets", "mrp": 132.50,
     "desc": "Ramistar 5 is an ACE inhibitor used to treat high blood pressure and heart failure.",
     "uses": "Hypertension, Heart failure, Kidney protection",
     "side_effects": "Dry cough, Dizziness, Headache"},

    {"name": "Clopitab 75 Tablet", "slug": "clopitab-75-tablet", "salt": "Clopidogrel (75mg)", "mfr": "Lupin Ltd", "cat": "Heart & BP", "form": "Tablet", "pack": "10 Tablets", "mrp": 88.00,
     "desc": "Clopitab 75 prevents blood clots and reduces the risk of heart attack and stroke.",
     "uses": "Blood clot prevention, Heart attack prevention",
     "side_effects": "Bleeding, Bruising, Stomach pain"},

    {"name": "Metolar XR 50 Tablet", "slug": "metolar-xr-50-tablet", "salt": "Metoprolol Succinate (50mg)", "mfr": "Cipla Ltd", "cat": "Heart & BP", "form": "Tablet", "pack": "10 Tablets", "mrp": 105.00,
     "desc": "Metolar XR 50 is a beta-blocker used to treat high blood pressure, angina, and heart failure.",
     "uses": "Hypertension, Angina, Heart failure, Arrhythmia",
     "side_effects": "Dizziness, Tiredness, Slow heart rate"},

    # --- Thyroid (4) ---
    {"name": "Thyronorm 50mcg Tablet", "slug": "thyronorm-50mcg-tablet", "salt": "Thyroxine Sodium (50mcg)", "mfr": "Abbott India", "cat": "Thyroid", "form": "Tablet", "pack": "120 Tablets", "mrp": 140.00,
     "desc": "Thyronorm 50mcg is used to treat hypothyroidism by replacing the deficient thyroid hormone.",
     "uses": "Hypothyroidism, Goiter, Thyroid hormone replacement",
     "side_effects": "Headache, Palpitations, Weight changes, Tremors"},

    {"name": "Eltroxin 100mcg Tablet", "slug": "eltroxin-100mcg-tablet", "salt": "Thyroxine Sodium (100mcg)", "mfr": "GSK Pharmaceuticals", "cat": "Thyroid", "form": "Tablet", "pack": "100 Tablets", "mrp": 182.00,
     "desc": "Eltroxin 100mcg is prescribed for thyroid hormone replacement therapy.",
     "uses": "Hypothyroidism, Myxedema coma, Thyroid deficiency",
     "side_effects": "Anxiety, Tremors, Heart palpitations"},

    {"name": "Thyrox 75mcg Tablet", "slug": "thyrox-75mcg-tablet", "salt": "Thyroxine Sodium (75mcg)", "mfr": "Macleods Pharmaceuticals", "cat": "Thyroid", "form": "Tablet", "pack": "100 Tablets", "mrp": 135.00,
     "desc": "Thyrox 75mcg is used to treat hypothyroidism.",
     "uses": "Hypothyroidism",
     "side_effects": "Headache, Sweating, Weight loss"},

    {"name": "Thyrofit 25mcg Tablet", "slug": "thyrofit-25mcg-tablet", "salt": "Thyroxine Sodium (25mcg)", "mfr": "Torrent Pharmaceuticals", "cat": "Thyroid", "form": "Tablet", "pack": "100 Tablets", "mrp": 98.00,
     "desc": "Thyrofit 25mcg is used for the treatment of hypothyroidism.",
     "uses": "Hypothyroidism, Subclinical hypothyroidism",
     "side_effects": "Tremor, Palpitations, Weight changes"},

    # --- Antibiotics (6) ---
    {"name": "Augmentin 625 Duo Tablet", "slug": "augmentin-625-duo-tablet", "salt": "Amoxycillin (500mg) + Clavulanic Acid (125mg)", "mfr": "GSK Pharmaceuticals", "cat": "Antibiotics", "form": "Tablet", "pack": "10 Tablets", "mrp": 220.43,
     "desc": "Augmentin 625 Duo is a broad-spectrum antibiotic used to treat bacterial infections.",
     "uses": "Respiratory infections, UTI, Skin infections, Dental infections",
     "side_effects": "Diarrhea, Nausea, Vomiting, Skin rash"},

    {"name": "Azithral 500 Tablet", "slug": "azithral-500-tablet", "salt": "Azithromycin (500mg)", "mfr": "Alembic Pharmaceuticals", "cat": "Antibiotics", "form": "Tablet", "pack": "5 Tablets", "mrp": 113.39,
     "desc": "Azithral 500 is a macrolide antibiotic used to treat various bacterial infections.",
     "uses": "Throat infection, Ear infection, Pneumonia, Skin infection",
     "side_effects": "Nausea, Diarrhea, Stomach pain, Headache"},

    {"name": "Ciplox 500 Tablet", "slug": "ciplox-500-tablet", "salt": "Ciprofloxacin (500mg)", "mfr": "Cipla Ltd", "cat": "Antibiotics", "form": "Tablet", "pack": "10 Tablets", "mrp": 118.90,
     "desc": "Ciplox 500 is a fluoroquinolone antibiotic used to treat bacterial infections.",
     "uses": "UTI, Respiratory infections, Ear infections, Bone infections",
     "side_effects": "Nausea, Diarrhea, Headache, Dizziness"},

    {"name": "Monocef 200 Tablet", "slug": "monocef-200-tablet", "salt": "Cefixime (200mg)", "mfr": "Aristo Pharmaceuticals", "cat": "Antibiotics", "form": "Tablet", "pack": "10 Tablets", "mrp": 186.50,
     "desc": "Monocef 200 is a third-generation cephalosporin antibiotic.",
     "uses": "UTI, Gonorrhea, Throat infections, Ear infections",
     "side_effects": "Diarrhea, Stomach pain, Nausea"},

    {"name": "Moxikind CV 625 Tablet", "slug": "moxikind-cv-625-tablet", "salt": "Amoxycillin (500mg) + Clavulanic Acid (125mg)", "mfr": "Mankind Pharma", "cat": "Antibiotics", "form": "Tablet", "pack": "10 Tablets", "mrp": 174.00,
     "desc": "Moxikind CV 625 is a penicillin-type antibiotic used to treat bacterial infections.",
     "uses": "Respiratory infections, Ear infections, UTI, Skin infections",
     "side_effects": "Diarrhea, Nausea, Vomiting"},

    {"name": "Doxycycline 100mg Capsule", "slug": "doxycycline-100mg-capsule", "salt": "Doxycycline (100mg)", "mfr": "Cipla Ltd", "cat": "Antibiotics", "form": "Capsule", "pack": "10 Capsules", "mrp": 75.00,
     "desc": "Doxycycline is a tetracycline antibiotic used to treat acne, UTI, and other bacterial infections.",
     "uses": "Acne, UTI, Respiratory infections, Malaria prevention",
     "side_effects": "Stomach upset, Sun sensitivity, Nausea"},

    # --- Gastric & Liver (6) ---
    {"name": "Pan 40 Tablet", "slug": "pan-40-tablet", "salt": "Pantoprazole (40mg)", "mfr": "Alkem Laboratories", "cat": "Gastric & Liver", "form": "Tablet", "pack": "15 Tablets", "mrp": 123.00,
     "desc": "Pan 40 is a proton pump inhibitor (PPI) used to reduce stomach acid and treat acid reflux, GERD, and ulcers.",
     "uses": "GERD, Acid reflux, Stomach ulcers, Heartburn",
     "side_effects": "Headache, Diarrhea, Flatulence, Stomach pain"},

    {"name": "Pan D Capsule", "slug": "pan-d-capsule", "salt": "Pantoprazole (40mg) + Domperidone (30mg)", "mfr": "Alkem Laboratories", "cat": "Gastric & Liver", "form": "Capsule", "pack": "15 Capsules", "mrp": 172.50,
     "desc": "Pan D Capsule is used for treating acidity, acid reflux, heartburn and stomach ulcers.",
     "uses": "GERD, Acid reflux, Nausea, Vomiting, Bloating",
     "side_effects": "Headache, Diarrhea, Dry mouth"},

    {"name": "Rantac 150 Tablet", "slug": "rantac-150-tablet", "salt": "Ranitidine (150mg)", "mfr": "JB Chemicals", "cat": "Gastric & Liver", "form": "Tablet", "pack": "30 Tablets", "mrp": 42.00,
     "desc": "Rantac 150 is used for treating acidity, heartburn, and peptic ulcers.",
     "uses": "Acidity, Heartburn, Peptic ulcers, GERD",
     "side_effects": "Headache, Constipation, Diarrhea"},

    {"name": "Omez 20 Capsule", "slug": "omez-20-capsule", "salt": "Omeprazole (20mg)", "mfr": "Dr. Reddy's", "cat": "Gastric & Liver", "form": "Capsule", "pack": "15 Capsules", "mrp": 90.30,
     "desc": "Omez 20 is a proton pump inhibitor used to treat acid-related disorders of the stomach.",
     "uses": "GERD, Acid reflux, Stomach ulcers, Zollinger-Ellison syndrome",
     "side_effects": "Headache, Nausea, Diarrhea, Flatulence"},

    {"name": "Duphalac Solution", "slug": "duphalac-solution", "salt": "Lactulose (10g/15ml)", "mfr": "Abbott India", "cat": "Gastric & Liver", "form": "Syrup", "pack": "200ml", "mrp": 198.00,
     "desc": "Duphalac is a laxative used to treat chronic constipation and hepatic encephalopathy.",
     "uses": "Constipation, Hepatic encephalopathy, Liver cirrhosis",
     "side_effects": "Bloating, Gas, Stomach cramps"},

    {"name": "Hepamerz Sachets", "slug": "hepamerz-sachets", "salt": "L-Ornithine L-Aspartate (3g)", "mfr": "Win-Medicare Pvt Ltd", "cat": "Gastric & Liver", "form": "Sachet", "pack": "10 Sachets", "mrp": 310.00,
     "desc": "Hepamerz is used for the treatment and prevention of liver diseases.",
     "uses": "Liver disease, Hepatic encephalopathy, Liver support",
     "side_effects": "Nausea, Vomiting"},

    # --- Vitamins & Supplements (5) ---
    {"name": "Shelcal 500 Tablet", "slug": "shelcal-500-tablet", "salt": "Calcium Carbonate (500mg) + Vitamin D3 (250 IU)", "mfr": "Torrent Pharmaceuticals", "cat": "Vitamins & Supplements", "form": "Tablet", "pack": "15 Tablets", "mrp": 130.50,
     "desc": "Shelcal 500 is a calcium and vitamin D supplement used to prevent and treat calcium deficiency.",
     "uses": "Calcium deficiency, Osteoporosis, Bone health",
     "side_effects": "Constipation, Gas, Bloating"},

    {"name": "Becosules Capsule", "slug": "becosules-capsule", "salt": "Vitamin B Complex + Vitamin C", "mfr": "Pfizer Ltd", "cat": "Vitamins & Supplements", "form": "Capsule", "pack": "20 Capsules", "mrp": 30.00,
     "desc": "Becosules is a multivitamin capsule used to treat vitamin B complex and vitamin C deficiency.",
     "uses": "Vitamin B deficiency, Mouth ulcers, Fatigue, Hair health",
     "side_effects": "Nausea, Stomach upset (rare)"},

    {"name": "Limcee 500mg Tablet", "slug": "limcee-500mg-tablet", "salt": "Ascorbic Acid / Vitamin C (500mg)", "mfr": "Abbott India", "cat": "Vitamins & Supplements", "form": "Chewable Tablet", "pack": "15 Tablets", "mrp": 27.00,
     "desc": "Limcee is a vitamin C supplement used to treat and prevent vitamin C deficiency and boost immunity.",
     "uses": "Vitamin C deficiency, Scurvy, Immunity booster",
     "side_effects": "Stomach upset (high doses), Kidney stones (very high doses)"},

    {"name": "Supradyn Daily Tablet", "slug": "supradyn-daily-tablet", "salt": "Multivitamin + Multimineral", "mfr": "Bayer Zydus Pharma", "cat": "Vitamins & Supplements", "form": "Tablet", "pack": "15 Tablets", "mrp": 60.00,
     "desc": "Supradyn is a complete daily multivitamin that provides essential vitamins and minerals for energy and vitality.",
     "uses": "Daily nutrition, Energy, Immunity, Overall health",
     "side_effects": "Nausea (if taken on empty stomach)"},

    {"name": "Zincovit Tablet", "slug": "zincovit-tablet", "salt": "Zinc + Multivitamin + Multimineral", "mfr": "Apex Laboratories", "cat": "Vitamins & Supplements", "form": "Tablet", "pack": "15 Tablets", "mrp": 88.00,
     "desc": "Zincovit is a nutritional supplement with zinc, vitamins, and minerals for immune support.",
     "uses": "Zinc deficiency, Immunity booster, Nutritional support",
     "side_effects": "Nausea, Metallic taste (rare)"},

    # --- Respiratory (5) ---
    {"name": "Montair LC Tablet", "slug": "montair-lc-tablet", "salt": "Montelukast (10mg) + Levocetirizine (5mg)", "mfr": "Cipla Ltd", "cat": "Respiratory", "form": "Tablet", "pack": "15 Tablets", "mrp": 185.00,
     "desc": "Montair LC is used for the treatment of allergic conditions and asthma.",
     "uses": "Allergic rhinitis, Asthma, Sneezing, Runny nose, Itchy eyes",
     "side_effects": "Drowsiness, Headache, Dry mouth"},

    {"name": "Deriphyllin Retard 150 Tablet", "slug": "deriphyllin-retard-150-tablet", "salt": "Etophylline (77mg) + Theophylline (23mg)", "mfr": "Zydus Cadila", "cat": "Respiratory", "form": "Tablet", "pack": "15 Tablets", "mrp": 46.00,
     "desc": "Deriphyllin helps to relax the muscles in the airways and lungs, making breathing easier.",
     "uses": "Asthma, Chronic bronchitis, COPD, Wheezing",
     "side_effects": "Nausea, Headache, Palpitations, Insomnia"},

    {"name": "Foracort 200 Inhaler", "slug": "foracort-200-inhaler", "salt": "Budesonide (200mcg) + Formoterol (6mcg)", "mfr": "Cipla Ltd", "cat": "Respiratory", "form": "Inhaler", "pack": "1 Inhaler (120 doses)", "mrp": 435.00,
     "desc": "Foracort Inhaler is used for the maintenance treatment of asthma and COPD.",
     "uses": "Asthma, COPD, Breathing difficulty",
     "side_effects": "Oral thrush, Hoarse voice, Headache"},

    {"name": "Asthalin Inhaler", "slug": "asthalin-inhaler", "salt": "Salbutamol (100mcg)", "mfr": "Cipla Ltd", "cat": "Respiratory", "form": "Inhaler", "pack": "1 Inhaler (200 doses)", "mrp": 145.00,
     "desc": "Asthalin is a quick-relief bronchodilator used to treat asthma attacks and COPD.",
     "uses": "Asthma, COPD, Bronchospasm, Exercise-induced asthma",
     "side_effects": "Tremor, Palpitations, Headache"},

    {"name": "Alex Cough Syrup", "slug": "alex-cough-syrup", "salt": "Dextromethorphan (10mg) + Phenylephrine (5mg) + Chlorpheniramine (2mg)", "mfr": "Glenmark Pharmaceuticals", "cat": "Respiratory", "form": "Syrup", "pack": "100ml", "mrp": 92.00,
     "desc": "Alex Cough Syrup provides relief from dry cough and associated symptoms of cold and allergy.",
     "uses": "Dry cough, Cold, Allergic cough, Nasal congestion",
     "side_effects": "Drowsiness, Dry mouth, Dizziness"},

    # --- Skin & Allergy (5) ---
    {"name": "Allegra 120mg Tablet", "slug": "allegra-120mg-tablet", "salt": "Fexofenadine (120mg)", "mfr": "Sanofi India", "cat": "Skin & Allergy", "form": "Tablet", "pack": "10 Tablets", "mrp": 178.00,
     "desc": "Allegra 120 is a non-drowsy antihistamine used to relieve symptoms of seasonal allergies.",
     "uses": "Allergic rhinitis, Sneezing, Runny nose, Itchy eyes, Hives",
     "side_effects": "Headache, Nausea, Dizziness (rare)"},

    {"name": "Cetrizine 10mg Tablet", "slug": "cetrizine-10mg-tablet", "salt": "Cetirizine (10mg)", "mfr": "Cipla Ltd", "cat": "Skin & Allergy", "form": "Tablet", "pack": "10 Tablets", "mrp": 25.00,
     "desc": "Cetirizine is an antihistamine used to relieve allergy symptoms like sneezing, itching, and hives.",
     "uses": "Allergic rhinitis, Hay fever, Hives, Itching, Sneezing",
     "side_effects": "Drowsiness, Dry mouth, Headache"},

    {"name": "Betadine 10% Solution", "slug": "betadine-10-solution", "salt": "Povidone Iodine (10%)", "mfr": "Win-Medicare Pvt Ltd", "cat": "Skin & Allergy", "form": "Solution", "pack": "100ml", "mrp": 96.50,
     "desc": "Betadine is an antiseptic solution used for wound cleaning and prevention of skin infections.",
     "uses": "Wound cleaning, Skin infection prevention, Antiseptic",
     "side_effects": "Skin irritation, Staining"},

    {"name": "Candid B Cream", "slug": "candid-b-cream", "salt": "Clotrimazole (1%) + Beclometasone (0.025%)", "mfr": "Glenmark Pharmaceuticals", "cat": "Skin & Allergy", "form": "Cream", "pack": "15g Tube", "mrp": 92.00,
     "desc": "Candid B Cream is used to treat fungal skin infections with associated itching and redness.",
     "uses": "Fungal infections, Ringworm, Jock itch, Athlete's foot",
     "side_effects": "Burning, Itching at site, Skin thinning (prolonged use)"},

    {"name": "Clobetasol Cream", "slug": "clobetasol-cream", "salt": "Clobetasol Propionate (0.05%)", "mfr": "Glaxo SmithKline", "cat": "Skin & Allergy", "form": "Cream", "pack": "30g Tube", "mrp": 165.00,
     "desc": "Clobetasol is a potent topical corticosteroid used to treat severe skin conditions.",
     "uses": "Eczema, Psoriasis, Dermatitis, Skin inflammation",
     "side_effects": "Skin thinning, Stretch marks, Burning sensation"},
]


def generate_price(mrp: float, pharmacy_index: int, medicine_index: int) -> dict:
    """Generate realistic price variation for a pharmacy."""
    # Each pharmacy has different typical discount ranges
    discount_ranges = {
        0: (5, 28),    # 1mg — moderate discounts
        1: (3, 20),    # Apollo — lower discounts (premium brand)
        2: (8, 35),    # PharmEasy — aggressive discounts
        3: (6, 30),    # Netmeds — good discounts
        4: (12, 45),   # Truemeds — highest discounts (generic focus)
        5: (4, 22),    # MedPlusmart — moderate discounts
    }

    low, high = discount_ranges.get(pharmacy_index, (5, 25))

    # Use deterministic but varied discount
    seed_val = (medicine_index * 7 + pharmacy_index * 13 + 42) % 100
    discount_pct = low + (seed_val / 100) * (high - low)
    discount_pct = round(discount_pct, 1)

    selling_price = round(mrp * (1 - discount_pct / 100), 2)

    # Some items randomly out of stock (10% chance based on seed)
    in_stock = not ((medicine_index + pharmacy_index) % 10 == 7)

    return {
        "mrp": mrp,
        "selling_price": selling_price,
        "discount_percentage": discount_pct,
        "in_stock": in_stock
    }


def seed_database():
    """Populate the database with seed data."""
    # Remove old database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[x] Removed old database")

    # Initialize fresh tables
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # === Insert Categories ===
    print("[+] Inserting categories...")
    category_ids = {}
    for cat in CATEGORIES:
        cursor.execute('''
            INSERT INTO categories (name, slug, icon, description)
            VALUES (?, ?, ?, ?)
        ''', (cat["name"], cat["slug"], cat["icon"], cat["description"]))
        category_ids[cat["name"]] = cursor.lastrowid

    # === Insert Pharmacies ===
    print("[+] Inserting pharmacies...")
    pharmacy_ids = {}
    for idx, pharm in enumerate(PHARMACIES):
        cursor.execute('''
            INSERT INTO pharmacies (name, slug, website_url, logo_url, rating, delivery_time, return_policy, free_delivery_above)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pharm["name"], pharm["slug"], pharm["website_url"], pharm["logo_url"],
              pharm["rating"], pharm["delivery_time"], pharm["return_policy"], pharm["free_delivery_above"]))
        pharmacy_ids[pharm["name"]] = cursor.lastrowid

    # === Insert Medicines + Prices ===
    print("[+] Inserting medicines and prices...")
    for med_idx, med in enumerate(MEDICINES):
        cat_id = category_ids.get(med["cat"])

        cursor.execute('''
            INSERT INTO medicines (name, slug, active_salt, manufacturer, category_id, dosage_form, pack_size_label, description, uses, side_effects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (med["name"], med["slug"], med["salt"], med["mfr"], cat_id,
              med["form"], med["pack"], med["desc"], med["uses"], med["side_effects"]))
        medicine_id = cursor.lastrowid

        # Insert prices for each pharmacy
        for pharm_idx, pharm in enumerate(PHARMACIES):
            price_data = generate_price(med["mrp"], pharm_idx, med_idx)
            pharm_id = pharmacy_ids[pharm["name"]]

            # Build product URL
            product_url = f"{pharm['website_url']}/drugs/{med['slug']}"

            # Calculate unit price
            pack_num = int(''.join(filter(str.isdigit, med["pack"][:5])) or '10')
            unit_price = round(price_data["selling_price"] / pack_num, 2)

            cursor.execute('''
                INSERT INTO prices (medicine_id, pharmacy_id, pack_size, mrp, selling_price, unit_price, discount_percentage, in_stock, product_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (medicine_id, pharm_id, med["pack"], price_data["mrp"], price_data["selling_price"],
                  unit_price, price_data["discount_percentage"], price_data["in_stock"], product_url))

    # === Update category medicine counts ===
    cursor.execute('''
        UPDATE categories SET medicine_count = (
            SELECT COUNT(*) FROM medicines WHERE medicines.category_id = categories.id
        )
    ''')

    conn.commit()

    # Print summary
    cursor.execute("SELECT COUNT(*) FROM medicines")
    med_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pharmacies")
    pharm_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM prices")
    price_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]

    conn.close()

    print(f"\n[OK] Seed complete!")
    print(f"   Categories:   {cat_count}")
    print(f"   Medicines:    {med_count}")
    print(f"   Pharmacies:   {pharm_count}")
    print(f"   Price points: {price_count}")


if __name__ == "__main__":
    seed_database()
