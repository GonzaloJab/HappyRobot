#!/usr/bin/env python3
"""
Script to create new loads/shipments to the HappyRobot backend API
Backend runs on port 8000
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import argparse


class LoadCreator:
    """Class to handle load creation to the backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> bool:
        """Check if the backend is running and healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is healthy: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to backend at {self.base_url}")
            print("Make sure the backend is running on port 8000")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def create_load(self, load_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new load/shipment
        
        Args:
            load_data: Dictionary containing load information
            
        Returns:
            Created load data if successful, None if failed
        """
        try:
            response = self.session.post(
                f"{self.base_url}/shipments",
                json=load_data
            )
            
            if response.status_code == 201:
                created_load = response.json()
                print(f"✅ Load created successfully!")
                print(f"   Load ID: {created_load['load_id']}")
                print(f"   Internal ID: {created_load['id']}")
                print(f"   Route: {created_load['origin']} → {created_load['destination']}")
                print(f"   Status: {created_load['status']}")
                return created_load
            else:
                print(f"❌ Failed to create load: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_all_loads(self) -> Optional[list]:
        """Get all existing loads"""
        try:
            response = self.session.get(f"{self.base_url}/shipments")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get loads: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_load(self, load_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific load by internal ID"""
        try:
            response = self.session.get(f"{self.base_url}/shipments/{load_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Load not found: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def find_load_by_load_id(self, load_id: str) -> Optional[Dict[str, Any]]:
        """Find a load by its human-readable load_id"""
        try:
            loads = self.get_all_loads()
            if loads:
                for load in loads:
                    if load.get('load_id') == load_id:
                        return load
            return None
        except Exception as e:
            print(f"❌ Error finding load: {e}")
            return None
    
    def update_load(self, shipment_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing load/shipment
        
        Args:
            shipment_id: Internal UUID of the shipment
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated load data if successful, None if failed
        """
        try:
            response = self.session.patch(
                f"{self.base_url}/shipments/{shipment_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                updated_load = response.json()
                print(f"✅ Load updated successfully!")
                print(f"   Load ID: {updated_load['load_id']}")
                print(f"   Status: {updated_load['status']}")
                print(f"   Updated at: {updated_load['updated_at']}")
                return updated_load
            else:
                print(f"❌ Failed to update load: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def assign_load(self, load_id: str, agreed_price: float = None, carrier_description: str = None) -> bool:
        """
        Assign a load by updating its status to 'agreed'
        
        Args:
            load_id: Human-readable load ID (e.g., "LD-2025-0001")
            agreed_price: Agreed price for the load (required when status is agreed)
            carrier_description: Carrier description/name (required when status is agreed)
            
        Returns:
            True if successful, False if failed
        """
        # First find the load by load_id
        load = self.find_load_by_load_id(load_id)
        if not load:
            print(f"❌ Load with ID '{load_id}' not found")
            return False
        
        # Build update data
        update_data = {"status": "agreed"}
        
        if agreed_price is not None:
            update_data["agreed_price"] = agreed_price
        if carrier_description is not None:
            update_data["carrier_description"] = carrier_description
        
        result = self.update_load(load['id'], update_data)
        return result is not None


def create_sample_load_data(load_id: str, origin: str, destination: str, 
                          pickup_date: str, delivery_date: str,
                          **kwargs) -> Dict[str, Any]:
    """
    Create sample load data with required and optional fields
    
    Args:
        load_id: Human-readable load ID (e.g., "LD-2025-0001")
        origin: Origin location
        destination: Destination location  
        pickup_date: Pickup datetime in ISO format (e.g., "2025-01-15T08:00:00Z")
        delivery_date: Delivery datetime in ISO format (e.g., "2025-01-16T18:00:00Z")
        **kwargs: Additional optional fields
        
    Returns:
        Dictionary with load data
    """
    load_data = {
        "load_id": load_id,
        "origin": origin,
        "destination": destination,
        "pickup_datetime": pickup_date,
        "delivery_datetime": delivery_date
    }
    
    # Add optional fields if provided
    optional_fields = [
        "equipment_type", "loadboard_rate", "notes", "weight", 
        "commodity_type", "num_of_pieces", "miles", "dimensions",
        "agreed_price", "carrier_description"
    ]
    
    for field in optional_fields:
        if field in kwargs:
            load_data[field] = kwargs[field]
    
    return load_data


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Create loads to HappyRobot backend")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Backend URL (default: http://localhost:8000)")
    parser.add_argument("--load-id", help="Load ID (e.g., LD-2025-0001)")
    parser.add_argument("--origin", help="Origin location")
    parser.add_argument("--destination", help="Destination location")
    parser.add_argument("--pickup", help="Pickup datetime (ISO format)")
    parser.add_argument("--delivery", help="Delivery datetime (ISO format)")
    parser.add_argument("--equipment", help="Equipment type (e.g., Dry Van, Reefer)")
    parser.add_argument("--rate", type=float, help="Loadboard rate")
    parser.add_argument("--weight", type=float, help="Weight in pounds")
    parser.add_argument("--miles", type=float, help="Distance in miles")
    parser.add_argument("--notes", help="Additional notes")
    parser.add_argument("--list", action="store_true", help="List all existing loads")
    parser.add_argument("--sample", action="store_true", help="Create a sample load")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--assign", help="Assign a load by load_id (e.g., LD-2025-0001)")
    parser.add_argument("--agreed-price", type=float, help="Agreed price for the load")
    parser.add_argument("--carrier", help="Carrier description/name")
    parser.add_argument("--update-status", help="Update load status (pending/agreed)")
    parser.add_argument("--update-load-id", help="Load ID to update")
    parser.add_argument("--update-origin", help="Update origin location")
    parser.add_argument("--update-destination", help="Update destination location")
    parser.add_argument("--update-equipment", help="Update equipment type")
    parser.add_argument("--update-rate", type=float, help="Update loadboard rate")
    parser.add_argument("--update-agreed-price", type=float, help="Update agreed price")
    parser.add_argument("--update-carrier", help="Update carrier description")
    parser.add_argument("--update-notes", help="Update notes")
    
    args = parser.parse_args()
    
    # Initialize load creator
    creator = LoadCreator(args.url)
    
    # Health check first
    if not creator.health_check():
        sys.exit(1)
    
    # List loads if requested
    if args.list:
        print("\n📋 Existing loads:")
        loads = creator.get_all_loads()
        if loads:
            for i, load in enumerate(loads, 1):
                print(f"   {i}. {load['load_id']}: {load['origin']} → {load['destination']} ({load['status']})")
        else:
            print("   No loads found")
        return
    
    # Assign load if requested
    if args.assign:
        print(f"\n🚛 Assigning load: {args.assign}")
        success = creator.assign_load(
            args.assign, 
            agreed_price=args.agreed_price, 
            carrier_description=args.carrier
        )
        if success:
            print("✅ Load agreed successfully!")
        else:
            print("❌ Failed to assign load")
        return
    
    # Update load if requested
    if args.update_load_id:
        print(f"\n🔄 Updating load: {args.update_load_id}")
        
        # Find the load first
        load = creator.find_load_by_load_id(args.update_load_id)
        if not load:
            print(f"❌ Load with ID '{args.update_load_id}' not found")
            return
        
        # Build update data from command line arguments
        update_data = {}
        if args.update_status:
            if args.update_status not in ['pending', 'agreed']:
                print("❌ Status must be 'pending' or 'agreed'")
                return
            update_data['status'] = args.update_status
        if args.update_origin:
            update_data['origin'] = args.update_origin
        if args.update_destination:
            update_data['destination'] = args.update_destination
        if args.update_equipment:
            update_data['equipment_type'] = args.update_equipment
        if args.update_rate:
            update_data['loadboard_rate'] = args.update_rate
        if args.update_agreed_price:
            update_data['agreed_price'] = args.update_agreed_price
        if args.update_carrier:
            update_data['carrier_description'] = args.update_carrier
        if args.update_notes:
            update_data['notes'] = args.update_notes
        
        if not update_data:
            print("❌ No update fields provided. Use --update-status, --update-origin, etc.")
            return
        
        result = creator.update_load(load['id'], update_data)
        if result:
            print("✅ Load updated successfully!")
        else:
            print("❌ Failed to update load")
        return
    
    # Interactive mode
    if args.interactive:
        print("\n🚛 Interactive Load Creation")
        print("Enter load details (press Enter to skip optional fields):")
        
        load_id = input("Load ID (required): ").strip()
        if not load_id:
            print("❌ Load ID is required")
            return
            
        origin = input("Origin (required): ").strip()
        if not origin:
            print("❌ Origin is required")
            return
            
        destination = input("Destination (required): ").strip()
        if not destination:
            print("❌ Destination is required")
            return
            
        pickup = input("Pickup datetime (ISO format, e.g., 2025-01-15T08:00:00Z): ").strip()
        if not pickup:
            print("❌ Pickup datetime is required")
            return
            
        delivery = input("Delivery datetime (ISO format, e.g., 2025-01-16T18:00:00Z): ").strip()
        if not delivery:
            print("❌ Delivery datetime is required")
            return
        
        # Optional fields
        equipment = input("Equipment type (optional): ").strip() or None
        rate_str = input("Loadboard rate (optional): ").strip()
        rate = float(rate_str) if rate_str else None
        agreed_price_str = input("Agreed price (optional): ").strip()
        agreed_price = float(agreed_price_str) if agreed_price_str else None
        carrier = input("Carrier description (optional): ").strip() or None
        weight_str = input("Weight in pounds (optional): ").strip()
        weight = float(weight_str) if weight_str else None
        miles_str = input("Miles (optional): ").strip()
        miles = float(miles_str) if miles_str else None
        notes = input("Notes (optional): ").strip() or None
        
        load_data = create_sample_load_data(
            load_id, origin, destination, pickup, delivery,
            equipment_type=equipment, loadboard_rate=rate, 
            agreed_price=agreed_price, carrier_description=carrier,
            weight=weight, miles=miles, notes=notes
        )
        
        creator.create_load(load_data)
        return
    
    # Create sample load if requested
    if args.sample:
        print("\n🚛 Creating sample load...")
        
        # Generate sample data
        now = datetime.now()
        pickup_time = now + timedelta(days=1)
        delivery_time = pickup_time + timedelta(days=2)
        
        load_data = create_sample_load_data(
            load_id="LD-SAMPLE-001",
            origin="Los Angeles, CA",
            destination="New York, NY", 
            pickup_date=pickup_time.isoformat() + "Z",
            delivery_date=delivery_time.isoformat() + "Z",
            equipment_type="Dry Van",
            loadboard_rate=2500.50,
            agreed_price=2300.00,
            carrier_description="ABC Transport Co.",
            weight=1500.0,
            commodity_type="Electronics",
            num_of_pieces=100,
            miles=2800.0,
            dimensions="48x40x60 in",
            notes="Fragile cargo - handle with care"
        )
        
        creator.create_load(load_data)
        return
    
    # Command line mode - check required fields
    if not all([args.load_id, args.origin, args.destination, args.pickup, args.delivery]):
        print("❌ Missing required fields. Use --help for usage information.")
        print("Required: --load-id, --origin, --destination, --pickup, --delivery")
        print("Or use --interactive for guided input, or --sample for a sample load")
        return
    
    # Create load from command line arguments
    load_data = create_sample_load_data(
        args.load_id, args.origin, args.destination, 
        args.pickup, args.delivery,
        equipment_type=args.equipment,
        loadboard_rate=args.rate,
        agreed_price=args.agreed_price,
        carrier_description=args.carrier,
        weight=args.weight,
        miles=args.miles,
        notes=args.notes
    )
    
    creator.create_load(load_data)


if __name__ == "__main__":
    main()
