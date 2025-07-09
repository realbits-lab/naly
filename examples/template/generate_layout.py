#!/usr/bin/env python3
"""
Generate a PowerPoint file with custom slide using available layouts.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.shapes import PP_PLACEHOLDER


def generate_default_powerpoint():
    """Generate a default PowerPoint presentation with python-pptx library."""
    # Check if blank.pptx exists in the current directory
    blank_path = os.path.join(os.path.dirname(__file__), "blank.pptx")
    if os.path.exists(blank_path):
        prs = Presentation(blank_path)
    else:
        # Create a blank presentation if blank.pptx doesn't exist
        prs = Presentation()

    # Add a slide using an existing layout with placeholders
    add_custom_layout(prs)

    return prs


def add_custom_layout(prs):
    """Add a slide using an existing layout and demonstrate adding content."""
    # Get an existing layout that has title and content placeholders
    # Most presentations have a title and content layout
    layout = None
    for slide_layout in prs.slide_layouts:
        if len(slide_layout.placeholders) >= 2:
            layout = slide_layout
            break

    if layout is None:
        # Fallback to first layout if no suitable layout found
        layout = prs.slide_layouts[0]

    # Add a slide using this layout
    slide = prs.slides.add_slide(layout)

    # Try to populate placeholders if they exist
    if len(layout.placeholders) > 0:
        # Usually placeholder 0 is the title
        title_placeholder = layout.placeholders[0]
        if hasattr(title_placeholder, 'text'):
            title_placeholder.text = "Custom Layout Example"

    if len(layout.placeholders) > 1:
        # Usually placeholder 1 is the content
        content_placeholder = layout.placeholders[1]
        if hasattr(content_placeholder, 'text'):
            content_placeholder.text = "This demonstrates using existing layouts with placeholders."

    print(
        f"Added slide using layout with {len(layout.placeholders)} placeholders")
    return layout


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
    """Main function to generate PowerPoint with custom slide."""
    print("Generating PowerPoint presentation...")

    # Generate the presentation
    prs = generate_default_powerpoint()

    # Save to file
    save_powerpoint(prs)

    print("\n=== Summary ===")
    print(f"Total slides: {len(prs.slides)}")
    print(f"Total slide layouts: {len(prs.slide_layouts)}")

    # Show information about the layouts
    if len(prs.slide_layouts) > 0:
        layout = prs.slide_layouts[0]
        print(f"First layout name: {layout.name}")
        print(f"First layout placeholders: {len(layout.placeholders)}")

    print("Presentation created successfully!")


if __name__ == "__main__":
    main()
