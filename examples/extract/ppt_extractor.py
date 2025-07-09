#!/usr/bin/env python3

import sys
import json
import argparse
import base64
import zipfile
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from pptx import Presentation
from pptx.shapes.base import BaseShape
from pptx.slide import Slide, SlideLayout
from typing import Dict, List, Any, Optional


class PPTExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.presentation = Presentation(file_path)
        self.media_files = {}
        self.document_properties = {}
        self.relationships = {}

    def extract_fill_properties(self, fill) -> Dict[str, Any]:
        """Extract detailed fill properties including colors, gradients, and patterns"""
        fill_info = {
            'type': str(fill.type) if fill.type else None
        }

        try:
            from pptx.enum.dml import MSO_FILL_TYPE, MSO_COLOR_TYPE

            if fill.type == MSO_FILL_TYPE.SOLID:
                fill_info['solid'] = True
                color_info = self.extract_color_properties(fill.fore_color)
                fill_info['fore_color'] = color_info

            elif fill.type == MSO_FILL_TYPE.PATTERN:
                fill_info['pattern'] = True
                fill_info['fore_color'] = self.extract_color_properties(
                    fill.fore_color)
                fill_info['back_color'] = self.extract_color_properties(
                    fill.back_color)
                # Extract pattern type if available
                if hasattr(fill, 'pattern'):
                    fill_info['pattern_type'] = str(fill.pattern)

            elif fill.type == MSO_FILL_TYPE.GRADIENT:
                fill_info['gradient'] = True
                # Extract gradient stops and direction
                gradient_info = self.extract_gradient_properties(fill)
                fill_info.update(gradient_info)

            elif fill.type == MSO_FILL_TYPE.PICTURE:
                fill_info['picture'] = True
                # Extract picture fill information
                picture_info = self.extract_picture_fill_properties(fill)
                fill_info.update(picture_info)

            elif fill.type == MSO_FILL_TYPE.BACKGROUND:
                fill_info['background'] = True

        except Exception as e:
            fill_info['error'] = f"Could not extract fill properties: {str(e)}"

        return fill_info

    def extract_gradient_properties(self, fill) -> Dict[str, Any]:
        """Extract gradient fill properties"""
        gradient_info = {}

        try:
            # Extract gradient stops
            if hasattr(fill, 'gradient_stops'):
                stops = []
                for stop in fill.gradient_stops:
                    stop_info = {
                        'position': stop.position if hasattr(stop, 'position') else None,
                        'color': self.extract_color_properties(stop.color) if hasattr(stop, 'color') else None
                    }
                    stops.append(stop_info)
                gradient_info['gradient_stops'] = stops

            # Extract gradient angle and direction
            if hasattr(fill, 'gradient_angle'):
                gradient_info['gradient_angle'] = fill.gradient_angle

        except Exception as e:
            gradient_info[
                'gradient_error'] = f"Could not extract gradient properties: {str(e)}"

        return gradient_info

    def extract_picture_fill_properties(self, fill) -> Dict[str, Any]:
        """Extract picture fill properties"""
        picture_info = {}

        try:
            # Extract picture data if available
            if hasattr(fill, 'picture'):
                picture = fill.picture
                if hasattr(picture, 'image'):
                    image_info = {
                        'filename': picture.image.filename if hasattr(picture.image, 'filename') else None,
                        'content_type': picture.image.content_type if hasattr(picture.image, 'content_type') else None,
                        'size': len(picture.image.blob) if hasattr(picture.image, 'blob') else None
                    }
                    picture_info['image'] = image_info

                    # Store image data for media extraction
                    if hasattr(picture.image, 'blob') and hasattr(picture.image, 'filename'):
                        self.media_files[picture.image.filename] = {
                            'data': base64.b64encode(picture.image.blob).decode('utf-8'),
                            'content_type': picture.image.content_type
                        }

        except Exception as e:
            picture_info[
                'picture_error'] = f"Could not extract picture properties: {str(e)}"

        return picture_info

    def extract_color_properties(self, color) -> Dict[str, Any]:
        """Extract color properties including RGB values, theme colors, and adjustments"""
        color_info = {
            'type': str(color.type) if hasattr(color, 'type') and color.type else None
        }

        try:
            from pptx.enum.dml import MSO_COLOR_TYPE

            if hasattr(color, 'type') and color.type == MSO_COLOR_TYPE.RGB:
                if hasattr(color, 'rgb') and color.rgb:
                    rgb = color.rgb
                    color_info['rgb'] = {
                        'hex': str(rgb),
                        'red': rgb.red if hasattr(rgb, 'red') else None,
                        'green': rgb.green if hasattr(rgb, 'green') else None,
                        'blue': rgb.blue if hasattr(rgb, 'blue') else None
                    }

            elif hasattr(color, 'type') and color.type == MSO_COLOR_TYPE.SCHEME:
                if hasattr(color, 'theme_color'):
                    color_info['theme_color'] = str(color.theme_color)

            # Extract brightness and tint if available
            if hasattr(color, 'brightness') and color.brightness is not None:
                color_info['brightness'] = color.brightness

            if hasattr(color, 'tint_and_shade') and color.tint_and_shade is not None:
                color_info['tint_and_shade'] = color.tint_and_shade

        except Exception as e:
            color_info['error'] = f"Could not extract color properties: {str(e)}"

        return color_info

    def extract_line_properties(self, line) -> Dict[str, Any]:
        """Extract line/border properties"""
        line_info = {}

        try:
            # Line width
            if hasattr(line, 'width') and line.width is not None:
                line_info['width'] = line.width

            # Line color
            if hasattr(line, 'color'):
                color_info = self.extract_color_properties(line.color)
                line_info['color'] = color_info

            # Line fill (for compound lines)
            if hasattr(line, 'fill'):
                fill_info = self.extract_fill_properties(line.fill)
                line_info['fill'] = fill_info

        except Exception as e:
            line_info['error'] = f"Could not extract line properties: {str(e)}"

        return line_info

    def _safe_get_auto_shape_type(self, shape) -> str:
        """Safely get auto shape type string"""
        try:
            if hasattr(shape, 'auto_shape_type'):
                return str(shape.auto_shape_type)
        except Exception:
            pass
        return None

    def get_auto_shape_type(self, shape) -> str:
        """Extract the specific auto shape type for MSO_SHAPE_TYPE.AUTO_SHAPE"""
        try:
            from pptx.enum.shapes import MSO_SHAPE_TYPE

            if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                # Try to get the auto shape type from the shape element
                if hasattr(shape, '_element') and hasattr(shape._element, 'prstGeom'):
                    prst_geom = shape._element.prstGeom
                    if hasattr(prst_geom, 'prst') and prst_geom.prst:
                        # Map internal geometry names to MSO_SHAPE names
                        geom_name = prst_geom.prst
                        return self.map_geometry_to_shape_name(geom_name)

                # If we can't determine the specific type, try to get it from shape properties
                if hasattr(shape, 'auto_shape_type'):
                    try:
                        return str(shape.auto_shape_type)
                    except Exception:
                        pass

                # Fallback: return the generic AUTO_SHAPE with number
                return f"AUTO_SHAPE ({shape.shape_type.value})"
            else:
                # For non-auto shapes, return the shape type with number (avoid duplication)
                shape_name = str(shape.shape_type).split('.')[-1]
                return f"{shape_name} ({shape.shape_type.value})"

        except Exception:
            # Fallback to original behavior
            return str(shape.shape_type)

    def map_geometry_to_shape_name(self, geom_name: str) -> str:
        """Map internal PowerPoint geometry names to MSO_SHAPE names"""
        # Mapping from internal geometry names to MSO_SHAPE constants
        geometry_mapping = {
            'rect': 'RECTANGLE',
            'roundRect': 'ROUNDED_RECTANGLE',
            'ellipse': 'OVAL',
            'triangle': 'ISOSCELES_TRIANGLE',
            'rtTriangle': 'RIGHT_TRIANGLE',
            'parallelogram': 'PARALLELOGRAM',
            'trapezoid': 'TRAPEZOID',
            'diamond': 'DIAMOND',
            'pentagon': 'PENTAGON',
            'hexagon': 'HEXAGON',
            'heptagon': 'HEPTAGON',
            'octagon': 'OCTAGON',
            'decagon': 'DECAGON',
            'dodecagon': 'DODECAGON',
            'pie': 'PIE',
            'chord': 'CHORD',
            'teardrop': 'TEAR',
            'frame': 'FRAME',
            'halfFrame': 'HALF_FRAME',
            'corner': 'CORNER',
            'diagStripe': 'DIAGONAL_STRIPE',
            'plus': 'CROSS',
            'plaque': 'PLAQUE',
            'can': 'CAN',
            'cube': 'CUBE',
            'bevel': 'BEVEL',
            'donut': 'DONUT',
            'noSmoking': 'NO_SYMBOL',
            'blockArc': 'BLOCK_ARC',
            'foldedCorner': 'FOLDED_CORNER',
            'smileyFace': 'SMILEY_FACE',
            'heart': 'HEART',
            'lightningBolt': 'LIGHTNING_BOLT',
            'sun': 'SUN',
            'moon': 'MOON',
            'arc': 'ARC',
            'bracketPair': 'DOUBLE_BRACKET',
            'bracePair': 'DOUBLE_BRACE',
            'leftBracket': 'LEFT_BRACKET',
            'rightBracket': 'RIGHT_BRACKET',
            'leftBrace': 'LEFT_BRACE',
            'rightBrace': 'RIGHT_BRACE',
            'rightArrow': 'RIGHT_ARROW',
            'leftArrow': 'LEFT_ARROW',
            'upArrow': 'UP_ARROW',
            'downArrow': 'DOWN_ARROW',
            'leftRightArrow': 'LEFT_RIGHT_ARROW',
            'upDownArrow': 'UP_DOWN_ARROW',
            'quadArrow': 'QUAD_ARROW',
            'leftRightUpArrow': 'LEFT_RIGHT_UP_ARROW',
            'bentArrow': 'BENT_ARROW',
            'uturnArrow': 'U_TURN_ARROW',
            'leftUpArrow': 'LEFT_UP_ARROW',
            'bentUpArrow': 'BENT_UP_ARROW',
            'curvedRightArrow': 'CURVED_RIGHT_ARROW',
            'curvedLeftArrow': 'CURVED_LEFT_ARROW',
            'curvedUpArrow': 'CURVED_UP_ARROW',
            'curvedDownArrow': 'CURVED_DOWN_ARROW',
            'stripedRightArrow': 'STRIPED_RIGHT_ARROW',
            'notchedRightArrow': 'NOTCHED_RIGHT_ARROW',
            'circularArrow': 'CIRCULAR_ARROW',
            'swooshArrow': 'SWOOSH_ARROW',
            'star4': 'STAR_4_POINT',
            'star5': 'STAR_5_POINT',
            'star6': 'STAR_6_POINT',
            'star7': 'STAR_7_POINT',
            'star8': 'STAR_8_POINT',
            'star10': 'STAR_10_POINT',
            'star12': 'STAR_12_POINT',
            'star16': 'STAR_16_POINT',
            'star24': 'STAR_24_POINT',
            'star32': 'STAR_32_POINT',
            'ribbon2': 'UP_RIBBON',
            'ribbon': 'DOWN_RIBBON',
            'ellipseRibbon2': 'CURVED_UP_RIBBON',
            'ellipseRibbon': 'CURVED_DOWN_RIBBON',
            'verticalScroll': 'VERTICAL_SCROLL',
            'horizontalScroll': 'HORIZONTAL_SCROLL',
            'wave': 'WAVE',
            'doubleWave': 'DOUBLE_WAVE',
            'gear6': 'GEAR_6',
            'gear9': 'GEAR_9',
            'funnel': 'FUNNEL',
            'mathPlus': 'MATH_PLUS',
            'mathMinus': 'MATH_MINUS',
            'mathMultiply': 'MATH_MULTIPLY',
            'mathDivide': 'MATH_DIVIDE',
            'mathEqual': 'MATH_EQUAL',
            'mathNotEqual': 'MATH_NOT_EQUAL',
            'homePlate': 'PENTAGON',
            'chevron': 'CHEVRON',
            'pieWedge': 'PIE_WEDGE',
            'irregularSeal1': 'EXPLOSION1',
            'irregularSeal2': 'EXPLOSION2',
            'cloud': 'CLOUD',
            'cloudCallout': 'CLOUD_CALLOUT',
            'callout1': 'RECTANGULAR_CALLOUT',
            'callout2': 'ROUNDED_RECTANGULAR_CALLOUT',
            'callout3': 'OVAL_CALLOUT',
            'wedgeEllipseCallout': 'OVAL_CALLOUT',
            'wedgeRectCallout': 'RECTANGULAR_CALLOUT',
            'wedgeRRectCallout': 'ROUNDED_RECTANGULAR_CALLOUT',
            'borderCallout1': 'LINE_CALLOUT_1',
            'borderCallout2': 'LINE_CALLOUT_2',
            'borderCallout3': 'LINE_CALLOUT_3',
            'accentCallout1': 'LINE_CALLOUT_1_ACCENT_BAR',
            'accentCallout2': 'LINE_CALLOUT_2_ACCENT_BAR',
            'accentCallout3': 'LINE_CALLOUT_3_ACCENT_BAR',
            'callout90': 'LINE_CALLOUT_4',
            'accentCallout90': 'LINE_CALLOUT_4_ACCENT_BAR',
            'borderCallout90': 'LINE_CALLOUT_4_BORDER_AND_ACCENT_BAR',
        }

        return geometry_mapping.get(geom_name, geom_name.upper())

    def get_shape_type_enum_name(self, shape_type_value: int) -> str:
        """Convert MSO_SHAPE_TYPE enum value to consistent name format"""
        # Map MSO_SHAPE_TYPE enum values to their names
        shape_type_names = {
            -2: 'MIXED',
            1: 'AUTO_SHAPE',
            2: 'CALLOUT',
            3: 'CHART',
            4: 'COMMENT',
            5: 'FREEFORM',
            6: 'GROUP',
            7: 'EMBEDDED_OLE_OBJECT',
            8: 'FORM_CONTROL',
            9: 'LINE',
            10: 'LINKED_OLE_OBJECT',
            11: 'LINKED_PICTURE',
            12: 'OLE_CONTROL_OBJECT',
            13: 'PICTURE',
            14: 'PLACEHOLDER',
            15: 'TEXT_EFFECT',
            16: 'MEDIA',
            17: 'TEXT_BOX',
            18: 'SCRIPT_ANCHOR',
            19: 'TABLE',
            20: 'CANVAS',
            21: 'DIAGRAM',
            22: 'INK',
            23: 'INK_COMMENT',
            24: 'IGX_GRAPHIC',
            26: 'WEB_VIDEO',
            27: 'CONTENT_APP',
            28: 'GRAPHIC',
            29: 'LINKED_GRAPHIC',
            30: '3D_MODEL',
            31: 'LINKED_3D_MODEL',
        }

        return shape_type_names.get(shape_type_value, f'UNKNOWN_{shape_type_value}')

    def extract_chart_data(self, chart) -> Dict[str, Any]:
        """Extract chart data and properties"""
        chart_info = {
            'chart_type': str(chart.chart_type) if hasattr(chart, 'chart_type') else None,
            'has_title': hasattr(chart, 'chart_title') and chart.chart_title.has_text_frame,
            'title': chart.chart_title.text_frame.text if hasattr(chart, 'chart_title') and chart.chart_title.has_text_frame else None,
            'categories': [],
            'series': [],
            'has_legend': hasattr(chart, 'has_legend') and chart.has_legend
        }

        try:
            # Extract categories
            if hasattr(chart, 'plots') and chart.plots:
                plot = chart.plots[0]
                if hasattr(plot, 'categories') and plot.categories:
                    chart_info['categories'] = [cat for cat in plot.categories]

                # Extract series data
                if hasattr(plot, 'series'):
                    for series in plot.series:
                        series_info = {
                            'name': series.name if hasattr(series, 'name') else None,
                            'values': [val for val in series.values] if hasattr(series, 'values') else []
                        }
                        chart_info['series'].append(series_info)

        except Exception as e:
            chart_info['error'] = f"Could not extract chart data: {str(e)}"

        return chart_info

    def extract_table_data(self, table) -> Dict[str, Any]:
        """Extract table data and properties"""
        table_info = {
            'rows': table.rows.__len__() if hasattr(table, 'rows') else 0,
            'columns': table.columns.__len__() if hasattr(table, 'columns') else 0,
            'data': []
        }

        try:
            # Extract table cell data
            for row_idx, row in enumerate(table.rows):
                row_data = []
                for col_idx, cell in enumerate(row.cells):
                    cell_text = cell.text if hasattr(cell, 'text') else ''
                    row_data.append(cell_text)
                table_info['data'].append(row_data)

        except Exception as e:
            table_info['error'] = f"Could not extract table data: {str(e)}"

        return table_info

    def _safe_extract_placeholder_info(self, shape) -> Dict[str, Any]:
        """Safely extract placeholder information"""
        try:
            return self.extract_placeholder_info(shape)
        except Exception as e:
            return {'error': f"Could not extract placeholder info: {str(e)}"}

    def extract_placeholder_info(self, shape) -> Dict[str, Any]:
        """Extract placeholder-specific information"""
        placeholder_info = {}

        try:
            if hasattr(shape, 'placeholder_format') and shape.placeholder_format:
                placeholder_info['placeholder_type'] = str(
                    shape.placeholder_format.type)
                placeholder_info['placeholder_idx'] = shape.placeholder_format.idx if hasattr(
                    shape.placeholder_format, 'idx') else None

        except Exception as e:
            placeholder_info['error'] = f"Could not extract placeholder info: {str(e)}"

        return placeholder_info

    def extract_text_formatting(self, text_frame) -> Dict[str, Any]:
        """Extract comprehensive text formatting information"""
        text_info = {
            'margin_left': text_frame.margin_left if hasattr(text_frame, 'margin_left') else None,
            'margin_right': text_frame.margin_right if hasattr(text_frame, 'margin_right') else None,
            'margin_top': text_frame.margin_top if hasattr(text_frame, 'margin_top') else None,
            'margin_bottom': text_frame.margin_bottom if hasattr(text_frame, 'margin_bottom') else None,
            'word_wrap': text_frame.word_wrap if hasattr(text_frame, 'word_wrap') else None,
            'auto_size': str(text_frame.auto_size) if hasattr(text_frame, 'auto_size') else None,
            'vertical_anchor': str(text_frame.vertical_anchor) if hasattr(text_frame, 'vertical_anchor') else None,
            'paragraphs': []
        }

        try:
            # Extract paragraph-level formatting
            for para_idx, paragraph in enumerate(text_frame.paragraphs):
                para_info = {
                    'text': paragraph.text,
                    'alignment': str(paragraph.alignment) if hasattr(paragraph, 'alignment') and paragraph.alignment else None,
                    'level': paragraph.level if hasattr(paragraph, 'level') else None,
                    'space_before': paragraph.space_before if hasattr(paragraph, 'space_before') else None,
                    'space_after': paragraph.space_after if hasattr(paragraph, 'space_after') else None,
                    'line_spacing': paragraph.line_spacing if hasattr(paragraph, 'line_spacing') else None,
                    'runs': []
                }

                # Extract run-level formatting
                for run_idx, run in enumerate(paragraph.runs):
                    run_info = {
                        'text': run.text,
                        'font_name': run.font.name if hasattr(run.font, 'name') and run.font.name else None,
                        'font_size': run.font.size if hasattr(run.font, 'size') and run.font.size else None,
                        'bold': run.font.bold if hasattr(run.font, 'bold') else None,
                        'italic': run.font.italic if hasattr(run.font, 'italic') else None,
                        'underline': str(run.font.underline) if hasattr(run.font, 'underline') and run.font.underline else None,
                        'color': self.extract_color_properties(run.font.color) if hasattr(run.font, 'color') else None
                    }
                    para_info['runs'].append(run_info)

                text_info['paragraphs'].append(para_info)

        except Exception as e:
            text_info['error'] = f"Could not extract text formatting: {str(e)}"

        return text_info

    def extract_media_files(self) -> Dict[str, Any]:
        """Extract media files from the PowerPoint presentation"""
        media_info = {
            'images': {},
            'audio': {},
            'video': {},
            'embedded_objects': {}
        }

        try:
            # Extract media from ZIP structure
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.filename.startswith('ppt/media/'):
                        media_data = zip_ref.read(file_info.filename)
                        file_ext = Path(file_info.filename).suffix.lower()

                        media_entry = {
                            'filename': file_info.filename,
                            'size': len(media_data),
                            'data': base64.b64encode(media_data).decode('utf-8')
                        }

                        # Categorize by file type
                        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                            media_info['images'][file_info.filename] = media_entry
                        elif file_ext in ['.mp3', '.wav', '.wma', '.m4a', '.aac']:
                            media_info['audio'][file_info.filename] = media_entry
                        elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                            media_info['video'][file_info.filename] = media_entry
                        else:
                            media_info['embedded_objects'][file_info.filename] = media_entry

        except Exception as e:
            media_info['error'] = f"Could not extract media files: {str(e)}"

        return media_info

    def extract_document_properties(self) -> Dict[str, Any]:
        """Extract document properties and metadata"""
        doc_props = {}

        try:
            # Extract core properties
            if hasattr(self.presentation, 'core_properties'):
                core_props = self.presentation.core_properties
                doc_props['core_properties'] = {
                    'title': core_props.title if hasattr(core_props, 'title') else None,
                    'author': core_props.author if hasattr(core_props, 'author') else None,
                    'subject': core_props.subject if hasattr(core_props, 'subject') else None,
                    'keywords': core_props.keywords if hasattr(core_props, 'keywords') else None,
                    'comments': core_props.comments if hasattr(core_props, 'comments') else None,
                    'category': core_props.category if hasattr(core_props, 'category') else None,
                    'created': str(core_props.created) if hasattr(core_props, 'created') and core_props.created else None,
                    'modified': str(core_props.modified) if hasattr(core_props, 'modified') and core_props.modified else None,
                    'last_modified_by': core_props.last_modified_by if hasattr(core_props, 'last_modified_by') else None,
                    'revision': core_props.revision if hasattr(core_props, 'revision') else None,
                    'version': core_props.version if hasattr(core_props, 'version') else None
                }

            # Extract slide size and orientation
            if hasattr(self.presentation, 'slide_width') and hasattr(self.presentation, 'slide_height'):
                doc_props['slide_size'] = {
                    'width': self.presentation.slide_width,
                    'height': self.presentation.slide_height
                }

        except Exception as e:
            doc_props['error'] = f"Could not extract document properties: {str(e)}"

        return doc_props

    def extract_shadow_properties(self, shadow) -> Dict[str, Any]:
        """Extract shadow properties"""
        shadow_info = {}

        try:
            if hasattr(shadow, 'inherit'):
                shadow_info['inherit'] = shadow.inherit
            if hasattr(shadow, 'visible'):
                shadow_info['visible'] = shadow.visible
            if hasattr(shadow, 'style'):
                shadow_info['style'] = str(shadow.style)
            if hasattr(shadow, 'blur_radius'):
                shadow_info['blur_radius'] = shadow.blur_radius
            if hasattr(shadow, 'distance'):
                shadow_info['distance'] = shadow.distance
            if hasattr(shadow, 'direction'):
                shadow_info['direction'] = shadow.direction

        except Exception as e:
            shadow_info['error'] = f"Could not extract shadow properties: {str(e)}"

        return shadow_info

    def extract_3d_properties(self, three_d) -> Dict[str, Any]:
        """Extract 3D properties"""
        three_d_info = {}

        try:
            if hasattr(three_d, 'bevel_top'):
                three_d_info['bevel_top'] = str(three_d.bevel_top)
            if hasattr(three_d, 'bevel_bottom'):
                three_d_info['bevel_bottom'] = str(three_d.bevel_bottom)
            if hasattr(three_d, 'extrusion_height'):
                three_d_info['extrusion_height'] = three_d.extrusion_height
            if hasattr(three_d, 'extrusion_color'):
                three_d_info['extrusion_color'] = self.extract_color_properties(
                    three_d.extrusion_color)

        except Exception as e:
            three_d_info['error'] = f"Could not extract 3D properties: {str(e)}"

        return three_d_info

    def extract_image_properties(self, image) -> Dict[str, Any]:
        """Extract image properties for picture shapes"""
        image_info = {}

        try:
            if hasattr(image, 'filename'):
                image_info['filename'] = image.filename
            if hasattr(image, 'content_type'):
                image_info['content_type'] = image.content_type
            if hasattr(image, 'blob'):
                image_info['size'] = len(image.blob)
                # Store image data for media extraction
                filename = image.filename if hasattr(
                    image, 'filename') else f"image_{len(self.media_files)}"
                self.media_files[filename] = {
                    'data': base64.b64encode(image.blob).decode('utf-8'),
                    'content_type': image.content_type if hasattr(image, 'content_type') else 'image/unknown'
                }
                image_info['media_key'] = filename

        except Exception as e:
            image_info['error'] = f"Could not extract image properties: {str(e)}"

        return image_info

    def extract_shapes(self) -> List[Dict[str, Any]]:
        """Extract shape information from all slides"""
        shapes_data = []

        from pptx.enum.shapes import MSO_SHAPE_TYPE

        for slide_idx, slide in enumerate(self.presentation.slides):
            # Print all attributes of slide
            print(f"Slide {slide_idx} attributes:")
            for attr in dir(slide):
                print(f"attr: {attr}")

            slide_shapes = []

            for shape_idx, shape in enumerate(slide.shapes):
                shape_info = {
                    'slide_index': slide_idx,
                    'shape_index': shape_idx,
                    'shape_id': shape.shape_id if hasattr(shape, 'shape_id') else None,
                    'name': shape.name if hasattr(shape, 'name') else None,
                    'shape_type': self.get_auto_shape_type(shape),
                    'left': shape.left if hasattr(shape, 'left') else None,
                    'top': shape.top if hasattr(shape, 'top') else None,
                    'width': shape.width if hasattr(shape, 'width') else None,
                    'height': shape.height if hasattr(shape, 'height') else None,
                    'adjustments': list(shape.adjustments) if hasattr(shape, 'adjustments') and shape.adjustments else None,
                    'auto_shape_type': self._safe_get_auto_shape_type(shape),
                    'click_action': str(shape.click_action) if hasattr(shape, 'click_action') and shape.click_action else None,
                    'element': self.extract_element_attributes(shape.element) if hasattr(shape, 'element') else None,
                    'fill': self.extract_fill_properties(shape.fill) if hasattr(shape, 'fill') else None,
                    'get_or_add_ln': str(shape.get_or_add_ln) if hasattr(shape, 'get_or_add_ln') else None,
                    'has_chart': shape.has_chart if hasattr(shape, 'has_chart') else None,
                    'has_table': shape.has_table if hasattr(shape, 'has_table') else None,
                    'has_text_frame': shape.has_text_frame if hasattr(shape, 'has_text_frame') else None,
                    'is_placeholder': shape.is_placeholder if hasattr(shape, 'is_placeholder') else None,
                    'line': self.extract_line_properties(shape.line) if hasattr(shape, 'line') else None,
                    'ln': str(shape.ln) if hasattr(shape, 'ln') else None,
                    'part': str(shape.part) if hasattr(shape, 'part') else None,
                    'placeholder_format': self._safe_extract_placeholder_info(shape),
                    'rotation': shape.rotation if hasattr(shape, 'rotation') else None,
                    'shadow': self.extract_shadow_properties(shape.shadow) if hasattr(shape, 'shadow') else None,
                    'text': shape.text if hasattr(shape, 'text') else None,
                    'text_frame': self.extract_text_formatting(shape.text_frame) if hasattr(shape, 'text_frame') and shape.text_frame else None,
                }

                # Extract chart data for chart shapes
                if shape.shape_type == MSO_SHAPE_TYPE.CHART:
                    if hasattr(shape, 'chart'):
                        shape_info['chart_data'] = self.extract_chart_data(
                            shape.chart)

                # Extract table data for table shapes
                elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                    if hasattr(shape, 'table'):
                        shape_info['table_data'] = self.extract_table_data(
                            shape.table)

                # Extract image properties for picture shapes
                elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    if hasattr(shape, 'image'):
                        shape_info['image_properties'] = self.extract_image_properties(
                            shape.image)

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
        """Extract comprehensive theme information from the presentation"""
        theme_data = {
            'slide_master': {},
            'color_scheme': {},
            'font_scheme': {},
            'theme_name': 'Default Theme',
            'slide_masters': [],
            'layout_masters': []
        }

        # Extract slide master information
        slide_master = self.presentation.slide_master
        master_info = {
            'name': slide_master.name if hasattr(slide_master, 'name') else 'Unknown',
            'width': slide_master.width if hasattr(slide_master, 'width') else None,
            'height': slide_master.height if hasattr(slide_master, 'height') else None,
            'background': self.extract_background_properties(slide_master.background) if hasattr(slide_master, 'background') else None,
            'placeholders': []
        }

        # Extract master placeholders
        try:
            for placeholder in slide_master.placeholders:
                placeholder_info = {
                    'placeholder_type': str(placeholder.placeholder_format.type) if hasattr(placeholder, 'placeholder_format') else None,
                    'name': placeholder.name if hasattr(placeholder, 'name') else None,
                    'left': placeholder.left if hasattr(placeholder, 'left') else None,
                    'top': placeholder.top if hasattr(placeholder, 'top') else None,
                    'width': placeholder.width if hasattr(placeholder, 'width') else None,
                    'height': placeholder.height if hasattr(placeholder, 'height') else None,
                }
                master_info['placeholders'].append(placeholder_info)
        except Exception as e:
            master_info['placeholders_error'] = f"Could not extract placeholders: {str(e)}"

        theme_data['slide_master'] = master_info

        # Extract theme colors with proper mapping
        try:
            theme_part = self.presentation.part.theme_part
            if theme_part:
                theme_data['theme_name'] = theme_part.name if hasattr(
                    theme_part, 'name') else 'Default Theme'
        except:
            theme_data['theme_name'] = 'Default Theme'

        # Extract comprehensive color scheme information
        try:
            color_scheme = slide_master.theme.color_scheme
            theme_colors = {}

            # Define theme color names for better mapping
            color_names = [
                'lt1', 'dk1', 'lt2', 'dk2', 'accent1', 'accent2',
                'accent3', 'accent4', 'accent5', 'accent6', 'hlink', 'folHlink'
            ]

            for i, color in enumerate(color_scheme):
                color_name = color_names[i] if i < len(
                    color_names) else f'color_{i}'
                theme_colors[color_name] = {
                    'rgb': str(color.rgb) if hasattr(color, 'rgb') and color.rgb else None,
                    'type': str(color.color_type) if hasattr(color, 'color_type') else None
                }
            theme_data['color_scheme'] = theme_colors
        except Exception as e:
            theme_data['color_scheme'] = {
                'error': f'Could not extract color scheme: {str(e)}'}

        # Extract comprehensive font scheme information
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
        except Exception as e:
            theme_data['font_scheme'] = {
                'error': f'Could not extract font scheme: {str(e)}'}

        # Extract effect scheme if available
        try:
            if hasattr(slide_master.theme, 'effect_scheme'):
                theme_data['effect_scheme'] = str(
                    slide_master.theme.effect_scheme)
        except Exception as e:
            theme_data['effect_scheme'] = {
                'error': f'Could not extract effect scheme: {str(e)}'}

        return theme_data

    def extract_background_properties(self, background) -> Dict[str, Any]:
        """Extract background properties from slide master or slide"""
        bg_info = {}

        try:
            if hasattr(background, 'fill') and background.fill:
                bg_info['fill'] = self.extract_fill_properties(background.fill)
            if hasattr(background, 'graphics'):
                bg_info['has_graphics'] = True

        except Exception as e:
            bg_info['error'] = f"Could not extract background properties: {str(e)}"

        return bg_info

    def extract_element_attributes(self, element) -> Dict[str, Any]:
        """Extract all attributes from a shape element"""
        element_info = {
            'tag': element.tag if hasattr(element, 'tag') else None,
            'text': element.text if hasattr(element, 'text') else None,
            'tail': element.tail if hasattr(element, 'tail') else None,
            'attributes': {},
            'children': [],
            'namespace': None
        }

        try:
            # Extract all attributes
            if hasattr(element, 'attrib'):
                element_info['attributes'] = dict(element.attrib)
            
            # Extract namespace info
            if hasattr(element, 'nsmap'):
                element_info['namespace'] = element.nsmap
            
            # Extract children elements (non-recursive to avoid deep nesting)
            if hasattr(element, '__iter__'):
                for child in element:
                    child_info = {
                        'tag': child.tag if hasattr(child, 'tag') else None,
                        'text': child.text if hasattr(child, 'text') else None,
                        'attributes': dict(child.attrib) if hasattr(child, 'attrib') else {},
                        'children_count': len(list(child)) if hasattr(child, '__iter__') else 0
                    }
                    element_info['children'].append(child_info)
            
            # Extract XML string representation
            try:
                import xml.etree.ElementTree as ET
                element_info['xml_string'] = ET.tostring(element, encoding='unicode') if element is not None else None
            except Exception:
                element_info['xml_string'] = str(element) if element is not None else None

        except Exception as e:
            element_info['extraction_error'] = f"Could not extract element attributes: {str(e)}"

        return element_info

    def save_to_json(self, data: Any, output_file: str):
        """Save data to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced PowerPoint extractor with comprehensive shape, layout, theme, media, and formatting extraction')
    parser.add_argument(
        'input_file', help='Path to the PowerPoint file (.ppt or .pptx)')
    parser.add_argument('--output-dir', default='.',
                        help='Output directory for JSON files (default: current directory)')
    parser.add_argument('--extract-media', action='store_true',
                        help='Extract and embed media files as base64 data')
    parser.add_argument('--detailed-text', action='store_true',
                        help='Extract detailed text formatting information')
    parser.add_argument('--include-properties', action='store_true',
                        help='Extract document properties and metadata')

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File '{args.input_file}' does not exist.")
        sys.exit(1)

    if not input_path.suffix.lower() in ['.ppt', '.pptx']:
        print(
            f"Error: File '{args.input_file}' is not a PowerPoint file (.ppt or .pptx).")
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

        # Extract media files
        print("Extracting media files...")
        media_data = extractor.extract_media_files()
        media_output = output_dir / f"{base_name}_media.json"
        extractor.save_to_json(media_data, media_output)

        # Extract document properties
        print("Extracting document properties...")
        doc_props = extractor.extract_document_properties()
        doc_props_output = output_dir / f"{base_name}_properties.json"
        extractor.save_to_json(doc_props, doc_props_output)

        # Create summary with all extracted data
        summary_data = {
            'file_path': str(input_path),
            'base_name': base_name,
            'extraction_files': {
                'shapes': str(shapes_output),
                'layouts': str(layouts_output),
                'theme': str(theme_output),
                'media': str(media_output),
                'properties': str(doc_props_output)
            },
            'statistics': {
                'slide_count': len(extractor.presentation.slides),
                'layout_count': len(extractor.presentation.slide_layouts),
                'media_file_count': len(extractor.media_files),
                'total_shapes': sum(len(slide_data['shapes']) for slide_data in shapes_data)
            }
        }

        summary_output = output_dir / f"{base_name}_summary.json"
        extractor.save_to_json(summary_data, summary_output)

        print(f"\nExtraction completed successfully!")
        print(f"Output files created in: {output_dir}")
        print(f"Files generated:")
        print(f"  - Shapes: {shapes_output}")
        print(f"  - Layouts: {layouts_output}")
        print(f"  - Theme: {theme_output}")
        print(f"  - Media: {media_output}")
        print(f"  - Properties: {doc_props_output}")
        print(f"  - Summary: {summary_output}")
        print(f"\nStatistics:")
        print(f"  - Slides: {summary_data['statistics']['slide_count']}")
        print(f"  - Layouts: {summary_data['statistics']['layout_count']}")
        print(
            f"  - Media files: {summary_data['statistics']['media_file_count']}")
        print(
            f"  - Total shapes: {summary_data['statistics']['total_shapes']}")

    except Exception as e:
        print(f"Error processing PowerPoint file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
