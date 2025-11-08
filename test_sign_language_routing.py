"""
Test script to verify semantic router correctly routes sign language images

Usage:
  # Test with Docker (default port 8001)
  python test_sign_language_routing.py
  
  # Test with local Python server (port 8000)
  ROUTER_URL=http://localhost:8000 python test_sign_language_routing.py
"""

import requests
import base64
import json
import os
from pathlib import Path
from typing import Optional


def test_semantic_router_with_image(image_path: str, router_url: Optional[str] = None):
    """
    Test the semantic router with a sign language image
    
    Args:
        image_path: Path to the test image
        router_url: URL of the semantic router API (defaults to Docker port 8001)
    """
    if router_url is None:
        router_url = os.environ.get("ROUTER_URL", "http://localhost:8001")
    
    print("=" * 70)
    print("Testing Semantic Router - Sign Language Detection")
    print("=" * 70)
    
    # Check if image exists
    image_file = Path(image_path)
    if not image_file.exists():
        print(f"❌ Error: Image not found at {image_path}")
        return
    
    print(f"\n📁 Loading image: {image_path}")
    
    # Read and encode image
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"✅ Image loaded and encoded to base64 ({len(image_base64)} characters)")
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return
    
    # Test 1: Health Check
    print(f"\n🏥 Testing health endpoint...")
    try:
        health_response = requests.get(f"{router_url}/health", timeout=5)
        if health_response.status_code == 200:
            print(f"✅ Router is healthy: {health_response.json()}")
        else:
            print(f"⚠️  Router health check returned: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Router health check failed: {e}")
        print("Make sure the router is running: python api_server.py")
        return
    
    # Test 2: Analyze endpoint (get routing decision only)
    print(f"\n🔍 Testing /analyze endpoint (routing decision only)...")
    try:
        analyze_payload = {
            "image_base64": image_base64,
            "audio_description": "Person making hand gestures for sign language"
        }
        
        analyze_response = requests.post(
            f"{router_url}/analyze",
            json=analyze_payload,
            timeout=30
        )
        
        if analyze_response.status_code == 200:
            result = analyze_response.json()
            print(f"\n📊 Routing Decision:")
            print(f"   Route: {result.get('route')}")
            print(f"   Confidence: {result.get('confidence', 0):.1%}")
            print(f"   Reasoning: {result.get('reasoning')}")
            print(f"   Error: {result.get('error', False)}")
            
            if result.get('route') == 'sign_language':
                print(f"\n✅ SUCCESS! Router correctly identified this as sign language!")
            else:
                print(f"\n⚠️  Router identified this as: {result.get('route')}")
                print(f"   Expected: sign_language")
        else:
            print(f"❌ Analyze request failed: {analyze_response.status_code}")
            print(f"   Response: {analyze_response.text}")
            
    except Exception as e:
        print(f"❌ Error calling /analyze endpoint: {e}")
    
    # Test 3: Route endpoint (full integration - will call Sign Language API)
    print(f"\n🚀 Testing /route endpoint (will call Sign Language API)...")
    print("⚠️  Note: This requires the Sign Language API to be running!")
    
    try:
        route_payload = {
            "image_base64": image_base64,
            "audio_description": "Person making hand gestures"
        }
        
        route_response = requests.post(
            f"{router_url}/route",
            json=route_payload,
            timeout=30
        )
        
        if route_response.status_code == 200:
            result = route_response.json()
            print(f"\n📊 Full Routing Result:")
            print(f"\n1️⃣  Routing Decision:")
            print(f"   Route: {result.get('routing_decision', {}).get('route')}")
            print(f"   Confidence: {result.get('routing_decision', {}).get('confidence', 0):.1%}")
            print(f"   Reasoning: {result.get('routing_decision', {}).get('reasoning')}")
            
            print(f"\n2️⃣  API Response:")
            api_response = result.get('api_response')
            if api_response:
                print(f"   Success: {api_response.get('success')}")
                print(f"   Hand Detected: {api_response.get('hand_detected')}")
                print(f"   Predicted Sign: {api_response.get('predicted_sign')}")
                print(f"   Confidence: {api_response.get('confidence', 0):.1%}")
                print(f"   Message: {api_response.get('message')}")
            else:
                print(f"   No API response (API might not be running)")
            
            print(f"\n3️⃣  Status: {result.get('status')}")
            
            # Check if everything worked
            routing_decision = result.get('routing_decision', {})
            if (routing_decision.get('route') == 'sign_language' and 
                api_response and 
                api_response.get('hand_detected')):
                print(f"\n✅ FULL SUCCESS! Sign language detected and API called successfully!")
            elif routing_decision.get('route') == 'sign_language':
                print(f"\n⚠️  Router correctly identified sign language, but API call had issues")
            else:
                print(f"\n⚠️  Router did not identify this as sign language")
                
        else:
            print(f"❌ Route request failed: {route_response.status_code}")
            print(f"   Response: {route_response.text}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out - Sign Language API might not be running")
    except Exception as e:
        print(f"❌ Error calling /route endpoint: {e}")
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


def test_multiple_scenarios(router_url: Optional[str] = None):
    """Test different scenarios"""
    
    if router_url is None:
        router_url = os.environ.get("ROUTER_URL", "http://localhost:8001")
    
    print("\n" + "=" * 70)
    print("Testing Multiple Scenarios")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Sign Language Gesture",
            "audio_description": "Person making hand gestures for sign language",
            "expected": "sign_language"
        },
        {
            "name": "Person Speaking",
            "audio_description": "Someone is speaking clearly",
            "expected": "speech"
        },
        {
            "name": "Face Only",
            "audio_description": "I see a person's face",
            "expected": "people_recognition"
        }
    ]
    
    # Use the same image but with different context
    image_path = "test/B_test.jpg"
    
    if not Path(image_path).exists():
        print(f"❌ Test image not found: {image_path}")
        return
    
    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─' * 70}")
        print(f"Scenario {i}: {scenario['name']}")
        print(f"Context: {scenario['audio_description']}")
        print(f"Expected Route: {scenario['expected']}")
        print(f"{'─' * 70}")
        
        try:
            payload = {
                "image_base64": image_base64,
                "audio_description": scenario['audio_description']
            }
            
            response = requests.post(
                f"{router_url}/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                route = result.get('route')
                confidence = result.get('confidence', 0)
                
                if route == scenario['expected']:
                    print(f"✅ CORRECT: Routed to {route} (confidence: {confidence:.1%})")
                else:
                    print(f"⚠️  Got: {route} | Expected: {scenario['expected']} (confidence: {confidence:.1%})")
                
                print(f"   Reasoning: {result.get('reasoning')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    # Default test image
    test_image = "test/B_test.jpg"
    # Default router URL - use env var or default to Docker port (8001)
    router_url = os.environ.get("ROUTER_URL", "http://localhost:8001")
    
    # Allow custom image path from command line
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
    
    if len(sys.argv) > 2:
        router_url = sys.argv[2]
    
    # Run main test
    test_semantic_router_with_image(test_image, router_url)
    
    # Run multiple scenario tests
    print("\n")
    test_multiple_scenarios(router_url)
