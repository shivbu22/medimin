import difflib
import re

def normalize_price(match_query: str, raw_name: str, raw_pack: str, raw_price: float) -> dict:
    """
    Standardizes raw scraping result into an 'Apples-to-Apples' comparison object.
    """
    # 1. Similarity Match
    similarity = difflib.SequenceMatcher(None, match_query.lower(), raw_name.lower()).ratio()
    
    # 2. Extract Pack Size (improved heuristic)
    # Search for numeric patterns like '15 tablets', 'strip of 10', '20.0 tabs'
    pack_size = 1
    pack_matches = re.findall(r'(\d+)', raw_pack)
    if not pack_matches:
        # try checking the name itself
        pack_matches = re.findall(r'(\d+)', raw_name)
        
    if pack_matches:
        # Heuristic: usually the largest number in a pack description is the count
        # (avoiding things like 650 in 'Dolo 650')
        counts = [int(x) for x in pack_matches if int(x) < 500] 
        if counts:
            pack_size = max(counts)

    # 3. Calculate Normalized Unit Price
    unit_price = round(raw_price / pack_size, 2)
    
    return {
        "raw_name": raw_name,
        "is_exact_match": similarity > 0.8,
        "is_similar": similarity > 0.4,
        "pack_size": pack_size,
        "selling_price": raw_price,
        "unit_price": unit_price,
        "similarity_score": round(similarity, 2)
    }
