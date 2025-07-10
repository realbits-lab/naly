# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PowerPoint template generation and collection framework. The project focuses on creating and managing PowerPoint templates through a systematic approach.

## Core Architecture

### Main Components

1. **Fidelity Testing Framework** (`docs/`): Comprehensive testing tools for measuring and improving reconstruction fidelity

### Data Flow

1. **Testing**: Original vs Generated → Fidelity analysis and improvement recommendations

## Development Commands

### Python Environment Setup
```bash
pip install python-pptx
```

### Testing and Fidelity Analysis
```bash
cd docs
chmod +x *.sh *.py

# Run fidelity comparison
./compare_pptx_structures.sh original.pptx generated.pptx

# Run iterative testing
./iterative_testing.sh

# XML analysis
python analyze_xml_differences.py original.xml generated.xml
```

## Key Features

### Testing Framework
- Structural comparison between original and generated files
- XML-level analysis with namespace handling
- Media integrity verification
- Fidelity scoring with weighted metrics
- Iterative improvement tracking

## Fidelity Metrics

The testing framework uses weighted scoring:
- **XML Content**: 50% (core structure and formatting)
- **File Structure**: 20% (required files and relationships)
- **Media Preservation**: 20% (embedded media integrity)
- **Directory Structure**: 10% (basic container structure)

Target fidelity: 85%+ for production use

## Architecture Notes

### Project Structure
```
docs/                      # Testing framework and documentation
docs/plan.md              # Development roadmap
docs/new-architecture.md  # Digital marketplace architecture (separate feature)
```

### Key Dependencies
- `python-pptx>=0.6.21` (primary PowerPoint manipulation library)
- Standard Python libraries for XML, JSON, and file handling

### Documentation References
- `docs/python-pptx.md` - Complete python-pptx library documentation and API reference

### Development Workflow
1. Run fidelity tests to measure impact
2. Analyze XML differences for specific issues
3. Iterate until achieving target fidelity scores
4. Use examples/extract/outputs directory to test the fidelity of the generator.

## Important Considerations

- Media files are base64-encoded for JSON storage
- XML namespace handling is critical for proper generation
- Relationship files (.rels) must be preserved for valid PPTX structure
- Theme application affects all visual elements
- Layout inheritance from master slides must be maintained
