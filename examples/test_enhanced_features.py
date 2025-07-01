#!/usr/bin/env python3

import json
from pathlib import Path

def test_chart_table_support():
    """Test the new chart and table support functionality"""
    
    # Test shape data with chart information
    test_shapes_data = [
        {
            "slide_index": 0,
            "shapes": [
                {
                    "slide_index": 0,
                    "shape_index": 0,
                    "shape_id": 1,
                    "name": "Test Chart",
                    "shape_type": "CHART (3)",
                    "left": 1000000,
                    "top": 1000000,
                    "width": 5000000,
                    "height": 3000000,
                    "chart_data": {
                        "chart_type": "COLUMN_CLUSTERED",
                        "title": "Sales Data",
                        "categories": ["Q1", "Q2", "Q3", "Q4"],
                        "series": [
                            {
                                "name": "Revenue",
                                "values": [100, 120, 140, 160]
                            },
                            {
                                "name": "Profit",
                                "values": [20, 25, 30, 35]
                            }
                        ],
                        "has_legend": True
                    }
                },
                {
                    "slide_index": 0,
                    "shape_index": 1,
                    "shape_id": 2,
                    "name": "Test Table",
                    "shape_type": "TABLE (19)",
                    "left": 1000000,
                    "top": 5000000,
                    "width": 6000000,
                    "height": 2000000,
                    "table_data": {
                        "rows": 3,
                        "columns": 3,
                        "data": [
                            ["Product", "Q1 Sales", "Q2 Sales"],
                            ["Widget A", "1000", "1200"],
                            ["Widget B", "800", "950"]
                        ]
                    }
                },
                {
                    "slide_index": 0,
                    "shape_index": 2,
                    "shape_id": 3,
                    "name": "Test Text Box",
                    "shape_type": "TEXT_BOX (17)",
                    "left": 500000,
                    "top": 500000,
                    "width": 3000000,
                    "height": 1000000,
                    "text": "This is a test text box with enhanced formatting support."
                }
            ]
        }
    ]
    
    # Test layouts data
    test_layouts_data = [
        {
            "layout_index": 0,
            "name": "Blank",
            "placeholders": []
        }
    ]
    
    # Test theme data
    test_theme_data = {
        "theme_name": "Test Theme",
        "slide_master": {
            "name": "Test Master",
            "background": None
        },
        "color_scheme": {},
        "font_scheme": {}
    }
    
    # Save test files
    output_dir = Path(".")
    
    with open(output_dir / "test_shapes.json", 'w', encoding='utf-8') as f:
        json.dump(test_shapes_data, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / "test_layouts.json", 'w', encoding='utf-8') as f:
        json.dump(test_layouts_data, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / "test_theme.json", 'w', encoding='utf-8') as f:
        json.dump(test_theme_data, f, indent=2, ensure_ascii=False)
    
    print("Test data files created successfully!")
    print("- test_shapes.json (with chart, table, and text box data)")
    print("- test_layouts.json")
    print("- test_theme.json")
    print("\nTo test the enhanced features, run:")
    print("python ppt_generator.py test_shapes.json test_layouts.json test_theme.json --output test_enhanced.pptx")

if __name__ == "__main__":
    test_chart_table_support()