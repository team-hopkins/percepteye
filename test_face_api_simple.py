"""
Simple test for Face Recognition + TTS API integration

This tests the semantic router with a scenario that should route to face recognition
"""

import requests
import base64
import os
from pathlib import Path


def test_face_recognition_scenario():
    """Test with a scenario description that should route to face recognition"""
    
    ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8001")
    
    print("=" * 70)
    print("🤖 SEMANTIC ROUTER - Face Recognition + TTS Test")
    print("=" * 70)
    
    # Test 1: Just analyze endpoint with face scenario
    print(f"\n📋 Test 1: Analyze endpoint with face scenario")
    print(f"   Endpoint: {ROUTER_URL}/analyze")
    
    payload = {
        "audio_description": "I see a person in front of me, can you tell me who they are?"
    }
    
    try:
        response = requests.post(
            f"{ROUTER_URL}/analyze",
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"\n✅ Routing Decision:")
        print(f"   Route: {result.get('route', 'none').upper()}")
        print(f"   Confidence: {result.get('confidence', 0) * 100:.1f}%")
        print(f"   Reasoning: {result.get('reasoning', '')}")
        
        if result.get('route') == 'face_recognition_tts':
            print(f"\n✅ ✅ ✅ SUCCESS! Router correctly identified FACE_RECOGNITION_TTS")
        else:
            print(f"\n⚠️  Router selected: {result.get('route')}")
            print(f"   Expected: face_recognition_tts")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Test with the sign language image but face-focused description
    print(f"\n\n📋 Test 2: Route endpoint with image + face description")
    print(f"   Note: Using test/B_test.jpg but with face-focused description")
    
    image_path = "test/B_test.jpg"
    if Path(image_path).exists():
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "image_base64": image_base64,
            "audio_description": "I see a person's face, can you identify who they are?"
        }
        
        try:
            response = requests.post(
                f"{ROUTER_URL}/route",
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            routing = result.get('routing_decision', {})
            api_response = result.get('api_response', {})
            status = result.get('status')
            
            print(f"\n✅ Response received!")
            print(f"\n🎯 Routing Decision:")
            print(f"   Route: {routing.get('route', 'none').upper()}")
            print(f"   Confidence: {routing.get('confidence', 0) * 100:.1f}%")
            print(f"   Reasoning: {routing.get('reasoning', '')}")
            
            print(f"\n📊 Status: {status}")
            
            if api_response:
                if 'faces' in api_response:
                    print(f"\n👥 Face Recognition API Response:")
                    print(f"   Faces detected: {api_response.get('faces', [])}")
                    print(f"   Unknown count: {api_response.get('unknown_count', 0)}")
                    if api_response.get('announcement'):
                        print(f"   Announcement: {api_response.get('announcement')}")
                elif 'predicted_sign' in api_response:
                    print(f"\n🤟 Sign Language API Response:")
                    print(f"   Predicted sign: {api_response.get('predicted_sign')}")
                    print(f"   Confidence: {api_response.get('confidence', 0) * 100:.1f}%")
                else:
                    print(f"\n📦 API Response: {api_response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ⚠️  Test image not found: {image_path}")
    
    # Test 3: Direct call to Face Recognition API endpoint
    print(f"\n\n📋 Test 3: Direct call to Face Recognition API")
    print(f"   Testing API at: http://143.198.4.179/process")
    
    if Path(image_path).exists():
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Test the Face Recognition API directly
        try:
            response = requests.post(
                "http://143.198.4.179/process",
                data={
                    'image': image_base64,
                    'annotated': 'true',
                    'announce': 'true',
                    'speak': 'false'
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"\n✅ Direct API call successful!")
            print(f"   Faces detected: {result.get('faces', [])}")
            print(f"   Locations: {result.get('locations', [])}")
            print(f"   Unknown count: {result.get('unknown_count', 0)}")
            if result.get('announcement'):
                print(f"   Announcement: {result.get('announcement')}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text[:200]}")
    
    print(f"\n{'=' * 70}")
    print("Tests completed!")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    test_face_recognition_scenario()
