#!/usr/bin/env python3
"""
Quick script to add a single phone call with string fields
"""

import requests
import json
import random

# Configuration
BASE_URL = "http://happyrobot-1700442240.eu-north-1.elb.amazonaws.com"
BASE_URL = "http://localhost:8000"
API_KEY = "HapRob-OTVHhErcXLu2eKkUMP6lDtrd8UNi61KZo4FvGALqem0NoJO1uWlz7OywCN0BNoNaG2x5Y"

headers = {'Content-Type': 'application/json', 'X-API-Key': API_KEY}

# Get random shipment
shipment = requests.get(f"{BASE_URL}/shipments/random", headers=headers).json()
print(f"Adding call to: {shipment['load_id']}")

# Add phone call with string fields
call_data = {
    "agreed": "True",  # String boolean
    "minutes": "12.5",  # String number
    "call_type": "agent",
    "sentiment": "positive",
    "notes": "Quick test call with string fields",
    "call_id": f"QUICK-{random.randint(1000, 9999)}"
}

result = requests.post(f"{BASE_URL}/shipments/{shipment['id']}/phone-calls", json=call_data, headers=headers)

if result.status_code == 201:
    call = result.json()
    print(f"✅ Success! Call ID: {call['id']}")
    print(f"   Parsed agreed: {call['agreed']} (type: {type(call['agreed']).__name__})")
    print(f"   Parsed minutes: {call['minutes']} (type: {type(call['minutes']).__name__})")
else:
    print(f"❌ Failed: {result.status_code} - {result.text}")
