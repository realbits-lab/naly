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
        
        # Determine primary color from dominant colors
        dominant_colors = features.get('dominant_colors', [(128, 128, 128)])
        if dominant_colors:
            primary_color = self._rgb_to_color_name(dominant_colors[0])
            recommendations['colors'] = [primary_color]
        
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


class MultimodalChatGenerator:
    """Main orchestrator for the image-based shape generation program"""
    
    def __init__(self, template_path: str = "blank.pptx"):
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
    
    args = parser.parse_args()
    
    try:
        generator = MultimodalChatGenerator(args.template)
        
        # Determine verbosity
        verbose = args.verbose and not args.quiet
        
        if args.interactive:
            generator.interactive_chat()
        elif args.image:
            generator.generate_shape_from_image(args.image, args.output, verbose=verbose)
        else:
            print("Usage: Either provide --image, or use --interactive mode")
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()