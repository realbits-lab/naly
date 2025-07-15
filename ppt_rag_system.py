#!/usr/bin/env python3

import os
import sys
import json
import uuid
import zipfile
import tempfile
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import xml.etree.ElementTree as ET
from pptx import Presentation
from PIL import Image
import base64
import io

# Import the existing extractor
sys.path.append(str(Path(__file__).parent / "examples" / "extract"))
from ppt_extractor import PPTExtractor

@dataclass
class SlideData:
    """Data structure for slide information"""
    slide_index: int
    pdf_page_number: int
    description: str
    shapes: List[Dict[str, Any]]
    xml_content: str
    media_files: Dict[str, str]
    
class PowerPointRAGSystem:
    """
    PowerPoint RAG System that extracts shape data, generates descriptions,
    and stores everything in a vector database for RAG search.
    """
    
    def __init__(self, output_dir: str = "ppt_rag_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize storage
        self.slides_data: List[SlideData] = []
        self.processed_files: Dict[str, str] = {}
        
    def convert_pptx_to_pdf(self, pptx_path: str) -> str:
        """Convert PowerPoint file to PDF using LibreOffice"""
        pptx_path = Path(pptx_path)
        output_pdf = self.output_dir / f"{pptx_path.stem}.pdf"
        
        print(f"Converting {pptx_path} to PDF...")
        
        try:
            # Try LibreOffice first
            cmd = [
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(self.output_dir),
                str(pptx_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_pdf.exists():
                print(f"✅ PDF created: {output_pdf}")
                return str(output_pdf)
            else:
                print(f"❌ LibreOffice conversion failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ LibreOffice conversion timed out")
        except FileNotFoundError:
            print("❌ LibreOffice not found")
            
        # Fallback: try using python-pptx to extract slide images
        return self._extract_slide_images_as_pdf_fallback(pptx_path)
    
    def _extract_slide_images_as_pdf_fallback(self, pptx_path: str) -> str:
        """Fallback method: extract slide images and create PDF"""
        print("Using fallback method: extracting slide images...")
        
        try:
            # Extract slides as images using existing slide images if available
            sample_dir = Path(pptx_path).parent / "sample1"
            if sample_dir.exists():
                print(f"Using existing slide images from {sample_dir}")
                
                # Create a simple PDF from images (placeholder - would need actual PDF library)
                pdf_path = self.output_dir / f"{Path(pptx_path).stem}.pdf"
                
                # For now, return a placeholder PDF path
                # In a real implementation, you'd use a library like reportlab or img2pdf
                with open(pdf_path, 'w') as f:
                    f.write("Placeholder PDF - slide images available in sample1/ directory")
                
                return str(pdf_path)
            
            # If no existing images, create placeholder
            pdf_path = self.output_dir / f"{Path(pptx_path).stem}.pdf"
            with open(pdf_path, 'w') as f:
                f.write("Placeholder PDF - conversion not available")
                
            return str(pdf_path)
            
        except Exception as e:
            print(f"❌ Fallback PDF creation failed: {e}")
            raise
    
    def extract_powerpoint_data(self, pptx_path: str) -> Dict[str, Any]:
        """Extract comprehensive PowerPoint data using existing extractor"""
        print(f"Extracting PowerPoint data from {pptx_path}...")
        
        # Use the existing extractor
        extractor = PPTExtractor(pptx_path)
        
        # Extract all components
        shapes_data = extractor.extract_shapes()
        layouts_data = extractor.extract_layouts()
        theme_data = extractor.extract_theme()
        media_data = extractor.extract_media_files()
        properties_data = extractor.extract_document_properties()
        
        return {
            'shapes': shapes_data,
            'layouts': layouts_data,
            'theme': theme_data,
            'media': media_data,
            'properties': properties_data
        }
    
    def extract_slide_xml(self, pptx_path: str) -> Dict[int, str]:
        """Extract slide XML content from PowerPoint file"""
        print("Extracting slide XML content...")
        
        slide_xmls = {}
        
        try:
            with zipfile.ZipFile(pptx_path, 'r') as zip_file:
                # Find all slide XML files
                for file_info in zip_file.filelist:
                    if file_info.filename.startswith('ppt/slides/slide') and file_info.filename.endswith('.xml'):
                        # Extract slide number from filename
                        slide_num = int(file_info.filename.split('slide')[1].split('.')[0])
                        
                        # Read XML content
                        xml_content = zip_file.read(file_info.filename).decode('utf-8')
                        slide_xmls[slide_num] = xml_content
                        
        except Exception as e:
            print(f"❌ Error extracting slide XML: {e}")
            
        return slide_xmls
    
    def generate_slide_descriptions(self, pdf_path: str, num_slides: int) -> List[str]:
        """Generate descriptions for slides using LLM (placeholder)"""
        print(f"Generating descriptions for {num_slides} slides...")
        
        descriptions = []
        
        # TODO: Implement actual LLM-based description generation
        # For now, create placeholder descriptions
        for i in range(num_slides):
            description = f"Slide {i+1}: This slide contains various shapes and elements that need to be analyzed by an LLM to provide a meaningful description. The slide includes text, graphics, and formatting elements that contribute to the overall presentation content."
            descriptions.append(description)
            
        return descriptions
    
    def process_powerpoint_file(self, pptx_path: str) -> str:
        """Process a PowerPoint file completely"""
        print(f"🚀 Processing PowerPoint file: {pptx_path}")
        
        # Step 1: Convert to PDF
        pdf_path = self.convert_pptx_to_pdf(pptx_path)
        
        # Step 2: Extract PowerPoint data
        ppt_data = self.extract_powerpoint_data(pptx_path)
        
        # Step 3: Extract slide XML
        slide_xmls = self.extract_slide_xml(pptx_path)
        
        # Step 4: Generate descriptions
        num_slides = len(ppt_data['shapes'])
        descriptions = self.generate_slide_descriptions(pdf_path, num_slides)
        
        # Step 5: Combine all data
        combined_data = {
            'source_file': pptx_path,
            'pdf_file': pdf_path,
            'num_slides': num_slides,
            'slides': []
        }
        
        for i, slide_shapes in enumerate(ppt_data['shapes']):
            slide_data = {
                'slide_index': i,
                'pdf_page_number': i + 1,
                'description': descriptions[i] if i < len(descriptions) else "No description available",
                'shapes': slide_shapes['shapes'],
                'xml_content': slide_xmls.get(i + 1, ""),
                'media_files': ppt_data['media'],
                'theme': ppt_data['theme'],
                'layouts': ppt_data['layouts']
            }
            combined_data['slides'].append(slide_data)
        
        # Step 6: Save processed data
        output_file = self.output_dir / f"{Path(pptx_path).stem}_processed.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Processing complete. Data saved to: {output_file}")
        return str(output_file)
    
    def create_vector_database_entries(self, processed_data_path: str) -> List[Dict[str, Any]]:
        """Create vector database entries from processed data"""
        print("Creating vector database entries...")
        
        with open(processed_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = []
        
        for slide in data['slides']:
            slide_idx = slide['slide_index']
            
            # Create entry for slide description
            description_entry = {
                'id': f"slide_{slide_idx}_description",
                'text': slide['description'],
                'metadata': {
                    'type': 'slide_description',
                    'slide_index': slide_idx,
                    'source_file': data['source_file'],
                    'pdf_page': slide['pdf_page_number']
                }
            }
            entries.append(description_entry)
            
            # Create entries for each shape
            for shape_idx, shape in enumerate(slide['shapes']):
                if shape.get('text'):
                    shape_entry = {
                        'id': f"slide_{slide_idx}_shape_{shape_idx}",
                        'text': shape['text'],
                        'metadata': {
                            'type': 'shape_text',
                            'slide_index': slide_idx,
                            'shape_index': shape_idx,
                            'shape_type': shape.get('shape_type', 'unknown'),
                            'shape_name': shape.get('name', 'unnamed'),
                            'source_file': data['source_file'],
                            'pdf_page': slide['pdf_page_number'],
                            'shape_data': {
                                'left': shape.get('left'),
                                'top': shape.get('top'),
                                'width': shape.get('width'),
                                'height': shape.get('height'),
                                'xml_content': slide['xml_content']
                            }
                        }
                    }
                    entries.append(shape_entry)
        
        # Save vector database entries
        entries_file = self.output_dir / f"{Path(processed_data_path).stem}_vector_entries.json"
        with open(entries_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created {len(entries)} vector database entries")
        return entries
    
    def export_for_nodejs_rag(self, entries: List[Dict[str, Any]]) -> str:
        """Export data in format compatible with Node.js RAG system"""
        print("Exporting for Node.js RAG system...")
        
        # Create Node.js compatible format
        nodejs_data = {
            'documents': entries,
            'metadata': {
                'created_at': str(Path().resolve()),
                'total_entries': len(entries),
                'entry_types': {}
            }
        }
        
        # Count entry types
        for entry in entries:
            entry_type = entry['metadata']['type']
            nodejs_data['metadata']['entry_types'][entry_type] = \
                nodejs_data['metadata']['entry_types'].get(entry_type, 0) + 1
        
        # Save in Node.js compatible format
        nodejs_file = self.output_dir / "powerpoint_rag_data.json"
        with open(nodejs_file, 'w', encoding='utf-8') as f:
            json.dump(nodejs_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Node.js RAG data exported to: {nodejs_file}")
        return str(nodejs_file)

def main():
    parser = argparse.ArgumentParser(
        description='PowerPoint RAG System - Extract shape data and build RAG database'
    )
    parser.add_argument('input_file', help='Path to PowerPoint file (.pptx)')
    parser.add_argument('--output-dir', default='ppt_rag_output', 
                        help='Output directory for processed files')
    parser.add_argument('--export-nodejs', action='store_true',
                        help='Export data for Node.js RAG system')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input_file).exists():
        print(f"❌ Error: File '{args.input_file}' does not exist.")
        sys.exit(1)
    
    if not args.input_file.lower().endswith('.pptx'):
        print(f"❌ Error: File '{args.input_file}' is not a PowerPoint file (.pptx).")
        sys.exit(1)
    
    try:
        # Initialize system
        rag_system = PowerPointRAGSystem(args.output_dir)
        
        # Process PowerPoint file
        processed_data_path = rag_system.process_powerpoint_file(args.input_file)
        
        # Create vector database entries
        entries = rag_system.create_vector_database_entries(processed_data_path)
        
        # Export for Node.js RAG system if requested
        if args.export_nodejs:
            nodejs_file = rag_system.export_for_nodejs_rag(entries)
            print(f"✅ Ready for Node.js RAG system: {nodejs_file}")
        
        print("\n🎉 PowerPoint RAG processing complete!")
        print(f"Output directory: {args.output_dir}")
        print(f"Processed {len(entries)} entries ready for vector database")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()