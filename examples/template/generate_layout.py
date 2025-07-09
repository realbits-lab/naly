#!/usr/bin/env python3
"""
Generate a default PowerPoint file and analyze the first layout attributes.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.shapes import PP_PLACEHOLDER


def generate_default_powerpoint():
    """Generate a default PowerPoint presentation with python-pptx library."""
    prs = Presentation("blank.pptx")

    # Add a new layout with title and graphic frame placeholders
    add_custom_layout(prs)

    return prs


def add_custom_layout(prs):
    """Add a custom layout with title and graphic frame placeholders."""
    # Get the slide master
    slide_master = prs.slide_masters[0]

    # Create a new slide layout
    custom_layout = slide_master.slide_layouts.add_slide_layout(
        name="Custom Layout")

    # Add title placeholder
    title_placeholder = custom_layout.placeholders.add_placeholder(
        placeholder_type=PP_PLACEHOLDER.TITLE,
        left=Inches(1),
        top=Inches(0.5),
        width=Inches(8),
        height=Inches(1.5)
    )

    # Add graphic frame placeholder (for charts, tables, etc.)
    graphic_placeholder = custom_layout.placeholders.add_placeholder(
        placeholder_type=PP_PLACEHOLDER.OBJECT,
        left=Inches(1),
        top=Inches(2.5),
        width=Inches(8),
        height=Inches(5)
    )

    print(
        f"Added custom layout with {len(custom_layout.placeholders)} placeholders")
    return custom_layout


def save_powerpoint(prs, filename="default_template.pptx"):
    """Save the PowerPoint presentation to a file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)

    # Check if file exists
    if os.path.exists(filepath):
        print(f"File {filename} already exists. Replacing it.")
        os.remove(filepath)

    # Save the presentation
    prs.save(filepath)
    print(f"PowerPoint saved as: {filepath}")

    # Show file info
    file_size = os.path.getsize(filepath)
    print(f"File size: {file_size} bytes")


def main():
    """Main function to generate PowerPoint and analyze layout."""
    print("Generating default PowerPoint presentation...")

    # Generate the presentation
    prs = generate_default_powerpoint()

    # Save to file
    save_powerpoint(prs)

    print("\n=== Summary ===")
    print(f"Total slides: {len(prs.slides)}")
    print(f"Total slide layouts: {len(prs.slide_layouts)}")

    # Show information about the custom layout
    if len(prs.slide_layouts) > 0:
        custom_layout = prs.slide_layouts[-1]  # Last added layout
        print(f"Custom layout name: {custom_layout.name}")
        print(f"Custom layout placeholders: {len(custom_layout.placeholders)}")

    print("Presentation created successfully!")


if __name__ == "__main__":
    main()
