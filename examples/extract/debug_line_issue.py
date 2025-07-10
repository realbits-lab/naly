#!/usr/bin/env python3

import json
import xml.etree.ElementTree as ET

def debug_line_issue():
    """Debug why line properties are showing solidFill instead of noFill"""
    
    # Load the extracted shapes data
    with open('sample1-2_shapes.json', 'r') as f:
        shapes_data = json.load(f)
    
    print("=== DEBUGGING LINE ISSUE ===\n")
    
    # Check what the original XML shows
    for slide_data in shapes_data:
        shapes = slide_data.get('shapes', [])
        for i, shape in enumerate(shapes):
            line_info = shape.get('line', {})
            width = line_info.get('width', 'undefined')
            xml_string = shape.get('element', {}).get('xml_string', '')
            
            print(f"Shape {i + 1}:")
            print(f"  - Width: {width}")
            print(f"  - Line info: {line_info}")
            
            # Parse and check the original XML
            if xml_string:
                try:
                    # Parse the XML string and look for line properties
                    root = ET.fromstring(xml_string)
                    
                    # Find the line element
                    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                          'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
                    
                    ln_element = root.find('.//a:ln', ns)
                    if ln_element is not None:
                        print(f"  - Original line XML: {ET.tostring(ln_element, encoding='unicode')}")
                        
                        # Check for noFill
                        no_fill = ln_element.find('a:noFill', ns)
                        solid_fill = ln_element.find('a:solidFill', ns)
                        
                        print(f"  - Has noFill: {no_fill is not None}")
                        print(f"  - Has solidFill: {solid_fill is not None}")
                    else:
                        print("  - No line element found in original XML")
                        
                except Exception as e:
                    print(f"  - Error parsing XML: {e}")
            
            print()
    
    # Now check what the generated XML shows
    print("=== GENERATED XML ANALYSIS ===\n")
    try:
        with open('sample1-2_enhanced/ppt/slides/slide1.xml', 'r') as f:
            generated_xml = f.read()
        
        root = ET.fromstring(generated_xml)
        ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
              'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
        
        # Find all line elements in generated XML
        ln_elements = root.findall('.//a:ln', ns)
        print(f"Found {len(ln_elements)} line elements in generated XML:")
        
        for i, ln in enumerate(ln_elements):
            print(f"Line {i + 1}: {ET.tostring(ln, encoding='unicode')}")
            
            no_fill = ln.find('a:noFill', ns)
            solid_fill = ln.find('a:solidFill', ns)
            
            print(f"  - Has noFill: {no_fill is not None}")
            print(f"  - Has solidFill: {solid_fill is not None}")
            print()
            
    except Exception as e:
        print(f"Error reading generated XML: {e}")

if __name__ == "__main__":
    debug_line_issue()