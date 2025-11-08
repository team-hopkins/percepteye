"""
Demo showing what the output looks like when Sign Language API is connected

Usage:
  # Test with Docker (default port 8001)
  python test_demo.py
  
  # Test with local Python server (port 8000)
  ROUTER_URL=http://localhost:8000 python test_demo.py
"""

import requests
import base64
import os
from pathlib import Path


def demo_full_integration():
    """Show what the complete integration looks like"""
    
    IMAGE_PATH = "test/B_test.jpg"
    # Router URL - defaults to 8001 for Docker deployment, use 8000 for local Python
    ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8001")
    
    print("\n" + "=" * 70)
    print("🤖 SEMANTIC ROUTER - Full Integration Demo")
    print("=" * 70)
    
    # Load image
    if not Path(IMAGE_PATH).exists():
        print(f"\n❌ Error: Image not found at {IMAGE_PATH}")
        return
    
    print(f"\n📸 Loading image from {IMAGE_PATH}...")
    with open(IMAGE_PATH, "rb") as image_file:
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    print(f"✅ Image loaded: {len(image_bytes)} bytes → {len(image_base64)} chars (base64)")
    
    # Send to router
    print(f"\n🚀 Sending to semantic router at {ROUTER_URL}/route...")
    
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
        
        result = response.json()
        
        # Display results
        print(f"\n✅ Response received!\n")
        
        routing = result.get('routing_decision', {})
        api_resp = result.get('api_response')
        status = result.get('status')
        
        print("┌" + "─" * 68 + "┐")
        print("│ 🎯 ROUTING DECISION" + " " * 47 + "│")
        print("├" + "─" * 68 + "┤")
        print(f"│ Route: {routing.get('route', 'none').upper():<58} │")
        print(f"│ Confidence: {routing.get('confidence', 0):.0%} {' ' * 53} │")
        print(f"│ Reasoning: {routing.get('reasoning', '')[:54]:<54} │")
        print("└" + "─" * 68 + "┘")
        
        print("\n┌" + "─" * 68 + "┐")
        print("│ 🤟 SIGN LANGUAGE API RESULT" + " " * 40 + "│")
        print("├" + "─" * 68 + "┤")
        
        if api_resp and api_resp.get('hand_detected'):
            sign = api_resp.get('predicted_sign', 'N/A')
            conf = api_resp.get('confidence', 0)
            
            print(f"│ ✅ Hand Detected: YES" + " " * 46 + "│")
            print(f"│ 🔤 Predicted Sign: '{sign}'" + " " * (53 - len(sign)) + "│")
            print(f"│ 📊 Confidence: {conf:.1%}" + " " * 51 + "│")
            
            predictions = api_resp.get('all_predictions', [])
            if predictions:
                print("│" + " " * 68 + "│")
                print("│ 📋 Top Predictions:" + " " * 48 + "│")
                for i, pred in enumerate(predictions[:3], 1):
                    p_sign = pred.get('sign', 'N/A')
                    p_conf = pred.get('confidence', 0)
                    print(f"│    {i}. {p_sign} - {p_conf:.1%}" + " " * (58 - len(p_sign)) + "│")
        elif status == 'skipped':
            print("│ ⚠️  Status: SKIPPED (Low confidence)" + " " * 30 + "│")
            print("│ The router wasn't confident enough to route" + " " * 23 + "│")
        else:
            print("│ ⚠️  Sign Language API not responding" + " " * 30 + "│")
            print("│ Make sure the API is running on Digital Ocean" + " " * 20 + "│")
        
        print("└" + "─" * 68 + "┘")
        
        # Summary
        if (routing.get('route') == 'sign_language' and 
            api_resp and api_resp.get('hand_detected')):
            print("\n" + "🎉" * 35)
            print("✅ FULL SUCCESS!")
            print(f"   Detected sign language gesture: '{api_resp.get('predicted_sign')}'")
            print("🎉" * 35)
        elif routing.get('route') == 'sign_language':
            print("\n⚠️  Router identified sign language, but API isn't connected")
            print("   Set SIGN_LANGUAGE_API_URL in .env to connect the API")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to router at {ROUTER_URL}")
        print("   Start it with: docker-compose up -d")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print()


def show_expected_output():
    """Show what the output looks like when everything is connected"""
    
    print("\n" + "=" * 70)
    print("📋 EXPECTED OUTPUT (When Sign Language API is connected)")
    print("=" * 70)
    
    print("""
┌────────────────────────────────────────────────────────────────────┐
│ 🎯 ROUTING DECISION                                                │
├────────────────────────────────────────────────────────────────────┤
│ Route: SIGN_LANGUAGE                                               │
│ Confidence: 95%                                                    │
│ Reasoning: Hand gestures detected, routing to sign language API   │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ 🤟 SIGN LANGUAGE API RESULT                                        │
├────────────────────────────────────────────────────────────────────┤
│ ✅ Hand Detected: YES                                              │
│ 🔤 Predicted Sign: 'B'                                             │
│ 📊 Confidence: 99.6%                                               │
│                                                                    │
│ 📋 Top Predictions:                                                │
│    1. B - 99.6%                                                    │
│    2. W - 0.3%                                                     │
│    3. E - 0.1%                                                     │
└────────────────────────────────────────────────────────────────────┘

🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
✅ FULL SUCCESS!
   Detected sign language gesture: 'B'
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
""")
    
    print("=" * 70)
    print("To see this for real:")
    print("1. Deploy/start your Sign Language API")
    print("2. Update SIGN_LANGUAGE_API_URL in .env")
    print("3. Run: python test_simple.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Try actual test first
    demo_full_integration()
    
    # Show expected output
    print("\n" * 2)
    show_expected_output()
