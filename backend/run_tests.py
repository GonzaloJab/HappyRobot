#!/usr/bin/env python3
"""
Simple test runner for assignment tracking functionality
"""

import sys
import traceback
from datetime import datetime, timedelta
from app.main import app, shipments_db
from app.models import Shipment
from fastapi.testclient import TestClient

def run_test(test_func, test_name):
    """Run a single test and report results"""
    try:
        test_func()
        print(f"✅ {test_name}")
        return True
    except Exception as e:
        print(f"❌ {test_name}: {str(e)}")
        traceback.print_exc()
        return False

def test_create_shipment_sets_assigned_via_url_true():
    """Test that creating a shipment via API sets assigned_via_url to True"""
    client = TestClient(app)
    shipments_db.clear()
    
    shipment_data = {
        "load_id": "LD-2025-0001",
        "origin": "Madrid",
        "destination": "Paris",
        "pickup_datetime": "2025-01-15T08:00:00Z",
        "delivery_datetime": "2025-01-16T18:00:00Z",
        "status": "pending"
    }
    
    response = client.post("/shipments", json=shipment_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["assigned_via_url"] is True

def test_update_shipment_manual_sets_assigned_via_url_false():
    """Test that updating a shipment via manual endpoint sets assigned_via_url to False"""
    client = TestClient(app)
    shipments_db.clear()
    
    # Create a shipment first
    shipment_data = {
        "load_id": "LD-2025-0001",
        "origin": "Madrid",
        "destination": "Paris",
        "pickup_datetime": "2025-01-15T08:00:00Z",
        "delivery_datetime": "2025-01-16T18:00:00Z",
        "status": "pending"
    }
    
    create_response = client.post("/shipments", json=shipment_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    shipment_id = create_response.json()["id"]
    
    # Update the shipment via manual endpoint
    update_data = {"status": "agreed", "agreed_price": 1500.0}
    response = client.patch(f"/shipments/{shipment_id}/manual", json=update_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_via_url"] is False

def test_stats_endpoint_returns_correct_split():
    """Test that stats endpoint returns correct manual vs URL/API split"""
    client = TestClient(app)
    shipments_db.clear()
    
    # Create shipments with different assignment sources
    shipment1_data = {
        "load_id": "LD-2025-0001",
        "origin": "Madrid",
        "destination": "Paris",
        "pickup_datetime": "2025-01-15T08:00:00Z",
        "delivery_datetime": "2025-01-16T18:00:00Z",
        "status": "agreed",
        "agreed_price": 1500.0,
        "loadboard_rate": 1400.0,
        "avg_time_per_call_seconds": 120.0
    }
    
    shipment2_data = {
        "load_id": "LD-2025-0002",
        "origin": "Barcelona",
        "destination": "Lyon",
        "pickup_datetime": "2025-01-15T08:00:00Z",
        "delivery_datetime": "2025-01-16T18:00:00Z",
        "status": "agreed",
        "agreed_price": 2000.0,
        "loadboard_rate": 1800.0,
        "avg_time_per_call_seconds": 90.0
    }
    
    # Create via API (assigned_via_url=True)
    client.post("/shipments", json=shipment1_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    # Create via API and then update via manual (assigned_via_url=False)
    create_response = client.post("/shipments", json=shipment2_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    shipment2_id = create_response.json()["id"]
    client.patch(f"/shipments/{shipment2_id}/manual", json={"status": "agreed"}, headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    # Get stats
    response = client.get("/shipments/stats", headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    assert response.status_code == 200
    stats = response.json()
    
    # Check structure
    assert "manual" in stats
    assert "url_api" in stats
    
    # Check manual stats
    assert stats["manual"]["count"] == 1
    assert stats["manual"]["total_agreed_price"] == 2000.0
    assert stats["manual"]["total_agreed_minus_loadboard"] == 200.0
    assert stats["manual"]["avg_time_per_call_seconds"] == 90.0
    
    # Check URL/API stats
    assert stats["url_api"]["count"] == 1
    assert stats["url_api"]["total_agreed_price"] == 1500.0
    assert stats["url_api"]["total_agreed_minus_loadboard"] == 100.0
    assert stats["url_api"]["avg_time_per_call_seconds"] == 120.0

def test_filter_by_assigned_via_url():
    """Test filtering shipments by assigned_via_url"""
    client = TestClient(app)
    shipments_db.clear()
    
    # Create shipments with different assignment sources
    shipment1_data = {
        "load_id": "LD-2025-0001",
        "origin": "Madrid",
        "destination": "Paris",
        "pickup_datetime": "2025-01-15T08:00:00Z",
        "delivery_datetime": "2025-01-16T18:00:00Z"
    }
    
    shipment2_data = {
        "load_id": "LD-2025-0002",
        "origin": "Barcelona",
        "destination": "Lyon",
        "pickup_datetime": "2025-01-15T08:00:00Z",
        "delivery_datetime": "2025-01-16T18:00:00Z"
    }
    
    # Create via API (assigned_via_url=True)
    client.post("/shipments", json=shipment1_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    # Create via API and then update via manual (assigned_via_url=False)
    create_response = client.post("/shipments", json=shipment2_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
    shipment2_id = create_response.json()["id"]
    client.patch(f"/shipments/{shipment2_id}/manual", json={"status": "agreed"}, headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    # Test filtering
    response_true = client.get("/shipments?assigned_via_url=true", headers={"X-API-Key": "happyrobot-api-key-2025"})
    response_false = client.get("/shipments?assigned_via_url=false", headers={"X-API-Key": "happyrobot-api-key-2025"})
    
    assert response_true.status_code == 200
    assert response_false.status_code == 200
    
    # Should have one shipment with assigned_via_url=True and one with False
    assert len(response_true.json()) == 1
    assert len(response_false.json()) == 1

def main():
    """Run all tests"""
    print("Running Assignment Tracking Tests...")
    print("=" * 50)
    
    tests = [
        (test_create_shipment_sets_assigned_via_url_true, "Create shipment sets assigned_via_url=True"),
        (test_update_shipment_manual_sets_assigned_via_url_false, "Manual update sets assigned_via_url=False"),
        (test_stats_endpoint_returns_correct_split, "Stats endpoint returns correct split"),
        (test_filter_by_assigned_via_url, "Filter by assigned_via_url works"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func, test_name in tests:
        if run_test(test_func, test_name):
            passed += 1
    
    print("=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
