import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_endpoint(name, path, params=None):
    print(f"Testing {name} ({path})...")
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}{path}", params=params)
        duration = time.time() - start_time
        print(f"  Status: {response.status_code}")
        print(f"  Duration: {duration:.2f}s")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"  Count: {len(data)}")
                if len(data) > 0:
                    print(f"  First item: {json.dumps(data[0], indent=2)[:200]}...")
            else:
                print(f"  Data: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {str(e)}")
    print("-" * 30)

if __name__ == "__main__":
    test_endpoint("Stats", "/stats/")
    test_endpoint("Autocomplete", "/autocomplete/", params={"q": "Paracet"})
    test_endpoint("Search", "/search/", params={"q": "Paracetamol"})
    # Test detail view with a verified slug from medicine table
    test_endpoint("Medicine Detail", "/medicines/augmentin-625-duo-tablet-0/")
    
    # Test popular
    test_endpoint("Popular", "/medicines/popular/")
    
    # Test compat-autocomplete
    test_endpoint("Autocomplete Compat", "/medicines/autocomplete/", params={"q": "Paracet"})

    # Test redirect (using price ID 1 or similar)
    test_endpoint("Redirect", "/redirect/1/", params={"sid": "test-session"})
