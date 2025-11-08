"""
Test suite for Face Recognition + TTS API integration with pytest assertions

This tests the semantic router with scenarios that should route to face recognition
"""

import pytest
import requests
import base64
import os
from pathlib import Path


ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8001")
FACE_API_URL = "http://143.198.4.179/process"
TEST_IMAGE = "test/B_test.jpg"


def test_face_recognition_analyze_endpoint():
    """Test 1: Analyze endpoint with face scenario - should route to face_recognition_tts"""
    
    payload = {
        "audio_description": "I see a person in front of me, can you tell me who they are?"
    }
    
    response = requests.post(
        f"{ROUTER_URL}/analyze",
        json=payload,
        timeout=30
    )
    
    # Assert HTTP status
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    result = response.json()
    
    # Assert routing decision
    assert result.get('route') == 'face_recognition_tts', \
        f"Expected route 'face_recognition_tts', got '{result.get('route')}'"
    
    # Assert confidence is above threshold
    confidence = result.get('confidence', 0)
    assert confidence > 0.5, \
        f"Expected confidence > 0.5, got {confidence}"
    
    # Assert response structure
    assert 'reasoning' in result, "Response should contain 'reasoning'"
    assert isinstance(result.get('error', False), bool), "'error' should be boolean"


def test_face_recognition_route_endpoint():
    """Test 2: Route endpoint with image + face description"""
    
    if not Path(TEST_IMAGE).exists():
        pytest.skip(f"Test image not found: {TEST_IMAGE}")
    
    with open(TEST_IMAGE, "rb") as image_file:
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "image_base64": image_base64,
        "audio_description": "I see a person's face, can you identify who they are?"
    }
    
    response = requests.post(
        f"{ROUTER_URL}/route",
        json=payload,
        timeout=60
    )
    
    # Assert HTTP status
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    result = response.json()
    
    # Assert response structure
    assert 'routing_decision' in result, "Response should contain 'routing_decision'"
    assert 'api_response' in result, "Response should contain 'api_response'"
    assert 'status' in result, "Response should contain 'status'"
    
    routing_decision = result['routing_decision']
    
    # Assert routing decision structure
    assert 'route' in routing_decision, "routing_decision should contain 'route'"
    assert 'confidence' in routing_decision, "routing_decision should contain 'confidence'"
    
    # Assert confidence is above threshold
    confidence = routing_decision.get('confidence', 0)
    assert confidence > 0.5, f"Expected confidence > 0.5, got {confidence}"
    
    # Assert status is success or valid
    status = result['status']
    assert status in ['success', 'skipped', 'error'], \
        f"Expected status in ['success', 'skipped', 'error'], got '{status}'"
    
    # If routed to face_recognition_tts, check API response structure
    if routing_decision['route'] == 'face_recognition_tts' and status == 'success':
        api_response = result['api_response']
        assert api_response is not None, "api_response should not be None for successful face recognition"
        
        # Check expected Face Recognition API fields
        assert 'faces' in api_response, "api_response should contain 'faces'"
        assert 'locations' in api_response, "api_response should contain 'locations'"
        assert 'unknown_count' in api_response, "api_response should contain 'unknown_count'"
        
        assert isinstance(api_response['faces'], list), "'faces' should be a list"
        assert isinstance(api_response['unknown_count'], int), "'unknown_count' should be an integer"
    
    # If routed to sign_language, check Sign Language API response structure
    elif routing_decision['route'] == 'sign_language' and status == 'success':
        api_response = result['api_response']
        assert api_response is not None, "api_response should not be None for successful sign language detection"
        
        # Check expected Sign Language API fields
        assert 'predicted_sign' in api_response or 'hand_detected' in api_response, \
            "api_response should contain sign language detection fields"


def test_face_recognition_direct_api_call():
    """Test 3: Direct call to Face Recognition API"""
    
    if not Path(TEST_IMAGE).exists():
        pytest.skip(f"Test image not found: {TEST_IMAGE}")
    
    with open(TEST_IMAGE, "rb") as image_file:
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    response = requests.post(
        FACE_API_URL,
        data={
            'image': image_base64,
            'annotated': 'true',
            'announce': 'true',
            'speak': 'false'
        },
        timeout=60
    )
    
    # Assert HTTP status
    assert response.status_code == 200, \
        f"Expected status 200 from Face API, got {response.status_code}: {response.text[:200]}"
    
    result = response.json()
    
    # Assert expected Face Recognition API fields exist
    assert 'faces' in result, "Face API response should contain 'faces'"
    assert 'locations' in result, "Face API response should contain 'locations'"
    assert 'unknown_count' in result, "Face API response should contain 'unknown_count'"
    
    # Assert field types
    assert isinstance(result['faces'], list), "'faces' should be a list"
    assert isinstance(result['locations'], list), "'locations' should be a list"
    assert isinstance(result['unknown_count'], int), "'unknown_count' should be an integer"
    
    # Assert result structure is valid (even if no faces detected)
    assert len(result['faces']) >= 0, "'faces' list should have non-negative length"
    assert result['unknown_count'] >= 0, "'unknown_count' should be non-negative"


def test_router_health_check():
    """Test 4: Router health check"""
    
    response = requests.get(f"{ROUTER_URL}/health", timeout=10)
    
    # Assert HTTP status
    assert response.status_code == 200, f"Health check failed with status {response.status_code}"
    
    result = response.json()
    
    # Assert health check response
    assert 'status' in result, "Health check should contain 'status'"
    assert result['status'] == 'healthy', f"Expected status 'healthy', got '{result.get('status')}'"


if __name__ == "__main__":
    # Run with pytest if available, otherwise run basic tests
    try:
        import pytest
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not installed, running basic tests...")
        print("\nTest 1: Face Recognition Analyze Endpoint")
        test_face_recognition_analyze_endpoint()
        print("✅ PASSED")
        
        print("\nTest 2: Face Recognition Route Endpoint")
        test_face_recognition_route_endpoint()
        print("✅ PASSED")
        
        print("\nTest 3: Direct Face API Call")
        test_face_recognition_direct_api_call()
        print("✅ PASSED")
        
        print("\nTest 4: Router Health Check")
        test_router_health_check()
        print("✅ PASSED")
        
        print("\n" + "=" * 70)
        print("All tests passed!")
        print("=" * 70)
