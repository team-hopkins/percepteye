"""
Simple test to demonstrate semantic router detecting sign language from base64 image

Usage:
  # Test with Docker (default port 8001)
  python test_simple.py
  
  # Test with local Python server (port 8000)
  ROUTER_URL=http://localhost:8000 python test_simple.py
"""

import requests
import base64
import os
from pathlib import Path


def test_sign_language_detection():
    """Test semantic router with sign language image"""
    
    # Configuration
    IMAGE_PATH = "test/B_test.jpg"
    # Router URL - defaults to 8001 for Docker deployment, use 8000 for local Python
    ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8001")
    
    print("\n" + "=" * 70)
    print("🤖 SEMANTIC ROUTER - Sign Language Detection Test")
    print("=" * 70)
    
    # Check if image exists
    if not Path(IMAGE_PATH).exists():
        print(f"\n❌ Error: Image not found at {IMAGE_PATH}")
        return
    
    # Step 1: Load and encode image
    print(f"\n📸 Step 1: Loading image from {IMAGE_PATH}...")
    with open(IMAGE_PATH, "rb") as image_file:
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    print(f"✅ Image loaded and encoded to base64")
    print(f"   Size: {len(image_bytes)} bytes")
    print(f"   Base64 length: {len(image_base64)} characters")
    
    # Step 2: Send to semantic router (full route with API call)
    print(f"\n🚀 Step 2: Sending to semantic router...")
    print(f"   Endpoint: {ROUTER_URL}/route")
    print(f"   Note: This will call the Sign Language Detection API")
    
    payload = {
        "image_base64": image_base64,
        "audio_description": "Person making hand gestures for sign language"
    }
    
    try:
        response = requests.post(
            f"{ROUTER_URL}/route",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"\n❌ Error: API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return
        
        # Step 3: Parse and display results
        result = response.json()
        
        print(f"\n✅ Response received!")
        
        # Display routing decision
        print(f"\n" + "=" * 70)
        print("🎯 ROUTING DECISION")
        print("=" * 70)
        
        routing_decision = result.get('routing_decision', {})
        route = routing_decision.get('route')
        confidence = routing_decision.get('confidence', 0)
        reasoning = routing_decision.get('reasoning', '')
        error = routing_decision.get('error', False)
        
        print(f"\n📍 Detected Route: {route.upper() if route else 'NONE'}")
        print(f"📊 Router Confidence: {confidence:.1%}")
        print(f"💭 Reasoning: {reasoning}")
        print(f"❌ Error: {error}")
        
        # Display Sign Language API response
        print(f"\n" + "=" * 70)
        print("🤟 SIGN LANGUAGE API RESPONSE")
        print("=" * 70)
        
        api_response = result.get('api_response')
        status = result.get('status')
        
        if api_response:
            success = api_response.get('success', False)
            hand_detected = api_response.get('hand_detected', False)
            predicted_sign = api_response.get('predicted_sign')
            sign_confidence = api_response.get('confidence', 0)
            message = api_response.get('message', '')
            contextual_meaning = api_response.get('contextual_meaning')
            alternative_contexts = api_response.get('alternative_contexts', [])
            
            print(f"\n✅ API Call Status: {status.upper()}")
            print(f"🎯 Success: {success}")
            print(f"👋 Hand Detected: {hand_detected}")
            
            if hand_detected and predicted_sign:
                print(f"\n🔤 Predicted Sign: '{predicted_sign}'")
                print(f"📊 Prediction Confidence: {sign_confidence:.1%}")
                print(f"💬 Message: {message}")
                
                if contextual_meaning:
                    print(f"🎯 Contextual Meaning: '{contextual_meaning}'")
                
                if alternative_contexts:
                    print(f"🔄 Alternative Meanings: {', '.join(alternative_contexts)}")
            else:
                print(f"\n⚠️  No hand detected or no prediction")
                print(f"💬 Message: {message}")
        else:
            print(f"\n⚠️  No API response received")
            print(f"📊 Status: {status}")
            print(f"   The Sign Language API might not be running")
        
        # Final verdict
        print(f"\n" + "=" * 70)
        if (route == 'sign_language' and not error and 
            api_response and api_response.get('hand_detected')):
            print("✅ ✅ ✅ FULL SUCCESS! ✅ ✅ ✅")
            print("\n🎉 The semantic router:")
            print("   1. Correctly identified this as SIGN LANGUAGE")
            print("   2. Called the Sign Language Detection API")
            print(f"   3. Detected the sign: '{api_response.get('predicted_sign')}'")
        elif route == 'sign_language' and not error:
            print("⚠️  PARTIAL SUCCESS")
            print("\n✅ Router correctly identified sign language")
            print("⚠️  But Sign Language API call had issues")
            print("   (Make sure the Sign Language API is running)")
        else:
            print("⚠️  UNEXPECTED RESULT")
            print(f"\nExpected route: sign_language")
            print(f"Got: {route}")
        
        print("=" * 70 + "\n")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Cannot connect to router at {ROUTER_URL}")
        print(f"   Make sure the router is running:")
        print(f"   → docker-compose up -d")
        print(f"   → or: python api_server.py")
    except requests.exceptions.Timeout:
        print(f"\n❌ Error: Request timed out")
        print(f"   The router might be processing slowly")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    test_sign_language_detection()
