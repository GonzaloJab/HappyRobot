"""
Comprehensive test suite for the updated Loads API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app, shipments_db

client = TestClient(app)

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestShipmentsEndpoint:
    """Test shipments endpoint"""
    
    def setup_method(self):
        """Clear the database before each test"""
        shipments_db.clear()
    
    def test_get_shipments_empty(self):
        """Test getting shipments when database is empty"""
        response = client.get("/shipments")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_shipments_with_data(self):
        """Test getting shipments with data"""
        # Create some test data
        shipment1 = {
            "load_id": "LD-001",
            "origin": "City A",
            "destination": "City B",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        }
        shipment2 = {
            "load_id": "LD-002",
            "origin": "City C",
            "destination": "City D",
            "pickup_datetime": "2024-01-03T08:00:00Z",
            "delivery_datetime": "2024-01-04T18:00:00Z"
        }

        client.post("/shipments", json=shipment1)
        client.post("/shipments", json=shipment2)

        response = client.get("/shipments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["load_id"] in ["LD-001", "LD-002"]
        assert data[1]["load_id"] in ["LD-001", "LD-002"]
    
    def test_get_shipments_sorted_by_created_at(self):
        """Test that shipments are sorted by created_at descending"""
        # Create shipments with slight delay
        client.post("/shipments", json={
            "load_id": "LD-FIRST",
            "origin": "Origin A",
            "destination": "Destination A",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        client.post("/shipments", json={
            "load_id": "LD-SECOND",
            "origin": "Origin B",
            "destination": "Destination B",
            "pickup_datetime": "2024-01-03T08:00:00Z",
            "delivery_datetime": "2024-01-04T18:00:00Z"
        })
        
        response = client.get("/shipments")
        data = response.json()
        assert len(data) == 2
        # Second shipment should be first (newest first)
        assert data[0]["load_id"] == "LD-SECOND"
        assert data[1]["load_id"] == "LD-FIRST"

class TestCreateShipment:
    """Test shipment creation"""
    
    def setup_method(self):
        """Clear the database before each test"""
        shipments_db.clear()
    
    def test_create_shipment_minimal(self):
        """Test creating a shipment with only required fields"""
        shipment_data = {
            "load_id": "LD-MINIMAL",
            "origin": "Origin City",
            "destination": "Destination City",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        }
        
        response = client.post("/shipments", json=shipment_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["load_id"] == "LD-MINIMAL"
        assert data["origin"] == "Origin City"
        assert data["destination"] == "Destination City"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_shipment_complete(self):
        """Test creating a shipment with all fields"""
        shipment_data = {
            "load_id": "LD-COMPLETE",
            "origin": "Los Angeles, CA",
            "destination": "New York, NY",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-03T18:00:00Z",
            "equipment_type": "Dry Van",
            "loadboard_rate": 2500.50,
            "notes": "Fragile cargo",
            "weight": 1500.0,
            "commodity_type": "Electronics",
            "num_of_pieces": 100,
            "miles": 2800.0,
            "dimensions": "48x40x60 in"
        }
        
        response = client.post("/shipments", json=shipment_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["load_id"] == "LD-COMPLETE"
        assert data["origin"] == "Los Angeles, CA"
        assert data["destination"] == "New York, NY"
        assert data["equipment_type"] == "Dry Van"
        assert data["loadboard_rate"] == 2500.50
        assert data["notes"] == "Fragile cargo"
        assert data["weight"] == 1500.0
        assert data["commodity_type"] == "Electronics"
        assert data["num_of_pieces"] == 100
        assert data["miles"] == 2800.0
        assert data["dimensions"] == "48x40x60 in"
        assert data["status"] == "pending"
    
    def test_create_shipment_validation_missing_required_fields(self):
        """Test shipment creation validation - missing required fields"""
        response = client.post("/shipments", json={"destination": "Test City"})
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_create_shipment_validation_empty_load_id(self):
        """Test shipment creation validation - empty load_id"""
        response = client.post("/shipments", json={
            "load_id": "",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        assert response.status_code == 422
    
    def test_create_shipment_validation_load_id_too_long(self):
        """Test shipment creation validation - load_id too long"""
        long_load_id = "x" * 51  # Exceeds max_length=50
        response = client.post("/shipments", json={
            "load_id": long_load_id,
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        assert response.status_code == 422
    
    def test_create_shipment_validation_destination_too_long(self):
        """Test shipment creation validation - destination too long"""
        long_destination = "x" * 201  # Exceeds max_length=200
        response = client.post("/shipments", json={
            "load_id": "LD-VALID",
            "origin": "Origin",
            "destination": long_destination,
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        assert response.status_code == 422
    
    def test_create_shipment_invalid_datetime_format(self):
        """Test shipment creation with invalid datetime format"""
        response = client.post("/shipments", json={
            "load_id": "LD-VALID",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "invalid-date",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        # Should fail due to invalid datetime format
        assert response.status_code == 422

    def test_create_shipment_duplicate_load_id(self):
        """Test creating shipment with duplicate load_id"""
        shipment_data = {
            "load_id": "LD-DUPLICATE",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        }
        
        # Create first shipment
        response1 = client.post("/shipments", json=shipment_data)
        assert response1.status_code == 201
        
        # Try to create second shipment with same load_id
        response2 = client.post("/shipments", json=shipment_data)
        assert response2.status_code == 409
        error_data = response2.json()
        assert "already exists" in error_data["detail"]

class TestUpdateShipment:
    """Test shipment updates"""
    
    def setup_method(self):
        """Clear the database before each test"""
        shipments_db.clear()
    
    def test_update_shipment_load_id(self):
        """Test updating shipment load_id"""
        # Create a shipment
        create_response = client.post("/shipments", json={
            "load_id": "LD-ORIGINAL",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        shipment_id = create_response.json()["id"]
        
        # Update the load_id
        update_data = {"load_id": "LD-UPDATED"}
        response = client.patch(f"/shipments/{shipment_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["load_id"] == "LD-UPDATED"
        assert data["updated_at"] != data["created_at"]
    
    def test_update_shipment_status(self):
        """Test updating shipment status"""
        # Create a shipment
        create_response = client.post("/shipments", json={
            "load_id": "LD-TEST",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        shipment_id = create_response.json()["id"]
        
        # Update the status
        update_data = {"status": "agreed"}
        response = client.patch(f"/shipments/{shipment_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "agreed"
        assert data["updated_at"] != data["created_at"]
    
    def test_update_shipment_multiple_fields(self):
        """Test updating multiple fields at once"""
        # Create a shipment
        create_response = client.post("/shipments", json={
            "load_id": "LD-ORIGINAL",
            "origin": "Original Origin",
            "destination": "Original Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        shipment_id = create_response.json()["id"]
        
        # Update multiple fields
        update_data = {
            "load_id": "LD-UPDATED",
            "origin": "Updated Origin",
            "destination": "Updated Destination",
            "equipment_type": "Reefer",
            "loadboard_rate": 3000.0
        }
        response = client.patch(f"/shipments/{shipment_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["load_id"] == "LD-UPDATED"
        assert data["origin"] == "Updated Origin"
        assert data["destination"] == "Updated Destination"
        assert data["equipment_type"] == "Reefer"
        assert data["loadboard_rate"] == 3000.0
    
    def test_update_shipment_invalid_status(self):
        """Test updating with invalid status"""
        # Create a shipment
        create_response = client.post("/shipments", json={
            "load_id": "LD-TEST",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        shipment_id = create_response.json()["id"]
        
        # Try to update with invalid status
        update_data = {"status": "invalid_status"}
        response = client.patch(f"/shipments/{shipment_id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_shipment_partial(self):
        """Test partial update (only some fields)"""
        # Create a shipment with all fields
        create_response = client.post("/shipments", json={
            "load_id": "LD-ORIGINAL",
            "origin": "Original Origin",
            "destination": "Original Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z",
            "equipment_type": "Dry Van",
            "loadboard_rate": 2000.0
        })
        shipment_id = create_response.json()["id"]
        
        # Update only one field
        update_data = {"equipment_type": "Flatbed"}
        response = client.patch(f"/shipments/{shipment_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["equipment_type"] == "Flatbed"
        assert data["load_id"] == "LD-ORIGINAL"  # Should remain unchanged
        assert data["loadboard_rate"] == 2000.0  # Should remain unchanged

class TestDeleteShipment:
    """Test shipment deletion"""
    
    def setup_method(self):
        """Clear the database before each test"""
        shipments_db.clear()
    
    def test_delete_shipment(self):
        """Test deleting a shipment"""
        # Create a shipment
        create_response = client.post("/shipments", json={
            "load_id": "LD-TO-DELETE",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        shipment_id = create_response.json()["id"]
        
        # Delete the shipment
        response = client.delete(f"/shipments/{shipment_id}")
        assert response.status_code == 204
        # FastAPI returns null for 204 responses, which is valid
        assert response.content in [b'', b'null']
        
        # Verify it's deleted
        get_response = client.get(f"/shipments/{shipment_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_shipment(self):
        """Test deleting a shipment that doesn't exist"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/shipments/{fake_id}")
        assert response.status_code == 404

class TestDataIntegrity:
    """Test data integrity and business rules"""
    
    def setup_method(self):
        """Clear the database before each test"""
        shipments_db.clear()
    
    def test_shipment_id_uniqueness(self):
        """Test that shipment IDs are unique"""
        response1 = client.post("/shipments", json={
            "load_id": "LD-UNIQUE-1",
            "origin": "Origin 1",
            "destination": "Destination 1",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        response2 = client.post("/shipments", json={
            "load_id": "LD-UNIQUE-2",
            "origin": "Origin 2",
            "destination": "Destination 2",
            "pickup_datetime": "2024-01-03T08:00:00Z",
            "delivery_datetime": "2024-01-04T18:00:00Z"
        })
        
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        assert id1 != id2
    
    def test_timestamps_are_set(self):
        """Test that created_at and updated_at timestamps are set"""
        response = client.post("/shipments", json={
            "load_id": "LD-TIMESTAMP",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        data = response.json()
        
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] == data["updated_at"]  # Should be equal on creation
    
    def test_updated_at_changes_on_update(self):
        """Test that updated_at changes when shipment is updated"""
        # Create a shipment
        create_response = client.post("/shipments", json={
            "load_id": "LD-UPDATE-TEST",
            "origin": "Origin",
            "destination": "Destination",
            "pickup_datetime": "2024-01-01T08:00:00Z",
            "delivery_datetime": "2024-01-02T18:00:00Z"
        })
        original_updated_at = create_response.json()["updated_at"]
        
        # Update the shipment
        shipment_id = create_response.json()["id"]
        update_response = client.patch(f"/shipments/{shipment_id}", json={"status": "agreed"})
        updated_at = update_response.json()["updated_at"]
        
        assert updated_at != original_updated_at

class TestErrorHandling:
    """Test error handling"""
    
    def setup_method(self):
        """Clear the database before each test"""
        shipments_db.clear()
    
    def test_get_nonexistent_shipment(self):
        """Test getting a shipment that doesn't exist"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/shipments/{fake_id}")
        assert response.status_code == 404
    
    def test_update_nonexistent_shipment(self):
        """Test updating a shipment that doesn't exist"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.patch(f"/shipments/{fake_id}", json={"status": "agreed"})
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test sending invalid JSON"""
        response = client.post("/shipments", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test sending request without content-type header"""
        response = client.post("/shipments", data='{"load_id": "test"}')
        assert response.status_code == 422
