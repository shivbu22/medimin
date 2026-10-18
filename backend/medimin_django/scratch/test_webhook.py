import requests
import json

URL = "http://127.0.0.1:8000/api/v1/webhooks/n8n-complete/"
SECRET = "medimin_secure_sync_2026_v1"
MEDICINE_NAME = "Augmentin 625 Duo Tablet"

payload = {
    "query": MEDICINE_NAME,
    "status": "finished"
}

headers = {
    "Content-Type": "application/json",
    "X-Webhook-Secret": SECRET
}

print(f"Testing Authorized Callback to {URL}...")
response = requests.post(URL, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")

if response.status_code == 200:
    print("SUCCESS: Callback processed correctly.")
else:
    print("FAILURE: Callback failed.")
