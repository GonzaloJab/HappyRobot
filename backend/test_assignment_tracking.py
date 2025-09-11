"""
Tests for assignment tracking functionality
"""

import pytest
from datetime import datetime
from app.main import app, shipments_db
from app.models import Shipment, ShipmentCreate, ShipmentUpdate
from fastapi.testclient import TestClient

client = TestClient(app)

class TestAssignmentTracking:
    """Test assignment tracking functionality"""
    
    def setup_method(self):
        """Clear the database before each test"""
        shipments_db.clear()
    
    def test_create_shipment_sets_assigned_via_url_true(self):
        """Test that creating a shipment via API sets assigned_via_url to True"""
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
    
    def test_update_shipment_sets_assigned_via_url_true(self):
        """Test that updating a shipment via API sets assigned_via_url to True"""
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
        
        # Update the shipment
        update_data = {"status": "agreed", "agreed_price": 1500.0}
        response = client.patch(f"/shipments/{shipment_id}", json=update_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_via_url"] is True
    
    def test_update_shipment_manual_sets_assigned_via_url_false(self):
        """Test that updating a shipment via manual endpoint sets assigned_via_url to False"""
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
    
    def test_filter_by_assigned_via_url(self):
        """Test filtering shipments by assigned_via_url"""
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
    
    def test_stats_endpoint_returns_correct_split(self):
        """Test that stats endpoint returns correct manual vs URL/API split"""
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
    
    def test_stats_endpoint_with_filters(self):
        """Test that stats endpoint respects filters"""
        # Create shipments with different statuses
        shipment1_data = {
            "load_id": "LD-2025-0001",
            "origin": "Madrid",
            "destination": "Paris",
            "pickup_datetime": "2025-01-15T08:00:00Z",
            "delivery_datetime": "2025-01-16T18:00:00Z",
            "status": "agreed",
            "agreed_price": 1500.0,
            "carrier_description": "Test Carrier"
        }
        
        shipment2_data = {
            "load_id": "LD-2025-0002",
            "origin": "Barcelona",
            "destination": "Lyon",
            "pickup_datetime": "2025-01-15T08:00:00Z",
            "delivery_datetime": "2025-01-16T18:00:00Z",
            "status": "pending"
        }
        
        # Create both shipments
        response1 = client.post("/shipments", json=shipment1_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
        response2 = client.post("/shipments", json=shipment2_data, headers={"X-API-Key": "happyrobot-api-key-2025"})
        
        # Debug: Check what was actually created
        print(f"Shipment 1 response: {response1.status_code}")
        if response1.status_code == 201:
            data1 = response1.json()
            print(f"Shipment 1: status={data1['status']}, assigned_via_url={data1['assigned_via_url']}")
        
        print(f"Shipment 2 response: {response2.status_code}")
        if response2.status_code == 201:
            data2 = response2.json()
            print(f"Shipment 2: status={data2['status']}, assigned_via_url={data2['assigned_via_url']}")
        
        # Get all shipments to debug
        all_response = client.get("/shipments", headers={"X-API-Key": "happyrobot-api-key-2025"})
        if all_response.status_code == 200:
            all_shipments = all_response.json()
            print(f"All shipments count: {len(all_shipments)}")
            for s in all_shipments:
                print(f"  - {s['load_id']}: status={s['status']}, assigned_via_url={s['assigned_via_url']}")
        
        # Get stats filtered by status=agreed
        response = client.get("/shipments/stats?status=agreed", headers={"X-API-Key": "happyrobot-api-key-2025"})
        
        assert response.status_code == 200
        stats = response.json()
        print(f"Stats for status=agreed: {stats}")
        
        # Should only count the agreed shipment (created via API, so assigned_via_url=True)
        assert stats["url_api"]["count"] == 1
        assert stats["manual"]["count"] == 0
        
        # Get stats filtered by status=pending
        response = client.get("/shipments/stats?status=pending", headers={"X-API-Key": "happyrobot-api-key-2025"})
        
        assert response.status_code == 200
        stats = response.json()
        
        # Should only count the pending shipment
        assert stats["url_api"]["count"] == 1
        assert stats["manual"]["count"] == 0
