# PowerPoint Fidelity Testing and Analysis Guide

## Overview

This guide provides a comprehensive methodology for testing and improving the fidelity of PowerPoint extraction and regeneration using the enhanced extractor and generator tools. The process involves deep structural comparison of PPTX files to identify gaps and drive improvements.

## Testing Methodology

### 1. File Preparation and Extraction

```bash
# Step 1: Extract data from original PowerPoint file
cd examples/
python ppt_extractor.py sample1.pptx

# This generates:
# - sample1_shapes.json
# - sample1_layouts.json  
# - sample1_theme.json
# - sample1_media.json
# - sample1_properties.json
# - sample1_summary.json
```

### 2. Generate Enhanced PowerPoint

```bash
# Step 2: Generate enhanced PowerPoint from extracted data
python ppt_generator_enhanced.py \
  sample1_shapes.json \
  sample1_layouts.json \
  sample1_theme.json \
  --media-file sample1_media.json \
  --properties-file sample1_properties.json \
  --output sample1_enhanced.pptx
```

### 3. Deep Structure Comparison

#### 3.1 Convert PPTX to ZIP Format

```bash
# Create comparison directory
mkdir -p comparison_analysis/
cd comparison_analysis/

# Copy files and rename to .zip
cp ../sample1.pptx original.zip
cp ../sample1_enhanced.pptx generated.zip

# Extract ZIP contents
mkdir original_structure generated_structure
cd original_structure && unzip ../original.zip && cd ..
cd generated_structure && unzip ../generated.zip && cd ..
```

#### 3.2 Directory Structure Analysis

```bash
# Compare directory structures
find original_structure -type d | sort > original_dirs.txt
find generated_structure -type d | sort > generated_dirs.txt
diff original_dirs.txt generated_dirs.txt > directory_diff.txt

# Compare file listings
find original_structure -type f | sort > original_files.txt
find generated_structure -type f | sort > generated_files.txt
diff original_files.txt generated_files.txt > file_diff.txt
```

#### 3.3 XML Content Comparison

```bash
# Compare XML files
for xml_file in $(find original_structure -name "*.xml" -o -name "*.rels"); do
    relative_path=$(echo $xml_file | sed 's|original_structure/||')
    if [ -f "generated_structure/$relative_path" ]; then
        echo "=== Comparing $relative_path ===" >> xml_comparison.txt
        diff "$xml_file" "generated_structure/$relative_path" >> xml_comparison.txt
        echo "" >> xml_comparison.txt
    else
        echo "Missing file in generated: $relative_path" >> missing_files.txt
    fi
done
```

#### 3.4 Media Content Analysis

```bash
# Compare media files
mkdir -p media_comparison/
cp original_structure/ppt/media/* media_comparison/original/ 2>/dev/null || echo "No media in original"
cp generated_structure/ppt/media/* media_comparison/generated/ 2>/dev/null || echo "No media in generated"

# Compare media file sizes and types
ls -la media_comparison/original/ > original_media_info.txt
ls -la media_comparison/generated/ > generated_media_info.txt
diff original_media_info.txt generated_media_info.txt > media_diff.txt
```

## Analysis Scripts

### 4.1 Automated Comparison Script

```bash
#!/bin/bash
# File: compare_pptx_structures.sh

compare_pptx_files() {
    local original=$1
    local generated=$2
    local output_dir="comparison_$(date +%Y%m%d_%H%M%S)"
    
    echo "Starting PPTX structure comparison..."
    mkdir -p "$output_dir"
    cd "$output_dir"
    
    # Convert and extract
    cp "../$original" original.zip
    cp "../$generated" generated.zip
    
    mkdir original_structure generated_structure
    cd original_structure && unzip ../original.zip >/dev/null 2>&1 && cd ..
    cd generated_structure && unzip ../generated.zip >/dev/null 2>&1 && cd ..
    
    # Directory comparison
    echo "Analyzing directory structures..."
    find original_structure -type d | sort > original_dirs.txt
    find generated_structure -type d | sort > generated_dirs.txt
    diff original_dirs.txt generated_dirs.txt > directory_diff.txt
    
    # File comparison
    echo "Analyzing file structures..."
    find original_structure -type f | sort > original_files.txt
    find generated_structure -type f | sort > generated_files.txt
    diff original_files.txt generated_files.txt > file_diff.txt
    
    # XML analysis
    echo "Analyzing XML content..."
    analyze_xml_differences
    
    # Media analysis
    echo "Analyzing media content..."
    analyze_media_differences
    
    # Generate report
    generate_comparison_report
    
    echo "Comparison complete. Results in $output_dir/"
}

analyze_xml_differences() {
    echo "=== XML CONTENT ANALYSIS ===" > xml_analysis.txt
    
    # Key XML files to analyze
    local key_files=(
        "ppt/presentation.xml"
        "ppt/slides/slide1.xml"
        "ppt/slideLayouts/slideLayout1.xml"
        "ppt/slideMasters/slideMaster1.xml"
        "ppt/theme/theme1.xml"
        "docProps/core.xml"
        "docProps/app.xml"
    )
    
    for file in "${key_files[@]}"; do
        if [ -f "original_structure/$file" ] && [ -f "generated_structure/$file" ]; then
            echo "--- $file ---" >> xml_analysis.txt
            # Use xmllint for pretty printing and comparison
            xmllint --format "original_structure/$file" > "orig_$file.formatted" 2>/dev/null
            xmllint --format "generated_structure/$file" > "gen_$file.formatted" 2>/dev/null
            diff "orig_$file.formatted" "gen_$file.formatted" >> xml_analysis.txt
            echo "" >> xml_analysis.txt
        else
            echo "Missing: $file" >> xml_analysis.txt
        fi
    done
}

analyze_media_differences() {
    echo "=== MEDIA CONTENT ANALYSIS ===" > media_analysis.txt
    
    # Compare media directories
    if [ -d "original_structure/ppt/media" ]; then
        echo "Original media files:" >> media_analysis.txt
        ls -la original_structure/ppt/media/ >> media_analysis.txt
        
        # Calculate file hashes for integrity check
        find original_structure/ppt/media -type f -exec md5sum {} \; > original_media_hashes.txt
    fi
    
    if [ -d "generated_structure/ppt/media" ]; then
        echo "Generated media files:" >> media_analysis.txt
        ls -la generated_structure/ppt/media/ >> media_analysis.txt
        
        find generated_structure/ppt/media -type f -exec md5sum {} \; > generated_media_hashes.txt
    fi
    
    # Compare hashes if both exist
    if [ -f "original_media_hashes.txt" ] && [ -f "generated_media_hashes.txt" ]; then
        echo "Media hash comparison:" >> media_analysis.txt
        diff original_media_hashes.txt generated_media_hashes.txt >> media_analysis.txt
    fi
}

generate_comparison_report() {
    cat > comparison_report.md <<EOF
# PowerPoint Fidelity Analysis Report

Generated: $(date)

## Overview
Comparison between original and generated PowerPoint files.

## Directory Structure
$(if [ -s directory_diff.txt ]; then echo "**Differences found:**"; cat directory_diff.txt; else echo "✅ Directory structures match"; fi)

## File Structure  
$(if [ -s file_diff.txt ]; then echo "**Differences found:**"; cat file_diff.txt; else echo "✅ File structures match"; fi)

## XML Content Analysis
$(if [ -f xml_analysis.txt ]; then cat xml_analysis.txt; else echo "No XML analysis performed"; fi)

## Media Content Analysis
$(if [ -f media_analysis.txt ]; then cat media_analysis.txt; else echo "No media analysis performed"; fi)

## Recommendations
Based on the analysis above, the following improvements are recommended:

### Extractor Improvements Needed:
- [ ] Missing XML elements extraction
- [ ] Incomplete media file handling  
- [ ] Missing relationship mappings
- [ ] Incomplete style/formatting capture

### Generator Improvements Needed:
- [ ] Missing XML structure generation
- [ ] Incomplete media embedding
- [ ] Missing relationship creation
- [ ] Incomplete formatting application

EOF
}

# Usage
compare_pptx_files "sample1.pptx" "sample1_enhanced.pptx"
```

### 4.2 Detailed XML Analysis Script

```python
#!/usr/bin/env python3
# File: analyze_xml_differences.py

import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path
import json

def analyze_xml_structure(original_xml, generated_xml):
    """Analyze differences between original and generated XML files"""
    
    try:
        orig_tree = ET.parse(original_xml)
        gen_tree = ET.parse(generated_xml)
        
        orig_root = orig_tree.getroot()
        gen_root = gen_tree.getroot()
        
        analysis = {
            'file': str(original_xml),
            'namespace_differences': compare_namespaces(orig_root, gen_root),
            'element_differences': compare_elements(orig_root, gen_root),
            'attribute_differences': compare_attributes(orig_root, gen_root),
            'missing_elements': find_missing_elements(orig_root, gen_root),
            'extra_elements': find_missing_elements(gen_root, orig_root),
        }
        
        return analysis
        
    except Exception as e:
        return {'error': str(e), 'file': str(original_xml)}

def compare_namespaces(orig_root, gen_root):
    """Compare XML namespaces"""
    orig_ns = set(orig_root.attrib.keys()) if orig_root.attrib else set()
    gen_ns = set(gen_root.attrib.keys()) if gen_root.attrib else set()
    
    return {
        'missing_in_generated': list(orig_ns - gen_ns),
        'extra_in_generated': list(gen_ns - orig_ns)
    }

def compare_elements(orig_root, gen_root):
    """Compare XML element structures"""
    orig_elements = get_element_paths(orig_root)
    gen_elements = get_element_paths(gen_root)
    
    return {
        'missing_in_generated': list(orig_elements - gen_elements),
        'extra_in_generated': list(gen_elements - orig_elements),
        'total_original': len(orig_elements),
        'total_generated': len(gen_elements),
        'match_percentage': len(orig_elements & gen_elements) / len(orig_elements) * 100 if orig_elements else 0
    }

def get_element_paths(element, path=""):
    """Get all element paths in XML tree"""
    paths = set()
    current_path = f"{path}/{element.tag}" if path else element.tag
    paths.add(current_path)
    
    for child in element:
        paths.update(get_element_paths(child, current_path))
    
    return paths

def compare_attributes(orig_root, gen_root):
    """Compare XML attributes"""
    orig_attrs = get_all_attributes(orig_root)
    gen_attrs = get_all_attributes(gen_root)
    
    return {
        'missing_in_generated': list(orig_attrs - gen_attrs),
        'extra_in_generated': list(gen_attrs - orig_attrs),
        'match_percentage': len(orig_attrs & gen_attrs) / len(orig_attrs) * 100 if orig_attrs else 0
    }

def get_all_attributes(element, path=""):
    """Get all attributes with their paths"""
    attrs = set()
    current_path = f"{path}/{element.tag}" if path else element.tag
    
    for attr_name, attr_value in element.attrib.items():
        attrs.add(f"{current_path}@{attr_name}")
    
    for child in element:
        attrs.update(get_all_attributes(child, current_path))
    
    return attrs

def find_missing_elements(source_root, target_root):
    """Find elements present in source but missing in target"""
    source_elements = get_detailed_elements(source_root)
    target_elements = get_detailed_elements(target_root)
    
    missing = []
    for elem_info in source_elements:
        if not any(target_elem['path'] == elem_info['path'] for target_elem in target_elements):
            missing.append(elem_info)
    
    return missing

def get_detailed_elements(element, path=""):
    """Get detailed element information"""
    elements = []
    current_path = f"{path}/{element.tag}" if path else element.tag
    
    elem_info = {
        'path': current_path,
        'tag': element.tag,
        'attributes': dict(element.attrib),
        'text': element.text.strip() if element.text else None,
        'children_count': len(list(element))
    }
    elements.append(elem_info)
    
    for child in element:
        elements.extend(get_detailed_elements(child, current_path))
    
    return elements

def main():
    if len(sys.argv) != 3:
        print("Usage: python analyze_xml_differences.py <original_xml> <generated_xml>")
        sys.exit(1)
    
    original_xml = sys.argv[1]
    generated_xml = sys.argv[2]
    
    if not os.path.exists(original_xml) or not os.path.exists(generated_xml):
        print("One or both XML files do not exist")
        sys.exit(1)
    
    analysis = analyze_xml_structure(original_xml, generated_xml)
    
    # Output analysis as JSON
    print(json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main()
```

## Improvement Process

### 5.1 Identifying Extractor Gaps

Based on comparison results, common issues to look for:

#### Missing XML Elements
```python
# In ppt_extractor.py, add extraction for missing elements:

def extract_slide_relationships(self, slide):
    """Extract slide relationship information"""
    relationships = {}
    
    # Extract slide master relationships
    if hasattr(slide, 'slide_master'):
        relationships['slide_master'] = slide.slide_master.name
    
    # Extract slide layout relationships  
    if hasattr(slide, 'slide_layout'):
        relationships['slide_layout'] = slide.slide_layout.name
    
    # Extract hyperlink relationships
    relationships['hyperlinks'] = self.extract_hyperlinks(slide)
    
    return relationships

def extract_hyperlinks(self, slide):
    """Extract hyperlink information from slide"""
    hyperlinks = []
    for shape in slide.shapes:
        if hasattr(shape, 'hyperlink') and shape.hyperlink.address:
            hyperlinks.append({
                'shape_id': shape.shape_id,
                'address': shape.hyperlink.address,
                'tooltip': getattr(shape.hyperlink, 'tooltip', None)
            })
    return hyperlinks
```

#### Missing Document Structure
```python
def extract_document_structure(self):
    """Extract complete document structure"""
    structure = {
        'slide_masters': self.extract_slide_masters(),
        'slide_layouts': self.extract_slide_layouts(), 
        'custom_properties': self.extract_custom_properties(),
        'content_types': self.extract_content_types(),
        'relationships': self.extract_document_relationships()
    }
    return structure

def extract_content_types(self):
    """Extract [Content_Types].xml information"""
    # Access the underlying ZIP structure
    import zipfile
    content_types = {}
    
    try:
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            if '[Content_Types].xml' in zip_ref.namelist():
                content_xml = zip_ref.read('[Content_Types].xml')
                # Parse and extract content type mappings
                content_types = self.parse_content_types_xml(content_xml)
    except Exception as e:
        print(f"Warning: Could not extract content types: {e}")
    
    return content_types
```

### 5.2 Identifying Generator Gaps

Common generator improvements needed:

#### Missing XML Structure Generation
```python
# In ppt_generator_enhanced.py, add structure generation:

def create_document_relationships(self):
    """Create proper document relationships"""
    # Access underlying presentation structure
    try:
        prs_part = self.presentation.part
        
        # Add missing relationships
        if hasattr(self, 'document_properties') and 'relationships' in self.document_properties:
            relationships = self.document_properties['relationships']
            for rel_info in relationships:
                self.add_relationship(prs_part, rel_info)
                
    except Exception as e:
        print(f"Warning: Could not create document relationships: {e}")

def create_missing_xml_elements(self, slide, slide_data):
    """Create missing XML elements in slide"""
    # Add missing slide properties
    if 'slide_properties' in slide_data:
        self.apply_slide_properties(slide, slide_data['slide_properties'])
    
    # Add missing transition effects
    if 'transitions' in slide_data:
        self.apply_slide_transitions(slide, slide_data['transitions'])
    
    # Add missing animations
    if 'animations' in slide_data:
        self.apply_slide_animations(slide, slide_data['animations'])
```

#### Improved Media Handling
```python
def embed_media_with_relationships(self, slide, media_info):
    """Embed media with proper relationship creation"""
    try:
        # Get media data
        media_data = base64.b64decode(media_info['data'])
        media_filename = media_info['filename']
        
        # Create proper media relationship
        media_part = self.presentation.part.package.get_or_add_media_part(media_data)
        
        # Add relationship to slide
        slide_part = slide.part
        rId = slide_part.relate_to(media_part, RELATIONSHIP_TYPE.IMAGE)
        
        # Create image shape with proper relationship reference
        image_shape = slide.shapes.add_picture(
            io.BytesIO(media_data),
            media_info['left'], media_info['top'],
            media_info['width'], media_info['height']
        )
        
        # Set proper relationship ID
        image_shape._element.set('r:embed', rId)
        
        return image_shape
        
    except Exception as e:
        print(f"Warning: Could not embed media with relationships: {e}")
        return None
```

### 5.3 Iterative Testing Process

```bash
#!/bin/bash
# File: iterative_testing.sh

run_iteration_test() {
    local iteration=$1
    echo "=== Testing Iteration $iteration ==="
    
    # Extract with current extractor
    python ppt_extractor.py sample1.pptx
    
    # Generate with current generator
    python ppt_generator_enhanced.py \
        sample1_shapes.json sample1_layouts.json sample1_theme.json \
        --media-file sample1_media.json \
        --properties-file sample1_properties.json \
        --output sample1_iteration_$iteration.pptx
    
    # Compare results
    ./compare_pptx_structures.sh sample1.pptx sample1_iteration_$iteration.pptx
    
    # Calculate fidelity score
    python calculate_fidelity_score.py \
        comparison_*/comparison_report.md > iteration_$iteration_score.txt
    
    echo "Iteration $iteration complete. Results in iteration_$iteration_score.txt"
}

# Run multiple iterations
for i in {1..5}; do
    run_iteration_test $i
    echo "Review results and make improvements before next iteration..."
    read -p "Press Enter to continue to next iteration..."
done
```

## Expected Issues and Solutions

### Common Structural Differences

1. **Missing Relationships**
   - Issue: `_rels/` directory missing files
   - Solution: Extract and recreate relationship mappings

2. **Incomplete Media Embedding**
   - Issue: `ppt/media/` files missing or corrupted
   - Solution: Improve base64 encoding/decoding and file embedding

3. **Theme Inconsistencies**
   - Issue: `ppt/theme/theme1.xml` missing elements
   - Solution: Extract complete theme information including color schemes, fonts, and effects

4. **Missing Document Properties**
   - Issue: `docProps/` files incomplete
   - Solution: Extract and apply all core and custom properties

### Fidelity Improvement Targets

- **Current**: 49.8% overall fidelity
- **Target**: 75-85% overall fidelity
- **Key Areas**:
  - Media preservation: 0% → 90%+
  - XML structure: 60% → 85%+
  - Theme fidelity: 70% → 90%+
  - Text formatting: 80% → 95%+

## Usage Instructions

1. **Initial Setup**:
   ```bash
   cd docs/
   chmod +x compare_pptx_structures.sh iterative_testing.sh
   ```

2. **Run Single Comparison**:
   ```bash
   ./compare_pptx_structures.sh sample1.pptx sample1_enhanced.pptx
   ```

3. **Run Iterative Testing**:
   ```bash
   ./iterative_testing.sh
   ```

4. **Analyze XML Differences**:
   ```bash
   python analyze_xml_differences.py \
     original_structure/ppt/slides/slide1.xml \
     generated_structure/ppt/slides/slide1.xml
   ```

This comprehensive testing methodology will help systematically identify and resolve fidelity gaps, leading to progressively better PowerPoint reconstruction quality.