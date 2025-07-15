#!/usr/bin/env python3
"""Test fidelity of generated PPTX files"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def test_pptx_structure(pptx_path: str) -> dict:
    """Test the structure and validity of a generated PPTX file"""
    
    results = {
        'valid_zip': False,
        'has_content_types': False,
        'has_rels': False,
        'has_slide1': False,
        'has_custom_shape': False,
        'xml_valid': False,
        'errors': []
    }
    
    try:
        # Test 1: Valid ZIP file
        with zipfile.ZipFile(pptx_path, 'r') as zip_file:
            files = zip_file.namelist()
            results['valid_zip'] = True
            
            # Test 2: Required files exist
            required_files = [
                '[Content_Types].xml',
                '_rels/.rels',
                'ppt/slides/slide1.xml'
            ]
            
            for req_file in required_files:
                if req_file in files:
                    if req_file == '[Content_Types].xml':
                        results['has_content_types'] = True
                    elif req_file == '_rels/.rels':
                        results['has_rels'] = True
                    elif req_file == 'ppt/slides/slide1.xml':
                        results['has_slide1'] = True
                else:
                    results['errors'].append(f"Missing required file: {req_file}")
            
            # Test 3: Parse slide1.xml and check for custom shape
            if results['has_slide1']:
                try:
                    slide1_content = zip_file.read('ppt/slides/slide1.xml')
                    root = ET.fromstring(slide1_content)
                    
                    # Check for namespace declarations
                    namespaces = {
                        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
                        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
                    }
                    
                    # Look for custom shapes (should have custGeom)
                    custom_shapes = root.findall('.//a:custGeom', namespaces)
                    if custom_shapes:
                        results['has_custom_shape'] = True
                        print(f"✅ Found {len(custom_shapes)} custom shape(s)")
                    else:
                        results['errors'].append("No custom shapes found in slide1.xml")
                    
                    # Check for shape elements
                    shapes = root.findall('.//p:sp', namespaces)
                    print(f"📊 Total shapes in slide: {len(shapes)}")
                    
                    results['xml_valid'] = True
                    
                except ET.ParseError as e:
                    results['errors'].append(f"XML parsing error: {e}")
                except Exception as e:
                    results['errors'].append(f"Error reading slide1.xml: {e}")
    
    except zipfile.BadZipFile:
        results['errors'].append("Invalid ZIP file")
    except Exception as e:
        results['errors'].append(f"General error: {e}")
    
    return results

def main():
    """Test all generated PPTX files"""
    test_files = [
        'test_diamond.pptx',
        'test_star.pptx', 
        'test_organic.pptx',
        'test_triangle.pptx',
        'test_circle.pptx'
    ]
    
    print("🔍 Testing PPTX File Fidelity")
    print("=" * 50)
    
    overall_success = True
    
    for pptx_file in test_files:
        if os.path.exists(pptx_file):
            print(f"\n📁 Testing: {pptx_file}")
            results = test_pptx_structure(pptx_file)
            
            # Calculate score
            score = 0
            total_tests = 5
            
            if results['valid_zip']:
                score += 1
                print("✅ Valid ZIP structure")
            else:
                print("❌ Invalid ZIP structure")
                
            if results['has_content_types']:
                score += 1
                print("✅ Has [Content_Types].xml")
            else:
                print("❌ Missing [Content_Types].xml")
                
            if results['has_rels']:
                score += 1
                print("✅ Has _rels/.rels")
            else:
                print("❌ Missing _rels/.rels")
                
            if results['has_slide1']:
                score += 1
                print("✅ Has slide1.xml")
            else:
                print("❌ Missing slide1.xml")
                
            if results['has_custom_shape']:
                score += 1
                print("✅ Contains custom shape")
            else:
                print("❌ No custom shape found")
            
            fidelity_score = (score / total_tests) * 100
            print(f"🎯 Fidelity Score: {fidelity_score:.1f}%")
            
            if fidelity_score < 80:
                overall_success = False
            
            if results['errors']:
                print("⚠️  Errors:")
                for error in results['errors']:
                    print(f"   - {error}")
        else:
            print(f"❌ File not found: {pptx_file}")
            overall_success = False
    
    print("\n" + "=" * 50)
    if overall_success:
        print("🎉 All tests PASSED! System is working correctly.")
    else:
        print("❌ Some tests FAILED. Check individual file results above.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)