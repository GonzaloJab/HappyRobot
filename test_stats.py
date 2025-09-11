#!/usr/bin/env python3
"""
Test script to verify the stats endpoint is working
"""

import requests
import json

def test_stats_endpoint():
    url = "http://localhost:8000/shipments/stats"
    headers = {
        "X-API-Key": "HapRob-OTVHhErcXLu2eKkUMP6lDtrd8UNi61KZo4FvGALqem0NoJO1uWlz7OywCN0BNoNaG2x5Y",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Stats Response:")
            print(json.dumps(data, indent=2))
            
            # Check if we have the expected structure
            if "manual" in data and "url_api" in data:
                print("\n✅ Stats endpoint is working correctly!")
                print(f"Manual assignments: {data['manual']['count']} loads")
                print(f"URL/API assignments: {data['url_api']['count']} loads")
                
                if data['manual']['count'] > 0:
                    print(f"Manual avg time per call: {data['manual']['avg_time_per_call_seconds']:.1f} seconds")
                    print(f"Manual price difference: ${data['manual']['total_agreed_minus_loadboard']:.2f}")
                
                if data['url_api']['count'] > 0:
                    print(f"URL/API avg time per call: {data['url_api']['avg_time_per_call_seconds']:.1f} seconds")
                    print(f"URL/API price difference: ${data['url_api']['total_agreed_minus_loadboard']:.2f}")
            else:
                print("❌ Stats response missing expected structure")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_stats_endpoint()
