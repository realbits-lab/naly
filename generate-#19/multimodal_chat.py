#!/usr/bin/env python3
"""
Multimodal Chat Program for Custom Shape Generation
Receives image path and prompt, generates custom shapes using ECMA-376 DrawingML
"""

import argparse
import sys
import os
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import shutil

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not installed. Image analysis will be limited.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not installed. Advanced image analysis will be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not installed. Advanced image analysis will be limited.")

# New imports for feedback loop functionality
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Warning: pdf2image not installed. PDF conversion will be limited.")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not installed. PDF processing will be limited.")

try:
    from skimage.metrics import structural_similarity as ssim
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("Warning: scikit-image not installed. Advanced image comparison will be limited.")

try:
    import comtypes.client
    COMTYPES_AVAILABLE = True
except ImportError:
    COMTYPES_AVAILABLE = False
    print("Warning: comtypes not installed. Windows PowerPoint automation not available.")

try:
    import openai
    from openai import OpenAI
    import base64
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Multimodal image comparison not available.")
    

class ImageAnalyzer:
    """Analyzes input images to extract visual features for shape generation"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image and extract relevant features for shape generation"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Basic image properties
        try:
            if not PIL_AVAILABLE:
                raise ValueError("PIL not available for image processing")
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                format_type = img.format
        except Exception as e:
            raise ValueError(f"Cannot open image: {e}")
        
        # Try advanced analysis if libraries available
        features = {
            'width': width,
            'height': height,
            'aspect_ratio': width / height if height > 0 else 1.0,
            'mode': mode,
            'format': format_type,
            'dominant_colors': [],
            'edges': [],
            'contours': [],
            'description': ""
        }
        
        try:
            # Extract dominant colors
            if PIL_AVAILABLE:
                features['dominant_colors'] = self._extract_dominant_colors(image_path)
            
            # Extract edges and contours for shape inspiration
            if CV2_AVAILABLE and NUMPY_AVAILABLE:
                features['edges'], features['contours'] = self._extract_shapes(image_path)
            
        except Exception as e:
            print(f"Advanced analysis failed: {e}")
        
        # Generate description
        features['description'] = self._generate_image_description(features)
        
        # Generate shape recommendations based on analysis
        features['shape_recommendations'] = self._generate_shape_recommendations(features)
        
        return features
    
    def _generate_image_description(self, features: Dict[str, Any]) -> str:
        """Generate a descriptive text of the image analysis"""
        
        # Basic properties
        description = f"Image Analysis:\n"
        description += f"- Dimensions: {features['width']}x{features['height']} pixels\n"
        description += f"- Aspect ratio: {features['aspect_ratio']:.2f}\n"
        description += f"- Color mode: {features['mode']}\n"
        description += f"- Format: {features['format']}\n"
        
        # Dominant colors
        if features['dominant_colors']:
            color_names = []
            for r, g, b in features['dominant_colors'][:3]:  # Top 3 colors
                if r > 200 and g > 200 and b > 200:
                    color_names.append("light/white")
                elif r < 50 and g < 50 and b < 50:
                    color_names.append("dark/black")
                elif r > g and r > b:
                    color_names.append("red-ish")
                elif g > r and g > b:
                    color_names.append("green-ish")
                elif b > r and b > g:
                    color_names.append("blue-ish")
                else:
                    color_names.append("neutral")
            description += f"- Dominant colors: {', '.join(color_names)}\n"
        
        # Shape analysis
        if features['contours']:
            num_shapes = len(features['contours'])
            description += f"- Detected shapes: {num_shapes} distinct regions\n"
            
            # Analyze shape characteristics
            shape_types = []
            for contour in features['contours'][:5]:  # Top 5 shapes
                vertices = contour.get('vertices', 0)
                aspect = contour.get('aspect_ratio', 1.0)
                
                if vertices == 3:
                    shape_types.append("triangular")
                elif vertices == 4:
                    if 0.8 <= aspect <= 1.2:
                        shape_types.append("square-like")
                    else:
                        shape_types.append("rectangular")
                elif vertices > 6:
                    shape_types.append("circular/curved")
                else:
                    shape_types.append(f"{vertices}-sided polygon")
            
            if shape_types:
                description += f"- Shape characteristics: {', '.join(set(shape_types))}\n"
        
        # Visual complexity
        if features['contours']:
            total_area = sum(c.get('area', 0) for c in features['contours'])
            if total_area > 10000:
                description += "- Visual complexity: High (many detailed elements)\n"
            elif total_area > 1000:
                description += "- Visual complexity: Medium (moderate detail)\n"
            else:
                description += "- Visual complexity: Low (simple elements)\n"
        
        # Suggested shape generation approach
        if features['aspect_ratio'] > 1.5:
            description += "- Suggested orientation: Horizontal/landscape shapes\n"
        elif features['aspect_ratio'] < 0.7:
            description += "- Suggested orientation: Vertical/portrait shapes\n"
        else:
            description += "- Suggested orientation: Balanced/square shapes\n"
        
        return description
    
    def _generate_shape_recommendations(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate shape generation recommendations based on image analysis"""
        
        recommendations = {
            'shape_type': 'rectangle',  # default
            'colors': ['blue'],  # default
            'complexity': 'medium',
            'style_hints': {},
            'size_hints': {},
            'reasoning': ''
        }
        
        # Analyze aspect ratio for shape orientation
        aspect_ratio = features.get('aspect_ratio', 1.0)
        
        # Determine primary color from dominant colors (skip white/light colors)
        dominant_colors = features.get('dominant_colors', [(128, 128, 128)])
        selected_colors = []
        
        if dominant_colors:
            # Try to find non-white, non-light colors first
            for rgb in dominant_colors:
                r, g, b = rgb
                # Skip very light/white colors that won't be visible
                if not (r > 200 and g > 200 and b > 200):
                    color_name = self._rgb_to_color_name(rgb)
                    if color_name != 'white' and color_name not in selected_colors:
                        selected_colors.append(color_name)
                        if len(selected_colors) >= 2:  # Get up to 2 good colors
                            break
            
            # If no good colors found, use fallback colors but avoid white
            if not selected_colors:
                # Use more vibrant fallback colors based on image content
                fallback_colors = ['blue', 'red', 'green', 'orange', 'purple']
                selected_colors = [fallback_colors[0]]  # Default to blue
            
            recommendations['colors'] = selected_colors
        
        # Analyze contours to determine best shape type
        contours = features.get('contours', [])
        if contours:
            # Find the most prominent shape characteristics
            total_shapes = len(contours)
            
            # Count shape types in the image
            triangular_count = sum(1 for c in contours if c.get('vertices', 0) == 3)
            rectangular_count = sum(1 for c in contours if c.get('vertices', 0) == 4)
            circular_count = sum(1 for c in contours if c.get('vertices', 0) > 6)
            
            # Calculate shape percentages
            if total_shapes > 0:
                tri_percent = triangular_count / total_shapes
                rect_percent = rectangular_count / total_shapes
                circ_percent = circular_count / total_shapes
                
                # Choose dominant shape type
                if circ_percent > 0.3:
                    recommendations['shape_type'] = 'circle'
                    recommendations['reasoning'] = f'Detected {circular_count} circular/curved shapes ({circ_percent:.1%})'
                elif tri_percent > 0.2:
                    recommendations['shape_type'] = 'triangle'
                    recommendations['reasoning'] = f'Detected {triangular_count} triangular shapes ({tri_percent:.1%})'
                elif rect_percent > 0.4:
                    recommendations['shape_type'] = 'rectangle'
                    recommendations['reasoning'] = f'Detected {rectangular_count} rectangular shapes ({rect_percent:.1%})'
                else:
                    # Use complexity to determine organic vs geometric
                    if total_shapes > 20:
                        recommendations['shape_type'] = 'organic'
                        recommendations['reasoning'] = f'High complexity with {total_shapes} shapes suggests organic form'
                    elif total_shapes > 10:
                        recommendations['shape_type'] = 'star'
                        recommendations['reasoning'] = f'Moderate complexity with {total_shapes} shapes suggests star pattern'
                    else:
                        recommendations['shape_type'] = 'diamond'
                        recommendations['reasoning'] = f'Low-medium complexity with {total_shapes} shapes suggests diamond'
        else:
            # No contour data - use color and aspect ratio
            if aspect_ratio > 1.5:
                recommendations['shape_type'] = 'rectangle'
                recommendations['reasoning'] = 'Wide aspect ratio suggests rectangular shape'
            elif aspect_ratio < 0.7:
                recommendations['shape_type'] = 'triangle'
                recommendations['reasoning'] = 'Tall aspect ratio suggests triangular shape'
            else:
                recommendations['shape_type'] = 'circle'
                recommendations['reasoning'] = 'Balanced aspect ratio suggests circular shape'
        
        # Determine complexity level
        if contours and len(contours) > 15:
            recommendations['complexity'] = 'high'
        elif contours and len(contours) > 5:
            recommendations['complexity'] = 'medium'
        else:
            recommendations['complexity'] = 'low'
        
        # Set style hints based on shape characteristics
        if contours:
            avg_vertices = sum(c.get('vertices', 4) for c in contours[:5]) / min(len(contours), 5)
            if avg_vertices > 6:
                recommendations['style_hints']['edges'] = 'smooth'
            else:
                recommendations['style_hints']['edges'] = 'sharp'
        
        # Size hints based on image dimensions
        width = features.get('width', 1000)
        height = features.get('height', 1000)
        
        if width > 1200 or height > 1200:
            recommendations['size_hints']['relative_size'] = 'large'
        elif width < 600 or height < 600:
            recommendations['size_hints']['relative_size'] = 'small'
        else:
            recommendations['size_hints']['relative_size'] = 'medium'
        
        return recommendations
    
    def _rgb_to_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to color name"""
        r, g, b = rgb
        
        # Define color ranges
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r > max(g, b) + 50:
            return 'red'
        elif g > max(r, b) + 50:
            return 'green'
        elif b > max(r, g) + 50:
            return 'blue'
        elif r > 150 and g > 150 and b < 100:
            return 'yellow'
        elif r > 150 and g < 100 and b > 150:
            return 'purple'
        elif r > 150 and g > 100 and b < 100:
            return 'orange'
        else:
            return 'gray'
    
    def _extract_dominant_colors(self, image_path: str) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from the image"""
        if not PIL_AVAILABLE:
            return [(128, 128, 128)]  # Default gray
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize for faster processing
                img = img.resize((150, 150))
                
                # Get colors
                colors = img.getcolors(maxcolors=256*256*256)
                if colors:
                    # Sort by frequency and return top 5
                    colors.sort(key=lambda x: x[0], reverse=True)
                    return [color[1] for color in colors[:5]]
        except:
            pass
        return [(128, 128, 128)]  # Default gray
    
    def _extract_shapes(self, image_path: str) -> Tuple[List, List]:
        """Extract edge information and contours that could inspire shapes"""
        edges = []
        contours = []
        
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            return edges, contours
        
        try:
            # Read image with cv2
            img = cv2.imread(image_path)
            if img is None:
                return edges, contours
                
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges_detected = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours_detected, _ = cv2.findContours(edges_detected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze contours for shape characteristics
            for contour in contours_detected:
                if cv2.contourArea(contour) > 100:  # Filter small contours
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Approximate contour to polygon
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    contours.append({
                        'vertices': len(approx),
                        'area': cv2.contourArea(contour),
                        'perimeter': cv2.arcLength(contour, True),
                        'bounding_rect': (x, y, w, h),
                        'aspect_ratio': w/h if h > 0 else 1.0
                    })
            
        except Exception as e:
            print(f"Shape extraction failed: {e}")
        
        return edges, contours


class ImageBasedShapeDecider:
    """Decides shape generation parameters based purely on image analysis"""
    
    def __init__(self):
        # No keywords needed since we're working with image analysis directly
        pass
    
    def process_image_analysis(self, image_features: Dict[str, Any]) -> Dict[str, Any]:
        """Process image analysis and convert to shape generation parameters"""
        
        # Extract recommendations from image analysis
        recommendations = image_features.get('shape_recommendations', {})
        description = image_features.get('description', '')
        
        # Convert to format expected by DrawingMLGenerator
        result = {
            'original_prompt': f"Generated from image analysis: {recommendations.get('reasoning', 'Image-based shape generation')}",
            'image_description': description,
            'combined_prompt': description,
            'shape_type': recommendations.get('shape_type', 'rectangle'),
            'colors': recommendations.get('colors', ['blue']),
            'size_hints': recommendations.get('size_hints', {'relative_size': 'medium'}),
            'style_hints': recommendations.get('style_hints', {}),
            'complexity': recommendations.get('complexity', 'medium'),
            'reasoning': recommendations.get('reasoning', 'Based on image analysis')
        }
        
        return result


class DrawingMLGenerator:
    """Generates ECMA-376 compliant DrawingML custom geometry"""
    
    def __init__(self):
        self.namespaces = {
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'
        }
    
    def generate_custom_shape(self, image_features: Dict[str, Any], 
                            prompt_data: Dict[str, Any]) -> str:
        """Generate DrawingML XML for a custom shape based on inputs"""
        
        # Determine shape parameters
        shape_type = prompt_data['shape_type']
        colors = prompt_data['colors']
        style_hints = prompt_data['style_hints']
        
        # Generate based on shape type
        if shape_type == 'circle':
            return self._generate_circle(colors, style_hints)
        elif shape_type == 'rectangle':
            return self._generate_rectangle(colors, style_hints)
        elif shape_type == 'triangle':
            return self._generate_triangle(colors, style_hints)
        elif shape_type == 'star':
            return self._generate_star(colors, style_hints)
        elif shape_type == 'diamond':
            return self._generate_diamond(colors, style_hints)
        elif shape_type == 'organic':
            return self._generate_organic_shape(image_features, colors, style_hints)
        else:
            return self._generate_custom_polygon(image_features, colors, style_hints)
    
    def _generate_circle(self, colors: List[str], style_hints: Dict[str, Any]) -> str:
        """Generate a circular shape"""
        color = self._get_rgb_color(colors[0] if colors else 'blue')
        
        return f'''<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomCircle"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="2000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <a:avLst/>
            <a:gdLst>
                <a:gd name="w" fmla="*/ ss 1 1"/>
                <a:gd name="h" fmla="*/ ss 1 1"/>
                <a:gd name="hc" fmla="*/ w 1 2"/>
                <a:gd name="vc" fmla="*/ h 1 2"/>
            </a:gdLst>
            <a:pathLst>
                <a:path w="2000000" h="2000000">
                    <a:moveTo>
                        <a:pt x="2000000" y="1000000"/>
                    </a:moveTo>
                    <a:arcTo wR="1000000" hR="1000000" stAng="0" swAng="21600000"/>
                    <a:close/>
                </a:path>
            </a:pathLst>
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="{color}"/>
        </a:solidFill>
    </p:spPr>
</p:sp>'''
    
    def _generate_rectangle(self, colors: List[str], style_hints: Dict[str, Any]) -> str:
        """Generate a rectangular shape"""
        color = self._get_rgb_color(colors[0] if colors else 'blue')
        
        return f'''<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomRectangle"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="3000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <a:avLst/>
            <a:gdLst>
                <a:gd name="w" fmla="*/ w 1 1"/>
                <a:gd name="h" fmla="*/ h 1 1"/>
            </a:gdLst>
            <a:pathLst>
                <a:path w="3000000" h="2000000">
                    <a:moveTo>
                        <a:pt x="0" y="0"/>
                    </a:moveTo>
                    <a:lnTo>
                        <a:pt x="3000000" y="0"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="3000000" y="2000000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="0" y="2000000"/>
                    </a:lnTo>
                    <a:close/>
                </a:path>
            </a:pathLst>
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="{color}"/>
        </a:solidFill>
    </p:spPr>
</p:sp>'''
    
    def _generate_triangle(self, colors: List[str], style_hints: Dict[str, Any]) -> str:
        """Generate a triangular shape"""
        color = self._get_rgb_color(colors[0] if colors else 'blue')
        
        return f'''<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomTriangle"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="2000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <a:avLst/>
            <a:gdLst>
                <a:gd name="w" fmla="*/ w 1 1"/>
                <a:gd name="h" fmla="*/ h 1 1"/>
                <a:gd name="hc" fmla="*/ w 1 2"/>
            </a:gdLst>
            <a:pathLst>
                <a:path w="2000000" h="2000000">
                    <a:moveTo>
                        <a:pt x="1000000" y="0"/>
                    </a:moveTo>
                    <a:lnTo>
                        <a:pt x="2000000" y="2000000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="0" y="2000000"/>
                    </a:lnTo>
                    <a:close/>
                </a:path>
            </a:pathLst>
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="{color}"/>
        </a:solidFill>
    </p:spPr>
</p:sp>'''
    
    def _generate_star(self, colors: List[str], style_hints: Dict[str, Any]) -> str:
        """Generate a star shape"""
        color = self._get_rgb_color(colors[0] if colors else 'blue')
        
        return f'''<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomStar"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="2000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <a:avLst/>
            <a:gdLst>
                <a:gd name="w" fmla="*/ w 1 1"/>
                <a:gd name="h" fmla="*/ h 1 1"/>
                <a:gd name="hc" fmla="*/ w 1 2"/>
                <a:gd name="vc" fmla="*/ h 1 2"/>
            </a:gdLst>
            <a:pathLst>
                <a:path w="2000000" h="2000000">
                    <a:moveTo>
                        <a:pt x="1000000" y="0"/>
                    </a:moveTo>
                    <a:lnTo>
                        <a:pt x="1300000" y="700000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="2000000" y="700000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="1500000" y="1200000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="1700000" y="2000000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="1000000" y="1600000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="300000" y="2000000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="500000" y="1200000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="0" y="700000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="700000" y="700000"/>
                    </a:lnTo>
                    <a:close/>
                </a:path>
            </a:pathLst>
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="{color}"/>
        </a:solidFill>
    </p:spPr>
</p:sp>'''
    
    def _generate_diamond(self, colors: List[str], style_hints: Dict[str, Any]) -> str:
        """Generate a diamond shape"""
        color = self._get_rgb_color(colors[0] if colors else 'blue')
        
        return f'''<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomDiamond"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="2000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <a:avLst/>
            <a:gdLst>
                <a:gd name="w" fmla="*/ w 1 1"/>
                <a:gd name="h" fmla="*/ h 1 1"/>
                <a:gd name="hc" fmla="*/ w 1 2"/>
                <a:gd name="vc" fmla="*/ h 1 2"/>
            </a:gdLst>
            <a:pathLst>
                <a:path w="2000000" h="2000000">
                    <a:moveTo>
                        <a:pt x="1000000" y="0"/>
                    </a:moveTo>
                    <a:lnTo>
                        <a:pt x="2000000" y="1000000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="1000000" y="2000000"/>
                    </a:lnTo>
                    <a:lnTo>
                        <a:pt x="0" y="1000000"/>
                    </a:lnTo>
                    <a:close/>
                </a:path>
            </a:pathLst>
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="{color}"/>
        </a:solidFill>
    </p:spPr>
</p:sp>'''
    
    def _generate_organic_shape(self, image_features: Dict[str, Any], 
                              colors: List[str], style_hints: Dict[str, Any]) -> str:
        """Generate an organic, curved shape inspired by image features"""
        color = self._get_rgb_color(colors[0] if colors else 'blue')
        
        # Use image aspect ratio to influence shape
        aspect_ratio = image_features.get('aspect_ratio', 1.0)
        
        return f'''<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomOrganic"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="2000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <a:avLst/>
            <a:gdLst>
                <a:gd name="w" fmla="*/ w 1 1"/>
                <a:gd name="h" fmla="*/ h 1 1"/>
            </a:gdLst>
            <a:pathLst>
                <a:path w="2000000" h="2000000">
                    <a:moveTo>
                        <a:pt x="200000" y="800000"/>
                    </a:moveTo>
                    <a:cubicBezTo>
                        <a:pt x="600000" y="200000"/>
                        <a:pt x="1400000" y="200000"/>
                        <a:pt x="1800000" y="800000"/>
                    </a:cubicBezTo>
                    <a:cubicBezTo>
                        <a:pt x="1900000" y="1200000"/>
                        <a:pt x="1600000" y="1800000"/>
                        <a:pt x="1000000" y="1900000"/>
                    </a:cubicBezTo>
                    <a:cubicBezTo>
                        <a:pt x="400000" y="1800000"/>
                        <a:pt x="100000" y="1200000"/>
                        <a:pt x="200000" y="800000"/>
                    </a:cubicBezTo>
                    <a:close/>
                </a:path>
            </a:pathLst>
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="{color}"/>
        </a:solidFill>
    </p:spPr>
</p:sp>'''
    
    def _generate_custom_polygon(self, image_features: Dict[str, Any], 
                               colors: List[str], style_hints: Dict[str, Any]) -> str:
        """Generate a custom polygon based on image contours"""
        color = self._get_rgb_color(colors[0] if colors else 'blue')
        
        # If we have contour data, use it to create a polygon
        contours = image_features.get('contours', [])
        if contours:
            # Find the most significant contour
            main_contour = max(contours, key=lambda c: c['area'])
            vertices = main_contour.get('vertices', 6)
            
            # Generate polygon with that many vertices
            if vertices == 3:
                return self._generate_triangle(colors, style_hints)
            elif vertices == 4:
                return self._generate_rectangle(colors, style_hints)
            else:
                # Generate a regular polygon
                return self._generate_regular_polygon(vertices, color)
        
        # Default to hexagon
        return self._generate_regular_polygon(6, color)
    
    def _generate_regular_polygon(self, sides: int, color: str) -> str:
        """Generate a regular polygon with specified number of sides"""
        import math
        
        # Calculate points for regular polygon
        points = []
        center_x, center_y = 1000000, 1000000
        radius = 800000
        
        for i in range(sides):
            angle = 2 * math.pi * i / sides - math.pi / 2  # Start from top
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(f'<a:pt x="{int(x)}" y="{int(y)}"/>')
        
        points_xml = '\n                    '.join(points[1:])  # Skip first point (it's in moveTo)
        
        return f'''<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomPolygon"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="2000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <a:avLst/>
            <a:gdLst>
                <a:gd name="w" fmla="*/ w 1 1"/>
                <a:gd name="h" fmla="*/ h 1 1"/>
            </a:gdLst>
            <a:pathLst>
                <a:path w="2000000" h="2000000">
                    <a:moveTo>
                        {points[0]}
                    </a:moveTo>
                    <a:lnTo>
                        {points_xml}
                    </a:lnTo>
                    <a:close/>
                </a:path>
            </a:pathLst>
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="{color}"/>
        </a:solidFill>
    </p:spPr>
</p:sp>'''
    
    def _get_rgb_color(self, color_name: str) -> str:
        """Convert color name to RGB hex value"""
        color_map = {
            'red': 'FF0000',
            'blue': '0000FF',
            'green': '00FF00',
            'yellow': 'FFFF00',
            'purple': '800080',
            'orange': 'FFA500',
            'black': '000000',
            'white': 'FFFFFF',
            'gray': '808080'
        }
        return color_map.get(color_name.lower(), '0000FF')  # Default to blue


class PowerPointModifier:
    """Handles PPTX file manipulation - unzip, modify, zip"""
    
    def __init__(self, template_path: str = "blank.pptx"):
        self.template_path = template_path
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
    
    def modify_slide1_with_shape(self, shape_xml: str, output_path: str, verbose: bool = False):
        """Unzip PPTX, modify slide1.xml with custom shape, and rezip"""
        
        if verbose:
            print("\n" + "="*60)
            print("📄 GENERATED SHAPE XML:")
            print("="*60)
            print(shape_xml)
            print("="*60)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract PPTX to temp directory
            with zipfile.ZipFile(self.template_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            # Find and modify slide1.xml
            slide1_path = os.path.join(temp_dir, 'ppt', 'slides', 'slide1.xml')
            
            if not os.path.exists(slide1_path):
                raise FileNotFoundError("slide1.xml not found in template")
            
            # Read original slide1.xml
            if verbose:
                with open(slide1_path, 'r', encoding='utf-8') as f:
                    original_slide = f.read()
                print("\n📄 ORIGINAL SLIDE1.XML:")
                print("="*60)
                print(original_slide)
                print("="*60)
            
            # Parse existing slide1.xml
            tree = ET.parse(slide1_path)
            root = tree.getroot()
            
            # Register namespaces
            namespaces = {
                'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
            }
            
            # Find the slide's shape tree
            sp_tree = root.find('.//p:spTree', namespaces)
            
            if sp_tree is None:
                raise ValueError("Could not find shape tree in slide1.xml")
            
            # Parse and add the custom shape
            try:
                # Create a temporary root with namespaces to parse the shape
                temp_xml = f'''<root xmlns:p="{namespaces['p']}" xmlns:a="{namespaces['a']}">{shape_xml}</root>'''
                temp_root = ET.fromstring(temp_xml)
                shape_element = temp_root.find('p:sp', namespaces)
                
                if shape_element is None:
                    raise ValueError("Could not find shape element in generated XML")
                
                # Add the shape to the shape tree
                sp_tree.append(shape_element)
                
            except ET.ParseError as e:
                raise ValueError(f"Invalid shape XML: {e}")
            
            # Write modified slide1.xml back
            tree.write(slide1_path, encoding='utf-8', xml_declaration=True)
            
            # Read and display modified slide1.xml
            if verbose:
                with open(slide1_path, 'r', encoding='utf-8') as f:
                    modified_slide = f.read()
                print("\n📄 MODIFIED SLIDE1.XML:")
                print("="*60)
                print(modified_slide)
                print("="*60)
            
            # Rezip the PPTX
            self._create_pptx_from_directory(temp_dir, output_path)
    
    def _create_pptx_from_directory(self, directory: str, output_path: str):
        """Create a PPTX file from a directory structure"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, directory)
                    zip_file.write(file_path, archive_name)


class PowerPointConverter:
    """Handles conversion of PowerPoint files to PDF"""
    
    def __init__(self):
        self.temp_dir = None
    
    def convert_to_pdf(self, pptx_path: str, pdf_path: str = None) -> str:
        """Convert PowerPoint file to PDF"""
        if not os.path.exists(pptx_path):
            raise FileNotFoundError(f"PowerPoint file not found: {pptx_path}")
        
        if pdf_path is None:
            pdf_path = pptx_path.replace('.pptx', '.pdf')
        
        # Try different conversion methods based on available tools
        success = False
        
        # Method 1: Try LibreOffice command line (cross-platform)
        if not success:
            success = self._convert_with_libreoffice(pptx_path, pdf_path)
        
        # Method 2: Try Windows COM automation
        if not success and COMTYPES_AVAILABLE and os.name == 'nt':
            success = self._convert_with_com(pptx_path, pdf_path)
        
        # Method 3: Try macOS automation (if on macOS)
        if not success and sys.platform == 'darwin':
            success = self._convert_with_macos_automation(pptx_path, pdf_path)
        
        if not success:
            raise RuntimeError("No available method for PowerPoint to PDF conversion")
        
        return pdf_path
    
    def _convert_with_libreoffice(self, pptx_path: str, pdf_path: str) -> bool:
        """Try conversion using LibreOffice command line"""
        try:
            import subprocess
            
            # Try to find LibreOffice
            libreoffice_cmd = None
            for cmd in ['libreoffice', 'soffice', '/Applications/LibreOffice.app/Contents/MacOS/soffice']:
                try:
                    subprocess.run([cmd, '--version'], capture_output=True, check=True)
                    libreoffice_cmd = cmd
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not libreoffice_cmd:
                return False
            
            # Create temp directory for output
            temp_dir = tempfile.mkdtemp()
            
            # Convert to PDF
            cmd = [
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', temp_dir,
                pptx_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Find the generated PDF
                base_name = os.path.splitext(os.path.basename(pptx_path))[0]
                temp_pdf = os.path.join(temp_dir, f"{base_name}.pdf")
                
                if os.path.exists(temp_pdf):
                    shutil.move(temp_pdf, pdf_path)
                    shutil.rmtree(temp_dir)
                    return True
            
            shutil.rmtree(temp_dir)
            return False
            
        except Exception as e:
            print(f"LibreOffice conversion failed: {e}")
            return False
    
    def _convert_with_com(self, pptx_path: str, pdf_path: str) -> bool:
        """Try conversion using Windows COM automation"""
        try:
            if not COMTYPES_AVAILABLE:
                return False
            
            # PowerPoint COM automation
            powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
            powerpoint.Visible = False
            
            presentation = powerpoint.Presentations.Open(os.path.abspath(pptx_path))
            presentation.SaveAs(os.path.abspath(pdf_path), 32)  # 32 = ppSaveAsPDF
            presentation.Close()
            powerpoint.Quit()
            
            return os.path.exists(pdf_path)
            
        except Exception as e:
            print(f"COM conversion failed: {e}")
            return False
    
    def _convert_with_macos_automation(self, pptx_path: str, pdf_path: str) -> bool:
        """Try conversion using macOS Keynote automation"""
        try:
            import subprocess
            
            # AppleScript to convert using Keynote
            applescript = f'''
            tell application "Keynote"
                set thePresentation to open POSIX file "{os.path.abspath(pptx_path)}"
                export thePresentation as PDF to POSIX file "{os.path.abspath(pdf_path)}"
                close thePresentation
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0 and os.path.exists(pdf_path)
            
        except Exception as e:
            print(f"macOS automation failed: {e}")
            return False


class PDFToImageConverter:
    """Handles conversion of PDF files to PNG images"""
    
    def __init__(self):
        pass
    
    def convert_to_png(self, pdf_path: str, png_path: str = None, page_number: int = 1) -> str:
        """Convert PDF to PNG image"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if png_path is None:
            png_path = pdf_path.replace('.pdf', '.png')
        
        success = False
        
        # Method 1: Try pdf2image
        if not success and PDF2IMAGE_AVAILABLE:
            success = self._convert_with_pdf2image(pdf_path, png_path, page_number)
        
        # Method 2: Try PyMuPDF
        if not success and PYMUPDF_AVAILABLE:
            success = self._convert_with_pymupdf(pdf_path, png_path, page_number)
        
        if not success:
            raise RuntimeError("No available method for PDF to PNG conversion")
        
        return png_path
    
    def _convert_with_pdf2image(self, pdf_path: str, png_path: str, page_number: int) -> bool:
        """Convert using pdf2image library"""
        try:
            images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number, dpi=150)
            
            if images:
                images[0].save(png_path, 'PNG')
                return True
            
            return False
            
        except Exception as e:
            print(f"pdf2image conversion failed: {e}")
            return False
    
    def _convert_with_pymupdf(self, pdf_path: str, png_path: str, page_number: int) -> bool:
        """Convert using PyMuPDF library"""
        try:
            doc = fitz.open(pdf_path)
            
            if page_number > len(doc):
                doc.close()
                return False
            
            page = doc[page_number - 1]  # 0-based indexing
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better quality
            pix.save(png_path)
            
            doc.close()
            return True
            
        except Exception as e:
            print(f"PyMuPDF conversion failed: {e}")
            return False


class ImageComparator:
    """Compares original and generated images to analyze differences"""
    
    def __init__(self):
        pass
    
    def compare_images(self, original_path: str, generated_path: str) -> Dict[str, Any]:
        """Compare two images and return difference analysis"""
        if not os.path.exists(original_path):
            raise FileNotFoundError(f"Original image not found: {original_path}")
        if not os.path.exists(generated_path):
            raise FileNotFoundError(f"Generated image not found: {generated_path}")
        
        comparison_result = {
            'similarity_score': 0.0,
            'differences': [],
            'recommendations': [],
            'structural_similarity': 0.0,
            'color_differences': [],
            'shape_differences': [],
            'improvement_suggestions': "",
            'is_blank_image': False,
            'validation_errors': []
        }
        
        try:
            # Load images
            if not PIL_AVAILABLE:
                raise ValueError("PIL not available for image comparison")
            
            with Image.open(original_path) as orig_img:
                with Image.open(generated_path) as gen_img:
                    
                    # Check if generated image is blank/empty
                    blank_check = self._is_blank_image(gen_img)
                    comparison_result['is_blank_image'] = blank_check['is_blank']
                    
                    if blank_check['is_blank']:
                        comparison_result['validation_errors'].append(
                            f"Generated image appears to be blank: {blank_check['reason']}"
                        )
                        comparison_result['similarity_score'] = 0.0
                        comparison_result['structural_similarity'] = 0.0
                        comparison_result['improvement_suggestions'] = (
                            f"CRITICAL: Generated image is blank ({blank_check['reason']}). "
                            "The shape generation or PDF conversion process failed. "
                            "Need to fix shape visibility and conversion pipeline."
                        )
                        return comparison_result
                    
                    # Resize generated image to match original for fair comparison
                    gen_img_resized = gen_img.resize(orig_img.size, Image.Resampling.LANCZOS)
                    
                    # Basic similarity analysis
                    comparison_result.update(self._analyze_basic_differences(orig_img, gen_img_resized))
                    
                    # Advanced analysis if libraries available
                    if CV2_AVAILABLE and NUMPY_AVAILABLE:
                        comparison_result.update(self._analyze_advanced_differences(orig_img, gen_img_resized))
                    
                    # Generate improvement suggestions
                    comparison_result['improvement_suggestions'] = self._generate_improvement_suggestions(comparison_result)
        
        except Exception as e:
            print(f"Image comparison failed: {e}")
            comparison_result['error'] = str(e)
        
        return comparison_result
    
    def _is_blank_image(self, img: Image.Image) -> Dict[str, Any]:
        """Check if an image is blank or mostly empty"""
        try:
            # Convert to RGB for consistent analysis
            img_rgb = img.convert('RGB')
            
            # Get image statistics
            width, height = img_rgb.size
            total_pixels = width * height
            
            # Get all pixel colors
            colors = img_rgb.getcolors(maxcolors=total_pixels)
            
            if not colors:
                return {'is_blank': True, 'reason': 'no colors detected'}
            
            # Check if image is completely one color
            if len(colors) == 1:
                color_count, color_rgb = colors[0]
                if color_count == total_pixels:
                    # Check if it's white or very light
                    r, g, b = color_rgb
                    if r > 240 and g > 240 and b > 240:
                        return {'is_blank': True, 'reason': f'completely white ({r},{g},{b})'}
                    elif r == g == b and r > 200:
                        return {'is_blank': True, 'reason': f'completely gray/white ({r},{g},{b})'}
            
            # Check if image is mostly white/light
            white_pixels = 0
            light_pixels = 0
            
            for count, (r, g, b) in colors:
                # Count white pixels
                if r > 240 and g > 240 and b > 240:
                    white_pixels += count
                # Count light pixels
                elif r > 200 and g > 200 and b > 200:
                    light_pixels += count
            
            white_percentage = white_pixels / total_pixels
            light_percentage = (white_pixels + light_pixels) / total_pixels
            
            if white_percentage > 0.95:
                return {'is_blank': True, 'reason': f'{white_percentage:.1%} white pixels'}
            elif light_percentage > 0.98:
                return {'is_blank': True, 'reason': f'{light_percentage:.1%} light/white pixels'}
            
            # Check for very low color diversity
            unique_colors = len(colors)
            if unique_colors < 10 and total_pixels > 1000:
                dominant_color = max(colors, key=lambda x: x[0])
                dominant_percentage = dominant_color[0] / total_pixels
                if dominant_percentage > 0.9:
                    return {'is_blank': True, 'reason': f'very low color diversity ({unique_colors} colors, {dominant_percentage:.1%} dominant)'}
            
            return {'is_blank': False, 'reason': f'normal image ({unique_colors} colors, {white_percentage:.1%} white)'}
            
        except Exception as e:
            return {'is_blank': True, 'reason': f'analysis failed: {e}'}
    
    def _analyze_basic_differences(self, orig_img: Image.Image, gen_img: Image.Image) -> Dict[str, Any]:
        """Analyze basic differences between images"""
        result = {}
        
        try:
            # Convert to RGB for consistency
            orig_rgb = orig_img.convert('RGB')
            gen_rgb = gen_img.convert('RGB')
            
            # Color histogram comparison
            orig_hist = orig_rgb.histogram()
            gen_hist = gen_rgb.histogram()
            
            # Calculate histogram similarity (simple correlation)
            hist_similarity = self._calculate_histogram_similarity(orig_hist, gen_hist)
            result['histogram_similarity'] = hist_similarity
            
            # Extract dominant colors from both images
            orig_colors = self._extract_dominant_colors_from_pil(orig_rgb)
            gen_colors = self._extract_dominant_colors_from_pil(gen_rgb)
            
            result['color_differences'] = self._compare_color_palettes(orig_colors, gen_colors)
            
        except Exception as e:
            print(f"Basic analysis failed: {e}")
        
        return result
    
    def _analyze_advanced_differences(self, orig_img: Image.Image, gen_img: Image.Image) -> Dict[str, Any]:
        """Analyze advanced differences using OpenCV"""
        result = {}
        
        try:
            # Convert PIL images to OpenCV format
            orig_cv = cv2.cvtColor(np.array(orig_img), cv2.COLOR_RGB2BGR)
            gen_cv = cv2.cvtColor(np.array(gen_img), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale for structural analysis
            orig_gray = cv2.cvtColor(orig_cv, cv2.COLOR_BGR2GRAY)
            gen_gray = cv2.cvtColor(gen_cv, cv2.COLOR_BGR2GRAY)
            
            # Structural similarity
            if SKIMAGE_AVAILABLE:
                ssim_score = ssim(orig_gray, gen_gray)
                result['structural_similarity'] = float(ssim_score)
            
            # Edge detection comparison
            orig_edges = cv2.Canny(orig_gray, 50, 150)
            gen_edges = cv2.Canny(gen_gray, 50, 150)
            
            # Compare edge patterns
            edge_diff = cv2.absdiff(orig_edges, gen_edges)
            edge_similarity = 1.0 - (np.sum(edge_diff > 0) / edge_diff.size)
            result['edge_similarity'] = float(edge_similarity)
            
            # Contour analysis
            orig_contours, _ = cv2.findContours(orig_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            gen_contours, _ = cv2.findContours(gen_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            result['shape_differences'] = self._compare_contours(orig_contours, gen_contours)
            
        except Exception as e:
            print(f"Advanced analysis failed: {e}")
        
        return result
    
    def _calculate_histogram_similarity(self, hist1: List[int], hist2: List[int]) -> float:
        """Calculate similarity between two histograms using improved method"""
        try:
            if len(hist1) != len(hist2):
                return 0.0
            
            # Normalize histograms to percentages
            total1 = sum(hist1)
            total2 = sum(hist2)
            
            if total1 == 0 or total2 == 0:
                return 0.0
            
            norm_hist1 = [h / total1 for h in hist1]
            norm_hist2 = [h / total2 for h in hist2]
            
            # Use intersection over union approach for better comparison
            intersection = sum(min(h1, h2) for h1, h2 in zip(norm_hist1, norm_hist2))
            union = sum(max(h1, h2) for h1, h2 in zip(norm_hist1, norm_hist2))
            
            if union == 0:
                return 1.0 if intersection == 0 else 0.0
            
            # Jaccard similarity (intersection over union)
            jaccard_sim = intersection / union
            
            # Also calculate chi-squared distance for additional validation
            chi_squared = 0.0
            for h1, h2 in zip(norm_hist1, norm_hist2):
                if h1 + h2 > 0:
                    chi_squared += ((h1 - h2) ** 2) / (h1 + h2)
            
            # Convert chi-squared to similarity (lower chi-squared = higher similarity)
            chi_sim = 1.0 / (1.0 + chi_squared)
            
            # Combine both metrics with weights
            final_similarity = 0.7 * jaccard_sim + 0.3 * chi_sim
            
            return max(0.0, min(1.0, final_similarity))
            
        except Exception:
            return 0.0
    
    def _extract_dominant_colors_from_pil(self, img: Image.Image) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from PIL image"""
        try:
            # Get the most common colors
            colors = img.getcolors(maxcolors=256*256*256)
            if colors:
                # Sort by frequency and take top 5
                colors.sort(key=lambda x: x[0], reverse=True)
                return [color[1] for color in colors[:5]]
            return []
        except Exception:
            return []
    
    def _compare_color_palettes(self, orig_colors: List[Tuple[int, int, int]], 
                               gen_colors: List[Tuple[int, int, int]]) -> List[str]:
        """Compare color palettes and return differences"""
        differences = []
        
        if not orig_colors and not gen_colors:
            return differences
        
        if not orig_colors:
            differences.append("Original image has no detectable colors")
            return differences
        
        if not gen_colors:
            differences.append("Generated image has no detectable colors")
            return differences
        
        # Convert to color names for easier comparison
        orig_color_names = [self._rgb_to_color_name(color) for color in orig_colors[:3]]
        gen_color_names = [self._rgb_to_color_name(color) for color in gen_colors[:3]]
        
        missing_colors = set(orig_color_names) - set(gen_color_names)
        extra_colors = set(gen_color_names) - set(orig_color_names)
        
        if missing_colors:
            differences.append(f"Missing colors from original: {', '.join(missing_colors)}")
        
        if extra_colors:
            differences.append(f"Extra colors not in original: {', '.join(extra_colors)}")
        
        return differences
    
    def _rgb_to_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB to approximate color name"""
        r, g, b = rgb
        
        # Simple color name mapping
        if r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > 200 and g < 100 and b < 100:
            return "red"
        elif r < 100 and g > 200 and b < 100:
            return "green"
        elif r < 100 and g < 100 and b > 200:
            return "blue"
        elif r > 200 and g > 200 and b < 100:
            return "yellow"
        elif r > 200 and g < 100 and b > 200:
            return "purple"
        elif r > 200 and g > 150 and b < 100:
            return "orange"
        else:
            return "gray"
    
    def _compare_contours(self, orig_contours: List, gen_contours: List) -> List[str]:
        """Compare contour shapes between images"""
        differences = []
        
        orig_count = len(orig_contours)
        gen_count = len(gen_contours)
        
        if orig_count == 0 and gen_count == 0:
            return differences
        
        differences.append(f"Original has {orig_count} shapes, generated has {gen_count} shapes")
        
        if orig_count > gen_count:
            differences.append("Generated image is missing some shapes from the original")
        elif gen_count > orig_count:
            differences.append("Generated image has extra shapes not in the original")
        
        # Analyze shape complexity if shapes exist
        if orig_contours and gen_contours:
            orig_complexity = np.mean([len(contour) for contour in orig_contours])
            gen_complexity = np.mean([len(contour) for contour in gen_contours])
            
            if abs(orig_complexity - gen_complexity) > 10:
                if orig_complexity > gen_complexity:
                    differences.append("Generated shapes are simpler than original")
                else:
                    differences.append("Generated shapes are more complex than original")
        
        return differences
    
    def _generate_improvement_suggestions(self, comparison_result: Dict[str, Any]) -> str:
        """Generate improvement suggestions based on comparison"""
        suggestions = []
        
        # Check structural similarity
        struct_sim = comparison_result.get('structural_similarity', 0)
        if struct_sim < 0.3:
            suggestions.append("The generated shape has very different structure from the original image")
            suggestions.append("Consider analyzing the original image's dominant shapes more carefully")
        elif struct_sim < 0.6:
            suggestions.append("The generated shape partially matches the original but could be improved")
        
        # Check color differences
        color_diffs = comparison_result.get('color_differences', [])
        if color_diffs:
            suggestions.extend(color_diffs)
            suggestions.append("Adjust the color selection to better match the original image")
        
        # Check shape differences
        shape_diffs = comparison_result.get('shape_differences', [])
        if shape_diffs:
            suggestions.extend(shape_diffs)
            suggestions.append("Consider changing the shape type to better match the original")
        
        if not suggestions:
            suggestions.append("The generated shape appears to match the original image well")
        
        return ". ".join(suggestions)


class OpenAIImageComparator:
    """Uses OpenAI's multimodal LLM to compare images and provide semantic analysis"""
    
    def __init__(self, api_key: str = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        
    def compare_images(self, original_path: str, generated_path: str) -> Dict[str, Any]:
        """Compare two images using OpenAI's multimodal model"""
        if not os.path.exists(original_path):
            raise FileNotFoundError(f"Original image not found: {original_path}")
        if not os.path.exists(generated_path):
            raise FileNotFoundError(f"Generated image not found: {generated_path}")
        
        comparison_result = {
            'similarity_score': 0.0,
            'multimodal_analysis': "",
            'improvement_suggestions': "",
            'shape_feedback': "",
            'color_feedback': "",
            'overall_feedback': "",
            'is_blank_image': False,
            'openai_response': ""
        }
        
        try:
            # First check if generated image is blank using simple method
            with Image.open(generated_path) as img:
                blank_check = self._is_blank_image(img)
                comparison_result['is_blank_image'] = blank_check['is_blank']
                
                if blank_check['is_blank']:
                    comparison_result['similarity_score'] = 0.0
                    comparison_result['improvement_suggestions'] = (
                        f"CRITICAL: Generated image is blank ({blank_check['reason']}). "
                        "The PowerPoint to PDF conversion failed or the shape is invisible. "
                        "Fix the conversion pipeline and ensure shapes have visible colors."
                    )
                    return comparison_result
            
            # Encode both images to base64
            original_base64 = self._encode_image_to_base64(original_path)
            generated_base64 = self._encode_image_to_base64(generated_path)
            
            # Create the multimodal prompt
            prompt = self._create_comparison_prompt()
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{original_base64}",
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": f"data:image/png;base64,{generated_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse the response
            openai_response = response.choices[0].message.content
            comparison_result['openai_response'] = openai_response
            comparison_result['multimodal_analysis'] = openai_response
            
            # Parse the structured response
            parsed_feedback = self._parse_openai_response(openai_response)
            comparison_result.update(parsed_feedback)
            
            return comparison_result
            
        except Exception as e:
            print(f"OpenAI image comparison failed: {e}")
            comparison_result['error'] = str(e)
            comparison_result['improvement_suggestions'] = (
                f"OpenAI comparison failed: {e}. "
                "Check API key and network connection. "
                "Falling back to basic analysis."
            )
            return comparison_result
    
    def _create_comparison_prompt(self) -> str:
        """Create the prompt for OpenAI multimodal analysis"""
        return """You are an expert image analyst comparing two images for a PowerPoint shape generation system.

I will show you two images:
1. ORIGINAL IMAGE: A source image (could be a document, chart, diagram, etc.)
2. GENERATED IMAGE: A PowerPoint slide with a generated shape intended to represent or complement the original

Please analyze these images and provide feedback in the following format:

SIMILARITY_SCORE: [0.0 to 1.0 - how well does the generated shape match or complement the original]

SHAPE_FEEDBACK: [Specific feedback about the shape type, size, position - what should be changed?]

COLOR_FEEDBACK: [Specific feedback about colors - what colors from the original should be used?]

OVERALL_FEEDBACK: [Overall assessment and key recommendations]

IMPROVEMENT_SUGGESTIONS: [Specific, actionable suggestions for the next iteration]

Focus on:
- Does the generated shape complement the original image's content?
- Are the colors appropriate for the original image's theme?
- Is the shape type suitable for the original image's context?
- What specific changes would improve the match?

Be specific and actionable in your feedback."""

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _is_blank_image(self, img: Image.Image) -> Dict[str, Any]:
        """Quick check if image is blank (reusing from ImageComparator)"""
        try:
            img_rgb = img.convert('RGB')
            width, height = img_rgb.size
            total_pixels = width * height
            
            colors = img_rgb.getcolors(maxcolors=total_pixels)
            
            if not colors:
                return {'is_blank': True, 'reason': 'no colors detected'}
            
            # Check if completely white
            if len(colors) == 1:
                color_count, color_rgb = colors[0]
                if color_count == total_pixels:
                    r, g, b = color_rgb
                    if r > 240 and g > 240 and b > 240:
                        return {'is_blank': True, 'reason': f'completely white ({r},{g},{b})'}
            
            # Check if mostly white
            white_pixels = sum(count for count, (r, g, b) in colors 
                              if r > 240 and g > 240 and b > 240)
            white_percentage = white_pixels / total_pixels
            
            if white_percentage > 0.95:
                return {'is_blank': True, 'reason': f'{white_percentage:.1%} white pixels'}
            
            return {'is_blank': False, 'reason': 'normal image'}
            
        except Exception as e:
            return {'is_blank': True, 'reason': f'analysis failed: {e}'}
    
    def _parse_openai_response(self, response: str) -> Dict[str, Any]:
        """Parse OpenAI response to extract structured feedback"""
        result = {
            'similarity_score': 0.0,
            'shape_feedback': "",
            'color_feedback': "",
            'overall_feedback': "",
            'improvement_suggestions': ""
        }
        
        try:
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('SIMILARITY_SCORE:'):
                    score_text = line.replace('SIMILARITY_SCORE:', '').strip()
                    try:
                        result['similarity_score'] = float(score_text)
                    except ValueError:
                        result['similarity_score'] = 0.0
                        
                elif line.startswith('SHAPE_FEEDBACK:'):
                    current_section = 'shape_feedback'
                    result['shape_feedback'] = line.replace('SHAPE_FEEDBACK:', '').strip()
                    
                elif line.startswith('COLOR_FEEDBACK:'):
                    current_section = 'color_feedback'
                    result['color_feedback'] = line.replace('COLOR_FEEDBACK:', '').strip()
                    
                elif line.startswith('OVERALL_FEEDBACK:'):
                    current_section = 'overall_feedback'
                    result['overall_feedback'] = line.replace('OVERALL_FEEDBACK:', '').strip()
                    
                elif line.startswith('IMPROVEMENT_SUGGESTIONS:'):
                    current_section = 'improvement_suggestions'
                    result['improvement_suggestions'] = line.replace('IMPROVEMENT_SUGGESTIONS:', '').strip()
                    
                elif current_section and line and not line.startswith(('SIMILARITY_SCORE:', 'SHAPE_FEEDBACK:', 'COLOR_FEEDBACK:', 'OVERALL_FEEDBACK:', 'IMPROVEMENT_SUGGESTIONS:')):
                    # Continue adding to current section
                    if result[current_section]:
                        result[current_section] += ' ' + line
                    else:
                        result[current_section] = line
            
            # If no improvement suggestions parsed, use overall feedback
            if not result['improvement_suggestions'] and result['overall_feedback']:
                result['improvement_suggestions'] = result['overall_feedback']
                
        except Exception as e:
            result['improvement_suggestions'] = f"Failed to parse OpenAI response: {e}. Raw response: {response}"
        
        return result


class FeedbackLoopGenerator:
    """Orchestrates the iterative improvement process using visual feedback"""
    
    def __init__(self, template_path: str, max_iterations: int = 3, use_openai: bool = True, openai_api_key: str = None):
        self.template_path = template_path
        self.max_iterations = max_iterations
        self.ppt_converter = PowerPointConverter()
        self.pdf_converter = PDFToImageConverter()
        self.use_openai = use_openai
        
        # Choose image comparator based on availability and preference
        if use_openai and OPENAI_AVAILABLE:
            try:
                self.image_comparator = OpenAIImageComparator(api_key=openai_api_key)
                print("🤖 Using OpenAI multimodal comparison")
            except Exception as e:
                print(f"⚠️  OpenAI setup failed: {e}")
                print("🔄 Falling back to traditional image comparison")
                self.image_comparator = ImageComparator()
                self.use_openai = False
        else:
            self.image_comparator = ImageComparator()
            if use_openai:
                print("⚠️  OpenAI not available, using traditional image comparison")
        
        self.base_generator = None
    
    def generate_with_feedback(self, original_image_path: str, output_path: str, 
                             verbose: bool = False) -> str:
        """Generate shape with iterative improvement using visual feedback"""
        
        if verbose:
            print("🔄 Starting Iterative Improvement Process")
            print("=" * 60)
        
        # Initialize base generator
        self.base_generator = MultimodalChatGenerator(self.template_path)
        
        current_pptx = output_path
        best_pptx = output_path
        best_similarity = 0.0
        
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n🔄 Iteration {iteration + 1}/{self.max_iterations}")
                print("-" * 40)
            
            try:
                # Generate or regenerate shape
                if iteration == 0:
                    # First iteration: use original image analysis
                    if verbose:
                        print("📊 Analyzing original image...")
                    current_pptx = self.base_generator.generate_shape_from_image(
                        original_image_path, current_pptx, verbose=verbose
                    )
                else:
                    # Subsequent iterations: use feedback from comparison
                    if verbose:
                        print("🔄 Regenerating based on feedback...")
                    current_pptx = self._regenerate_with_feedback(
                        original_image_path, current_pptx, improvement_suggestions, verbose
                    )
                
                if verbose:
                    print(f"✅ Generated: {current_pptx}")
                
                # Convert to PDF and PNG for comparison
                if verbose:
                    print("📄 Converting to PDF...")
                pdf_path = current_pptx.replace('.pptx', '.pdf')
                
                try:
                    self.ppt_converter.convert_to_pdf(current_pptx, pdf_path)
                    if not os.path.exists(pdf_path):
                        raise RuntimeError(f"PDF conversion failed - file not created: {pdf_path}")
                    
                    file_size = os.path.getsize(pdf_path)
                    if file_size < 1000:  # Less than 1KB is likely empty
                        if verbose:
                            print(f"⚠️  Warning: PDF file is very small ({file_size} bytes) - may be empty")
                    
                    if verbose:
                        print(f"✅ PDF created: {pdf_path} ({file_size} bytes)")
                        
                except Exception as e:
                    if verbose:
                        print(f"❌ PDF conversion failed: {e}")
                    raise RuntimeError(f"PDF conversion failed: {e}")
                
                if verbose:
                    print("🖼️  Converting to PNG...")
                generated_png = current_pptx.replace('.pptx', '_generated.png')
                
                try:
                    self.pdf_converter.convert_to_png(pdf_path, generated_png)
                    if not os.path.exists(generated_png):
                        raise RuntimeError(f"PNG conversion failed - file not created: {generated_png}")
                    
                    file_size = os.path.getsize(generated_png)
                    if file_size < 1000:  # Less than 1KB is likely empty
                        if verbose:
                            print(f"⚠️  Warning: PNG file is very small ({file_size} bytes) - may be empty")
                    
                    if verbose:
                        print(f"✅ PNG created: {generated_png} ({file_size} bytes)")
                        
                except Exception as e:
                    if verbose:
                        print(f"❌ PNG conversion failed: {e}")
                    raise RuntimeError(f"PNG conversion failed: {e}")
                
                # Compare with original image
                if verbose:
                    if self.use_openai:
                        print("🤖 OpenAI multimodal analysis in progress...")
                    else:
                        print("🔍 Analyzing differences...")
                comparison_result = self.image_comparator.compare_images(
                    original_image_path, generated_png
                )
                
                # Calculate overall similarity score
                similarity = self._calculate_overall_similarity(comparison_result)
                
                if verbose:
                    print(f"📊 Similarity Score: {similarity:.2f}")
                    
                    if self.use_openai and 'multimodal_analysis' in comparison_result:
                        print("\n🤖 OpenAI MULTIMODAL ANALYSIS:")
                        print("=" * 60)
                        print(comparison_result['multimodal_analysis'])
                        print("=" * 60)
                        
                        if comparison_result.get('shape_feedback'):
                            print(f"🔺 Shape Feedback: {comparison_result['shape_feedback']}")
                        if comparison_result.get('color_feedback'):
                            print(f"🎨 Color Feedback: {comparison_result['color_feedback']}")
                        if comparison_result.get('overall_feedback'):
                            print(f"📋 Overall Feedback: {comparison_result['overall_feedback']}")
                    
                    print(f"💡 Suggestions: {comparison_result['improvement_suggestions']}")
                
                # Track best result
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_pptx = current_pptx
                    if verbose:
                        print("⭐ New best result!")
                
                # Check if we're satisfied with the result
                if similarity > 0.8:  # 80% similarity threshold
                    if verbose:
                        print("🎉 Satisfactory result achieved!")
                    break
                
                # Prepare feedback for next iteration
                improvement_suggestions = comparison_result['improvement_suggestions']
                
                # Update output path for next iteration
                if iteration < self.max_iterations - 1:
                    base_name = output_path.replace('.pptx', '')
                    current_pptx = f"{base_name}_iter{iteration + 2}.pptx"
                
            except Exception as e:
                if verbose:
                    print(f"❌ Iteration {iteration + 1} failed: {e}")
                continue
        
        if verbose:
            print(f"\n🏆 Best Result: {best_pptx} (Similarity: {best_similarity:.2f})")
        
        return best_pptx
    
    def _calculate_overall_similarity(self, comparison_result: Dict[str, Any]) -> float:
        """Calculate overall similarity score from comparison results"""
        scores = []
        
        # Structural similarity (most important)
        struct_sim = comparison_result.get('structural_similarity', 0)
        if struct_sim > 0:
            scores.append(struct_sim * 0.6)  # 60% weight
        
        # Histogram similarity
        hist_sim = comparison_result.get('histogram_similarity', 0)
        if hist_sim > 0:
            scores.append(hist_sim * 0.3)  # 30% weight
        
        # Edge similarity
        edge_sim = comparison_result.get('edge_similarity', 0)
        if edge_sim > 0:
            scores.append(edge_sim * 0.1)  # 10% weight
        
        return sum(scores) if scores else 0.0
    
    def _regenerate_with_feedback(self, original_image_path: str, output_path: str, 
                                feedback: str, verbose: bool) -> str:
        """Regenerate shape using feedback from comparison"""
        
        # Create a modified version of the image analyzer that incorporates feedback
        analyzer = ImageAnalyzer()
        original_features = analyzer.analyze_image(original_image_path)
        
        # Parse feedback to modify generation parameters
        modified_features = self._modify_features_based_on_feedback(original_features, feedback)
        
        # Use modified features to regenerate
        decider = ImageBasedShapeDecider()
        generation_params = decider.process_image_analysis(modified_features)
        
        if verbose:
            print(f"🔧 Modified parameters based on feedback:")
            print(f"   Shape: {generation_params['shape_type']}")
            print(f"   Colors: {generation_params['colors']}")
            print(f"   Reasoning: {generation_params['reasoning']}")
        
        # Generate new shape
        generator = DrawingMLGenerator()
        shape_xml = generator.generate_custom_shape(
            modified_features,
            generation_params
        )
        
        # Create new PowerPoint file
        modifier = PowerPointModifier(self.template_path)
        modifier.modify_slide1_with_shape(shape_xml, output_path, verbose=verbose)
        
        return output_path
    
    def _modify_features_based_on_feedback(self, features: Dict[str, Any], 
                                         feedback: str) -> Dict[str, Any]:
        """Modify image features based on feedback suggestions"""
        modified_features = features.copy()
        
        feedback_lower = feedback.lower()
        
        # Analyze feedback for shape type changes
        if "missing shapes" in feedback_lower or "simpler" in feedback_lower:
            # Try a more complex shape
            recommendations = modified_features.get('shape_recommendations', {})
            current_shape = recommendations.get('shape_type', 'circle')
            
            if current_shape == 'circle':
                recommendations['shape_type'] = 'organic'
            elif current_shape == 'rectangle':
                recommendations['shape_type'] = 'star'
            
            recommendations['reasoning'] = f"Feedback suggests more complexity: {feedback}"
            
        elif "extra shapes" in feedback_lower or "complex" in feedback_lower:
            # Try a simpler shape
            recommendations = modified_features.get('shape_recommendations', {})
            current_shape = recommendations.get('shape_type', 'circle')
            
            if current_shape == 'organic':
                recommendations['shape_type'] = 'circle'
            elif current_shape == 'star':
                recommendations['shape_type'] = 'rectangle'
            
            recommendations['reasoning'] = f"Feedback suggests simplification: {feedback}"
        
        # Analyze feedback for color changes
        if "missing colors" in feedback_lower:
            # Extract color names from feedback
            color_words = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'black', 'white']
            missing_colors = [color for color in color_words if color in feedback_lower]
            
            if missing_colors:
                recommendations = modified_features.get('shape_recommendations', {})
                recommendations['colors'] = missing_colors[:2]  # Take first 2 colors
        
        return modified_features


class MultimodalChatGenerator:
    """Main orchestrator for the image-based shape generation program"""
    
    def __init__(self, template_path: str = "blank.pptx"):
        self.template_path = template_path
        self.image_analyzer = ImageAnalyzer()
        self.shape_decider = ImageBasedShapeDecider()
        self.drawingml_generator = DrawingMLGenerator()
        self.powerpoint_modifier = PowerPointModifier(template_path)
    
    def generate_shape_from_image(self, image_path: str, 
                                output_path: str = "output.pptx", verbose: bool = True) -> str:
        """Generate custom shape from image analysis only, output to PPTX"""
        
        print(f"🖼️  Analyzing image: {image_path}")
        image_features = self.image_analyzer.analyze_image(image_path)
        
        if verbose:
            print("\n" + "="*60)
            print("📊 IMAGE ANALYSIS DESCRIPTION:")
            print("="*60)
            print(image_features.get('description', 'No description available'))
            print("="*60)
            
            # Show shape recommendations
            recommendations = image_features.get('shape_recommendations', {})
            if recommendations:
                print("\n🔍 SHAPE GENERATION RECOMMENDATIONS:")
                print("="*60)
                print(f"Recommended Shape: {recommendations.get('shape_type', 'N/A')}")
                print(f"Recommended Colors: {recommendations.get('colors', ['N/A'])}")
                print(f"Complexity Level: {recommendations.get('complexity', 'N/A')}")
                print(f"Reasoning: {recommendations.get('reasoning', 'N/A')}")
                print("="*60)
        
        print(f"🧠 Processing image analysis for shape generation...")
        shape_data = self.shape_decider.process_image_analysis(image_features)
        
        if verbose:
            print("\n🎯 GENERATED SHAPE PARAMETERS:")
            print("="*60)
            print(f"Shape Type: {shape_data['shape_type']}")
            print(f"Colors: {shape_data['colors']}")
            print(f"Size Hints: {shape_data['size_hints']}")
            print(f"Style Hints: {shape_data['style_hints']}")
            print(f"Complexity: {shape_data['complexity']}")
            print(f"Reasoning: {shape_data['reasoning']}")
            print("="*60)
        
        print(f"🎨 Generating custom shape...")
        shape_xml = self.drawingml_generator.generate_custom_shape(
            image_features, shape_data)
        
        print(f"📊 Modifying PowerPoint file...")
        self.powerpoint_modifier.modify_slide1_with_shape(shape_xml, output_path, verbose=verbose)
        
        print(f"✅ Generated: {output_path}")
        return output_path
    
    def generate_shape_with_feedback(self, image_path: str, output_path: str = "output.pptx", 
                                   verbose: bool = False, max_iterations: int = 3) -> str:
        """Generate shape with iterative improvement using visual feedback"""
        
        if verbose:
            print("🔄 Starting Feedback Loop Generation")
            print("This will iteratively improve the shape by comparing with the original image")
            print("=" * 80)
        
        try:
            # Initialize feedback loop generator
            feedback_generator = FeedbackLoopGenerator(
                template_path=self.template_path,
                max_iterations=max_iterations
            )
            
            # Generate with feedback
            result = feedback_generator.generate_with_feedback(
                original_image_path=image_path,
                output_path=output_path,
                verbose=verbose
            )
            
            if verbose:
                print("\n" + "=" * 80)
                print("🎉 Feedback Loop Generation Complete!")
                print(f"📁 Final Result: {result}")
            
            return result
            
        except Exception as e:
            error_msg = f"Feedback loop generation failed: {e}"
            if verbose:
                print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def interactive_chat(self):
        """Run interactive chat interface"""
        print("🎯 Image-Based Shape Generator")
        print("Enter image path to automatically generate custom shapes in PowerPoint based on image analysis")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                # Get image path
                image_path = input("📁 Image path: ").strip()
                if image_path.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not image_path:
                    print("❌ Please provide an image path")
                    continue
                
                # Generate output filename
                base_name = Path(image_path).stem
                output_path = f"{base_name}_generated.pptx"
                
                # Generate shape
                result = self.generate_shape_from_image(image_path, output_path)
                print(f"🎉 Success! Created: {result}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Image-Based Shape Generation Program for PowerPoint")
    
    parser.add_argument("--image", "-i", help="Path to input image")
    parser.add_argument("--output", "-o", default="output.pptx", 
                       help="Output PPTX file path")
    parser.add_argument("--template", "-t", default="blank.pptx",
                       help="Template PPTX file path")
    parser.add_argument("--interactive", "-I", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed console logs and XML output")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Minimal output mode")
    parser.add_argument("--feedback", "-f", action="store_true",
                       help="Enable iterative improvement using visual feedback")
    parser.add_argument("--max-iterations", "-m", type=int, default=3,
                       help="Maximum iterations for feedback loop (default: 3)")
    
    args = parser.parse_args()
    
    try:
        generator = MultimodalChatGenerator(args.template)
        
        # Determine verbosity
        verbose = args.verbose and not args.quiet
        
        if args.interactive:
            generator.interactive_chat()
        elif args.image:
            if args.feedback:
                generator.generate_shape_with_feedback(
                    args.image, args.output, verbose=verbose, max_iterations=args.max_iterations
                )
            else:
                generator.generate_shape_from_image(args.image, args.output, verbose=verbose)
        else:
            print("Usage: Either provide --image, or use --interactive mode")
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()