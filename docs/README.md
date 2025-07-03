# PowerPoint Fidelity Testing Framework

This directory contains a comprehensive testing framework for analyzing and improving the fidelity of PowerPoint extraction and regeneration using the enhanced extractor and generator tools.

## Overview

The framework provides tools to:
- **Compare** original and generated PowerPoint files at the structural level
- **Analyze** differences in XML content, media files, and document properties
- **Track** fidelity improvements across iterations
- **Identify** specific areas needing improvement
- **Generate** detailed reports with actionable recommendations

## Quick Start

### 1. Basic Comparison

Compare an original PowerPoint file with a generated one:

```bash
# Make scripts executable (first time only)
chmod +x compare_pptx_structures.sh iterative_testing.sh
chmod +x analyze_xml_differences.py

# Run comparison
./compare_pptx_structures.sh ../examples/sample1.pptx ../examples/sample1_enhanced.pptx
```

This will generate a detailed comparison report with fidelity scores.

### 2. Iterative Testing

Run multiple test iterations to progressively improve fidelity:

```bash
./iterative_testing.sh
```

This will:
- Extract data from the test file
- Generate enhanced PowerPoint
- Compare structures and calculate fidelity
- Provide recommendations for improvements
- Track progress across iterations

### 3. XML Analysis

Analyze specific XML differences between files:

```bash
# Single file analysis
python analyze_xml_differences.py \
  comparison_*/original_structure/ppt/slides/slide1.xml \
  comparison_*/generated_structure/ppt/slides/slide1.xml

# Batch analysis of all XML files
python analyze_xml_differences.py --batch \
  comparison_*/original_structure \
  comparison_*/generated_structure \
  --output xml_analysis_results.json
```

## File Structure

```
docs/
├── README.md                           # This file
├── powerpoint-fidelity-testing-guide.md # Comprehensive testing guide
├── compare_pptx_structures.sh          # Main comparison script
├── analyze_xml_differences.py          # XML analysis tool
├── iterative_testing.sh               # Iterative testing framework
└── comparison_*/                       # Generated comparison results
    ├── comparison_report.md            # Main analysis report
    ├── original_structure/             # Extracted original PPTX
    ├── generated_structure/            # Extracted generated PPTX
    ├── statistics.txt                  # Numerical statistics
    ├── xml_analysis.txt               # XML comparison details
    └── media_analysis.txt             # Media file analysis
```

## Understanding Fidelity Scores

The framework calculates weighted fidelity scores:

| Component | Weight | Description |
|-----------|--------|-------------|
| **XML Content** | 50% | Core PowerPoint structure and formatting |
| **File Structure** | 20% | Presence of required files and relationships |
| **Media Preservation** | 20% | Images, audio, video file integrity |
| **Directory Structure** | 10% | Basic PPTX container structure |

### Score Interpretation

- **90-100%**: Excellent fidelity, minor differences only
- **75-89%**: Good fidelity, some missing features
- **60-74%**: Moderate fidelity, significant gaps
- **40-59%**: Poor fidelity, major structural issues
- **< 40%**: Critical fidelity problems

## Testing Methodology

### Phase 1: Structure Comparison

1. **Extract PPTX contents** by converting to ZIP and unzipping
2. **Compare directory structures** for missing/extra directories
3. **Compare file lists** for missing/extra files
4. **Analyze file sizes** for content integrity

### Phase 2: XML Analysis

1. **Parse XML files** using ElementTree
2. **Compare namespaces** for proper declarations
3. **Compare element structures** for missing/extra elements
4. **Compare attributes** for proper formatting preservation
5. **Analyze critical elements** specific to PowerPoint structure

### Phase 3: Media Analysis

1. **Extract media files** from ppt/media/ directories
2. **Calculate file hashes** for integrity verification
3. **Compare file sizes** and formats
4. **Verify embedding** relationships

### Phase 4: Content Analysis

1. **Extract text content** from XML elements
2. **Compare formatting** properties and styles
3. **Analyze relationships** between slides, masters, layouts
4. **Verify theme** color and font preservation

## Common Issues and Solutions

### Issue: Low XML Fidelity (< 70%)

**Symptoms:**
- Missing XML elements in generated files
- Incorrect namespace declarations
- Missing attributes or properties

**Solutions:**
1. Review `ppt_extractor.py` for complete XML element extraction
2. Enhance `ppt_generator_enhanced.py` XML generation logic
3. Ensure proper namespace handling
4. Add missing relationship creation

**Code Examples:**
```python
# In ppt_extractor.py - Extract missing elements
def extract_slide_transitions(self, slide):
    """Extract slide transition information"""
    transitions = {}
    if hasattr(slide, 'slide_transition'):
        transitions['type'] = slide.slide_transition.type
        transitions['speed'] = slide.slide_transition.speed
    return transitions

# In ppt_generator_enhanced.py - Generate missing elements  
def apply_slide_transitions(self, slide, transition_info):
    """Apply slide transitions from extracted data"""
    if transition_info and hasattr(slide, 'slide_transition'):
        if 'type' in transition_info:
            slide.slide_transition.type = transition_info['type']
```

### Issue: Low Media Preservation (< 50%)

**Symptoms:**
- Missing images in generated presentation
- Corrupted media files
- Incorrect file sizes

**Solutions:**
1. Verify base64 encoding/decoding in extractor
2. Improve media embedding in generator
3. Ensure proper relationship creation
4. Test with various media formats

**Code Examples:**
```python
# Fix media embedding with proper relationships
def embed_media_with_relationships(self, slide, media_info):
    try:
        media_data = base64.b64decode(media_info['data'])
        image_stream = io.BytesIO(media_data)
        
        # Add picture with proper relationship
        picture = slide.shapes.add_picture(
            image_stream, 
            Inches(media_info['left']), 
            Inches(media_info['top']),
            Inches(media_info['width']), 
            Inches(media_info['height'])
        )
        
        return picture
    except Exception as e:
        print(f"Media embedding failed: {e}")
        return None
```

### Issue: Low File Structure Fidelity (< 80%)

**Symptoms:**
- Missing relationship files (.rels)
- Missing content type definitions
- Incorrect directory structure

**Solutions:**
1. Extract complete document relationships
2. Generate all required PPTX files
3. Ensure proper content type mappings
4. Create missing directories

## Advanced Usage

### Custom Test Files

To test with your own PowerPoint files:

1. Place your test file in `examples/` directory
2. Update the test file name in scripts
3. Run the testing framework

### Batch Testing

Test multiple files simultaneously:

```bash
# Create batch test script
for file in examples/*.pptx; do
    base_name=$(basename "$file" .pptx)
    echo "Testing $base_name..."
    
    # Extract
    python examples/ppt_extractor.py "$file"
    
    # Generate
    python examples/ppt_generator_enhanced.py \
        "${base_name}_shapes.json" \
        "${base_name}_layouts.json" \
        "${base_name}_theme.json" \
        --media-file "${base_name}_media.json" \
        --properties-file "${base_name}_properties.json" \
        --output "${base_name}_generated.pptx"
    
    # Compare
    ./docs/compare_pptx_structures.sh "$file" "${base_name}_generated.pptx"
done
```

### Custom Analysis

Extend the XML analysis for specific PowerPoint features:

```python
# Add custom critical elements
custom_critical_elements = {
    'ppt/slides/slide1.xml': [
        'p:sld/p:cSld/p:spTree/p:sp[contains(@type,"chart")]',
        'p:sld/p:cSld/p:spTree/p:sp[contains(@type,"table")]',
        'p:sld/p:cSld/p:spTree/p:sp/p:spPr/a:xfrm/@rot'  # Rotation
    ]
}
```

## Performance Considerations

### Large Files

For large PowerPoint files (> 50MB):
- Use `--summary` flag for faster analysis
- Limit XML analysis depth
- Process slides in batches

### Memory Usage

Monitor memory usage for presentations with many slides:
- Use streaming XML parsing for large files
- Process media files individually
- Clear caches between iterations

## Integration with Development Workflow

### Pre-commit Testing

Add fidelity testing to your development workflow:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running PowerPoint fidelity tests..."
./docs/compare_pptx_structures.sh examples/sample1.pptx examples/sample1_test.pptx

# Extract fidelity score
fidelity=$(grep "Overall Fidelity Score:" comparison_*/comparison_report.md | grep -o '[0-9]*%' | grep -o '[0-9]*')

if [ "$fidelity" -lt 75 ]; then
    echo "❌ Fidelity too low: ${fidelity}%. Minimum required: 75%"
    exit 1
fi

echo "✅ Fidelity test passed: ${fidelity}%"
```

### CI/CD Integration

For continuous integration:

```yaml
# .github/workflows/fidelity-test.yml
name: PowerPoint Fidelity Test
on: [push, pull_request]

jobs:
  test-fidelity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install python-pptx
      - name: Run fidelity tests
        run: |
          cd docs
          ./iterative_testing.sh
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: fidelity-results
          path: docs/iterative_test_*/
```

## Troubleshooting

### Common Errors

**Error: "xmllint command not found"**
```bash
# Install xmllint (optional, used for pretty XML formatting)
# macOS:
brew install libxml2
# Ubuntu:
sudo apt-get install libxml2-utils
```

**Error: "Permission denied"**
```bash
# Make scripts executable
chmod +x docs/*.sh docs/*.py
```

**Error: "python-pptx module not found"**
```bash
# Install required Python package
pip install python-pptx
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Set debug mode
export DEBUG=1
./compare_pptx_structures.sh sample1.pptx sample1_enhanced.pptx
```

## Contributing

To contribute improvements to the testing framework:

1. Test your changes with multiple PowerPoint files
2. Ensure backward compatibility
3. Update documentation for new features
4. Add test cases for new functionality

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review existing comparison reports for similar issues
3. Create detailed issue reports with sample files
4. Include fidelity scores and specific error messages

---

*This testing framework is designed to help achieve 85%+ PowerPoint reconstruction fidelity through systematic analysis and improvement.*