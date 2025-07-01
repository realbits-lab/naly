#!/usr/bin/env python3

import sys
import json
import argparse
from pathlib import Path
from pptx import Presentation
from pptx.shapes.base import BaseShape
from pptx.slide import Slide, SlideLayout
from typing import Dict, List, Any


class PPTExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.presentation = Presentation(file_path)
        
    def extract_shapes(self) -> List[Dict[str, Any]]:
        """Extract shape information from all slides"""
        shapes_data = []
        
        for slide_idx, slide in enumerate(self.presentation.slides):
            slide_shapes = []
            
            for shape_idx, shape in enumerate(slide.shapes):
                shape_info = {
                    'slide_index': slide_idx,
                    'shape_index': shape_idx,
                    'shape_id': shape.shape_id,
                    'name': shape.name,
                    'shape_type': str(shape.shape_type),
                    'left': shape.left,
                    'top': shape.top,
                    'width': shape.width,
                    'height': shape.height,
                }
                
                # Add text content if available
                if hasattr(shape, 'text_frame') and shape.text_frame:
                    shape_info['text'] = shape.text_frame.text
                
                # Add additional properties based on shape type
                if hasattr(shape, 'fill'):
                    shape_info['has_fill'] = True
                    if shape.fill.type:
                        shape_info['fill_type'] = str(shape.fill.type)
                
                if hasattr(shape, 'line'):
                    shape_info['has_line'] = True
                    if shape.line.fill.type:
                        shape_info['line_fill_type'] = str(shape.line.fill.type)
                
                slide_shapes.append(shape_info)
            
            shapes_data.append({
                'slide_index': slide_idx,
                'shapes': slide_shapes
            })
        
        return shapes_data
    
    def extract_layouts(self) -> List[Dict[str, Any]]:
        """Extract layout information from the presentation"""
        layouts_data = []
        
        for layout_idx, layout in enumerate(self.presentation.slide_layouts):
            layout_info = {
                'layout_index': layout_idx,
                'name': layout.name,
                'placeholders': []
            }
            
            # Extract placeholder information
            for placeholder in layout.placeholders:
                placeholder_info = {
                    'placeholder_format': str(placeholder.placeholder_format.type),
                    'name': placeholder.name,
                    'left': placeholder.left,
                    'top': placeholder.top,
                    'width': placeholder.width,
                    'height': placeholder.height,
                }
                layout_info['placeholders'].append(placeholder_info)
            
            layouts_data.append(layout_info)
        
        return layouts_data
    
    def extract_theme(self) -> Dict[str, Any]:
        """Extract theme information from the presentation"""
        theme_data = {
            'slide_master': {},
            'color_scheme': {},
            'font_scheme': {}
        }
        
        # Extract slide master information
        slide_master = self.presentation.slide_master
        theme_data['slide_master'] = {
            'name': slide_master.name if hasattr(slide_master, 'name') else 'Unknown',
            'background': str(slide_master.background.fill.type) if slide_master.background.fill else None,
        }
        
        # Extract theme colors
        try:
            theme_part = self.presentation.part.theme_part
            if theme_part:
                theme_data['theme_name'] = theme_part.name if hasattr(theme_part, 'name') else 'Default Theme'
        except:
            theme_data['theme_name'] = 'Default Theme'
        
        # Extract color scheme information
        try:
            color_scheme = slide_master.theme.color_scheme
            theme_colors = {}
            for i, color in enumerate(color_scheme):
                theme_colors[f'color_{i}'] = {
                    'rgb': str(color.rgb) if hasattr(color, 'rgb') else None,
                    'type': str(color.color_type) if hasattr(color, 'color_type') else None
                }
            theme_data['color_scheme'] = theme_colors
        except:
            theme_data['color_scheme'] = {'error': 'Could not extract color scheme'}
        
        # Extract font scheme information
        try:
            font_scheme = slide_master.theme.font_scheme
            theme_data['font_scheme'] = {
                'major_font': {
                    'latin': font_scheme.major_font.latin if hasattr(font_scheme.major_font, 'latin') else None,
                    'ea': font_scheme.major_font.ea if hasattr(font_scheme.major_font, 'ea') else None,
                    'cs': font_scheme.major_font.cs if hasattr(font_scheme.major_font, 'cs') else None,
                },
                'minor_font': {
                    'latin': font_scheme.minor_font.latin if hasattr(font_scheme.minor_font, 'latin') else None,
                    'ea': font_scheme.minor_font.ea if hasattr(font_scheme.minor_font, 'ea') else None,
                    'cs': font_scheme.minor_font.cs if hasattr(font_scheme.minor_font, 'cs') else None,
                }
            }
        except:
            theme_data['font_scheme'] = {'error': 'Could not extract font scheme'}
        
        return theme_data
    
    def save_to_json(self, data: Any, output_file: str):
        """Save data to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Extract shapes, layouts, and theme from PowerPoint files')
    parser.add_argument('input_file', help='Path to the PowerPoint file (.ppt or .pptx)')
    parser.add_argument('--output-dir', default='.', help='Output directory for JSON files (default: current directory)')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File '{args.input_file}' does not exist.")
        sys.exit(1)
    
    if not input_path.suffix.lower() in ['.ppt', '.pptx']:
        print(f"Error: File '{args.input_file}' is not a PowerPoint file (.ppt or .pptx).")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract base filename for output files
    base_name = input_path.stem
    
    try:
        # Initialize extractor
        extractor = PPTExtractor(args.input_file)
        
        # Extract shapes
        print("Extracting shapes...")
        shapes_data = extractor.extract_shapes()
        shapes_output = output_dir / f"{base_name}_shapes.json"
        extractor.save_to_json(shapes_data, shapes_output)
        
        # Extract layouts
        print("Extracting layouts...")
        layouts_data = extractor.extract_layouts()
        layouts_output = output_dir / f"{base_name}_layouts.json"
        extractor.save_to_json(layouts_data, layouts_output)
        
        # Extract theme
        print("Extracting theme...")
        theme_data = extractor.extract_theme()
        theme_output = output_dir / f"{base_name}_theme.json"
        extractor.save_to_json(theme_data, theme_output)
        
        print(f"\nExtraction completed successfully!")
        print(f"Output files created in: {output_dir}")
        
    except Exception as e:
        print(f"Error processing PowerPoint file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()