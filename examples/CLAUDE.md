# CLAUDE.md - Python-PPTX Examples

This file provides guidance to Claude Code when working with the Python-PPTX examples in this directory.

## Overview

This directory contains Python scripts that demonstrate the usage of the python-pptx library for creating and extracting data from PowerPoint presentations.

## Python-PPTX Documentation

For comprehensive guidance on handling the python-pptx library, please refer to:
- [Python-PPTX Handling Guide](../docs/python-pptx-handling.md)

## Directory Contents

- `ppt_generator.py` - Script for generating PowerPoint presentations programmatically
- `ppt_extractor.py` - Script for extracting data from existing PowerPoint files
- `test_enhanced_features.py` - Test script demonstrating advanced features
- `pyproject.toml` - Python project configuration with dependencies
- `sample1.pptx` - Sample PowerPoint file for testing extraction

## Development Guidelines

### 1. Environment Setup
```bash
# Install dependencies from pyproject.toml
pip install -e .
# Or install python-pptx directly
pip install python-pptx
```

### 2. Running Scripts
```bash
# Generate a new presentation
python ppt_generator.py

# Extract data from a presentation
python ppt_extractor.py sample1.pptx

# Test enhanced features
python test_enhanced_features.py
```

### 3. Code Style
- Follow PEP 8 conventions
- Use type hints where applicable
- Add docstrings to functions and classes
- Handle exceptions appropriately

### 4. Common Tasks

#### Creating a New Generator Script
1. Import necessary modules from pptx
2. Create a Presentation object
3. Add slides with appropriate layouts
4. Add content (text, images, charts, tables)
5. Save the presentation

#### Creating a New Extractor Script
1. Load the presentation file
2. Iterate through slides
3. Check shape types and extract data
4. Format and output the extracted data

### 5. Best Practices for This Project

1. **File Paths**: Use relative paths for input/output files
2. **Error Handling**: Always check if files exist before processing
3. **Output**: Save generated files in the examples directory
4. **Logging**: Use print statements to show progress
5. **Testing**: Test with sample1.pptx before using other files

### 6. Important Notes

- The python-pptx library requires Python 3.6 or later
- Some features may require specific PowerPoint versions
- Binary files (.pptx) should not be committed if they contain sensitive data
- Always validate input files before processing

### 7. Troubleshooting

If you encounter issues:
1. Check that python-pptx is installed correctly
2. Verify file permissions for reading/writing
3. Ensure PowerPoint files are not corrupted
4. Check Python version compatibility
5. Review the main documentation at ../docs/python-pptx-handling.md