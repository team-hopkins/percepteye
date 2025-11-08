"""
Test script for the Semantic Router
"""

import requests
import base64
import json
from pathlib import Path


def test_analyze_endpoint(router_url: str, image_path: str = None, audio_desc: str = None):
    """Test the /analyze endpoint"""
    print("\n=== Testing /analyze endpoint ===")
    
    payload = {}
    
    if image_path:
        # Load and encode image
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            payload["image_base64"] = img_base64
    
    if audio_desc:
        payload["audio_description"] = audio_desc
    
    try:
        response = requests.post(f"{router_url}/analyze", json=payload)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Success!")
        print(f"  Route: {result['route']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Reasoning: {result['reasoning']}")
        
        return result
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def test_route_endpoint(router_url: str, image_path: str = None, audio_desc: str = None):
    """Test the /route endpoint"""
    print("\n=== Testing /route endpoint ===")
    
    payload = {}
    
    if image_path:
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            payload["image_base64"] = img_base64
    
    if audio_desc:
        payload["audio_description"] = audio_desc
    
    try:
        response = requests.post(f"{router_url}/route", json=payload)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Success!")
        print(f"  Routing Decision: {result['routing_decision']}")
        print(f"  API Response: {result['api_response']}")
        print(f"  Status: {result['status']}")
        
        return result
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def test_health_check(router_url: str):
    """Test the health check endpoint"""
    print("\n=== Testing /health endpoint ===")
    
    try:
        response = requests.get(f"{router_url}/health")
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Health check passed!")
        print(f"  {json.dumps(result, indent=2)}")
        
        return True
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    router_url = "http://localhost:8000"
    
    print("PerceptEye Semantic Router - Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    test_health_check(router_url)
    
    # Test 2: Analyze with audio description
    test_analyze_endpoint(
        router_url,
        audio_desc="Someone is speaking clearly"
    )
    
    # Test 3: Analyze with hypothetical scenarios
    print("\n=== Testing different scenarios ===")
    
    scenarios = [
        {"audio_description": "A person is waving their hands in sign language"},
        {"audio_description": "I see someone's face clearly"},
        {"audio_description": "Someone is talking to me"},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario}")
        test_analyze_endpoint(router_url, **scenario)
    
    print("\n" + "=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    main()
