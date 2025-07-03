#!/usr/bin/env python3
"""
XML Differences Analysis Tool for PowerPoint Fidelity Testing

This script performs deep analysis of XML differences between original and generated
PowerPoint files to identify specific gaps in extraction and generation.

Usage:
    python analyze_xml_differences.py <original_xml> <generated_xml>
    python analyze_xml_differences.py --batch <original_dir> <generated_dir>
"""

import xml.etree.ElementTree as ET
import sys
import os
import json
import argparse
from pathlib import Path
from collections import defaultdict
import difflib

class XMLAnalyzer:
    def __init__(self):
        self.namespace_map = {}
        self.critical_elements = {
            'ppt/presentation.xml': [
                'p:presentation/p:sldIdLst',
                'p:presentation/p:sldMasterIdLst', 
                'p:presentation/p:sldSz',
                'p:presentation/p:defaultTextStyle'
            ],
            'ppt/slides/slide1.xml': [
                'p:sld/p:cSld/p:spTree',
                'p:sld/p:timing',
                'p:sld/p:transition',
                'p:sld/p:cSld/p:bg'
            ],
            'ppt/theme/theme1.xml': [
                'a:theme/a:themeElements/a:clrScheme',
                'a:theme/a:themeElements/a:fontScheme',
                'a:theme/a:themeElements/a:fmtScheme'
            ]
        }
    
    def analyze_xml_structure(self, original_xml, generated_xml, file_context=""):
        """Analyze differences between original and generated XML files"""
        
        try:
            # Parse XML files
            orig_tree = ET.parse(original_xml)
            gen_tree = ET.parse(generated_xml)
            
            orig_root = orig_tree.getroot()
            gen_root = gen_tree.getroot()
            
            # Extract namespace information
            orig_namespaces = self._extract_namespaces(orig_root)
            gen_namespaces = self._extract_namespaces(gen_root)
            
            analysis = {
                'file': str(original_xml),
                'file_context': file_context,
                'summary': self._generate_summary(orig_root, gen_root),
                'namespaces': self._compare_namespaces(orig_namespaces, gen_namespaces),
                'structure': self._compare_structure(orig_root, gen_root),
                'attributes': self._compare_attributes(orig_root, gen_root),
                'content': self._compare_content(orig_root, gen_root),
                'critical_elements': self._analyze_critical_elements(orig_root, gen_root, file_context),
                'recommendations': self._generate_recommendations(orig_root, gen_root, file_context)
            }
            
            return analysis
            
        except ET.ParseError as e:
            return {
                'error': f'XML Parse Error: {str(e)}',
                'file': str(original_xml),
                'file_context': file_context
            }
        except Exception as e:
            return {
                'error': f'Analysis Error: {str(e)}',
                'file': str(original_xml),
                'file_context': file_context
            }
    
    def _extract_namespaces(self, root):
        """Extract namespace declarations from XML root"""
        namespaces = {}
        
        # Get namespace declarations from root element
        for key, value in root.attrib.items():
            if key.startswith('xmlns'):
                prefix = key.split(':')[1] if ':' in key else 'default'
                namespaces[prefix] = value
        
        return namespaces
    
    def _compare_namespaces(self, orig_ns, gen_ns):
        """Compare namespace declarations"""
        missing_in_gen = {k: v for k, v in orig_ns.items() if k not in gen_ns}
        extra_in_gen = {k: v for k, v in gen_ns.items() if k not in orig_ns}
        mismatched = {k: {'original': orig_ns[k], 'generated': gen_ns[k]} 
                     for k in orig_ns if k in gen_ns and orig_ns[k] != gen_ns[k]}
        
        return {
            'missing_in_generated': missing_in_gen,
            'extra_in_generated': extra_in_gen,
            'mismatched': mismatched,
            'match_percentage': self._calculate_namespace_match(orig_ns, gen_ns)
        }
    
    def _calculate_namespace_match(self, orig_ns, gen_ns):
        """Calculate namespace match percentage"""
        if not orig_ns:
            return 100.0
        
        matches = sum(1 for k, v in orig_ns.items() if gen_ns.get(k) == v)
        return round(matches / len(orig_ns) * 100, 2)
    
    def _compare_structure(self, orig_root, gen_root):
        """Compare XML element structure"""
        orig_elements = self._get_element_paths(orig_root)
        gen_elements = self._get_element_paths(gen_root)
        
        missing_elements = orig_elements - gen_elements
        extra_elements = gen_elements - orig_elements
        common_elements = orig_elements & gen_elements
        
        return {
            'total_original': len(orig_elements),
            'total_generated': len(gen_elements),
            'common_count': len(common_elements),
            'missing_in_generated': sorted(list(missing_elements)),
            'extra_in_generated': sorted(list(extra_elements)),
            'match_percentage': round(len(common_elements) / len(orig_elements) * 100, 2) if orig_elements else 100.0
        }
    
    def _get_element_paths(self, element, path="", max_depth=10, current_depth=0):
        """Get all element paths in XML tree with depth limit"""
        if current_depth > max_depth:
            return set()
            
        paths = set()
        
        # Clean element tag (remove namespace prefix for comparison)
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        current_path = f"{path}/{tag}" if path else tag
        paths.add(current_path)
        
        # Recursively process children
        for child in element:
            child_paths = self._get_element_paths(child, current_path, max_depth, current_depth + 1)
            paths.update(child_paths)
        
        return paths
    
    def _compare_attributes(self, orig_root, gen_root):
        """Compare XML attributes across all elements"""
        orig_attrs = self._get_all_attributes(orig_root)
        gen_attrs = self._get_all_attributes(gen_root)
        
        missing_attrs = orig_attrs - gen_attrs
        extra_attrs = gen_attrs - orig_attrs
        common_attrs = orig_attrs & gen_attrs
        
        return {
            'total_original': len(orig_attrs),
            'total_generated': len(gen_attrs),
            'common_count': len(common_attrs),
            'missing_in_generated': sorted(list(missing_attrs)),
            'extra_in_generated': sorted(list(extra_attrs)),
            'match_percentage': round(len(common_attrs) / len(orig_attrs) * 100, 2) if orig_attrs else 100.0
        }
    
    def _get_all_attributes(self, element, path="", max_depth=10, current_depth=0):
        """Get all attributes with their paths"""
        if current_depth > max_depth:
            return set()
            
        attrs = set()
        
        # Clean element tag
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        current_path = f"{path}/{tag}" if path else tag
        
        # Add attributes for current element
        for attr_name in element.attrib:
            clean_attr = attr_name.split('}')[-1] if '}' in attr_name else attr_name
            attrs.add(f"{current_path}@{clean_attr}")
        
        # Recursively process children
        for child in element:
            child_attrs = self._get_all_attributes(child, current_path, max_depth, current_depth + 1)
            attrs.update(child_attrs)
        
        return attrs
    
    def _compare_content(self, orig_root, gen_root):
        """Compare text content between XML trees"""
        orig_texts = self._extract_text_content(orig_root)
        gen_texts = self._extract_text_content(gen_root)
        
        # Find matching and missing text content
        common_texts = orig_texts & gen_texts
        missing_texts = orig_texts - gen_texts
        extra_texts = gen_texts - orig_texts
        
        return {
            'total_original_texts': len(orig_texts),
            'total_generated_texts': len(gen_texts),
            'common_texts': len(common_texts),
            'missing_texts': sorted(list(missing_texts)),
            'extra_texts': sorted(list(extra_texts)),
            'text_match_percentage': round(len(common_texts) / len(orig_texts) * 100, 2) if orig_texts else 100.0
        }
    
    def _extract_text_content(self, element, path=""):
        """Extract all text content from XML tree"""
        texts = set()
        
        # Add text content if present
        if element.text and element.text.strip():
            texts.add(element.text.strip())
        
        # Recursively process children
        for child in element:
            child_texts = self._extract_text_content(child, path)
            texts.update(child_texts)
        
        return texts
    
    def _analyze_critical_elements(self, orig_root, gen_root, file_context):
        """Analyze critical elements specific to the file type"""
        critical_analysis = {}
        
        if file_context in self.critical_elements:
            for element_path in self.critical_elements[file_context]:
                orig_elem = self._find_element_by_path(orig_root, element_path)
                gen_elem = self._find_element_by_path(gen_root, element_path)
                
                critical_analysis[element_path] = {
                    'present_in_original': orig_elem is not None,
                    'present_in_generated': gen_elem is not None,
                    'status': self._get_element_status(orig_elem, gen_elem)
                }
                
                if orig_elem is not None and gen_elem is not None:
                    critical_analysis[element_path]['details'] = self._compare_element_details(orig_elem, gen_elem)
        
        return critical_analysis
    
    def _find_element_by_path(self, root, path):
        """Find element by XPath-like path"""
        try:
            # Simplified path finding - split by / and navigate
            parts = path.split('/')
            current = root
            
            for part in parts:
                if ':' in part:
                    # Handle namespaced elements
                    tag = part.split(':')[1]
                else:
                    tag = part
                
                # Find child with matching tag
                found = False
                for child in current:
                    child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    if child_tag == tag:
                        current = child
                        found = True
                        break
                
                if not found:
                    return None
            
            return current
            
        except Exception:
            return None
    
    def _get_element_status(self, orig_elem, gen_elem):
        """Get status of element comparison"""
        if orig_elem is None and gen_elem is None:
            return "both_missing"
        elif orig_elem is None:
            return "extra_in_generated"
        elif gen_elem is None:
            return "missing_in_generated"
        else:
            return "present_in_both"
    
    def _compare_element_details(self, orig_elem, gen_elem):
        """Compare details of two elements"""
        return {
            'attributes_match': orig_elem.attrib == gen_elem.attrib,
            'text_match': (orig_elem.text or "").strip() == (gen_elem.text or "").strip(),
            'children_count_original': len(list(orig_elem)),
            'children_count_generated': len(list(gen_elem))
        }
    
    def _generate_summary(self, orig_root, gen_root):
        """Generate high-level summary of differences"""
        orig_element_count = len(list(orig_root.iter()))
        gen_element_count = len(list(gen_root.iter()))
        
        orig_attr_count = sum(len(elem.attrib) for elem in orig_root.iter())
        gen_attr_count = sum(len(elem.attrib) for elem in gen_root.iter())
        
        return {
            'elements_original': orig_element_count,
            'elements_generated': gen_element_count,
            'attributes_original': orig_attr_count,
            'attributes_generated': gen_attr_count,
            'size_ratio': round(gen_element_count / orig_element_count, 3) if orig_element_count > 0 else 0
        }
    
    def _generate_recommendations(self, orig_root, gen_root, file_context):
        """Generate specific recommendations based on analysis"""
        recommendations = []
        
        # Check for major structural differences
        orig_children = len(list(orig_root))
        gen_children = len(list(gen_root))
        
        if gen_children < orig_children * 0.5:
            recommendations.append({
                'priority': 'high',
                'category': 'structure',
                'issue': f'Generated XML has significantly fewer child elements ({gen_children} vs {orig_children})',
                'suggestion': 'Review element extraction and generation logic'
            })
        
        # Check for missing critical elements
        if file_context in self.critical_elements:
            missing_critical = []
            for element_path in self.critical_elements[file_context]:
                if self._find_element_by_path(orig_root, element_path) and not self._find_element_by_path(gen_root, element_path):
                    missing_critical.append(element_path)
            
            if missing_critical:
                recommendations.append({
                    'priority': 'high',
                    'category': 'critical_elements',
                    'issue': f'Missing critical elements: {missing_critical}',
                    'suggestion': 'Ensure extraction and generation of critical PowerPoint elements'
                })
        
        # Check namespace issues
        orig_ns = self._extract_namespaces(orig_root)
        gen_ns = self._extract_namespaces(gen_root)
        
        if len(gen_ns) < len(orig_ns):
            recommendations.append({
                'priority': 'medium',
                'category': 'namespaces',
                'issue': 'Missing namespace declarations',
                'suggestion': 'Ensure all required namespaces are included in generated XML'
            })
        
        return recommendations

def analyze_batch(original_dir, generated_dir):
    """Analyze all XML files in directories"""
    analyzer = XMLAnalyzer()
    results = []
    
    original_path = Path(original_dir)
    generated_path = Path(generated_dir)
    
    # Find all XML files in original directory
    for xml_file in original_path.rglob("*.xml"):
        relative_path = xml_file.relative_to(original_path)
        generated_file = generated_path / relative_path
        
        if generated_file.exists():
            print(f"Analyzing {relative_path}...")
            file_context = str(relative_path).replace('\\', '/')
            analysis = analyzer.analyze_xml_structure(str(xml_file), str(generated_file), file_context)
            results.append(analysis)
        else:
            results.append({
                'file': str(xml_file),
                'file_context': str(relative_path),
                'error': 'Generated file not found'
            })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Analyze XML differences between PowerPoint files')
    parser.add_argument('--batch', action='store_true', help='Batch analyze directories')
    parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    parser.add_argument('--summary', action='store_true', help='Show summary only')
    parser.add_argument('files', nargs=2, help='Original and generated XML files/directories')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch analysis of directories
        results = analyze_batch(args.files[0], args.files[1])
    else:
        # Single file analysis
        if not os.path.exists(args.files[0]) or not os.path.exists(args.files[1]):
            print("Error: One or both XML files do not exist")
            sys.exit(1)
        
        analyzer = XMLAnalyzer()
        file_context = os.path.basename(args.files[0])
        results = [analyzer.analyze_xml_structure(args.files[0], args.files[1], file_context)]
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        if args.summary:
            # Print summary
            for result in results:
                if 'error' in result:
                    print(f"❌ {result['file']}: {result['error']}")
                else:
                    print(f"📄 {result['file_context']}")
                    if 'structure' in result:
                        print(f"   Structure match: {result['structure']['match_percentage']}%")
                    if 'attributes' in result:
                        print(f"   Attributes match: {result['attributes']['match_percentage']}%")
                    if 'content' in result:
                        print(f"   Content match: {result['content']['text_match_percentage']}%")
                    print()
        else:
            # Print detailed results
            print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()