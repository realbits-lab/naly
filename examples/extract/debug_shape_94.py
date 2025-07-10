#!/usr/bin/env python3

import json
from ppt_generator import PPTGenerator

def debug_shape_94():
    """Debug why shape 94 is not being generated as a picture"""
    
    print("=== DEBUGGING SHAPE 94 ISSUE ===\n")
    
    # Load the extracted shapes data
    with open('sample1-2_shapes.json', 'r') as f:
        shapes_data = json.load(f)
    
    # Find shape 94
    shape_94 = None
    for slide_data in shapes_data:
        shapes = slide_data.get('shapes', [])
        for shape in shapes:
            if shape.get('shape_id') == 94:
                shape_94 = shape
                break
        if shape_94:
            break
    
    if not shape_94:
        print("Shape 94 not found!")
        return
    
    print("Shape 94 found:")
    print(f"  - ID: {shape_94.get('shape_id')}")
    print(f"  - Name: {shape_94.get('name')}")
    print(f"  - Type: {shape_94.get('shape_type')}")
    print(f"  - Has XML string: {bool(shape_94.get('element', {}).get('xml_string'))}")
    
    # Check image properties
    image_props = shape_94.get('image_properties', {})
    print(f"  - Image properties: {image_props}")
    
    # Load media data to check if the image exists
    try:
        with open('sample1-2_media.json', 'r') as f:
            media_data = json.load(f)
        
        print("\nMedia cache contents:")
        images = media_data.get('images', {})
        for key, value in images.items():
            print(f"  - Key: '{key}', filename: '{value.get('filename')}'")
        
        # Check for the specific media key
        media_key = image_props.get('media_key')
        filename = image_props.get('filename')
        
        print(f"\nLooking for media_key: '{media_key}' or filename: '{filename}'")
        
        if media_key in images:
            print(f"✓ Found media with key: '{media_key}'")
        elif filename in images:
            print(f"✓ Found media with filename: '{filename}'")
        else:
            print("✗ Media not found with either key or filename")
            # Check if there's a similar key
            for key in images.keys():
                if media_key and media_key in key:
                    print(f"  Similar key found: '{key}'")
                if filename and filename in key:
                    print(f"  Similar filename found: '{key}'")
    
    except Exception as e:
        print(f"Error loading media: {e}")
    
    # Test the generator with this specific shape
    print("\n=== TESTING GENERATOR ===")
    try:
        generator = PPTGenerator()
        generator.load_json_files(
            shapes_file='sample1-2_shapes.json',
            layouts_file='sample1-2_layouts.json', 
            theme_file='sample1-2_theme.json',
            media_file='sample1-2_media.json'
        )
        
        print(f"Generator media cache has {len(generator.media_cache)} items:")
        for key in generator.media_cache.keys():
            print(f"  - '{key}'")
        
        # Check the specific media key mapping
        media_key = image_props.get('media_key')
        if media_key and media_key in generator.media_cache:
            print(f"✓ Media key '{media_key}' found in generator cache")
        else:
            print(f"✗ Media key '{media_key}' NOT found in generator cache")
            
        # Check if any key contains the filename
        filename = image_props.get('filename')
        if filename:
            matching_keys = [k for k in generator.media_cache.keys() if filename in k]
            if matching_keys:
                print(f"Keys containing '{filename}': {matching_keys}")
            
    except Exception as e:
        print(f"Error creating generator: {e}")

if __name__ == "__main__":
    debug_shape_94()