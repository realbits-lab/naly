# Python-PPTX Library Handling Guide

This guide provides comprehensive instructions for working with the python-pptx library in the Naly project.

## Overview

The python-pptx library is a Python library for creating and updating PowerPoint (.pptx) files. This project uses it to programmatically generate and extract data from PowerPoint presentations.

## Installation

```bash
pip install python-pptx
```

## Core Concepts

### 1. Presentation Structure
- **Presentation**: The main container for all slides
- **Slide**: Individual pages in the presentation
- **Slide Layout**: Pre-defined arrangement of placeholders
- **Shapes**: Objects on a slide (text boxes, images, charts, tables, etc.)
- **Placeholders**: Pre-defined areas in layouts for content

### 2. Working with Presentations

#### Creating a New Presentation
```python
from pptx import Presentation

# Create a new presentation
prs = Presentation()

# Or use a template
prs = Presentation('template.pptx')
```

#### Adding Slides
```python
# Get available slide layouts
slide_layouts = prs.slide_layouts

# Add a slide with title layout
title_slide_layout = slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)

# Access placeholders
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Hello World"
subtitle.text = "python-pptx was here!"
```

### 3. Working with Shapes

#### Text Boxes
```python
from pptx.util import Inches, Pt

# Add a text box
left = Inches(1)
top = Inches(2)
width = Inches(4)
height = Inches(1)
textbox = slide.shapes.add_textbox(left, top, width, height)
text_frame = textbox.text_frame

# Add paragraphs and runs
p = text_frame.add_paragraph()
run = p.add_run()
run.text = "Bold text"
run.font.bold = True
run.font.size = Pt(18)
```

#### Tables
```python
# Add a table
rows, cols = 3, 3
left = Inches(1)
top = Inches(2)
width = Inches(6)
height = Inches(2)
table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Access cells
cell = table.cell(0, 0)
cell.text = "Header"
```

#### Charts
```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# Define chart data
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Series 1', (19.2, 21.4, 16.7, 22.3))

# Add chart to slide
x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart
```

#### Images
```python
# Add an image
img_path = 'picture.png'
left = Inches(1)
top = Inches(1)
pic = slide.shapes.add_picture(img_path, left, top)

# Resize image
pic.height = Inches(3)
pic.width = Inches(4)
```

### 4. Advanced Features

#### Auto Shapes
```python
from pptx.enum.shapes import MSO_SHAPE

# Add various shapes
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    left=Inches(1), top=Inches(1),
    width=Inches(2), height=Inches(1)
)
shape.text = "Rounded Rectangle"
```

#### Connectors
```python
from pptx.enum.shapes import MSO_CONNECTOR

# Add connector between shapes
connector = slide.shapes.add_connector(
    MSO_CONNECTOR.STRAIGHT,
    begin_x=Inches(1), begin_y=Inches(1),
    end_x=Inches(3), end_y=Inches(2)
)
```

### 5. Extracting Data from Presentations

```python
# Open existing presentation
prs = Presentation('existing.pptx')

# Iterate through slides
for slide in prs.slides:
    # Iterate through shapes
    for shape in slide.shapes:
        # Check shape type
        if shape.has_text_frame:
            print(shape.text)
        
        if shape.has_table:
            table = shape.table
            for row in table.rows:
                for cell in row.cells:
                    print(cell.text)
        
        if shape.has_chart:
            chart = shape.chart
            print(f"Chart type: {chart.chart_type}")
```

### 6. Best Practices

1. **Memory Management**: When working with large presentations, process slides one at a time
2. **Error Handling**: Always wrap file operations in try-except blocks
3. **Template Usage**: Use templates for consistent styling
4. **Shape Positioning**: Use Inches() or Cm() for precise positioning
5. **Font Management**: Check if fonts are available on the target system

### 7. Common Issues and Solutions

#### Issue: Cannot find specific placeholder
```python
# List all placeholders
for shape in slide.placeholders:
    print(f"idx: {shape.placeholder_format.idx}, type: {shape.placeholder_format.type}")
```

#### Issue: Chart data not updating
```python
# Replace chart data completely
chart.replace_data(new_chart_data)
```

#### Issue: Text formatting lost
```python
# Preserve formatting by working with runs
for paragraph in shape.text_frame.paragraphs:
    for run in paragraph.runs:
        # Modify run.text instead of paragraph.text
        run.text = run.text.upper()
```

### 8. Performance Tips

1. **Batch Operations**: Group similar operations together
2. **Lazy Loading**: Only load slides/shapes when needed
3. **Template Reuse**: Create base templates for common layouts
4. **Image Optimization**: Compress images before adding to presentations

### 9. Integration with Naly Project

The Naly project uses python-pptx in the `examples/` directory for:
- Generating sample presentations (`ppt_generator.py`)
- Extracting data from presentations (`ppt_extractor.py`)
- Testing enhanced features (`test_enhanced_features.py`)

When working with these scripts:
1. Ensure python-pptx is installed in your environment
2. Check the pyproject.toml for specific version requirements
3. Run scripts from the examples directory
4. Output files will be created in the same directory

### 10. Resources

- [Official Documentation](https://python-pptx.readthedocs.io/)
- [GitHub Repository](https://github.com/scanny/python-pptx)
- [API Reference](https://python-pptx.readthedocs.io/en/latest/api/slides.html)