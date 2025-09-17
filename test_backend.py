#!/usr/bin/env python3
"""
Backend Testing Script for HappyRobot Shipments API
Tests all existing endpoints with various scenarios
"""

import requests
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ShipmentsAPITester:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request and return response"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"{method.upper()} {url} -> {response.status_code}")
            
            if response.status_code == 204:  # No content
                return {"status": "success", "message": "No content"}
            
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"status": "error", "message": "Invalid JSON response", "text": response.text}
                
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}
    
    def generate_random_load_data(self) -> Dict:
        """Generate random load data for testing"""
        origins = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ", 
                  "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX", "San Jose, CA"]
        destinations = ["Miami, FL", "Seattle, WA", "Denver, CO", "Boston, MA", "Atlanta, GA",
                       "Portland, OR", "Las Vegas, NV", "Nashville, TN", "Austin, TX", "Orlando, FL"]
        equipment_types = ["Dry Van", "Refrigerated", "Flatbed", "Container", "Tanker"]
        commodity_types = ["Electronics", "Food", "Automotive", "Textiles", "Machinery", "Chemicals"]
        
        pickup_date = datetime.now() + timedelta(days=random.randint(1, 7))
        delivery_date = pickup_date + timedelta(days=random.randint(1, 5))
        
        return {
            "load_id": f"TEST-{random.randint(1000, 9999)}",
            "origin": random.choice(origins),
            "destination": random.choice(destinations),
            "pickup_datetime": pickup_date.isoformat(),
            "delivery_datetime": delivery_date.isoformat(),
            "equipment_type": random.choice(equipment_types),
            "loadboard_rate": round(random.uniform(1000, 5000), 2),
            "weight": random.randint(1000, 45000),
            "miles": random.randint(100, 2000),
            "commodity_type": random.choice(commodity_types),
            "num_of_pieces": random.randint(1, 100),
            "notes": f"Test load created at {datetime.now().isoformat()}",
            "status": "pending"
        }
    
    def add_load(self, load_data: Optional[Dict] = None, use_random: bool = True) -> Dict:
        """Add a new load (random or hardcoded data)"""
        print("\n" + "="*50)
        print("ADDING NEW LOAD")
        print("="*50)
        
        if use_random and load_data is None:
            load_data = self.generate_random_load_data()
            print("Using random data:")
        elif load_data is None:
            # Hardcoded test data
            load_data = {
                "load_id": "HARDCODED-001",
                "origin": "New York, NY",
                "destination": "Miami, FL",
                "pickup_datetime": (datetime.now() + timedelta(days=2)).isoformat(),
                "delivery_datetime": (datetime.now() + timedelta(days=5)).isoformat(),
                "equipment_type": "Dry Van",
                "loadboard_rate": 2500.00,
                "weight": 25000,
                "miles": 1200,
                "commodity_type": "Electronics",
                "num_of_pieces": 50,
                "notes": "Hardcoded test load",
                "status": "pending"
            }
            print("Using hardcoded data:")
        
        print(json.dumps(load_data, indent=2))
        
        result = self.make_request('POST', '/shipments', load_data)
        
        if result.get('status') == 'error':
            print(f"❌ Error adding load: {result.get('message')}")
        else:
            print(f"✅ Load added successfully!")
            if 'id' in result:
                print(f"   Load ID: {result['id']}")
        
        return result
    
    def list_loads(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List all loads with optional filters"""
        print("\n" + "="*50)
        print("LISTING LOADS")
        print("="*50)
        
        endpoint = '/shipments'
        if filters:
            # Build query string
            params = []
            for key, value in filters.items():
                if value is not None:
                    params.append(f"{key}={value}")
            if params:
                endpoint += '?' + '&'.join(params)
        
        result = self.make_request('GET', endpoint)
        
        if isinstance(result, list):
            print(f"✅ Found {len(result)} loads")
            for i, load in enumerate(result, 1):
                print(f"\n{i}. Load ID: {load.get('load_id', 'N/A')}")
                print(f"   Origin: {load.get('origin', 'N/A')}")
                print(f"   Destination: {load.get('destination', 'N/A')}")
                print(f"   Status: {load.get('status', 'N/A')}")
                print(f"   Rate: ${load.get('loadboard_rate', 'N/A')}")
                print(f"   Assigned via URL: {load.get('assigned_via_url', 'N/A')}")
        else:
            print(f"❌ Error listing loads: {result.get('message', 'Unknown error')}")
        
        return result if isinstance(result, list) else []
    
    def edit_load(self, load_id: str, status: str = "agreed", time_per_call: Optional[float] = None, manual: bool = True, agreed_price: Optional[float] = None) -> Dict:
        """Edit/patch a load, change status and clean up fields when changing to agreed"""
        print("\n" + "="*50)
        print(f"EDITING LOAD: {load_id}")
        print("="*50)
        
        # First, get the current load to see its ID
        loads = self.list_loads()
        target_load = None
        
        for load in loads:
            if load.get('load_id') == load_id:
                target_load = load
                break
        
        if not target_load:
            print(f"❌ Load with load_id '{load_id}' not found")
            return {"status": "error", "message": "Load not found"}
        
        # Prepare update data
        update_data = {
            "status": status
        }
        
        # Add time_per_call_seconds if provided
        if time_per_call is not None:
            update_data["time_per_call_seconds"] = time_per_call
        
        # If changing to agreed, add required fields and clean up
        if status == "agreed":
            update_data.update({
                "agreed_price": agreed_price,
                "carrier_description": f"Test Carrier {random.randint(1, 100)}",
                "assigned_via_url": False  # Manual assignment
            })
            print("Changing to 'agreed' status - adding required fields")
        else:
            # If changing to pending, remove agreed-specific fields
            update_data.update({
                "agreed_price": None,
                "carrier_description": None,
                "assigned_via_url": None
            })
            print("Changing to 'pending' status - removing agreed-specific fields")
        
        print(f"Update data: {json.dumps(update_data, indent=2)}")
        
        # Use the internal ID for the API call
        internal_id = target_load.get('id')
        if not internal_id:
            print("❌ Could not find internal ID for the load")
            return {"status": "error", "message": "Internal ID not found"}
        
        # Use manual update endpoint for frontend assignments
        result = self.make_request('PATCH', f'/shipments/{internal_id}/manual', update_data)
        
        if result.get('status') == 'error':
            print(f"❌ Error updating load: {result.get('message')}")
        else:
            print(f"✅ Load updated successfully!")
            print(f"   New status: {status}")
            if 'agreed_price' in update_data:
                print(f"   Agreed price: ${update_data['agreed_price']}")
        
        return result
    
    def delete_load(self, load_id: str) -> Dict:
        """Delete a load by load_id"""
        print("\n" + "="*50)
        print(f"DELETING LOAD: {load_id}")
        print("="*50)
        
        # First, find the load to get its internal ID
        loads = self.list_loads()
        target_load = None
        
        for load in loads:
            if load.get('load_id') == load_id:
                target_load = load
                break
        
        if not target_load:
            print(f"❌ Load with load_id '{load_id}' not found")
            return {"status": "error", "message": "Load not found"}
        
        # Use the internal ID for the API call
        internal_id = target_load.get('id')
        if not internal_id:
            print("❌ Could not find internal ID for the load")
            return {"status": "error", "message": "Internal ID not found"}
        
        print(f"Deleting load: {load_id} (Internal ID: {internal_id})")
        
        result = self.make_request('DELETE', f'/shipments/{internal_id}')
        
        if result.get('status') == 'error':
            print(f"❌ Error deleting load: {result.get('message')}")
        else:
            print(f"✅ Load deleted successfully!")
        
        return result
    
    def get_load_stats(self) -> Dict:
        """Get shipment statistics"""
        print("\n" + "="*50)
        print("GETTING LOAD STATISTICS")
        print("="*50)
        
        result = self.make_request('GET', '/shipments/stats')
        
        if result.get('status') == 'error':
            print(f"❌ Error getting stats: {result.get('message')}")
        else:
            print("✅ Statistics retrieved successfully!")
            print(json.dumps(result, indent=2))
        
        return result
    
    def get_random_load(self, origin: Optional[str] = None) -> Dict:
        """Get a random load"""
        print("\n" + "="*50)
        print("GETTING RANDOM LOAD")
        print("="*50)
        
        endpoint = '/shipments/random'
        if origin:
            endpoint += f'?origin={origin}'
        
        result = self.make_request('GET', endpoint)
        
        if result.get('status') == 'error':
            print(f"❌ Error getting random load: {result.get('message')}")
        else:
            print("✅ Random load retrieved successfully!")
            print(json.dumps(result, indent=2))
        
        return result
    
    def health_check(self) -> Dict:
        """Check backend health"""
        print("\n" + "="*50)
        print("HEALTH CHECK")
        print("="*50)
        
        result = self.make_request('GET', '/health')
        
        if result.get('status') == 'error':
            print(f"❌ Health check failed: {result.get('message')}")
        else:
            print("✅ Backend is healthy!")
            print(json.dumps(result, indent=2))
        
        return result
    
    def add_phone_call(self, load_id: str, agreed: bool = None, minutes: float = None, call_type: str = None, sentiment: str = None, notes: str = None, call_id: str = None) -> Dict:
        """Add a phone call to a load"""
        print("\n" + "="*50)
        print(f"ADDING PHONE CALL TO LOAD: {load_id}")
        print("="*50)
        
        # Generate random phone call data if not provided
        if agreed is None:
            agreed = random.choice([True, False])
        if minutes is None:
            minutes = round(random.uniform(2, 30), 1)
        if call_type is None:
            call_type = random.choice(["manual", "agent"])
        if sentiment is None:
            sentiment = random.choice(["positive", "neutral", "negative"])
        if notes is None:
            notes = f"Test call - {sentiment} sentiment, {'agreed' if agreed else 'not agreed'}"
        if call_id is None:
            call_id = f"CALL-{random.randint(1000, 9999)}"
        
        phone_call_data = {
            "agreed": agreed,
            "minutes": minutes,
            "call_type": call_type,
            "call_id": call_id,
            "sentiment": sentiment,
            "notes": notes
        }
        
        print(f"Phone call data: {json.dumps(phone_call_data, indent=2)}")
        
        # Use load_id directly - backend will resolve it to internal ID
        result = self.make_request('POST', f'/shipments/{load_id}/phone-calls', phone_call_data)
        
        if result.get('status') == 'error':
            print(f"❌ Error adding phone call: {result.get('message')}")
        else:
            print(f"✅ Phone call added successfully!")
            print(f"   Call ID: {result.get('id', 'N/A')}")
            print(f"   Agreed: {agreed}")
            print(f"   Duration: {minutes} minutes")
            print(f"   Type: {call_type}")
            print(f"   Sentiment: {sentiment}")
        
        return result
    
    def add_phone_call_with_strings(self, load_id: str) -> Dict:
        """Add a phone call to a load using string inputs to test parsing"""
        print("\n" + "="*50)
        print(f"ADDING PHONE CALL WITH STRING INPUTS TO LOAD: {load_id}")
        print("="*50)
        
        # Test different string formats
        test_cases = [
            {
                "name": "String boolean 'True' and string number",
                "data": {
                    "agreed": "True",
                    "minutes": "15.5",
                    "call_type": "agent",
                    "sentiment": "positive",
                    "notes": "Test call with string 'True' and '15.5'"
                }
            },
            {
                "name": "String boolean 'False' and string integer",
                "data": {
                    "agreed": "False",
                    "minutes": "8",
                    "call_type": "manual",
                    "sentiment": "neutral",
                    "notes": "Test call with string 'False' and '8'"
                }
            },
            {
                "name": "Alternative boolean strings 'yes'/'no'",
                "data": {
                    "agreed": "yes",
                    "minutes": "12.25",
                    "call_type": "agent",
                    "sentiment": "positive",
                    "notes": "Test call with 'yes' boolean"
                }
            },
            {
                "name": "Numeric boolean '1'/'0'",
                "data": {
                    "agreed": "1",
                    "minutes": "20.0",
                    "call_type": "manual",
                    "sentiment": "negative",
                    "notes": "Test call with '1' boolean"
                }
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['name']}")
            print(f"   Input data: {json.dumps(test_case['data'], indent=2)}")
            
            result = self.make_request('POST', f'/shipments/{load_id}/phone-calls', test_case['data'])
            
            if isinstance(result, dict) and 'id' in result:
                print(f"   ✅ Success! Created phone call ID: {result['id']}")
                print(f"   📊 Parsed values:")
                print(f"      - agreed: {result['agreed']} (type: {type(result['agreed']).__name__})")
                print(f"      - minutes: {result['minutes']} (type: {type(result['minutes']).__name__})")
                results.append(result)
            else:
                print(f"   ❌ Failed: {result}")
        
        return results
    
    def get_phone_calls(self, load_id: str) -> List[Dict]:
        """Get all phone calls for a load"""
        print("\n" + "="*50)
        print(f"GETTING PHONE CALLS FOR LOAD: {load_id}")
        print("="*50)
        
        # Use load_id directly - backend will resolve it to internal ID
        result = self.make_request('GET', f'/shipments/{load_id}/phone-calls')
        
        if isinstance(result, list):
            print(f"✅ Found {len(result)} phone calls")
            for i, call in enumerate(result, 1):
                print(f"\n{i}. Call ID: {call.get('id', 'N/A')}")
                print(f"   Agreed: {call.get('agreed', 'N/A')}")
                print(f"   Duration: {call.get('minutes', 'N/A')} minutes")
                print(f"   Type: {call.get('call_type', 'N/A')}")
                print(f"   Sentiment: {call.get('sentiment', 'N/A')}")
                print(f"   Notes: {call.get('notes', 'N/A')}")
                print(f"   Created: {call.get('created_at', 'N/A')}")
        else:
            print(f"❌ Error getting phone calls: {result.get('message', 'Unknown error')}")
        
        return result if isinstance(result, list) else []
    
    def delete_all_phone_calls(self, load_id: str) -> Dict:
        """Delete all phone calls for a load"""
        print("\n" + "="*50)
        print(f"DELETING ALL PHONE CALLS FOR LOAD: {load_id}")
        print("="*50)
        
        # Use load_id directly - backend will resolve it to internal ID
        result = self.make_request('DELETE', f'/shipments/{load_id}/phone-calls')
        
        if result.get('status') == 'error':
            print(f"❌ Error deleting phone calls: {result.get('message')}")
        else:
            print(f"✅ All phone calls deleted successfully!")
        
        return result
    
    def list_all_phone_calls(self) -> List[Dict]:
        """List all phone calls across all loads"""
        print("\n" + "="*50)
        print("LISTING ALL PHONE CALLS")
        print("="*50)
        
        # Get all loads first
        loads = self.list_loads()
        
        all_phone_calls = []
        total_calls = 0
        manual_calls = 0
        agent_calls = 0
        agreed_calls = 0
        total_minutes = 0.0
        
        for load in loads:
            load_id = load.get('load_id')
            if load_id:
                # Get phone calls for this load using load_id
                result = self.make_request('GET', f'/shipments/{load_id}/phone-calls')
                
                if isinstance(result, list):
                    for call in result:
                        call_info = {
                            'load_id': load.get('load_id', 'N/A'),
                            'call_id': call.get('call_id', 'N/A'),
                            'agreed': call.get('agreed', False),
                            'minutes': call.get('minutes', 0),
                            'call_type': call.get('call_type', 'N/A'),
                            'sentiment': call.get('sentiment', 'N/A'),
                            'notes': call.get('notes', 'N/A'),
                            'created_at': call.get('created_at', 'N/A')
                        }
                        all_phone_calls.append(call_info)
                        
                        # Update counters
                        total_calls += 1
                        if call.get('call_type') == 'manual':
                            manual_calls += 1
                        elif call.get('call_type') == 'agent':
                            agent_calls += 1
                        if call.get('agreed'):
                            agreed_calls += 1
                        total_minutes += call.get('minutes', 0)
        
        print(f"✅ Found {total_calls} phone calls across all loads")
        print(f"   Manual calls: {manual_calls}")
        print(f"   Agent calls: {agent_calls}")
        print(f"   Agreed calls: {agreed_calls}")
        print(f"   Total minutes: {total_minutes:.1f}")
        
        if all_phone_calls:
            print(f"\n📞 Phone Call Details:")
            for i, call in enumerate(all_phone_calls, 1):
                print(f"\n{i}. Load: {call['load_id']}")
                print(f"   Call ID: {call['call_id']}")
                print(f"   Type: {call['call_type']}")
                print(f"   Agreed: {'Yes' if call['agreed'] else 'No'}")
                print(f"   Duration: {call['minutes']} minutes")
                print(f"   Sentiment: {call['sentiment']}")
                print(f"   Notes: {call['notes']}")
                print(f"   Created: {call['created_at']}")
        else:
            print("   No phone calls found")
        
        return all_phone_calls
    
    def list_phone_calls_by_type(self, call_type: str) -> List[Dict]:
        """List all phone calls filtered by type (manual or agent)"""
        print("\n" + "="*50)
        print(f"LISTING {call_type.upper()} PHONE CALLS")
        print("="*50)
        
        if call_type not in ["manual", "agent"]:
            print(f"❌ Invalid call type: {call_type}. Must be 'manual' or 'agent'")
            return []
        
        # Get all loads first
        loads = self.list_loads()
        
        filtered_phone_calls = []
        total_calls = 0
        agreed_calls = 0
        total_minutes = 0.0
        
        for load in loads:
            load_id = load.get('load_id')
            if load_id:
                # Get phone calls for this load using load_id
                result = self.make_request('GET', f'/shipments/{load_id}/phone-calls')
                
                if isinstance(result, list):
                    for call in result:
                        if call.get('call_type') == call_type:
                            call_info = {
                                'load_id': load.get('load_id', 'N/A'),
                                'call_id': call.get('call_id', 'N/A'),
                                'agreed': call.get('agreed', False),
                                'minutes': call.get('minutes', 0),
                                'call_type': call.get('call_type', 'N/A'),
                                'sentiment': call.get('sentiment', 'N/A'),
                                'notes': call.get('notes', 'N/A'),
                                'created_at': call.get('created_at', 'N/A')
                            }
                            filtered_phone_calls.append(call_info)
                            
                            # Update counters
                            total_calls += 1
                            if call.get('agreed'):
                                agreed_calls += 1
                            total_minutes += call.get('minutes', 0)
        
        print(f"✅ Found {total_calls} {call_type} phone calls")
        print(f"   Agreed calls: {agreed_calls}")
        print(f"   Success rate: {(agreed_calls/total_calls*100):.1f}%" if total_calls > 0 else "   Success rate: 0%")
        print(f"   Total minutes: {total_minutes:.1f}")
        
        if filtered_phone_calls:
            print(f"\n📞 {call_type.title()} Phone Call Details:")
            for i, call in enumerate(filtered_phone_calls, 1):
                print(f"\n{i}. Load: {call['load_id']}")
                print(f"   Call ID: {call['call_id']}")
                print(f"   Agreed: {'Yes' if call['agreed'] else 'No'}")
                print(f"   Duration: {call['minutes']} minutes")
                print(f"   Sentiment: {call['sentiment']}")
                print(f"   Notes: {call['notes']}")
                print(f"   Created: {call['created_at']}")
        else:
            print(f"   No {call_type} phone calls found")
        
        return filtered_phone_calls
    
    def run_comprehensive_test(self):
        """Run a comprehensive test suite"""
        print("\n" + "="*60)
        print("COMPREHENSIVE BACKEND TEST SUITE")
        print("="*60)
        
        # 1. Health check
        self.health_check()
        
        # 2. List initial loads
        initial_loads = self.list_loads()
        
        # 3. Add random loads
        print("\n" + "="*50)
        print("ADDING MULTIPLE RANDOM LOADS")
        print("="*50)
        
        added_loads = []
        for i in range(3):
            result = self.add_load(use_random=True)
            if 'load_id' in result:
                added_loads.append(result['load_id'])
        
        # 4. Add hardcoded load
        hardcoded_result = self.add_load(use_random=False)
        if 'load_id' in hardcoded_result:
            added_loads.append(hardcoded_result['load_id'])
        
        # 5. List all loads
        all_loads = self.list_loads()
        
        # 6. Test filtering
        print("\n" + "="*50)
        print("TESTING FILTERS")
        print("="*50)
        
        # Filter by status
        pending_loads = self.list_loads({"status": "pending"})
        print(f"Found {len(pending_loads)} pending loads")
        
        # 7. Edit loads (change to agreed)
        if added_loads:
            print("\n" + "="*50)
            print("TESTING LOAD EDITS")
            print("="*50)
            
            for load_id in added_loads[:2]:  # Edit first 2 loads
                self.edit_load(load_id, "agreed", time_per_call=random.uniform(30, 300), agreed_price=random.uniform(30, 300))
                time.sleep(1)  # Small delay between requests
        
        # 8. List loads again to see changes
        updated_loads = self.list_loads()
        
        # 9. Test stats
        self.get_load_stats()
        
        # 10. Test random load
        self.get_random_load()
        
        # 11. Test phone call functionality
        if added_loads:
            print("\n" + "="*50)
            print("TESTING PHONE CALL FUNCTIONALITY")
            print("="*50)
            
            # Add some phone calls to the first load
            test_load = added_loads[0]
            self.add_phone_call(test_load, agreed=True, minutes=15.5, call_type="manual", sentiment="positive", call_id="CALL-001")
            self.add_phone_call(test_load, agreed=False, minutes=8.2, call_type="agent", sentiment="neutral", call_id="CALL-002")
            self.add_phone_call(test_load, agreed=True, minutes=22.1, call_type="manual", sentiment="positive", call_id="CALL-003")
            
            # Get phone calls for the load
            self.get_phone_calls(test_load)
            
            # Test stats with phone calls
            self.get_load_stats()
        
        # 12. Test changing back to pending
        if added_loads:
            self.edit_load(added_loads[0], "pending", agreed_price=None)
        
        # 13. Delete one load
        if added_loads:
            self.delete_load(added_loads[-1])  # Delete last added load
        
        # 14. Final stats
        print("\n" + "="*50)
        print("FINAL STATISTICS")
        print("="*50)
        self.get_load_stats()
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETED")
        print("="*60)


def main():
    """Main function to run the test script"""
    # Configuration
    BASE_URL = "http://happyrobot-1700442240.eu-north-1.elb.amazonaws.com"
    BASE_URL = "http://localhost:8000"
    API_KEY = "HapRob-OTVHhErcXLu2eKkUMP6lDtrd8UNi61KZo4FvGALqem0NoJO1uWlz7OywCN0BNoNaG2x5Y"
    
    # Create tester instance
    tester = ShipmentsAPITester(BASE_URL, API_KEY)
    
    print("🚀 HappyRobot Backend Testing Script")
    print(f"Testing API at: {BASE_URL}")
    print(f"Using API Key: {API_KEY[:20]}...")
    
    while True:
        print("\n" + "="*50)
        print("BACKEND TESTING MENU")
        print("="*50)
        print("1. Health Check")
        print("2. List All Loads")
        print("3. Add Random Load")
        print("4. Add Hardcoded Load")
        print("5. Edit Load (Change Status)")
        print("6. Delete Load")
        print("7. Get Load Statistics")
        print("8. Get Random Load")
        print("9. Run Comprehensive Test Suite")
        print("10. Test with Filters")
        print("11. Add Phone Call")
        print("12. Get Phone Calls for Load")
        print("13. Delete All Phone Calls for Load")
        print("14. List All Phone Calls")
        print("15. List Manual Phone Calls")
        print("16. List Agent Phone Calls")
        print("17. Test Phone Call with String Inputs")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-17): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            tester.health_check()
        elif choice == '2':
            tester.list_loads()
        elif choice == '3':
            tester.add_load(use_random=True)
        elif choice == '4':
            tester.add_load(use_random=False)
        elif choice == '5':
            load_id = input("Enter load_id to edit: ").strip()
            status = input("Enter new status (p=pending/a=agreed): ").strip()
            if status == 'a':
                time_call = input("Enter time_per_call_seconds (optional, press Enter to skip): ").strip()
                agreed_price = input("Sold price: ").strip()

                tester.edit_load(load_id, 'agreed', time_call, agreed_price=agreed_price)

            else:
                time_call = None
                agreed_price = None
                tester.edit_load(load_id, 'pending', time_call, agreed_price=agreed_price)
            
        elif choice == '6':
            load_id = input("Enter load_id to delete: ").strip()
            tester.delete_load(load_id)
        elif choice == '7':
            tester.get_load_stats()
        elif choice == '8':
            origin = input("Enter origin filter (optional, press Enter to skip): ").strip()
            origin = origin if origin else None
            tester.get_random_load(origin)
        elif choice == '9':
            tester.run_comprehensive_test()
        elif choice == '10':
            print("\nFilter options:")
            print("1. Filter by status")
            print("2. Filter by origin")
            print("3. Filter by equipment type")
            filter_choice = input("Enter filter choice (1-3): ").strip()
            
            filters = {}
            if filter_choice == '1':
                status = input("Enter status (p=pending/a=agreed): ").strip()
                filters['status'] = 'pending' if status == 'p' else 'agreed'
            elif filter_choice == '2':
                origin = input("Enter origin: ").strip()
                filters['origin'] = origin
            elif filter_choice == '3':
                equipment = input("Enter equipment type: ").strip()
                filters['equipment_type'] = equipment
            
            tester.list_loads(filters)
        elif choice == '11':
            load_id = input("Enter load_id to add phone call to: ").strip()
            agreed = input("Did they agree? (y/n, press Enter for random): ").strip()
            agreed = agreed.lower() == 'y' if agreed else None
            minutes = input("Call duration in minutes (press Enter for random): ").strip()
            minutes = float(minutes) if minutes else None
            call_type = input("Call type (manual/agent, press Enter for random): ").strip()
            call_type = call_type if call_type in ['manual', 'agent'] else None
            call_id = input("Call ID (press Enter for auto-generated): ").strip()
            call_id = call_id if call_id else None
            sentiment = input("Sentiment (positive/neutral/negative, press Enter for random): ").strip()
            sentiment = sentiment if sentiment in ['positive', 'neutral', 'negative'] else None
            notes = input("Notes (press Enter for auto-generated): ").strip()
            notes = notes if notes else None
            #Print the data types
            print(f"Data type of agreed: {type(agreed)}")
            print(f"Data type of minutes: {type(minutes)}")
            print(f"Data type of call_type: {type(call_type)}")
            print(f"Data type of sentiment: {type(sentiment)}")
            print(f"Data type of notes: {type(notes)}")
            print(f"Data type of call_id: {type(call_id)}")
            print(f"Data type of load_id: {type(load_id)}")
            tester.add_phone_call(load_id, agreed, minutes, call_type, sentiment, notes, call_id)
        elif choice == '12':
            load_id = input("Enter load_id to get phone calls for: ").strip()
            tester.get_phone_calls(load_id)
        elif choice == '13':
            load_id = input("Enter load_id to delete all phone calls for: ").strip()
            confirm = input("Are you sure you want to delete ALL phone calls? (y/n): ").strip()
            if confirm.lower() == 'y':
                tester.delete_all_phone_calls(load_id)
            else:
                print("❌ Operation cancelled")
        elif choice == '14':
            tester.list_all_phone_calls()
        elif choice == '15':
            tester.list_phone_calls_by_type('manual')
        elif choice == '16':
            tester.list_phone_calls_by_type('agent')
        elif choice == '17':
            load_id = input("Enter load_id to test string inputs with: ").strip()
            tester.add_phone_call_with_strings(load_id)
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
