#!/usr/bin/env python3
"""
Quick test to verify the stats endpoint works
"""

from fastapi.testclient import TestClient
from app.main import app, shipments_db

def test_stats_endpoint():
    client = TestClient(app)
    shipments_db.clear()
    
    # Create a shipment with agreed status
    shipment_data = {
        "load_id": "LD-2025-0001",
        "origin": "Madrid",
        "destination": "Paris",
        "pickup_datetime": "2025-01-15T08:00:00Z",
        "delivery_datetime": "2025-01-16T18:00:00Z",
        "status": "agreed",
        "agreed_price": 1500.0,
        "carrier_description": "Test Carrier"
    }
    
    # Create shipment
    response = client.post("/shipments", json=shipment_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    print(f"Create response: {response.status_code}")
    if response.status_code != 201:
        print(f"Error: {response.text}")
        return
    
    # Get stats
    response = client.get("/shipments/stats", headers={"X-API-Key": "happyrobot-api-key-2025"})
    print(f"Stats response: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Stats: {stats}")
    else:
        print(f"Error: {response.text}")
    
    # Get stats filtered by status=agreed
    response = client.get("/shipments/stats?status=agreed", headers={"X-API-Key": "happyrobot-api-key-2025"})
    print(f"Filtered stats response: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Filtered stats: {stats}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_stats_endpoint()
