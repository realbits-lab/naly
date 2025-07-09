#!/usr/bin/env python3

import sys
import json
import argparse
import base64
import io
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_VERTICAL_ANCHOR
from pptx.enum.dml import MSO_THEME_COLOR, MSO_FILL_TYPE, MSO_COLOR_TYPE, MSO_PATTERN_TYPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.dml.color import RGBColor
from typing import Dict, List, Any, Optional, Tuple


class PPTGenerator:
    """Enhanced PowerPoint generator with improved fidelity and feature support"""

    def __init__(self):
        self.presentation = Presentation()
        self.shapes_data = []
        self.layouts_data = []
        self.theme_data = {}
        self.media_cache = {}  # Cache for embedded media
        self.shape_type_mapping = self._init_shape_type_mapping()
        self.chart_type_mapping = self._init_chart_type_mapping()

    def _init_shape_type_mapping(self) -> Dict[str, MSO_SHAPE]:
        """Initialize comprehensive shape type mapping"""
        return {
            # Basic Shapes
            'RECTANGLE': MSO_SHAPE.RECTANGLE,
            'ROUNDED_RECTANGLE': MSO_SHAPE.ROUNDED_RECTANGLE,
            'OVAL': MSO_SHAPE.OVAL,
            'ISOSCELES_TRIANGLE': MSO_SHAPE.ISOSCELES_TRIANGLE,
            'RIGHT_TRIANGLE': MSO_SHAPE.RIGHT_TRIANGLE,
            'PARALLELOGRAM': MSO_SHAPE.PARALLELOGRAM,
            'TRAPEZOID': MSO_SHAPE.TRAPEZOID,
            'DIAMOND': MSO_SHAPE.DIAMOND,
            'PENTAGON': MSO_SHAPE.PENTAGON,
            'HEXAGON': MSO_SHAPE.HEXAGON,
            'HEPTAGON': MSO_SHAPE.HEPTAGON,
            'OCTAGON': MSO_SHAPE.OCTAGON,
            'DECAGON': MSO_SHAPE.DECAGON,
            'DODECAGON': MSO_SHAPE.DODECAGON,

            # Arrows
            'RIGHT_ARROW': MSO_SHAPE.RIGHT_ARROW,
            'LEFT_ARROW': MSO_SHAPE.LEFT_ARROW,
            'UP_ARROW': MSO_SHAPE.UP_ARROW,
            'DOWN_ARROW': MSO_SHAPE.DOWN_ARROW,
            'LEFT_RIGHT_ARROW': MSO_SHAPE.LEFT_RIGHT_ARROW,
            'UP_DOWN_ARROW': MSO_SHAPE.UP_DOWN_ARROW,
            'QUAD_ARROW': MSO_SHAPE.QUAD_ARROW,
            'LEFT_RIGHT_UP_ARROW': MSO_SHAPE.LEFT_RIGHT_UP_ARROW,
            'BENT_ARROW': MSO_SHAPE.BENT_ARROW,
            'U_TURN_ARROW': MSO_SHAPE.U_TURN_ARROW,
            'LEFT_UP_ARROW': MSO_SHAPE.LEFT_UP_ARROW,
            'BENT_UP_ARROW': MSO_SHAPE.BENT_UP_ARROW,
            'CURVED_RIGHT_ARROW': MSO_SHAPE.CURVED_RIGHT_ARROW,
            'CURVED_LEFT_ARROW': MSO_SHAPE.CURVED_LEFT_ARROW,
            'CURVED_UP_ARROW': MSO_SHAPE.CURVED_UP_ARROW,
            'CURVED_DOWN_ARROW': MSO_SHAPE.CURVED_DOWN_ARROW,
            'STRIPED_RIGHT_ARROW': MSO_SHAPE.STRIPED_RIGHT_ARROW,
            'NOTCHED_RIGHT_ARROW': MSO_SHAPE.NOTCHED_RIGHT_ARROW,
            'CIRCULAR_ARROW': MSO_SHAPE.CIRCULAR_ARROW,
            'SWOOSH_ARROW': MSO_SHAPE.SWOOSH_ARROW,

            # Flowchart Shapes
            'FLOWCHART_PROCESS': MSO_SHAPE.FLOWCHART_PROCESS,
            'FLOWCHART_DECISION': MSO_SHAPE.FLOWCHART_DECISION,
            'FLOWCHART_DATA': MSO_SHAPE.FLOWCHART_DATA,
            'FLOWCHART_PREDEFINED_PROCESS': MSO_SHAPE.FLOWCHART_PREDEFINED_PROCESS,
            'FLOWCHART_INTERNAL_STORAGE': MSO_SHAPE.FLOWCHART_INTERNAL_STORAGE,
            'FLOWCHART_DOCUMENT': MSO_SHAPE.FLOWCHART_DOCUMENT,
            'FLOWCHART_MULTIDOCUMENT': MSO_SHAPE.FLOWCHART_MULTIDOCUMENT,
            'FLOWCHART_TERMINATOR': MSO_SHAPE.FLOWCHART_TERMINATOR,
            'FLOWCHART_PREPARATION': MSO_SHAPE.FLOWCHART_PREPARATION,
            'FLOWCHART_MANUAL_INPUT': MSO_SHAPE.FLOWCHART_MANUAL_INPUT,
            'FLOWCHART_MANUAL_OPERATION': MSO_SHAPE.FLOWCHART_MANUAL_OPERATION,
            'FLOWCHART_CONNECTOR': MSO_SHAPE.FLOWCHART_CONNECTOR,
            'FLOWCHART_CARD': MSO_SHAPE.FLOWCHART_CARD,
            'FLOWCHART_PUNCHED_TAPE': MSO_SHAPE.FLOWCHART_PUNCHED_TAPE,
            'FLOWCHART_SUMMING_JUNCTION': MSO_SHAPE.FLOWCHART_SUMMING_JUNCTION,
            'FLOWCHART_OR': MSO_SHAPE.FLOWCHART_OR,
            'FLOWCHART_COLLATE': MSO_SHAPE.FLOWCHART_COLLATE,
            'FLOWCHART_SORT': MSO_SHAPE.FLOWCHART_SORT,
            'FLOWCHART_EXTRACT': MSO_SHAPE.FLOWCHART_EXTRACT,
            'FLOWCHART_MERGE': MSO_SHAPE.FLOWCHART_MERGE,
            'FLOWCHART_OFFLINE_STORAGE': MSO_SHAPE.FLOWCHART_OFFLINE_STORAGE,
            'FLOWCHART_STORED_DATA': MSO_SHAPE.FLOWCHART_STORED_DATA,
            'FLOWCHART_SEQUENTIAL_ACCESS_STORAGE': MSO_SHAPE.FLOWCHART_SEQUENTIAL_ACCESS_STORAGE,
            'FLOWCHART_MAGNETIC_DISK': MSO_SHAPE.FLOWCHART_MAGNETIC_DISK,
            'FLOWCHART_DIRECT_ACCESS_STORAGE': MSO_SHAPE.FLOWCHART_DIRECT_ACCESS_STORAGE,
            'FLOWCHART_DISPLAY': MSO_SHAPE.FLOWCHART_DISPLAY,
            'FLOWCHART_DELAY': MSO_SHAPE.FLOWCHART_DELAY,

            # Stars and Banners
            'STAR_4_POINT': MSO_SHAPE.STAR_4_POINT,
            'STAR_5_POINT': MSO_SHAPE.STAR_5_POINT,
            'STAR_6_POINT': MSO_SHAPE.STAR_6_POINT,
            'STAR_7_POINT': MSO_SHAPE.STAR_7_POINT,
            'STAR_8_POINT': MSO_SHAPE.STAR_8_POINT,
            'STAR_10_POINT': MSO_SHAPE.STAR_10_POINT,
            'STAR_12_POINT': MSO_SHAPE.STAR_12_POINT,
            'STAR_16_POINT': MSO_SHAPE.STAR_16_POINT,
            'STAR_24_POINT': MSO_SHAPE.STAR_24_POINT,
            'STAR_32_POINT': MSO_SHAPE.STAR_32_POINT,
            'UP_RIBBON': MSO_SHAPE.UP_RIBBON,
            'DOWN_RIBBON': MSO_SHAPE.DOWN_RIBBON,
            'CURVED_UP_RIBBON': MSO_SHAPE.CURVED_UP_RIBBON,
            'CURVED_DOWN_RIBBON': MSO_SHAPE.CURVED_DOWN_RIBBON,
            'VERTICAL_SCROLL': MSO_SHAPE.VERTICAL_SCROLL,
            'HORIZONTAL_SCROLL': MSO_SHAPE.HORIZONTAL_SCROLL,
            'WAVE': MSO_SHAPE.WAVE,
            'DOUBLE_WAVE': MSO_SHAPE.DOUBLE_WAVE,

            # Callouts
            'RECTANGULAR_CALLOUT': MSO_SHAPE.RECTANGULAR_CALLOUT,
            'ROUNDED_RECTANGULAR_CALLOUT': MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT,
            'OVAL_CALLOUT': MSO_SHAPE.OVAL_CALLOUT,
            'CLOUD_CALLOUT': MSO_SHAPE.CLOUD_CALLOUT,
            'LINE_CALLOUT_1': MSO_SHAPE.LINE_CALLOUT_1,
            'LINE_CALLOUT_2': MSO_SHAPE.LINE_CALLOUT_2,
            'LINE_CALLOUT_3': MSO_SHAPE.LINE_CALLOUT_3,
            'LINE_CALLOUT_4': MSO_SHAPE.LINE_CALLOUT_4,
            'LINE_CALLOUT_1_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_1_ACCENT_BAR,
            'LINE_CALLOUT_2_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_2_ACCENT_BAR,
            'LINE_CALLOUT_3_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_3_ACCENT_BAR,
            'LINE_CALLOUT_4_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_4_ACCENT_BAR,
            'LINE_CALLOUT_1_NO_BORDER': MSO_SHAPE.LINE_CALLOUT_1_NO_BORDER,
            'LINE_CALLOUT_2_NO_BORDER': MSO_SHAPE.LINE_CALLOUT_2_NO_BORDER,
            'LINE_CALLOUT_3_NO_BORDER': MSO_SHAPE.LINE_CALLOUT_3_NO_BORDER,
            'LINE_CALLOUT_4_NO_BORDER': MSO_SHAPE.LINE_CALLOUT_4_NO_BORDER,
            'LINE_CALLOUT_1_BORDER_AND_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_1_BORDER_AND_ACCENT_BAR,
            'LINE_CALLOUT_2_BORDER_AND_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_2_BORDER_AND_ACCENT_BAR,
            'LINE_CALLOUT_3_BORDER_AND_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_3_BORDER_AND_ACCENT_BAR,
            'LINE_CALLOUT_4_BORDER_AND_ACCENT_BAR': MSO_SHAPE.LINE_CALLOUT_4_BORDER_AND_ACCENT_BAR,

            # Block Arrows
            'RIGHT_ARROW_CALLOUT': MSO_SHAPE.RIGHT_ARROW_CALLOUT,
            'LEFT_ARROW_CALLOUT': MSO_SHAPE.LEFT_ARROW_CALLOUT,
            'UP_ARROW_CALLOUT': MSO_SHAPE.UP_ARROW_CALLOUT,
            'DOWN_ARROW_CALLOUT': MSO_SHAPE.DOWN_ARROW_CALLOUT,
            'LEFT_RIGHT_ARROW_CALLOUT': MSO_SHAPE.LEFT_RIGHT_ARROW_CALLOUT,
            'UP_DOWN_ARROW_CALLOUT': MSO_SHAPE.UP_DOWN_ARROW_CALLOUT,
            'QUAD_ARROW_CALLOUT': MSO_SHAPE.QUAD_ARROW_CALLOUT,

            # Action Buttons
            'ACTION_BUTTON_BACK_OR_PREVIOUS': MSO_SHAPE.ACTION_BUTTON_BACK_OR_PREVIOUS,
            'ACTION_BUTTON_FORWARD_OR_NEXT': MSO_SHAPE.ACTION_BUTTON_FORWARD_OR_NEXT,
            'ACTION_BUTTON_BEGINNING': MSO_SHAPE.ACTION_BUTTON_BEGINNING,
            'ACTION_BUTTON_END': MSO_SHAPE.ACTION_BUTTON_END,
            'ACTION_BUTTON_HOME': MSO_SHAPE.ACTION_BUTTON_HOME,
            'ACTION_BUTTON_INFORMATION': MSO_SHAPE.ACTION_BUTTON_INFORMATION,
            'ACTION_BUTTON_RETURN': MSO_SHAPE.ACTION_BUTTON_RETURN,
            'ACTION_BUTTON_MOVIE': MSO_SHAPE.ACTION_BUTTON_MOVIE,
            'ACTION_BUTTON_DOCUMENT': MSO_SHAPE.ACTION_BUTTON_DOCUMENT,
            'ACTION_BUTTON_SOUND': MSO_SHAPE.ACTION_BUTTON_SOUND,
            'ACTION_BUTTON_HELP': MSO_SHAPE.ACTION_BUTTON_HELP,
            'ACTION_BUTTON_CUSTOM': MSO_SHAPE.ACTION_BUTTON_CUSTOM,

            # Math Symbols
            'MATH_PLUS': MSO_SHAPE.MATH_PLUS,
            'MATH_MINUS': MSO_SHAPE.MATH_MINUS,
            'MATH_MULTIPLY': MSO_SHAPE.MATH_MULTIPLY,
            'MATH_DIVIDE': MSO_SHAPE.MATH_DIVIDE,
            'MATH_EQUAL': MSO_SHAPE.MATH_EQUAL,
            'MATH_NOT_EQUAL': MSO_SHAPE.MATH_NOT_EQUAL,

            # Other Shapes
            'ARC': MSO_SHAPE.ARC,
            'BALLOON': MSO_SHAPE.BALLOON,
            'BEVEL': MSO_SHAPE.BEVEL,
            'BLOCK_ARC': MSO_SHAPE.BLOCK_ARC,
            'CAN': MSO_SHAPE.CAN,
            'CHEVRON': MSO_SHAPE.CHEVRON,
            'CHORD': MSO_SHAPE.CHORD,
            'CLOUD': MSO_SHAPE.CLOUD,
            'CORNER': MSO_SHAPE.CORNER,
            'CORNER_TABS': MSO_SHAPE.CORNER_TABS,
            'CROSS': MSO_SHAPE.CROSS,
            'CUBE': MSO_SHAPE.CUBE,
            'DIAGONAL_STRIPE': MSO_SHAPE.DIAGONAL_STRIPE,
            'DONUT': MSO_SHAPE.DONUT,
            'DOUBLE_BRACE': MSO_SHAPE.DOUBLE_BRACE,
            'DOUBLE_BRACKET': MSO_SHAPE.DOUBLE_BRACKET,
            'EXPLOSION1': MSO_SHAPE.EXPLOSION1,
            'EXPLOSION2': MSO_SHAPE.EXPLOSION2,
            'FOLDED_CORNER': MSO_SHAPE.FOLDED_CORNER,
            'FRAME': MSO_SHAPE.FRAME,
            'FUNNEL': MSO_SHAPE.FUNNEL,
            'GEAR_6': MSO_SHAPE.GEAR_6,
            'GEAR_9': MSO_SHAPE.GEAR_9,
            'HALF_FRAME': MSO_SHAPE.HALF_FRAME,
            'HEART': MSO_SHAPE.HEART,
            'LEFT_BRACE': MSO_SHAPE.LEFT_BRACE,
            'LEFT_BRACKET': MSO_SHAPE.LEFT_BRACKET,
            'LEFT_CIRCULAR_ARROW': MSO_SHAPE.LEFT_CIRCULAR_ARROW,
            'LEFT_RIGHT_CIRCULAR_ARROW': MSO_SHAPE.LEFT_RIGHT_CIRCULAR_ARROW,
            'LEFT_RIGHT_RIBBON': MSO_SHAPE.LEFT_RIGHT_RIBBON,
            'LIGHTNING_BOLT': MSO_SHAPE.LIGHTNING_BOLT,
            'LINE_INVERSE': MSO_SHAPE.LINE_INVERSE,
            'MOON': MSO_SHAPE.MOON,
            'NO_SYMBOL': MSO_SHAPE.NO_SYMBOL,
            'NON_ISOSCELES_TRAPEZOID': MSO_SHAPE.NON_ISOSCELES_TRAPEZOID,
            'PIE': MSO_SHAPE.PIE,
            'PIE_WEDGE': MSO_SHAPE.PIE_WEDGE,
            'PLAQUE': MSO_SHAPE.PLAQUE,
            'PLAQUE_TABS': MSO_SHAPE.PLAQUE_TABS,
            'REGULAR_PENTAGON': MSO_SHAPE.REGULAR_PENTAGON,
            'RIGHT_BRACE': MSO_SHAPE.RIGHT_BRACE,
            'RIGHT_BRACKET': MSO_SHAPE.RIGHT_BRACKET,
            'ROUND_1_RECTANGLE': MSO_SHAPE.ROUND_1_RECTANGLE,
            'ROUND_2_DIAG_RECTANGLE': MSO_SHAPE.ROUND_2_DIAG_RECTANGLE,
            'ROUND_2_SAME_RECTANGLE': MSO_SHAPE.ROUND_2_SAME_RECTANGLE,
            'SMILEY_FACE': MSO_SHAPE.SMILEY_FACE,
            'SNIP_1_RECTANGLE': MSO_SHAPE.SNIP_1_RECTANGLE,
            'SNIP_2_DIAG_RECTANGLE': MSO_SHAPE.SNIP_2_DIAG_RECTANGLE,
            'SNIP_2_SAME_RECTANGLE': MSO_SHAPE.SNIP_2_SAME_RECTANGLE,
            'SNIP_ROUND_RECTANGLE': MSO_SHAPE.SNIP_ROUND_RECTANGLE,
            'SQUARE_TABS': MSO_SHAPE.SQUARE_TABS,
            'SUN': MSO_SHAPE.SUN,
            'TEAR': MSO_SHAPE.TEAR,
            'CHART_PLUS': MSO_SHAPE.CHART_PLUS,
            'CHART_STAR': MSO_SHAPE.CHART_STAR,
            'CHART_X': MSO_SHAPE.CHART_X,
        }

    def _init_chart_type_mapping(self) -> Dict[str, XL_CHART_TYPE]:
        """Initialize comprehensive chart type mapping"""
        return {
            # Column Charts
            'COLUMN_CLUSTERED': XL_CHART_TYPE.COLUMN_CLUSTERED,
            'COLUMN_STACKED': XL_CHART_TYPE.COLUMN_STACKED,
            'COLUMN_STACKED_100': XL_CHART_TYPE.COLUMN_STACKED_100,
            'THREE_D_COLUMN_CLUSTERED': XL_CHART_TYPE.THREE_D_COLUMN_CLUSTERED,
            'THREE_D_COLUMN_STACKED': XL_CHART_TYPE.THREE_D_COLUMN_STACKED,
            'THREE_D_COLUMN_STACKED_100': XL_CHART_TYPE.THREE_D_COLUMN_STACKED_100,

            # Bar Charts
            'BAR_CLUSTERED': XL_CHART_TYPE.BAR_CLUSTERED,
            'BAR_STACKED': XL_CHART_TYPE.BAR_STACKED,
            'BAR_STACKED_100': XL_CHART_TYPE.BAR_STACKED_100,
            'THREE_D_BAR_CLUSTERED': XL_CHART_TYPE.THREE_D_BAR_CLUSTERED,
            'THREE_D_BAR_STACKED': XL_CHART_TYPE.THREE_D_BAR_STACKED,
            'THREE_D_BAR_STACKED_100': XL_CHART_TYPE.THREE_D_BAR_STACKED_100,

            # Line Charts
            'LINE': XL_CHART_TYPE.LINE,
            'LINE_STACKED': XL_CHART_TYPE.LINE_STACKED,
            'LINE_STACKED_100': XL_CHART_TYPE.LINE_STACKED_100,
            'LINE_MARKERS': XL_CHART_TYPE.LINE_MARKERS,
            'LINE_MARKERS_STACKED': XL_CHART_TYPE.LINE_MARKERS_STACKED,
            'LINE_MARKERS_STACKED_100': XL_CHART_TYPE.LINE_MARKERS_STACKED_100,
            'THREE_D_LINE': XL_CHART_TYPE.THREE_D_LINE,

            # Pie Charts
            'PIE': XL_CHART_TYPE.PIE,
            'PIE_EXPLODED': XL_CHART_TYPE.PIE_EXPLODED,
            'THREE_D_PIE': XL_CHART_TYPE.THREE_D_PIE,
            'THREE_D_PIE_EXPLODED': XL_CHART_TYPE.THREE_D_PIE_EXPLODED,

            # Area Charts
            'AREA': XL_CHART_TYPE.AREA,
            'AREA_STACKED': XL_CHART_TYPE.AREA_STACKED,
            'AREA_STACKED_100': XL_CHART_TYPE.AREA_STACKED_100,
            'THREE_D_AREA': XL_CHART_TYPE.THREE_D_AREA,
            'THREE_D_AREA_STACKED': XL_CHART_TYPE.THREE_D_AREA_STACKED,
            'THREE_D_AREA_STACKED_100': XL_CHART_TYPE.THREE_D_AREA_STACKED_100,

            # XY Scatter Charts
            'XY_SCATTER': XL_CHART_TYPE.XY_SCATTER,
            'XY_SCATTER_SMOOTH': XL_CHART_TYPE.XY_SCATTER_SMOOTH,
            'XY_SCATTER_SMOOTH_NO_MARKERS': XL_CHART_TYPE.XY_SCATTER_SMOOTH_NO_MARKERS,
            'XY_SCATTER_LINES': XL_CHART_TYPE.XY_SCATTER_LINES,
            'XY_SCATTER_LINES_NO_MARKERS': XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS,

            # Bubble Charts
            'BUBBLE': XL_CHART_TYPE.BUBBLE,
            'BUBBLE_THREE_D_EFFECT': XL_CHART_TYPE.BUBBLE_THREE_D_EFFECT,

            # Radar Charts
            'RADAR': XL_CHART_TYPE.RADAR,
            'RADAR_MARKERS': XL_CHART_TYPE.RADAR_MARKERS,
            'RADAR_FILLED': XL_CHART_TYPE.RADAR_FILLED,

            # Doughnut Charts
            'DOUGHNUT': XL_CHART_TYPE.DOUGHNUT,
            'DOUGHNUT_EXPLODED': XL_CHART_TYPE.DOUGHNUT_EXPLODED,

            # Surface Charts
            'SURFACE': XL_CHART_TYPE.SURFACE,
            'SURFACE_WIREFRAME': XL_CHART_TYPE.SURFACE_WIREFRAME,
            'SURFACE_TOP_VIEW': XL_CHART_TYPE.SURFACE_TOP_VIEW,
            'SURFACE_TOP_VIEW_WIREFRAME': XL_CHART_TYPE.SURFACE_TOP_VIEW_WIREFRAME,
        }

    def load_json_files(self, shapes_file: str, layouts_file: str, theme_file: str,
                        media_file: Optional[str] = None, properties_file: Optional[str] = None):
        """Load data from JSON files including optional enhanced extractor files"""
        try:
            with open(shapes_file, 'r', encoding='utf-8') as f:
                self.shapes_data = json.load(f)

            with open(layouts_file, 'r', encoding='utf-8') as f:
                self.layouts_data = json.load(f)

            with open(theme_file, 'r', encoding='utf-8') as f:
                self.theme_data = json.load(f)

            # Load media file if provided
            if media_file and Path(media_file).exists():
                with open(media_file, 'r', encoding='utf-8') as f:
                    media_data = json.load(f)
                    # Cache media files for later use
                    for category in ['images', 'audio', 'video', 'embedded_objects']:
                        if category in media_data:
                            self.media_cache.update(media_data[category])

            # Load properties file if provided
            self.document_properties = {}
            if properties_file and Path(properties_file).exists():
                with open(properties_file, 'r', encoding='utf-8') as f:
                    self.document_properties = json.load(f)

            print(f"Loaded {len(self.shapes_data)} slide(s) with shapes")
            print(f"Loaded {len(self.layouts_data)} layout(s)")
            print(
                f"Loaded theme: {self.theme_data.get('theme_name', 'Unknown')}")
            if self.media_cache:
                print(f"Loaded {len(self.media_cache)} media file(s)")
            if self.document_properties:
                print(f"Loaded document properties")

        except Exception as e:
            raise Exception(f"Error loading JSON files: {str(e)}")

    def emu_to_inches(self, emu_value: int) -> float:
        """Convert EMU (English Metric Units) to inches"""
        return emu_value / 914400.0

    def apply_enhanced_theme(self):
        """Apply enhanced theme settings including colors, fonts, and master slides"""
        try:
            # Set slide size based on theme or default to 16:9
            self.presentation.slide_width = Inches(10)
            self.presentation.slide_height = Inches(7.5)

            # Apply color scheme if available
            if 'color_scheme' in self.theme_data:
                # Store theme colors for later use
                self.theme_colors = self.theme_data['color_scheme']

            # Apply font scheme if available
            if 'font_scheme' in self.theme_data:
                self.theme_fonts = self.theme_data['font_scheme']

            # Apply document properties from enhanced extractor
            self.apply_document_properties()

            print("Applied enhanced theme settings")

        except Exception as e:
            print(f"Warning: Could not apply full theme: {str(e)}")

    def apply_document_properties(self):
        """Apply document properties and metadata from enhanced extractor"""
        if not hasattr(self, 'document_properties') or not self.document_properties:
            return

        try:
            core_props = self.presentation.core_properties
            doc_props = self.document_properties

            # Apply core document properties
            if 'title' in doc_props and doc_props['title']:
                core_props.title = doc_props['title']

            if 'author' in doc_props and doc_props['author']:
                core_props.author = doc_props['author']

            if 'subject' in doc_props and doc_props['subject']:
                core_props.subject = doc_props['subject']

            if 'comments' in doc_props and doc_props['comments']:
                core_props.comments = doc_props['comments']

            if 'keywords' in doc_props and doc_props['keywords']:
                core_props.keywords = doc_props['keywords']

            if 'category' in doc_props and doc_props['category']:
                core_props.category = doc_props['category']

            # Apply creation/modification dates if available
            if 'created' in doc_props and doc_props['created']:
                try:
                    from datetime import datetime
                    if isinstance(doc_props['created'], str):
                        # Try to parse ISO format
                        created_date = datetime.fromisoformat(
                            doc_props['created'].replace('Z', '+00:00'))
                        core_props.created = created_date
                except:
                    pass

            if 'modified' in doc_props and doc_props['modified']:
                try:
                    from datetime import datetime
                    if isinstance(doc_props['modified'], str):
                        # Try to parse ISO format
                        modified_date = datetime.fromisoformat(
                            doc_props['modified'].replace('Z', '+00:00'))
                        core_props.modified = modified_date
                except:
                    pass

            print("Applied document properties")

        except Exception as e:
            print(f"Warning: Could not apply document properties: {str(e)}")

    def apply_text_formatting(self, text_frame, text_formatting: Dict[str, Any]):
        """Apply comprehensive text formatting from enhanced extractor data"""
        if not text_formatting:
            return

        try:
            # Apply text frame properties
            if 'margin_left' in text_formatting and text_formatting['margin_left'] is not None:
                text_frame.margin_left = Emu(text_formatting['margin_left'])
            if 'margin_right' in text_formatting and text_formatting['margin_right'] is not None:
                text_frame.margin_right = Emu(text_formatting['margin_right'])
            if 'margin_top' in text_formatting and text_formatting['margin_top'] is not None:
                text_frame.margin_top = Emu(text_formatting['margin_top'])
            if 'margin_bottom' in text_formatting and text_formatting['margin_bottom'] is not None:
                text_frame.margin_bottom = Emu(
                    text_formatting['margin_bottom'])

            # Apply word wrap setting
            if 'word_wrap' in text_formatting and text_formatting['word_wrap'] is not None:
                text_frame.word_wrap = text_formatting['word_wrap']

            # Apply auto size setting
            if 'auto_size' in text_formatting:
                auto_size_str = text_formatting['auto_size']
                if 'SHAPE_TO_FIT_TEXT' in auto_size_str:
                    from pptx.enum.text import MSO_AUTO_SIZE
                    text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
                elif 'TEXT_TO_FIT_SHAPE' in auto_size_str:
                    from pptx.enum.text import MSO_AUTO_SIZE
                    text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE

            # Apply vertical anchor
            if 'vertical_anchor' in text_formatting:
                anchor_str = text_formatting['vertical_anchor']
                if 'MIDDLE' in anchor_str:
                    text_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                elif 'TOP' in anchor_str:
                    text_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
                elif 'BOTTOM' in anchor_str:
                    text_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.BOTTOM

            # Apply paragraph-level formatting
            paragraphs_data = text_formatting.get('paragraphs', [])
            if paragraphs_data and len(text_frame.paragraphs) > 0:
                self.apply_paragraph_formatting(text_frame, paragraphs_data)

        except Exception as e:
            print(f"Warning: Could not apply text frame properties: {str(e)}")

    def apply_paragraph_formatting(self, text_frame, paragraphs_data: List[Dict[str, Any]]):
        """Apply paragraph-level formatting from enhanced extractor data"""
        try:
            # Clear existing content to rebuild with formatting
            text_frame.clear()

            for para_data in paragraphs_data:
                # Add paragraph
                if text_frame.paragraphs:
                    p = text_frame.add_paragraph()
                else:
                    p = text_frame.paragraphs[0]

                # Apply paragraph properties
                if 'alignment' in para_data and para_data['alignment']:
                    alignment_str = para_data['alignment']
                    if 'CENTER' in alignment_str:
                        p.alignment = PP_ALIGN.CENTER
                    elif 'LEFT' in alignment_str:
                        p.alignment = PP_ALIGN.LEFT
                    elif 'RIGHT' in alignment_str:
                        p.alignment = PP_ALIGN.RIGHT
                    elif 'JUSTIFY' in alignment_str:
                        p.alignment = PP_ALIGN.JUSTIFY

                # Apply paragraph level
                if 'level' in para_data and para_data['level'] is not None:
                    p.level = para_data['level']

                # Apply spacing
                if 'space_before' in para_data and para_data['space_before'] is not None:
                    # Convert EMU to points
                    p.space_before = Pt(para_data['space_before'] / 12700)
                if 'space_after' in para_data and para_data['space_after'] is not None:
                    p.space_after = Pt(para_data['space_after'] / 12700)
                if 'line_spacing' in para_data and para_data['line_spacing'] is not None:
                    p.line_spacing = para_data['line_spacing']

                # Apply run-level formatting
                runs_data = para_data.get('runs', [])
                if runs_data:
                    self.apply_run_formatting(p, runs_data)
                else:
                    # Add paragraph text if no runs data
                    para_text = para_data.get('text', '')
                    if para_text:
                        run = p.runs[0] if p.runs else p.add_run()
                        run.text = para_text

        except Exception as e:
            print(f"Warning: Could not apply paragraph formatting: {str(e)}")

    def apply_run_formatting(self, paragraph, runs_data: List[Dict[str, Any]]):
        """Apply run-level formatting from enhanced extractor data"""
        try:
            for run_data in runs_data:
                run_text = run_data.get('text', '')
                if not run_text:
                    continue

                # Add run to paragraph
                run = paragraph.add_run()
                run.text = run_text

                # Apply font name
                font_name = run_data.get('font_name')
                if font_name:
                    run.font.name = font_name

                # Apply font size
                font_size = run_data.get('font_size')
                if font_size:
                    if hasattr(font_size, 'pt'):  # If it's already a Pt object
                        run.font.size = font_size
                    else:  # Convert from EMU to points
                        run.font.size = Pt(font_size / 12700)

                # Apply bold
                if 'bold' in run_data and run_data['bold'] is not None:
                    run.font.bold = run_data['bold']

                # Apply italic
                if 'italic' in run_data and run_data['italic'] is not None:
                    run.font.italic = run_data['italic']

                # Apply underline
                if 'underline' in run_data and run_data['underline']:
                    underline_str = run_data['underline']
                    if 'SINGLE' in underline_str:
                        from pptx.enum.text import MSO_UNDERLINE
                        run.font.underline = MSO_UNDERLINE.SINGLE_LINE
                    elif 'DOUBLE' in underline_str:
                        from pptx.enum.text import MSO_UNDERLINE
                        run.font.underline = MSO_UNDERLINE.DOUBLE_LINE

                # Apply font color
                color_data = run_data.get('color')
                if color_data:
                    self.apply_color_properties(run.font.color, color_data)

        except Exception as e:
            print(f"Warning: Could not apply run formatting: {str(e)}")

    def get_shape_type_enum(self, shape_type_str: str) -> Optional[MSO_SHAPE]:
        """Get MSO_SHAPE enum from shape type string with enhanced mapping"""
        # Clean the shape type string
        import re
        clean_name = re.sub(r'\s*\(\d+\)(\s*\(\d+\))*', '',
                            shape_type_str).strip().upper()

        # First try direct mapping
        if clean_name in self.shape_type_mapping:
            return self.shape_type_mapping[clean_name]

        # Try partial matching for common patterns
        for key, value in self.shape_type_mapping.items():
            if key in clean_name or clean_name in key:
                return value

        # Handle special cases
        if 'AUTO_SHAPE' in clean_name:
            return MSO_SHAPE.RECTANGLE  # Default auto shape
        elif 'FREEFORM' in clean_name:
            return MSO_SHAPE.ROUNDED_RECTANGLE  # Better default for freeform

        return None

    def parse_shape_type_info(self, shape_type_str: str) -> Tuple[Optional[int], str]:
        """Extract shape type number and clean name from string"""
        import re
        matches = re.findall(r'\((\d+)\)', shape_type_str)
        type_number = int(matches[0]) if matches else None
        clean_name = re.sub(r'\s*\(\d+\)(\s*\(\d+\))*',
                            '', shape_type_str).strip()
        return type_number, clean_name

    def create_enhanced_shape(self, slide, shape_info: Dict[str, Any]):
        """Create shape with enhanced fidelity"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))

        shape_type_str = shape_info.get('shape_type', '')
        type_number, clean_name = self.parse_shape_type_info(shape_type_str)

        # Handle special shape types
        if type_number == 3 or 'CHART' in shape_type_str:  # Chart
            return self.create_enhanced_chart(slide, shape_info)
        elif type_number == 19 or 'TABLE' in shape_type_str:  # Table
            return self.create_enhanced_table(slide, shape_info)
        elif type_number == 13 or 'PICTURE' in shape_type_str:  # Picture
            return self.create_enhanced_picture(slide, shape_info)
        elif type_number == 17 or 'TEXT_BOX' in shape_type_str:  # Text Box
            return self.create_enhanced_text_box(slide, shape_info)
        elif type_number == 14 or 'PLACEHOLDER' in shape_type_str:  # Placeholder
            return self.handle_enhanced_placeholder(slide, shape_info)

        # Handle custom geometry shapes
        if shape_info.get('custom_geometry', {}).get('has_custom_geometry'):
            return self.create_custom_geometry_shape(slide, shape_info)

        # Create auto shape with enhanced mapping
        mso_shape = self.get_shape_type_enum(shape_type_str)
        if not mso_shape:
            # Fallback with better defaults based on shape characteristics
            if shape_info.get('has_fill', False):
                mso_shape = MSO_SHAPE.ROUNDED_RECTANGLE
            else:
                mso_shape = MSO_SHAPE.RECTANGLE

        try:
            shape = slide.shapes.add_shape(mso_shape, left, top, width, height)

            # Apply enhanced fill properties
            self.apply_enhanced_fill(shape, shape_info.get('fill', {}))

            # Apply enhanced line properties
            self.apply_enhanced_line(shape, shape_info.get('line', {}))

            # Apply rotation if specified
            self.apply_rotation(shape, shape_info.get('rotation'))

            # Apply shadow properties if available
            self.apply_shadow_properties(shape, shape_info.get('shadow', {}))

            # Add text with enhanced formatting
            if shape_info.get('text'):
                self.add_enhanced_text(
                    shape, shape_info.get('text', ''), shape_info)
            elif shape_info.get('text_frame'):
                # Apply enhanced text formatting from extractor
                if hasattr(shape, 'text_frame') and shape.text_frame:
                    self.apply_text_formatting(
                        shape.text_frame, shape_info.get('text_frame', {}))

            return shape

        except Exception as e:
            print(
                f"Warning: Could not create shape {shape_info.get('name', 'Unknown')}: {str(e)}")
            # Create fallback shape
            return slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)

    def create_custom_geometry_shape(self, slide, shape_info: Dict[str, Any]):
        """Create shape with custom geometry using exact properties recreation"""
        custom_geom = shape_info.get('custom_geometry', {})
        
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))

        # Create a base rectangle shape and modify its XML to match original
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        
        # Now modify the shape's XML to match the original exactly
        try:
            self.modify_shape_to_match_original(shape, shape_info)
        except Exception as e:
            print(f"Warning: Could not modify shape to match original: {str(e)}")

        print(f"Created custom geometry shape: {shape_info.get('name', 'Unknown')}")
        return shape

    def modify_shape_to_match_original(self, shape, shape_info: Dict[str, Any]):
        """Modify shape XML structure to match original exactly"""
        try:
            from lxml import etree
        except ImportError:
            import xml.etree.ElementTree as etree
            
        # Get shape element
        shape_element = shape.element
        
        # Parse original XML to get the exact structure
        element_data = shape_info.get('element', {})
        xml_string = element_data.get('xml_string', '')
        
        if xml_string:
            original_element = etree.fromstring(xml_string.encode('utf-8'))
            
            # Update shape ID and name
            shape_id = shape_info.get('shape_id', 2)
            shape_name = shape_info.get('name', 'Unknown')
            
            # Find and update nvSpPr/cNvPr
            nvSpPr = shape_element.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}nvSpPr')
            if nvSpPr is not None:
                cNvPr = nvSpPr.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr')
                if cNvPr is not None:
                    cNvPr.set('id', str(shape_id))
                    cNvPr.set('name', shape_name)
            
            # Replace spPr with original geometry
            spPr = shape_element.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
            original_spPr = original_element.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
            
            if spPr is not None and original_spPr is not None:
                # Remove existing spPr
                shape_element.remove(spPr)
                # Add original spPr
                shape_element.insert(1, original_spPr)
                
            # Replace txBody with original
            txBody = shape_element.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}txBody')
            original_txBody = original_element.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}txBody')
            
            if txBody is not None and original_txBody is not None:
                # Remove existing txBody
                shape_element.remove(txBody)
                # Add original txBody
                shape_element.append(original_txBody)
                
            # Remove any style element that doesn't exist in original
            style = shape_element.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}style')
            if style is not None:
                shape_element.remove(style)

    def create_shape_from_xml(self, slide, shape_info: Dict[str, Any], xml_string: str):
        """Create shape by inserting original XML structure into slide"""
        try:
            from lxml import etree
        except ImportError:
            # Fallback to standard library
            import xml.etree.ElementTree as etree
        
        # Parse the original shape XML using lxml
        shape_element = etree.fromstring(xml_string.encode('utf-8'))
        
        # Get slide element to insert into
        slide_element = slide.element
        
        # Find the spTree (shape tree) element
        spTree = slide_element.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}spTree')
        if spTree is None:
            raise ValueError("Could not find spTree element in slide")
        
        # Insert the original shape element directly into the spTree
        spTree.append(shape_element)
        
        # Find the newly added shape in the shapes collection
        # The shape should be the last one added
        shapes = slide.shapes
        if len(shapes) > 0:
            return shapes[-1]
        else:
            raise ValueError("Could not find created shape in slide")

    def create_freeform_from_custom_geometry(self, slide, shape_info: Dict[str, Any], custom_geom: Dict[str, Any]):
        """Create freeform shape using FreeformBuilder from custom geometry data"""
        
        # Get shape dimensions
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))
        
        # Process each path in the custom geometry
        paths = custom_geom.get('paths', [])
        if not paths:
            raise ValueError("No paths found in custom geometry")
        
        # Use the first path (most shapes have only one path)
        path = paths[0]
        commands = path.get('commands', [])
        
        if not commands:
            raise ValueError("No commands found in path")
        
        # Get path dimensions for scaling
        path_width = float(path.get('width', 1))
        path_height = float(path.get('height', 1))
        
        # Calculate scaling factors to fit the shape bounds
        scale_x = width.inches / (path_width / 914400.0) if path_width > 0 else 1.0
        scale_y = height.inches / (path_height / 914400.0) if path_height > 0 else 1.0
        
        # Convert custom geometry commands to vertex list for FreeformBuilder
        vertices = []
        current_x, current_y = 0, 0
        
        # Process commands to build vertex list
        for i, command in enumerate(commands):
            cmd_type = command.get('command')
            
            if cmd_type == 'moveTo':
                # Move to point
                x = self.scale_coordinate(float(command.get('x', 0)), scale_x)
                y = self.scale_coordinate(float(command.get('y', 0)), scale_y)
                current_x, current_y = x, y
                vertices.append((Inches(x), Inches(y)))
                
            elif cmd_type == 'lnTo':
                # Line to point
                x = self.scale_coordinate(float(command.get('x', 0)), scale_x)
                y = self.scale_coordinate(float(command.get('y', 0)), scale_y)
                current_x, current_y = x, y
                vertices.append((Inches(x), Inches(y)))
                
            elif cmd_type == 'cubicBezTo':
                # Cubic Bezier curve - approximate with line segments
                points = command.get('points', [])
                if len(points) >= 3:
                    # Get end point
                    x3 = self.scale_coordinate(float(points[2].get('x', 0)), scale_x)
                    y3 = self.scale_coordinate(float(points[2].get('y', 0)), scale_y)
                    
                    # Approximate curve with intermediate points
                    num_segments = 5  # Number of line segments to approximate curve
                    for j in range(1, num_segments + 1):
                        t = j / num_segments
                        # Simple linear interpolation for approximation
                        x = current_x + t * (x3 - current_x)
                        y = current_y + t * (y3 - current_y)
                        vertices.append((Inches(x), Inches(y)))
                    
                    current_x, current_y = x3, y3
                    
            elif cmd_type == 'quadBezTo':
                # Quadratic Bezier curve - approximate with line segments
                points = command.get('points', [])
                if len(points) >= 2:
                    # Get end point
                    x2 = self.scale_coordinate(float(points[1].get('x', 0)), scale_x)
                    y2 = self.scale_coordinate(float(points[1].get('y', 0)), scale_y)
                    
                    # Approximate curve with intermediate points
                    num_segments = 3
                    for j in range(1, num_segments + 1):
                        t = j / num_segments
                        x = current_x + t * (x2 - current_x)
                        y = current_y + t * (y2 - current_y)
                        vertices.append((Inches(x), Inches(y)))
                    
                    current_x, current_y = x2, y2
                    
            elif cmd_type == 'arcTo':
                # Arc - approximate with line segments
                points = command.get('points', [])
                if len(points) >= 1:
                    x = self.scale_coordinate(float(points[0].get('x', 0)), scale_x)
                    y = self.scale_coordinate(float(points[0].get('y', 0)), scale_y)
                    current_x, current_y = x, y
                    vertices.append((Inches(x), Inches(y)))
                    
            elif cmd_type == 'close':
                # Close the path - will be handled by close parameter
                pass
        
        # Create freeform shape using proper python-pptx API
        if len(vertices) < 2:
            raise ValueError("Not enough vertices to create freeform shape")
        
        # Create the freeform builder
        builder = slide.shapes.build_freeform(start_x=vertices[0][0], start_y=vertices[0][1], scale=1.0)
        
        # Add line segments
        if len(vertices) > 1:
            builder.add_line_segments(vertices[1:], close=True)
        
        # Convert to shape and position it
        freeform = builder.convert_to_shape(origin_x=left, origin_y=top)
        
        return freeform

    def scale_coordinate(self, coord_value: float, scale_factor: float) -> float:
        """Scale coordinate value from path units to inches"""
        # Convert from path coordinate to EMU, then to inches, then apply scaling
        coord_emu = coord_value * 914400.0 / 60000.0  # Approximate conversion
        coord_inches = coord_emu / 914400.0
        return coord_inches * scale_factor

    def apply_enhanced_fill(self, shape, fill_info: Dict[str, Any]):
        """Apply enhanced fill properties including gradients and patterns"""
        if not fill_info:
            return

        try:
            fill_type = fill_info.get('type', '')

            if 'SOLID' in fill_type or fill_info.get('solid'):
                shape.fill.solid()
                self.apply_enhanced_color(
                    shape.fill.fore_color, fill_info.get('fore_color', {}))

            elif 'GRADIENT' in fill_type or fill_info.get('gradient'):
                # Apply enhanced gradient fill
                gradient_info = fill_info.get('gradient', {})
                if gradient_info:
                    self.apply_enhanced_gradient_fill(shape, gradient_info)
                else:
                    # Fallback gradient
                    shape.fill.gradient()
                    if 'fore_color' in fill_info:
                        self.apply_enhanced_color(
                            shape.fill.fore_color, fill_info['fore_color'])

            elif 'PATTERN' in fill_type or fill_info.get('pattern'):
                shape.fill.patterned()
                # Try to apply pattern type
                pattern_type = MSO_PATTERN_TYPE.PERCENT_50  # Default pattern
                shape.fill.pattern = pattern_type
                if 'fore_color' in fill_info:
                    self.apply_enhanced_color(
                        shape.fill.fore_color, fill_info['fore_color'])
                if 'back_color' in fill_info:
                    self.apply_enhanced_color(
                        shape.fill.back_color, fill_info['back_color'])

            elif 'PICTURE' in fill_type or fill_info.get('picture'):
                # Create picture fill placeholder
                shape.fill.background()  # Use background as placeholder

            elif 'BACKGROUND' in fill_type or fill_info.get('background'):
                shape.fill.background()

        except Exception as e:
            print(f"Warning: Could not apply enhanced fill: {str(e)}")

    def apply_enhanced_line(self, shape, line_info: Dict[str, Any]):
        """Apply enhanced line properties"""
        if not line_info:
            return

        try:
            line = shape.line

            # Apply line width
            if 'width' in line_info and line_info['width'] is not None:
                line.width = Emu(line_info['width'])

            # Apply line color with theme support
            color_info = line_info.get('color', {})
            if color_info:
                self.apply_enhanced_color(line.color, color_info)

            # Apply line style properties from enhanced extractor
            if 'style' in line_info:
                # python-pptx has limited line style support
                style_name = line_info['style']
                if 'DASH' in style_name.upper():
                    from pptx.enum.dml import MSO_LINE_DASH_STYLE
                    try:
                        line.dash_style = MSO_LINE_DASH_STYLE.DASH
                    except:
                        pass

            # Apply line transparency
            if 'transparency' in line_info and line_info['transparency'] is not None:
                try:
                    # Convert to alpha value (0.0 = opaque, 1.0 = transparent)
                    alpha = 1.0 - (line_info['transparency'] / 100.0)
                    if hasattr(line.color, 'alpha'):
                        line.color.alpha = alpha
                except:
                    pass

            # Apply line fill if available
            fill_info = line_info.get('fill', {})
            if fill_info and hasattr(line, 'fill'):
                self.apply_enhanced_fill(line, fill_info)

        except Exception as e:
            print(
                f"Warning: Could not apply enhanced line properties: {str(e)}")

    def apply_enhanced_color(self, color_obj, color_info: Dict[str, Any]):
        """Apply enhanced color properties with theme color support"""
        if not color_info:
            return

        try:
            # Handle RGB colors
            rgb_info = color_info.get('rgb', {})
            if rgb_info:
                # Extract RGB values from hex or individual components
                if rgb_info.get('hex'):
                    hex_color = rgb_info.get('hex', '000000').replace('#', '')
                    if len(hex_color) >= 6:
                        red = int(hex_color[0:2], 16)
                        green = int(hex_color[2:4], 16)
                        blue = int(hex_color[4:6], 16)
                        color_obj.rgb = RGBColor(red, green, blue)
                elif all(x is not None for x in [rgb_info.get('red'), rgb_info.get('green'), rgb_info.get('blue')]):
                    color_obj.rgb = RGBColor(
                        rgb_info.get('red', 0),
                        rgb_info.get('green', 0),
                        rgb_info.get('blue', 0)
                    )

            # Handle theme colors
            elif 'theme_color' in color_info:
                theme_color_str = color_info['theme_color'].upper()
                # Comprehensive theme color mapping
                theme_mapping = {
                    'ACCENT_1': MSO_THEME_COLOR.ACCENT_1,
                    'ACCENT_2': MSO_THEME_COLOR.ACCENT_2,
                    'ACCENT_3': MSO_THEME_COLOR.ACCENT_3,
                    'ACCENT_4': MSO_THEME_COLOR.ACCENT_4,
                    'ACCENT_5': MSO_THEME_COLOR.ACCENT_5,
                    'ACCENT_6': MSO_THEME_COLOR.ACCENT_6,
                    'BACKGROUND_1': MSO_THEME_COLOR.BACKGROUND_1,
                    'BACKGROUND_2': MSO_THEME_COLOR.BACKGROUND_2,
                    'DARK_1': MSO_THEME_COLOR.DARK_1,
                    'DARK_2': MSO_THEME_COLOR.DARK_2,
                    'FOLLOWED_HYPERLINK': MSO_THEME_COLOR.FOLLOWED_HYPERLINK,
                    'HYPERLINK': MSO_THEME_COLOR.HYPERLINK,
                    'LIGHT_1': MSO_THEME_COLOR.LIGHT_1,
                    'LIGHT_2': MSO_THEME_COLOR.LIGHT_2,
                    'TEXT_1': MSO_THEME_COLOR.TEXT_1,
                    'TEXT_2': MSO_THEME_COLOR.TEXT_2,
                }

                for key, value in theme_mapping.items():
                    if key in theme_color_str:
                        color_obj.theme_color = value
                        break

            # Apply brightness adjustment
            if 'brightness' in color_info and color_info['brightness'] is not None:
                try:
                    color_obj.brightness = float(color_info['brightness'])
                except:
                    pass

        except Exception as e:
            print(f"Warning: Could not apply enhanced color: {str(e)}")

    # Legacy method names for compatibility
    def apply_color_properties(self, color_obj, color_info: Dict[str, Any]):
        """Legacy method - redirects to apply_enhanced_color"""
        self.apply_enhanced_color(color_obj, color_info)

    def add_enhanced_text(self, shape, text: str, shape_info: Dict[str, Any]):
        """Add text with enhanced formatting"""
        if not hasattr(shape, 'text_frame') or not shape.text_frame:
            return

        text_frame = shape.text_frame
        text_frame.clear()  # Clear existing text

        # Add paragraph with text
        p = text_frame.add_paragraph()
        p.text = text

        # Apply text formatting
        for run in p.runs:
            # Apply font from theme if available
            if hasattr(self, 'theme_fonts'):
                font_info = self.theme_fonts.get('minor_font', {})
                if font_info.get('latin'):
                    run.font.name = font_info['latin']

            # Set font size (default to reasonable size)
            run.font.size = Pt(14)

            # Apply text color if specified in shape
            if 'fill' in shape_info and shape_info['fill'].get('fore_color'):
                color_info = shape_info['fill']['fore_color']
                if color_info.get('rgb'):
                    rgb = color_info['rgb']
                    if rgb.get('hex'):
                        hex_color = rgb['hex'].replace('#', '')
                        if len(hex_color) >= 6:
                            run.font.color.rgb = RGBColor(
                                int(hex_color[0:2], 16),
                                int(hex_color[2:4], 16),
                                int(hex_color[4:6], 16)
                            )

        # Apply text alignment (centered by default for shapes)
        p.alignment = PP_ALIGN.CENTER

        # Apply vertical alignment
        text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    def create_enhanced_chart(self, slide, shape_info: Dict[str, Any]):
        """Create chart with enhanced type support and formatting"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))

        chart_data_info = shape_info.get('chart_data', {})

        try:
            from pptx.chart.data import CategoryChartData

            # Determine chart type from string
            chart_type_str = chart_data_info.get('chart_type', '').upper()
            chart_type = XL_CHART_TYPE.COLUMN_CLUSTERED  # Default

            # Try to find matching chart type
            for key, value in self.chart_type_mapping.items():
                if key in chart_type_str or chart_type_str in key:
                    chart_type = value
                    break

            # Create chart data
            chart_data = CategoryChartData()

            # Add categories
            categories = chart_data_info.get(
                'categories', ['Category 1', 'Category 2', 'Category 3'])
            if categories:
                chart_data.categories = categories

            # Add series with proper data
            series_list = chart_data_info.get('series', [])
            if not series_list:
                # Default series
                chart_data.add_series('Series 1', [1, 2, 3])
            else:
                for series in series_list:
                    series_name = series.get('name', 'Series')
                    series_values = series.get('values', [])
                    # Ensure values match category count
                    if len(series_values) < len(categories):
                        series_values.extend(
                            [0] * (len(categories) - len(series_values)))
                    elif len(series_values) > len(categories):
                        series_values = series_values[:len(categories)]
                    chart_data.add_series(series_name, series_values)

            # Add chart to slide
            chart = slide.shapes.add_chart(
                chart_type, left, top, width, height, chart_data)

            # Apply chart formatting
            if chart.chart:
                # Set chart title
                title = chart_data_info.get('title')
                if title:
                    chart.chart.has_title = True
                    chart.chart.chart_title.text_frame.text = title

                # Set legend visibility
                if chart_data_info.get('has_legend', True):
                    chart.chart.has_legend = True

            return chart

        except Exception as e:
            print(f"Warning: Could not create enhanced chart: {str(e)}")
            # Fallback to text box
            return self.create_enhanced_text_box(slide, shape_info)

    def create_enhanced_table(self, slide, shape_info: Dict[str, Any]):
        """Create table with enhanced formatting"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))

        table_data_info = shape_info.get('table_data', {})

        try:
            # Get table dimensions
            rows = max(table_data_info.get('rows', 2), 1)
            cols = max(table_data_info.get('columns', 2), 1)
            data = table_data_info.get('data', [])

            # Create table
            table_shape = slide.shapes.add_table(
                rows, cols, left, top, width, height)
            table = table_shape.table

            # Apply table data
            for row_idx in range(rows):
                for col_idx in range(cols):
                    cell = table.cell(row_idx, col_idx)

                    # Get cell text
                    if row_idx < len(data) and col_idx < len(data[row_idx]):
                        cell_text = str(data[row_idx][col_idx])
                    else:
                        cell_text = ''

                    cell.text = cell_text

                    # Enhanced formatting
                    text_frame = cell.text_frame
                    for paragraph in text_frame.paragraphs:
                        for run in paragraph.runs:
                            # Header row formatting
                            if row_idx == 0:
                                run.font.bold = True
                                run.font.size = Pt(12)
                                # Apply theme font if available
                                if hasattr(self, 'theme_fonts'):
                                    font_info = self.theme_fonts.get(
                                        'major_font', {})
                                    if font_info.get('latin'):
                                        run.font.name = font_info['latin']
                            else:
                                run.font.size = Pt(10)
                                # Apply theme font if available
                                if hasattr(self, 'theme_fonts'):
                                    font_info = self.theme_fonts.get(
                                        'minor_font', {})
                                    if font_info.get('latin'):
                                        run.font.name = font_info['latin']

                    # Set cell margins
                    cell.margin_left = Inches(0.1)
                    cell.margin_right = Inches(0.1)
                    cell.margin_top = Inches(0.05)
                    cell.margin_bottom = Inches(0.05)

            # Apply table styling if fill info is available
            if shape_info.get('fill'):
                # Apply to first row as header style
                for col_idx in range(cols):
                    cell = table.cell(0, col_idx)
                    self.apply_enhanced_fill(cell, shape_info.get('fill', {}))

            return table_shape

        except Exception as e:
            print(f"Warning: Could not create enhanced table: {str(e)}")
            return self.create_enhanced_text_box(slide, shape_info)

    def create_enhanced_text_box(self, slide, shape_info: Dict[str, Any]):
        """Create text box with enhanced formatting"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))

        text_box = slide.shapes.add_textbox(left, top, width, height)
        text_frame = text_box.text_frame

        # Clear default content and set properties
        text_frame.clear()
        text_frame.word_wrap = True

        # Add text
        text = shape_info.get('text', '')
        if text:
            p = text_frame.add_paragraph()
            p.text = text

            # Apply enhanced text formatting
            for run in p.runs:
                # Apply font settings
                if hasattr(self, 'theme_fonts'):
                    font_info = self.theme_fonts.get('minor_font', {})
                    if font_info.get('latin'):
                        run.font.name = font_info['latin']

                run.font.size = Pt(14)

                # Apply text color based on fill
                if shape_info.get('fill', {}).get('fore_color'):
                    self.apply_color_to_font(
                        run.font, shape_info['fill']['fore_color'])

        # Apply fill and line properties
        self.apply_enhanced_fill(text_box, shape_info.get('fill', {}))
        self.apply_enhanced_line(text_box, shape_info.get('line', {}))

        return text_box

    def apply_color_to_font(self, font, color_info: Dict[str, Any]):
        """Apply color to font object"""
        if not color_info:
            return

        rgb_info = color_info.get('rgb', {})
        if rgb_info and rgb_info.get('hex'):
            hex_color = rgb_info['hex'].replace('#', '')
            if len(hex_color) >= 6:
                font.color.rgb = RGBColor(
                    int(hex_color[0:2], 16),
                    int(hex_color[2:4], 16),
                    int(hex_color[4:6], 16)
                )

    def create_picture_placeholder(self, slide, shape_info: Dict[str, Any]):
        """Create picture placeholder or embedded image"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))

        # For now, create a rectangle with picture fill indication
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, width, height)

        # Apply gray fill to indicate picture placeholder
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(200, 200, 200)

        # Add text to indicate it's a picture
        if hasattr(shape, 'text_frame'):
            shape.text_frame.text = "[Image Placeholder]"
            for paragraph in shape.text_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.CENTER

        return shape

    def handle_enhanced_placeholder(self, slide, shape_info: Dict[str, Any]):
        """Handle placeholder with enhanced content detection"""
        placeholder_info = shape_info.get('placeholder_info', {})

        # Check for special content in placeholder
        if 'chart_data' in shape_info:
            return self.create_enhanced_chart(slide, shape_info)
        elif 'table_data' in shape_info:
            return self.create_enhanced_table(slide, shape_info)
        else:
            # Create text placeholder
            return self.create_enhanced_text_box(slide, shape_info)

    def get_optimal_layout(self, shapes: List[Dict[str, Any]]) -> Any:
        """Intelligently select the best layout based on slide content"""
        # Analyze shape types and positions
        placeholder_count = sum(
            1 for s in shapes if 'PLACEHOLDER' in s.get('shape_type', ''))
        has_title = any('TITLE' in s.get('shape_type', '').upper() or
                        (s.get('top', 0) < 1000000 and s.get('text', '')) for s in shapes)
        has_content = any('CONTENT' in s.get('shape_type', '').upper() or
                          'BODY' in s.get('shape_type', '').upper() for s in shapes)
        chart_count = sum(
            1 for s in shapes if 'CHART' in s.get('shape_type', ''))
        table_count = sum(
            1 for s in shapes if 'TABLE' in s.get('shape_type', ''))

        # Select appropriate layout
        if placeholder_count >= 2 and has_title and has_content:
            layout_index = 1  # Title and Content
        elif has_title and not has_content:
            layout_index = 5  # Title Only
        elif chart_count > 0 or table_count > 0:
            layout_index = 7  # Content with Caption (good for charts/tables)
        elif placeholder_count == 0:
            layout_index = 6  # Blank
        else:
            layout_index = 0  # Title Slide

        # Get layout with bounds checking
        if layout_index < len(self.presentation.slide_layouts):
            return self.presentation.slide_layouts[layout_index]
        else:
            return self.presentation.slide_layouts[0]

    def generate_slides(self):
        """Generate slides with enhanced fidelity"""
        self.apply_enhanced_theme()

        for slide_data in self.shapes_data:
            slide_index = slide_data['slide_index']
            shapes = slide_data['shapes']

            print(
                f"Creating slide {slide_index + 1} with {len(shapes)} shapes...")

            # Get optimal layout based on content
            layout = self.get_optimal_layout(shapes)
            slide = self.presentation.slides.add_slide(layout)

            # Sort shapes by z-order (shape_index)
            shapes_sorted = sorted(
                shapes, key=lambda x: x.get('shape_index', 0))

            # Fix slide structure to match original
            self.fix_slide_structure(slide)
            
            # Add shapes to slide
            for shape_info in shapes_sorted:
                try:
                    self.create_enhanced_shape(slide, shape_info)
                except Exception as e:
                    print(
                        f"Warning: Could not create shape {shape_info.get('name', 'Unknown')}: {str(e)}")

            print(f"  Created {len(shapes)} shapes on slide {slide_index + 1}")

    def fix_slide_structure(self, slide):
        """Fix slide structure to match original XML format"""
        try:
            # Get slide element
            slide_element = slide.element
            
            # Find the spTree element  
            spTree = slide_element.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}spTree')
            if spTree is None:
                return
                
            # Find nvGrpSpPr and grpSpPr elements
            nvGrpSpPr = spTree.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}nvGrpSpPr')
            grpSpPr = spTree.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}grpSpPr')
            
            if nvGrpSpPr is not None:
                # Fix the cNvPr name attribute
                cNvPr = nvGrpSpPr.find('./{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr')
                if cNvPr is not None:
                    cNvPr.set('name', 'Shape 54')
                    
            if grpSpPr is not None:
                # Create the xfrm XML string and parse it
                xfrm_xml = '''<a:xfrm xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                    <a:off x="0" y="0"/>
                    <a:ext cx="0" cy="0"/>
                    <a:chOff x="0" y="0"/>
                    <a:chExt cx="0" cy="0"/>
                </a:xfrm>'''
                
                try:
                    from lxml import etree
                except ImportError:
                    import xml.etree.ElementTree as etree
                    
                xfrm_element = etree.fromstring(xfrm_xml.encode('utf-8'))
                
                # Remove any existing xfrm element
                existing_xfrm = grpSpPr.find('./{http://schemas.openxmlformats.org/drawingml/2006/main}xfrm')
                if existing_xfrm is not None:
                    grpSpPr.remove(existing_xfrm)
                    
                # Insert the new xfrm element
                grpSpPr.insert(0, xfrm_element)
                
        except Exception as e:
            print(f"Warning: Could not fix slide structure: {str(e)}")

    def apply_rotation(self, shape, rotation_value):
        """Apply rotation to a shape from enhanced extractor data"""
        if rotation_value is None:
            return

        try:
            # Convert rotation value to float if it's not already
            if isinstance(rotation_value, (int, float)):
                # python-pptx expects rotation in degrees
                shape.rotation = float(rotation_value)
            elif isinstance(rotation_value, str):
                # Try to parse string rotation value
                rotation_degrees = float(rotation_value)
                shape.rotation = rotation_degrees

        except Exception as e:
            print(
                f"Warning: Could not apply rotation {rotation_value}: {str(e)}")

    def apply_shadow_properties(self, shape, shadow_info: Dict[str, Any]):
        """Apply shadow properties from enhanced extractor data"""
        if not shadow_info:
            return

        try:
            # python-pptx has limited shadow support, but we can apply what's available
            if hasattr(shape, 'shadow'):
                shadow = shape.shadow

                # Apply shadow visibility
                if 'visible' in shadow_info and shadow_info['visible'] is not None:
                    shadow.inherit = not shadow_info['visible']

                # Apply shadow style if available
                if 'style' in shadow_info and hasattr(shadow, 'style'):
                    # Map shadow style strings to enums
                    style_str = shadow_info['style'].upper()
                    if 'OUTER' in style_str and hasattr(shadow, 'style'):
                        from pptx.enum.dml import MSO_SHADOW_TYPE
                        try:
                            shadow.style = MSO_SHADOW_TYPE.OUTER
                        except:
                            pass

                # Apply blur radius if available
                if 'blur_radius' in shadow_info and hasattr(shadow, 'blur_radius'):
                    try:
                        blur_value = shadow_info['blur_radius']
                        if isinstance(blur_value, (int, float)):
                            shadow.blur_radius = Emu(int(blur_value))
                    except:
                        pass

                # Apply distance if available
                if 'distance' in shadow_info and hasattr(shadow, 'distance'):
                    try:
                        distance_value = shadow_info['distance']
                        if isinstance(distance_value, (int, float)):
                            shadow.distance = Emu(int(distance_value))
                    except:
                        pass

                # Apply direction/angle if available
                if 'direction' in shadow_info and hasattr(shadow, 'direction'):
                    try:
                        direction_value = shadow_info['direction']
                        if isinstance(direction_value, (int, float)):
                            shadow.direction = float(direction_value)
                    except:
                        pass

                # Apply shadow color if available
                if 'color' in shadow_info and hasattr(shadow, 'color'):
                    try:
                        color_info = shadow_info['color']
                        self.apply_enhanced_color(shadow.color, color_info)
                    except:
                        pass

                # Apply transparency/alpha if available
                if 'transparency' in shadow_info and hasattr(shadow, 'transparency'):
                    try:
                        transparency_value = shadow_info['transparency']
                        if isinstance(transparency_value, (int, float)):
                            # Convert percentage to decimal (0-100% -> 0.0-1.0)
                            shadow.transparency = transparency_value / 100.0
                    except:
                        pass

        except Exception as e:
            print(f"Warning: Could not apply shadow properties: {str(e)}")

    def create_enhanced_picture(self, slide, shape_info: Dict[str, Any]):
        """Create picture shape with actual image embedding from enhanced extractor data"""
        left = Inches(self.emu_to_inches(shape_info['left']))
        top = Inches(self.emu_to_inches(shape_info['top']))
        width = Inches(self.emu_to_inches(shape_info['width']))
        height = Inches(self.emu_to_inches(shape_info['height']))

        try:
            # Try to get image data from enhanced extractor
            image_properties = shape_info.get('image_properties', {})
            media_key = image_properties.get(
                'media_key') or image_properties.get('filename')

            if media_key and media_key in self.media_cache:
                # Get image data from cache
                media_info = self.media_cache[media_key]
                image_data_b64 = media_info.get('data')

                if image_data_b64:
                    # Decode base64 image data
                    image_data = base64.b64decode(image_data_b64)

                    # Create BytesIO stream for python-pptx
                    image_stream = io.BytesIO(image_data)

                    # Add picture to slide
                    picture = slide.shapes.add_picture(
                        image_stream, left, top, width, height)

                    # Apply rotation if specified
                    self.apply_rotation(picture, shape_info.get('rotation'))

                    print(f"Successfully embedded image: {media_key}")
                    return picture

            # Fallback: create placeholder if no image data available
            return self.create_picture_placeholder(slide, shape_info)

        except Exception as e:
            print(f"Warning: Could not embed image {media_key}: {str(e)}")
            # Fallback to placeholder
            return self.create_picture_placeholder(slide, shape_info)

    def apply_enhanced_gradient_fill(self, shape, gradient_info: Dict[str, Any]):
        """Apply enhanced gradient fill properties from enhanced extractor data"""
        if not gradient_info:
            return

        try:
            # python-pptx has limited gradient support, but we can apply basic gradients
            shape.fill.gradient()

            # Apply gradient stops if available
            gradient_stops = gradient_info.get('gradient_stops', [])
            if gradient_stops and hasattr(shape.fill, 'gradient_stops'):
                # Clear existing stops and add new ones
                stops = shape.fill.gradient_stops
                stops.clear()

                for stop_info in gradient_stops:
                    position = stop_info.get('position', 0.0)
                    color_info = stop_info.get('color', {})

                    # Add gradient stop
                    stop = stops.add_gradient_stop(position)
                    if color_info:
                        self.apply_enhanced_color(stop.color, color_info)

            # Apply gradient angle if available
            gradient_angle = gradient_info.get('gradient_angle')
            if gradient_angle is not None and hasattr(shape.fill, 'gradient_angle'):
                try:
                    shape.fill.gradient_angle = gradient_angle
                except:
                    pass

        except Exception as e:
            print(f"Warning: Could not apply enhanced gradient: {str(e)}")
            # Fallback to solid fill
            shape.fill.solid()

    def save_presentation(self, output_file: str):
        """Save the presentation to file"""
        self.presentation.save(output_file)
        print(f"\nPresentation saved to: {output_file}")
        print(f"Total slides: {len(self.presentation.slides)}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate PowerPoint presentation from JSON files with enhanced fidelity'
    )
    parser.add_argument('shapes_file', help='Path to shapes JSON file')
    parser.add_argument('layouts_file', help='Path to layouts JSON file')
    parser.add_argument('theme_file', help='Path to theme JSON file')
    parser.add_argument(
        '--media-file', help='Path to media JSON file (optional)')
    parser.add_argument('--properties-file',
                        help='Path to properties JSON file (optional)')
    parser.add_argument('--output', '-o', default='generated_presentation.pptx',
                        help='Output PowerPoint file name (default: generated_presentation.pptx)')

    args = parser.parse_args()

    # Validate required input files
    for file_path in [args.shapes_file, args.layouts_file, args.theme_file]:
        if not Path(file_path).exists():
            print(f"Error: File '{file_path}' does not exist.")
            sys.exit(1)

    # Validate optional files if provided
    if args.media_file and not Path(args.media_file).exists():
        print(
            f"Warning: Media file '{args.media_file}' does not exist, skipping media integration.")
        args.media_file = None

    if args.properties_file and not Path(args.properties_file).exists():
        print(
            f"Warning: Properties file '{args.properties_file}' does not exist, skipping properties integration.")
        args.properties_file = None

    try:
        # Initialize generator
        generator = PPTGenerator()

        # Load JSON data including optional enhanced files
        print("Loading JSON files...")
        generator.load_json_files(
            args.shapes_file,
            args.layouts_file,
            args.theme_file,
            media_file=args.media_file,
            properties_file=args.properties_file
        )

        # Generate slides with enhanced fidelity
        print("\nGenerating presentation...")
        generator.generate_slides()

        # Save presentation
        generator.save_presentation(args.output)

        print(f"\nPresentation generation completed successfully!")
        print(f"Enhanced features applied:")
        print(f"  - 100+ shape types supported")
        print(f"  - Enhanced fill properties (solid, gradient, pattern)")
        print(f"  - Theme color and font preservation")
        print(f"  - Improved chart type support")
        print(f"  - Better table formatting")
        print(f"  - Intelligent layout selection")
        print(f"  - Custom geometry support (fallback)")
        if args.media_file:
            print(f"  - Real image embedding from media data")
        if args.properties_file:
            print(f"  - Document properties integration")

    except Exception as e:
        print(f"Error generating presentation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()