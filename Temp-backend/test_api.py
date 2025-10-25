"""
Test script for iForgot Backend API
Demonstrates how to send images and queries to the detection endpoint
"""

import requests
import base64
import json
from pathlib import Path


def encode_image(image_path: str) -> str:
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"


def test_find_item(image_path: str, query: str):
    """
    Test the find-item endpoint
    
    Args:
        image_path: Path to image file
        query: User query (e.g., "I lost my keys")
    """
    print(f"\n{'='*60}")
    print(f"Testing: {query}")
    print(f"Image: {image_path}")
    print(f"{'='*60}\n")
    
    # Encode image
    try:
        image_data = encode_image(image_path)
    except FileNotFoundError:
        print(f"❌ Error: Image file not found: {image_path}")
        return
    
    # Prepare request
    url = "http://localhost:5000/api/find-item"
    payload = {
        "image": image_data,
        "query": query
    }
    
    # Send request
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        # Display results
        if result.get('success'):
            print(f"✅ Success!")
            print(f"   Item Type: {result.get('item_type')}")
            print(f"   Model Used: {result.get('model_used')}")
            print(f"   Found: {result.get('found')}")
            
            if result.get('found'):
                print(f"\n   Detections:")
                for i, det in enumerate(result.get('detections', []), 1):
                    print(f"   #{i}:")
                    print(f"      Class: {det['class']}")
                    print(f"      Confidence: {det['confidence']*100:.1f}%")
                    print(f"      Bounding Box: {det['bbox']}")
                
                print(f"\n   Message: {result.get('message')}")
                
                # Save annotated image
                if 'annotated_image' in result:
                    output_path = f"output_annotated_{Path(image_path).stem}.png"
                    image_data = result['annotated_image'].split(',')[1]
                    with open(output_path, 'wb') as f:
                        f.write(base64.b64decode(image_data))
                    print(f"   📁 Annotated image saved to: {output_path}")
            else:
                print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Error: {result.get('error')}")
            if 'message' in result:
                print(f"   {result['message']}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server")
        print("   Make sure the server is running: python backend_middleware.py")
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_list_models():
    """Test the models endpoint"""
    print(f"\n{'='*60}")
    print("Listing Available Models")
    print(f"{'='*60}\n")
    
    url = "http://localhost:5000/api/models"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        print("Available Models:")
        for model in result.get('available_models', []):
            print(f"  • {model}")
        
        print("\nKeyword Mappings:")
        mappings = result.get('keyword_mappings', {})
        for keyword, item_type in list(mappings.items())[:10]:
            print(f"  '{keyword}' → {item_type}")
        if len(mappings) > 10:
            print(f"  ... and {len(mappings) - 10} more")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_health_check():
    """Test the health endpoint"""
    print(f"\n{'='*60}")
    print("Health Check")
    print(f"{'='*60}\n")
    
    url = "http://localhost:5000/api/health"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('status') == 'healthy':
            print(f"✅ Server is healthy")
            print(f"   Service: {result.get('service')}")
        else:
            print(f"⚠️  Server status: {result.get('status')}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server")
        print("   Start the server with: python backend_middleware.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("iForgot Backend API Test Suite")
    print("="*60)
    
    # Test health check
    test_health_check()
    
    # Test list models
    test_list_models()
    
    # Test item detection
    # Replace these with actual image paths
    test_cases = [
        ("path/to/keys_image.jpg", "I lost my keys"),
        ("path/to/wallet_image.jpg", "Looking for my wallet"),
        ("path/to/headphones_image.jpg", "Can you find my headphones?"),
    ]
    
    print("\n" + "="*60)
    print("Detection Tests")
    print("="*60)
    print("\n⚠️  Update test_cases with actual image paths to run detection tests")
    
    # Uncomment when you have actual images
    # for image_path, query in test_cases:
    #     test_find_item(image_path, query)
    
    print("\n" + "="*60)
    print("Test suite complete!")
    print("="*60 + "\n")
