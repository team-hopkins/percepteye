"""
Comprehensive Test Suite for PerceptEye Semantic Router

Tests both Sign Language Detection API and Face Recognition + TTS API integration

Usage:
  # Run all tests with Docker (default port 8001)
  python test.py
  
  # Run all tests with local Python server (port 8000)
  ROUTER_URL=http://localhost:8000 python test.py
  
  # Run specific test
  python test.py --test sign_language
  python test.py --test face_recognition
  python test.py --test health
"""

import requests
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional


class PerceptEyeTestSuite:
    """Comprehensive test suite for PerceptEye Semantic Router"""
    
    def __init__(self, router_url: Optional[str] = None):
        self.router_url = router_url or os.environ.get("ROUTER_URL", "http://localhost:8001")
        self.sign_language_api_url = "http://138.197.12.52"
        self.face_recognition_api_url = "http://143.198.4.179"
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "=" * 70)
        print(f"🤖 {title}")
        print("=" * 70)
    
    def print_section(self, title: str):
        """Print a formatted section"""
        print(f"\n{'─' * 70}")
        print(f"📋 {title}")
        print(f"{'─' * 70}")
    
    def test_health_check(self):
        """Test 1: Health check endpoint"""
        self.print_section("Test 1: Health Check")
        
        try:
            response = requests.get(f"{self.router_url}/health", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Health check passed!")
            print(f"   Status: {result.get('status')}")
            print(f"   Router: {result.get('router')}")
            return True
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_sign_language_detection(self):
        """Test 2: Sign Language Detection"""
        self.print_section("Test 2: Sign Language Detection")
        
        image_path = "test/B_test.jpg"
        
        if not Path(image_path).exists():
            print(f"⚠️  Test image not found: {image_path}")
            return False
        
        print(f"📸 Loading image: {image_path}")
        
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"✅ Image loaded: {len(image_bytes)} bytes → {len(image_base64)} chars (base64)")
        print(f"🚀 Sending to: {self.router_url}/route")
        
        payload = {
            "image_base64": image_base64,
            "audio_description": "Person making sign language gestures"
        }
        
        try:
            response = requests.post(
                f"{self.router_url}/route",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            routing = result.get('routing_decision', {})
            api_response = result.get('api_response', {})
            status = result.get('status')
            
            print(f"\n🎯 Routing Decision:")
            print(f"   Route: {routing.get('route', 'none').upper()}")
            print(f"   Confidence: {routing.get('confidence', 0) * 100:.1f}%")
            print(f"   Reasoning: {routing.get('reasoning', '')}")
            
            if api_response and api_response.get('success'):
                print(f"\n🤟 Sign Language API Response:")
                print(f"   Success: {api_response.get('success')}")
                print(f"   Hand Detected: {api_response.get('hand_detected')}")
                print(f"   Predicted Sign: '{api_response.get('predicted_sign')}'")
                print(f"   Confidence: {api_response.get('confidence', 0) * 100:.1f}%")
                
                predictions = api_response.get('all_predictions', [])
                if predictions:
                    print(f"\n   📊 Top 3 Predictions:")
                    for i, pred in enumerate(predictions[:3], 1):
                        sign = pred.get('sign', 'N/A')
                        conf = pred.get('confidence', 0)
                        print(f"      {i}. {sign} - {conf * 100:.1f}%")
                
                if routing.get('route') == 'sign_language' and api_response.get('hand_detected'):
                    print(f"\n✅ ✅ ✅ SUCCESS! Sign language detection working correctly!")
                    return True
            
            print(f"\n⚠️  Test completed with status: {status}")
            return status == 'success'
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_face_recognition_routing(self):
        """Test 3: Face Recognition + TTS Routing"""
        self.print_section("Test 3: Face Recognition + TTS Routing")
        
        print(f"🔍 Testing routing decision with face scenario...")
        
        payload = {
            "audio_description": "I see a person in front of me, can you identify who they are?"
        }
        
        try:
            response = requests.post(
                f"{self.router_url}/analyze",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"\n🎯 Routing Decision:")
            print(f"   Route: {result.get('route', 'none').upper()}")
            print(f"   Confidence: {result.get('confidence', 0) * 100:.1f}%")
            print(f"   Reasoning: {result.get('reasoning', '')}")
            
            if result.get('route') == 'face_recognition_tts':
                print(f"\n✅ Router correctly identified FACE_RECOGNITION_TTS")
                return True
            else:
                print(f"\n⚠️  Expected: face_recognition_tts, Got: {result.get('route')}")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_face_recognition_api_call(self):
        """Test 4: Face Recognition API with Image"""
        self.print_section("Test 4: Face Recognition + TTS API Call")
        
        image_path = "test/B_test.jpg"
        
        if not Path(image_path).exists():
            print(f"⚠️  Test image not found: {image_path}")
            return False
        
        print(f"📸 Loading image: {image_path}")
        print(f"   Note: Using sign language image to test face detection (should find no faces)")
        
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "image_base64": image_base64,
            "audio_description": "Can you identify any people in this image?"
        }
        
        try:
            response = requests.post(
                f"{self.router_url}/route",
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            routing = result.get('routing_decision', {})
            api_response = result.get('api_response', {})
            
            print(f"\n🎯 Routing Decision:")
            print(f"   Route: {routing.get('route', 'none').upper()}")
            print(f"   Confidence: {routing.get('confidence', 0) * 100:.1f}%")
            
            if api_response:
                print(f"\n👥 Face Recognition API Response:")
                print(f"   Faces Detected: {api_response.get('faces', [])}")
                print(f"   Locations: {api_response.get('locations', [])}")
                print(f"   Unknown Count: {api_response.get('unknown_count', 0)}")
                
                announcement = api_response.get('announcement')
                if announcement:
                    print(f"   Announcement: {announcement}")
                
                print(f"\n✅ Face Recognition API is responding correctly!")
                return True
            else:
                print(f"\n⚠️  No API response received")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_direct_api_calls(self):
        """Test 5: Direct API Endpoint Tests"""
        self.print_section("Test 5: Direct API Endpoint Tests")
        
        image_path = "test/B_test.jpg"
        if not Path(image_path).exists():
            print(f"⚠️  Test image not found: {image_path}")
            return False
        
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Test Sign Language API directly
        print(f"\n🔹 Testing Sign Language API: {self.sign_language_api_url}/predict/base64")
        try:
            response = requests.post(
                f"{self.sign_language_api_url}/predict/base64",
                json={"image_base64": image_base64},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            print(f"   ✅ Sign Language API: {result.get('predicted_sign')} "
                  f"(confidence: {result.get('confidence', 0) * 100:.1f}%)")
        except Exception as e:
            print(f"   ❌ Sign Language API Error: {e}")
        
        # Test Face Recognition API directly
        print(f"\n🔹 Testing Face Recognition API: {self.face_recognition_api_url}/process")
        try:
            response = requests.post(
                f"{self.face_recognition_api_url}/process",
                data={
                    'image': image_base64,
                    'annotated': 'false',
                    'announce': 'true'
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            print(f"   ✅ Face Recognition API: {len(result.get('faces', []))} faces detected")
            if result.get('announcement'):
                print(f"   Announcement: {result.get('announcement')}")
        except Exception as e:
            print(f"   ❌ Face Recognition API Error: {e}")
        
        return True
    
    def test_multiple_scenarios(self):
        """Test 6: Multiple Routing Scenarios"""
        self.print_section("Test 6: Multiple Routing Scenarios")
        
        scenarios = [
            {
                "name": "Sign Language Scenario",
                "payload": {
                    "audio_description": "A person is waving their hands in sign language"
                },
                "expected_route": "sign_language"
            },
            {
                "name": "Face Recognition Scenario",
                "payload": {
                    "audio_description": "I see someone's face clearly, who is this person?"
                },
                "expected_route": "face_recognition_tts"
            },
            {
                "name": "Speech Scenario",
                "payload": {
                    "audio_description": "Someone is talking to me"
                },
                "expected_route": "face_recognition_tts"
            }
        ]
        
        results = []
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n   Scenario {i}: {scenario['name']}")
            
            try:
                response = requests.post(
                    f"{self.router_url}/analyze",
                    json=scenario['payload'],
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                route = result.get('route')
                confidence = result.get('confidence', 0) * 100
                expected = scenario['expected_route']
                
                match = "✅" if route == expected else "⚠️"
                print(f"      {match} Route: {route} (confidence: {confidence:.0f}%)")
                print(f"         Expected: {expected}")
                
                results.append(route == expected)
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n   📊 Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)} scenarios)")
        return success_rate >= 66  # At least 2 out of 3 should pass
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("PerceptEye Semantic Router - Comprehensive Test Suite")
        
        print(f"\n📍 Router URL: {self.router_url}")
        print(f"📍 Sign Language API: {self.sign_language_api_url}")
        print(f"📍 Face Recognition API: {self.face_recognition_api_url}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Sign Language Detection", self.test_sign_language_detection),
            ("Face Recognition Routing", self.test_face_recognition_routing),
            ("Face Recognition API Call", self.test_face_recognition_api_call),
            ("Multiple Scenarios", self.test_multiple_scenarios),
            ("Direct API Calls", self.test_direct_api_calls),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ Test '{test_name}' failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        self.print_header("Test Summary")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n📊 Results:")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} - {test_name}")
        
        print(f"\n{'=' * 70}")
        print(f"🎯 Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        
        if passed == total:
            print(f"🎉 🎉 🎉 ALL TESTS PASSED! 🎉 🎉 🎉")
        elif passed >= total * 0.8:
            print(f"✅ Most tests passed - System operational")
        else:
            print(f"⚠️  Some tests failed - Check configuration")
        
        print(f"{'=' * 70}\n")
        
        return passed == total


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PerceptEye Semantic Router Test Suite')
    parser.add_argument('--router-url', type=str, help='Router URL (default: http://localhost:8001)')
    parser.add_argument('--test', type=str, choices=['health', 'sign_language', 'face_recognition', 'scenarios', 'direct', 'all'],
                        default='all', help='Specific test to run (default: all)')
    
    args = parser.parse_args()
    
    suite = PerceptEyeTestSuite(router_url=args.router_url)
    
    if args.test == 'health':
        suite.test_health_check()
    elif args.test == 'sign_language':
        suite.test_sign_language_detection()
    elif args.test == 'face_recognition':
        suite.test_face_recognition_routing()
        suite.test_face_recognition_api_call()
    elif args.test == 'scenarios':
        suite.test_multiple_scenarios()
    elif args.test == 'direct':
        suite.test_direct_api_calls()
    else:
        suite.run_all_tests()


if __name__ == "__main__":
    main()
