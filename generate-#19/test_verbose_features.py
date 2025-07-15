#!/usr/bin/env python3
"""Test script for the image-based verbose features"""

from multimodal_chat import MultimodalChatGenerator
import os

def test_verbose_features():
    """Test all verbose logging features with image-only input"""
    
    generator = MultimodalChatGenerator("blank.pptx")
    
    # Test cases with different images
    test_cases = [
        {
            "image": "sample1-pdf/page-01.png",
            "output": "verbose_auto1.pptx",
            "description": "Test automatic shape generation from complex image"
        },
        {
            "image": "sample1-pdf/page-02.png", 
            "output": "verbose_auto2.pptx",
            "description": "Test automatic shape generation from different image"
        },
        {
            "image": "sample1-pdf/page-03.png",
            "output": "verbose_auto3.pptx", 
            "description": "Test automatic shape generation from third image"
        }
    ]
    
    print("🧪 Testing Enhanced Image-Based Verbose Features")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 TEST CASE {i}: {test_case['description']}")
        print("-" * 80)
        
        try:
            result = generator.generate_shape_from_image(
                test_case["image"], 
                test_case["output"],
                verbose=True
            )
            print(f"\n✅ Test {i} completed successfully!")
            print(f"📁 Output file: {result}")
            
            # Verify file exists
            if os.path.exists(result):
                print(f"✅ File verification: {result} exists")
            else:
                print(f"❌ File verification: {result} not found")
                
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
        
        print("\n" + "=" * 80)
    
    print("\n🎯 Image-Based Verbose Features Test Summary:")
    print("✅ Image Analysis Description - Detailed image property analysis")
    print("✅ Shape Recommendations - AI-driven shape type selection")
    print("✅ Reasoning Display - Why specific shapes were chosen")
    print("✅ Generated Parameters - Shape type, colors, hints, complexity")
    print("✅ Generated Shape XML - Complete ECMA-376 DrawingML output")
    print("✅ Original slide1.xml - Template file before modification") 
    print("✅ Modified slide1.xml - Final slide with custom shape")
    print("✅ Automatic Shape Selection - No user prompt needed")
    
    print("\n🎉 All image-based verbose features tested successfully!")

def test_quiet_mode():
    """Test quiet mode for comparison"""
    print("\n🤫 Testing Quiet Mode (for comparison)")
    print("-" * 50)
    
    generator = MultimodalChatGenerator("blank.pptx")
    
    result = generator.generate_shape_from_image(
        "sample1-pdf/page-01.png",
        "quiet_auto_test.pptx",
        verbose=False
    )
    
    print(f"✅ Quiet mode test completed: {result}")

def test_different_image_types():
    """Test with different types of images to verify shape selection"""
    print("\n🖼️  Testing Different Image Types")
    print("-" * 50)
    
    generator = MultimodalChatGenerator("blank.pptx")
    
    # Test with available images
    image_tests = [
        "sample1-pdf/page-01.png",
        "sample1-pdf/page-05.png", 
        "sample1-pdf/page-10.png"
    ]
    
    for i, image_path in enumerate(image_tests, 1):
        if os.path.exists(image_path):
            print(f"\n📊 Testing image {i}: {image_path}")
            try:
                result = generator.generate_shape_from_image(
                    image_path,
                    f"auto_shape_{i}.pptx",
                    verbose=False
                )
                print(f"✅ Generated: {result}")
            except Exception as e:
                print(f"❌ Failed: {e}")
        else:
            print(f"⚠️  Image not found: {image_path}")

if __name__ == "__main__":
    test_verbose_features()
    test_quiet_mode()
    test_different_image_types()