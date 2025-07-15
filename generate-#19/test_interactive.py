#!/usr/bin/env python3
"""Test script for image-based shape generation"""

from multimodal_chat import MultimodalChatGenerator
import os

def test_image_based_generation():
    """Test the image-based shape generation functionality"""
    
    generator = MultimodalChatGenerator("blank.pptx")
    
    # Test cases with different images
    test_cases = [
        {
            "image": "/Users/thomasjeon/GitHub/@dev.realbits/naly/examples/extract/sample_parts/sample1-1.png",
            "output": "test_image1_generated.pptx",
            "description": "Test with sample1-1.png"
        },
        {
            "image": "sample1-pdf/page-01.png", 
            "output": "test_image2_generated.pptx",
            "description": "Test with page-01.png"
        }
    ]
    
    print("🧪 Testing Image-Based Shape Generator...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['description']} ---")
        try:
            result = generator.generate_shape_from_image(
                test_case["image"], 
                test_case["output"],
                verbose=False  # Keep it quiet for testing
            )
            print(f"✅ Test {i} passed: {result}")
            
            # Verify file exists and is valid
            if os.path.exists(result):
                print(f"✅ File exists: {result}")
            else:
                print(f"❌ File not found: {result}")
                
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
    
    print("\n🎉 All tests completed!")

def test_verbose_mode():
    """Test verbose mode with detailed output"""
    print("\n🔍 Testing Verbose Mode...")
    
    generator = MultimodalChatGenerator("blank.pptx")
    
    try:
        result = generator.generate_shape_from_image(
            "sample1-pdf/page-01.png",
            "test_verbose_output.pptx",
            verbose=True
        )
        print(f"✅ Verbose test passed: {result}")
    except Exception as e:
        print(f"❌ Verbose test failed: {e}")

if __name__ == "__main__":
    test_image_based_generation()
    test_verbose_mode()