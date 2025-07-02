#!/usr/bin/env python3

import sys
import os
import zipfile
import xml.etree.ElementTree as ET
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import difflib
import tempfile
import shutil


class PowerPointStructureComparator:
    """Compare the internal structure of two PowerPoint files"""
    
    def __init__(self, file1_path: str, file2_path: str):
        self.file1_path = Path(file1_path)
        self.file2_path = Path(file2_path)
        self.temp_dir1 = None
        self.temp_dir2 = None
        self.comparison_results = {
            'file1': str(self.file1_path),
            'file2': str(self.file2_path),
            'structure_diff': {},
            'content_diff': {},
            'fidelity_score': 0.0,
            'summary': {}
        }
    
    def extract_pptx_structure(self, pptx_path: Path) -> str:
        """Extract PPTX file to temporary directory"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            return temp_dir
        except Exception as e:
            shutil.rmtree(temp_dir)
            raise Exception(f"Failed to extract {pptx_path}: {str(e)}")
    
    def get_file_structure(self, root_dir: str) -> Dict[str, List[str]]:
        """Get hierarchical file structure"""
        structure = {}
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            rel_path = os.path.relpath(dirpath, root_dir)
            if rel_path == '.':
                rel_path = ''
            
            # Store files in this directory
            structure[rel_path] = sorted(filenames)
            
            # Sort directories for consistent comparison
            dirnames.sort()
        
        return structure
    
    def compare_xml_content(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """Compare XML file content"""
        try:
            # Parse XML files
            tree1 = ET.parse(file1_path)
            tree2 = ET.parse(file2_path)
            
            root1 = tree1.getroot()
            root2 = tree2.getroot()
            
            # Compare root tags
            if root1.tag != root2.tag:
                return {
                    'identical': False,
                    'root_tag_diff': f"{root1.tag} != {root2.tag}"
                }
            
            # Compare element counts
            elements1 = list(root1.iter())
            elements2 = list(root2.iter())
            
            comparison = {
                'identical': len(elements1) == len(elements2),
                'element_count': {
                    'file1': len(elements1),
                    'file2': len(elements2)
                },
                'tag_frequency': {
                    'file1': self._count_tags(root1),
                    'file2': self._count_tags(root2)
                }
            }
            
            # Calculate similarity score
            if comparison['identical']:
                comparison['similarity'] = 1.0
            else:
                # Simple similarity based on element count
                max_count = max(len(elements1), len(elements2))
                min_count = min(len(elements1), len(elements2))
                comparison['similarity'] = min_count / max_count if max_count > 0 else 0
            
            return comparison
            
        except ET.ParseError as e:
            return {
                'identical': False,
                'error': f"XML parse error: {str(e)}"
            }
        except Exception as e:
            return {
                'identical': False,
                'error': f"Comparison error: {str(e)}"
            }
    
    def _count_tags(self, root: ET.Element) -> Dict[str, int]:
        """Count frequency of each tag in XML"""
        tag_count = {}
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            tag_count[tag] = tag_count.get(tag, 0) + 1
        return tag_count
    
    def compare_structure(self) -> Dict[str, Any]:
        """Compare the structure of two PowerPoint files"""
        try:
            # Extract both files
            print(f"Extracting {self.file1_path.name}...")
            self.temp_dir1 = self.extract_pptx_structure(self.file1_path)
            
            print(f"Extracting {self.file2_path.name}...")
            self.temp_dir2 = self.extract_pptx_structure(self.file2_path)
            
            # Get file structures
            structure1 = self.get_file_structure(self.temp_dir1)
            structure2 = self.get_file_structure(self.temp_dir2)
            
            # Compare structures
            all_dirs = set(structure1.keys()) | set(structure2.keys())
            
            structure_comparison = {
                'total_directories': len(all_dirs),
                'common_directories': len(set(structure1.keys()) & set(structure2.keys())),
                'unique_to_file1': list(set(structure1.keys()) - set(structure2.keys())),
                'unique_to_file2': list(set(structure2.keys()) - set(structure1.keys())),
                'file_differences': {}
            }
            
            # Compare files in each directory
            total_files = 0
            matching_files = 0
            
            for dir_path in all_dirs:
                files1 = set(structure1.get(dir_path, []))
                files2 = set(structure2.get(dir_path, []))
                
                common_files = files1 & files2
                unique_to_1 = files1 - files2
                unique_to_2 = files2 - files1
                
                total_files += len(files1 | files2)
                matching_files += len(common_files)
                
                if unique_to_1 or unique_to_2:
                    structure_comparison['file_differences'][dir_path] = {
                        'unique_to_file1': list(unique_to_1),
                        'unique_to_file2': list(unique_to_2)
                    }
            
            structure_comparison['total_files'] = total_files
            structure_comparison['matching_files'] = matching_files
            structure_comparison['file_match_rate'] = matching_files / total_files if total_files > 0 else 0
            
            self.comparison_results['structure_diff'] = structure_comparison
            
            # Compare content of matching XML files
            self._compare_xml_files(structure1, structure2)
            
            # Calculate overall fidelity score
            self._calculate_fidelity_score()
            
            # Generate summary
            self._generate_summary()
            
            return self.comparison_results
            
        finally:
            # Cleanup temporary directories
            if self.temp_dir1:
                shutil.rmtree(self.temp_dir1)
            if self.temp_dir2:
                shutil.rmtree(self.temp_dir2)
    
    def _compare_xml_files(self, structure1: Dict, structure2: Dict):
        """Compare content of XML files"""
        xml_comparison = {}
        total_similarity = 0
        xml_file_count = 0
        
        # Key XML files to compare
        important_xml_files = [
            ('', '[Content_Types].xml'),
            ('_rels', '.rels'),
            ('ppt', 'presentation.xml'),
            ('ppt/_rels', 'presentation.xml.rels'),
            ('ppt/theme', 'theme1.xml'),
        ]
        
        # Add slide XMLs
        for dir_path, files in structure1.items():
            if 'slides' in dir_path and not '_rels' in dir_path:
                for file in files:
                    if file.endswith('.xml'):
                        important_xml_files.append((dir_path, file))
        
        for dir_path, filename in important_xml_files:
            if filename in structure1.get(dir_path, []) and filename in structure2.get(dir_path, []):
                file1_path = os.path.join(self.temp_dir1, dir_path, filename)
                file2_path = os.path.join(self.temp_dir2, dir_path, filename)
                
                comparison = self.compare_xml_content(file1_path, file2_path)
                xml_comparison[os.path.join(dir_path, filename)] = comparison
                
                if 'similarity' in comparison:
                    total_similarity += comparison['similarity']
                    xml_file_count += 1
        
        self.comparison_results['content_diff'] = xml_comparison
        self.comparison_results['xml_similarity'] = total_similarity / xml_file_count if xml_file_count > 0 else 0
    
    def _calculate_fidelity_score(self):
        """Calculate overall fidelity score"""
        structure_diff = self.comparison_results['structure_diff']
        
        # Weight different aspects
        weights = {
            'structure': 0.3,  # File/directory structure
            'xml_content': 0.4,  # XML content similarity
            'slide_count': 0.2,  # Slide count match
            'media_preservation': 0.1  # Media file preservation
        }
        
        scores = {}
        
        # Structure score
        scores['structure'] = structure_diff.get('file_match_rate', 0)
        
        # XML content score
        scores['xml_content'] = self.comparison_results.get('xml_similarity', 0)
        
        # Slide count score
        slides1 = len([f for f in structure_diff.get('file_differences', {}).get('ppt/slides', {}).get('unique_to_file1', [])])
        slides2 = len([f for f in structure_diff.get('file_differences', {}).get('ppt/slides', {}).get('unique_to_file2', [])])
        slides_common = structure_diff.get('matching_files', 0) - slides1 - slides2
        
        if slides1 == 0 and slides2 == 0:
            scores['slide_count'] = 1.0
        else:
            scores['slide_count'] = 0.5  # Penalty for slide count mismatch
        
        # Media preservation score
        media_dirs = ['ppt/media', 'ppt/embeddings']
        media_preserved = True
        for media_dir in media_dirs:
            if media_dir in structure_diff.get('unique_to_file1', []):
                media_preserved = False
                break
        scores['media_preservation'] = 1.0 if media_preserved else 0.0
        
        # Calculate weighted score
        fidelity_score = sum(scores[aspect] * weight for aspect, weight in weights.items())
        
        self.comparison_results['fidelity_score'] = fidelity_score
        self.comparison_results['aspect_scores'] = scores
    
    def _generate_summary(self):
        """Generate comparison summary"""
        structure_diff = self.comparison_results['structure_diff']
        fidelity_score = self.comparison_results['fidelity_score']
        
        summary = {
            'overall_fidelity': f"{fidelity_score:.1%}",
            'structure_match': f"{structure_diff.get('file_match_rate', 0):.1%}",
            'xml_similarity': f"{self.comparison_results.get('xml_similarity', 0):.1%}",
            'missing_directories': len(structure_diff.get('unique_to_file1', [])),
            'extra_directories': len(structure_diff.get('unique_to_file2', [])),
            'recommendations': []
        }
        
        # Add recommendations based on findings
        if fidelity_score < 0.5:
            summary['recommendations'].append("Major structural differences detected. Review shape extraction logic.")
        
        if structure_diff.get('unique_to_file1'):
            if 'ppt/media' in structure_diff['unique_to_file1']:
                summary['recommendations'].append("Media files are missing. Implement media extraction and embedding.")
            if 'ppt/embeddings' in structure_diff['unique_to_file1']:
                summary['recommendations'].append("Embedded objects are missing. Add support for embedded content.")
        
        if self.comparison_results.get('xml_similarity', 0) < 0.7:
            summary['recommendations'].append("XML content has significant differences. Enhance property preservation.")
        
        aspect_scores = self.comparison_results.get('aspect_scores', {})
        if aspect_scores.get('slide_count', 1) < 1:
            summary['recommendations'].append("Slide count mismatch detected. Verify slide generation logic.")
        
        self.comparison_results['summary'] = summary
    
    def print_report(self):
        """Print detailed comparison report"""
        print("\n" + "="*80)
        print("POWERPOINT STRUCTURE COMPARISON REPORT")
        print("="*80)
        
        print(f"\nFile 1: {self.comparison_results['file1']}")
        print(f"File 2: {self.comparison_results['file2']}")
        
        summary = self.comparison_results['summary']
        print(f"\nOVERALL FIDELITY SCORE: {summary['overall_fidelity']}")
        print(f"  Structure Match: {summary['structure_match']}")
        print(f"  XML Similarity: {summary['xml_similarity']}")
        
        print("\nASPECT SCORES:")
        for aspect, score in self.comparison_results.get('aspect_scores', {}).items():
            print(f"  {aspect.replace('_', ' ').title()}: {score:.1%}")
        
        structure_diff = self.comparison_results['structure_diff']
        
        print(f"\nSTRUCTURE ANALYSIS:")
        print(f"  Total Directories: {structure_diff['total_directories']}")
        print(f"  Common Directories: {structure_diff['common_directories']}")
        print(f"  Total Files: {structure_diff['total_files']}")
        print(f"  Matching Files: {structure_diff['matching_files']}")
        
        if structure_diff['unique_to_file1']:
            print(f"\n  Directories only in File 1:")
            for dir_path in structure_diff['unique_to_file1']:
                print(f"    - {dir_path}")
        
        if structure_diff['unique_to_file2']:
            print(f"\n  Directories only in File 2:")
            for dir_path in structure_diff['unique_to_file2']:
                print(f"    - {dir_path}")
        
        # Print significant XML differences
        print("\nXML CONTENT ANALYSIS:")
        content_diff = self.comparison_results['content_diff']
        for xml_path, comparison in content_diff.items():
            if not comparison.get('identical', False):
                print(f"  {xml_path}:")
                if 'similarity' in comparison:
                    print(f"    Similarity: {comparison['similarity']:.1%}")
                if 'element_count' in comparison:
                    print(f"    Elements: {comparison['element_count']['file1']} vs {comparison['element_count']['file2']}")
        
        # Print recommendations
        if summary['recommendations']:
            print("\nRECOMMENDATIONS:")
            for i, rec in enumerate(summary['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)
    
    def save_report(self, output_file: str):
        """Save comparison report to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.comparison_results, f, indent=2)
        print(f"\nDetailed report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Compare the structure and content of two PowerPoint files'
    )
    parser.add_argument('file1', help='First PowerPoint file')
    parser.add_argument('file2', help='Second PowerPoint file') 
    parser.add_argument('--output', '-o', help='Save detailed report to JSON file')
    
    args = parser.parse_args()
    
    # Validate input files
    for file_path in [args.file1, args.file2]:
        if not Path(file_path).exists():
            print(f"Error: File '{file_path}' does not exist.")
            sys.exit(1)
        if not file_path.lower().endswith(('.ppt', '.pptx')):
            print(f"Error: File '{file_path}' is not a PowerPoint file.")
            sys.exit(1)
    
    try:
        # Create comparator
        comparator = PowerPointStructureComparator(args.file1, args.file2)
        
        # Run comparison
        print("Comparing PowerPoint structures...")
        comparator.compare_structure()
        
        # Print report
        comparator.print_report()
        
        # Save detailed report if requested
        if args.output:
            comparator.save_report(args.output)
        
    except Exception as e:
        print(f"Error during comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()