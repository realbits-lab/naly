#!/usr/bin/env python3

import sys
import json
import argparse
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from typing import Dict, List, Any, Optional


class PPTGenerator:
    def __init__(self):
        self.presentation = Presentation()
        self.shapes_data = []
        self.layouts_data = []
        self.theme_data = {}
        
    def load_json_files(self, shapes_file: str, layouts_file: str, theme_file: str):
        """Load data from JSON files"""
        try:
            with open(shapes_file, 'r', encoding='utf-8') as f:
                self.shapes_data = json.load(f)
            
            with open(layouts_file, 'r', encoding='utf-8') as f:
                self.layouts_data = json.load(f)
                
            with open(theme_file, 'r', encoding='utf-8') as f:
                self.theme_data = json.load(f)
                
            print(f"Loaded {len(self.shapes_data)} slide(s) with shapes")
            print(f"Loaded {len(self.layouts_data)} layout(s)")
            print(f"Loaded theme: {self.theme_data.get('theme_name', 'Unknown')}")
            
        except Exception as e:
            raise Exception(f"Error loading JSON files: {str(e)}")
    
    def emu_to_inches(self, emu_value: int) -> float:
        """Convert EMU (English Metric Units) to inches"""
        return emu_value / 914400.0
    
    def get_layout_by_name(self, layout_name: str) -> Optional[Any]:
        """Get slide layout by name, fallback to first available layout"""
        # Try to find matching layout in presentation
        for i, layout in enumerate(self.presentation.slide_layouts):
            if layout.name.upper() == layout_name.upper():
                return layout
        
        # Fallback to appropriate layout based on name
        layout_mapping = {
            'TITLE': 0,
            'SECTION_HEADER': 1,
            'TITLE_AND_BODY': 1,
            'TITLE_AND_TWO_COLUMNS': 2,
            'TITLE_ONLY': 5,
            'ONE_COLUMN_TEXT': 1,
            'MAIN_POINT': 1,
            'SECTION_TITLE_AND_DESCRIPTION': 1,
            'CAPTION_ONLY': 6,
            'BIG_NUMBER': 1,
            'BLANK': 6
        }
        
        layout_index = layout_mapping.get(layout_name.upper(), 0)
        if layout_index < len(self.presentation.slide_layouts):
            return self.presentation.slide_layouts[layout_index]
        
        # Ultimate fallback
        return self.presentation.slide_layouts[0]
    
    def add_text_to_shape(self, shape, text: str):
        """Add text to a shape if it has a text frame"""
        if hasattr(shape, 'text_frame') and shape.text_frame is not None:
            shape.text_frame.text = text
            # Apply basic formatting
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(18)
    
    def create_text_box(self, slide, shape_info: Dict[str, Any]):
        """Create a text box shape"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))
        
        text_box = slide.shapes.add_textbox(left, top, width, height)
        text_frame = text_box.text_frame
        text_frame.text = shape_info.get('text', '')
        
        # Apply formatting
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(14)
        
        return text_box
    
    def create_rectangle(self, slide, shape_info: Dict[str, Any]):
        """Create a rectangle shape"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))
        
        from pptx.enum.shapes import MSO_SHAPE
        rectangle = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, width, height
        )
        
        # Apply fill color if available
        if shape_info.get('has_fill') and shape_info.get('fill_type') == 'SOLID (1)':
            rectangle.fill.solid()
            # Use a default color since we don't have specific color info
            rectangle.fill.fore_color.rgb = RGBColor(173, 216, 230)  # Light blue
        
        return rectangle
    
    def apply_theme_to_presentation(self):
        """Apply theme settings to the presentation"""
        # Since theme extraction had errors, we'll apply basic styling
        print("Applying basic theme styling...")
        
        # Set slide size (standard 16:9)
        self.presentation.slide_width = Inches(10)
        self.presentation.slide_height = Inches(7.5)
    
    def generate_slides(self):
        """Generate slides based on shapes data"""
        self.apply_theme_to_presentation()
        
        for slide_data in self.shapes_data:
            slide_index = slide_data['slide_index']
            shapes = slide_data['shapes']
            
            print(f"Creating slide {slide_index + 1} with {len(shapes)} shapes...")
            
            # Determine the best layout based on shapes
            layout_name = 'BLANK'  # Default to blank layout
            if shapes:
                # Simple heuristic: if we have placeholder shapes, try to use appropriate layout
                placeholder_count = sum(1 for s in shapes if 'PLACEHOLDER' in s.get('shape_type', ''))
                if placeholder_count >= 2:
                    layout_name = 'TITLE_AND_BODY'
                elif placeholder_count == 1:
                    layout_name = 'TITLE_ONLY'
            
            # Get the layout
            layout = self.get_layout_by_name(layout_name)
            slide = self.presentation.slides.add_slide(layout)
            
            # Add shapes to the slide
            for shape_info in shapes:
                self.add_shape_to_slide(slide, shape_info)
    
    def add_shape_to_slide(self, slide, shape_info: Dict[str, Any]):
        """Add a shape to the slide based on shape info"""
        shape_type = shape_info.get('shape_type', '')
        text = shape_info.get('text', '')
        
        try:
            if 'PLACEHOLDER' in shape_type:
                # Try to fill existing placeholders first
                self.fill_placeholder(slide, shape_info)
            elif 'FREEFORM' in shape_type or 'RECTANGLE' in shape_type:
                # Create rectangle for freeform shapes
                shape = self.create_rectangle(slide, shape_info)
                if text:
                    self.add_text_to_shape(shape, text)
            else:
                # Default to text box for other shapes
                if text:  # Only create if there's text
                    self.create_text_box(slide, shape_info)
        except Exception as e:
            print(f"Warning: Could not create shape {shape_info.get('name', 'Unknown')}: {str(e)}")
    
    def fill_placeholder(self, slide, shape_info: Dict[str, Any]):
        """Try to fill slide placeholders with content"""
        text = shape_info.get('text', '')
        if not text:
            return
        
        # Try to find appropriate placeholder
        for placeholder in slide.placeholders:
            if hasattr(placeholder, 'text_frame') and placeholder.text_frame is not None:
                try:
                    if not placeholder.text_frame.text:  # Only fill empty placeholders
                        placeholder.text_frame.text = text
                        # Apply formatting
                        for paragraph in placeholder.text_frame.paragraphs:
                            for run in paragraph.runs:
                                run.font.size = Pt(18)
                        return
                except:
                    continue
        
        # If no placeholder available, create a text box
        self.create_text_box(slide, shape_info)
    
    def save_presentation(self, output_file: str):
        """Save the presentation to file"""
        self.presentation.save(output_file)
        print(f"Presentation saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate PowerPoint presentation from JSON files')
    parser.add_argument('shapes_file', help='Path to shapes JSON file')
    parser.add_argument('layouts_file', help='Path to layouts JSON file')
    parser.add_argument('theme_file', help='Path to theme JSON file')
    parser.add_argument('--output', '-o', default='generated_presentation.pptx', 
                       help='Output PowerPoint file name (default: generated_presentation.pptx)')
    
    args = parser.parse_args()
    
    # Validate input files
    for file_path in [args.shapes_file, args.layouts_file, args.theme_file]:
        if not Path(file_path).exists():
            print(f"Error: File '{file_path}' does not exist.")
            sys.exit(1)
    
    try:
        # Initialize generator
        generator = PPTGenerator()
        
        # Load JSON data
        print("Loading JSON files...")
        generator.load_json_files(args.shapes_file, args.layouts_file, args.theme_file)
        
        # Generate slides
        print("Generating presentation...")
        generator.generate_slides()
        
        # Save presentation
        generator.save_presentation(args.output)
        
        print(f"\nPresentation generation completed successfully!")
        print(f"Output file: {args.output}")
        
    except Exception as e:
        print(f"Error generating presentation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()