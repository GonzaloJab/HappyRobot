#!/usr/bin/env python3
import requests
import os
import json

def test_fmcsa_api():
    """Test FMCSA API with different parameter formats"""
    
    # Get API key from environment
    webkey = os.environ.get("FMCSA_WEBKEY")
    if not webkey:
        print("ERROR: FMCSA_WEBKEY environment variable not set")
        return
    
    print(f"API Key found: {webkey[:10]}...{webkey[-4:] if len(webkey) > 14 else webkey}")
    
    base_url = "https://mobile.fmcsa.dot.gov/qc/services/carriers/search/docket-number/"
    
    # Test different parameter formats
    test_cases = [
        {
            "name": "webKey in params",
            "params": {"webKey": webkey},
            "json": {"docketNumber": "1515"}
        },
        {
            "name": "Webkey in params (capital W)",
            "params": {"Webkey": webkey},
            "json": {"docketNumber": "1515"}
        },
        {
            "name": "webKey in headers",
            "params": {},
            "headers": {"webKey": webkey},
            "json": {"docketNumber": "1515"}
        },
        {
            "name": "Webkey in headers (capital W)",
            "params": {},
            "headers": {"Webkey": webkey},
            "json": {"docketNumber": "1515"}
        },
        {
            "name": "Authorization header",
            "params": {},
            "headers": {"Authorization": f"Bearer {webkey}"},
            "json": {"docketNumber": "1515"}
        },
        {
            "name": "API-Key header",
            "params": {},
            "headers": {"API-Key": webkey},
            "json": {"docketNumber": "1515"}
        }
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        try:
            # Merge headers
            test_headers = headers.copy()
            if 'headers' in test_case:
                test_headers.update(test_case['headers'])
            
            response = requests.post(
                base_url,
                params=test_case.get('params', {}),
                headers=test_headers,
                json=test_case.get('json', {}),
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("SUCCESS! Response:")
                    print(json.dumps(data, indent=2))
                    return  # Stop on first success
                except:
                    print("Response (not JSON):")
                    print(response.text)
            else:
                print("Error Response:")
                print(response.text[:500])  # Limit output
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_fmcsa_api()
