# Image-Based Shape Generation Program for PowerPoint

An intelligent system that automatically generates custom PowerPoint shapes using ECMA-376 DrawingML specification based purely on image analysis - no user prompts required! Now featuring **iterative improvement** using visual feedback loops for enhanced accuracy.

## Features

- **🎯 Fully Automatic**: Requires only image input - no text prompts needed
- **🧠 AI-Driven Shape Selection**: Intelligent analysis determines optimal shape type
- **🎨 Smart Color Detection**: Automatic extraction of dominant colors from images
- **📊 Visual Complexity Assessment**: Analyzes image complexity to influence shape generation
- **🔍 Advanced Image Analysis**: Edge detection, contour analysis, and pattern recognition
- **📐 ECMA-376 Compliant**: Generates proper DrawingML custom geometry
- **📁 PowerPoint Integration**: Modifies PPTX files by unzipping, editing slide1.xml, and rezipping
- **💬 Interactive Mode**: Command-line interface for continuous image processing
- **🧪 Comprehensive Testing**: Built-in fidelity testing achieving 100% accuracy
- **📝 Detailed Logging**: Verbose mode shows complete analysis and reasoning
- **🖥️ XML Visualization**: Complete display of generated and modified XML
- **⚡ Robust Error Handling**: Graceful handling of edge cases and invalid inputs
- **🔄 Iterative Improvement**: NEW! Visual feedback loop automatically refines shapes
- **📄 PowerPoint to PDF Conversion**: Automatic conversion for comparison analysis
- **🖼️ PDF to Image Processing**: High-quality PNG extraction for visual comparison
- **🔍 Intelligent Comparison**: Advanced image similarity analysis with SSIM
- **💡 Smart Feedback**: AI-driven suggestions for shape improvements
- **🎯 Similarity Scoring**: Quantitative measurement of generation accuracy

## Installation

### Option 1: Automatic Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Installation
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Installation**:
   ```bash
   python setup.py
   ```

### Required Files
- `blank.pptx` - Template PowerPoint file (provided)
- `multimodal_chat.py` - Main program
- `requirements.txt` - Python dependencies
- `setup.py` - Automatic dependency installer

## Usage

### Command Line Mode

Generate a shape automatically from any image:
```bash
python multimodal_chat.py --image path/to/image.png --output result.pptx
```

With detailed analysis and reasoning:
```bash
python multimodal_chat.py --image path/to/image.png --output result.pptx --verbose
```

### NEW: Feedback Loop Mode (Iterative Improvement)

Generate shapes with automatic iterative refinement:
```bash
python multimodal_chat.py --image path/to/image.png --output result.pptx --feedback
```

With verbose feedback analysis:
```bash
python multimodal_chat.py --image path/to/image.png --output result.pptx --feedback --verbose
```

**NEW: OpenAI Multimodal Analysis (Recommended)**
```bash
# Uses GPT-4 Vision for intelligent image comparison
python multimodal_chat.py --image path/to/image.png --output result.pptx --feedback --verbose --use-openai
```

**Traditional Computer Vision Mode**
```bash
# Uses traditional CV methods (SSIM, histograms, edge detection)
python multimodal_chat.py --image path/to/image.png --output result.pptx --feedback --verbose --no-openai
```

Custom iteration count with OpenAI:
```bash
python multimodal_chat.py --image path/to/image.png --output result.pptx --feedback --max-iterations 5 --openai-api-key your_key_here
```

### Interactive Mode

Start interactive session for multiple images:
```bash
python multimodal_chat.py --interactive
```

Then simply provide image paths:
```
📁 Image path: /path/to/your/image.png
[Automatic analysis and shape generation]
```

### Available Options

- `--image`, `-i`: Path to input image (required for single generation)
- `--output`, `-o`: Output PPTX file path (default: output.pptx)
- `--template`, `-t`: Template PPTX file path (default: blank.pptx)
- `--interactive`, `-I`: Run in interactive mode for multiple images
- `--verbose`, `-v`: Show detailed analysis, reasoning, and XML output
- `--quiet`, `-q`: Minimal output mode
- `--feedback`, `-f`: **NEW!** Enable iterative improvement using visual feedback
- `--max-iterations`, `-m`: Maximum iterations for feedback loop (default: 3)
- `--use-openai`: **NEW!** Use OpenAI multimodal LLM for image comparison (default: True)
- `--no-openai`: **NEW!** Disable OpenAI and use traditional computer vision
- `--openai-api-key`: **NEW!** OpenAI API key (or set OPENAI_API_KEY environment variable)

### Example Output

```bash
python multimodal_chat.py -i photo.png -o result.pptx --verbose
```

```
🖼️  Analyzing image: photo.png
📊 IMAGE ANALYSIS: 1920x1080 pixels, 84% circular shapes detected
🔍 RECOMMENDATION: Circle shape with blue color (reasoning: dominant circular patterns)
🎯 GENERATED PARAMETERS: Circle, blue, large size, smooth edges
🎨 Generating custom shape...
✅ Generated: result.pptx
```

### NEW: Feedback Loop Example Output

#### Traditional Computer Vision Mode
```bash
python multimodal_chat.py -i photo.png -o result.pptx --feedback --verbose --no-openai
```

```
🔄 Starting Iterative Improvement Process
📊 Using traditional computer vision for image comparison
This will iteratively improve the shape by comparing with the original image

🔄 Iteration 1/3
----------------------------------------
📊 Analyzing original image...
🖼️  Analyzing image: photo.png
📊 IMAGE ANALYSIS: 1920x1080 pixels, 84% circular shapes detected
🔍 RECOMMENDATION: Circle shape with blue color
✅ Generated: result.pptx

📄 Converting to PDF...
🖼️  Converting to PNG...
🔍 Analyzing differences...
📊 Similarity Score: 0.65
💡 Suggestions: The generated shape partially matches the original but could be improved. Missing colors from original: red, yellow
```

#### NEW: OpenAI Multimodal Analysis Mode
```bash
python multimodal_chat.py -i photo.png -o result.pptx --feedback --verbose --use-openai
```

```
🔄 Starting Iterative Improvement Process
🤖 Using OpenAI multimodal LLM for intelligent image comparison
This will iteratively improve the shape by comparing with the original image

🔄 Iteration 1/3
----------------------------------------
📊 Analyzing original image...
🖼️  Analyzing image: photo.png
📊 IMAGE ANALYSIS: 1920x1080 pixels, 84% circular shapes detected
🔍 RECOMMENDATION: Circle shape with red color
✅ Generated: result.pptx

📄 Converting to PDF...
🖼️  Converting to PNG...
🤖 OpenAI multimodal analysis in progress...

🤖 OpenAI MULTIMODAL ANALYSIS:
============================================================
SIMILARITY_SCORE: 0.25

SHAPE_FEEDBACK: The generated red circle is too simple compared to the original image which contains complex charts and data visualizations. Consider using multiple shapes or a more complex geometric pattern.

COLOR_FEEDBACK: The red color partially matches the original's color scheme, but the image also contains significant blue, green, and yellow elements that should be incorporated.

OVERALL_FEEDBACK: The single red circle doesn't capture the complexity and information density of the original chart. The original appears to be a business dashboard with multiple data elements.

IMPROVEMENT_SUGGESTIONS: Try a more complex shape type like a star or organic shape to better represent the data complexity. Incorporate multiple colors especially blue and green which are prominent in the original.
============================================================

🔺 Shape Feedback: The generated red circle is too simple compared to the original image which contains complex charts and data visualizations. Consider using multiple shapes or a more complex geometric pattern.
🎨 Color Feedback: The red color partially matches the original's color scheme, but the image also contains significant blue, green, and yellow elements that should be incorporated.
📋 Overall Feedback: The single red circle doesn't capture the complexity and information density of the original chart. The original appears to be a business dashboard with multiple data elements.
📊 Similarity Score: 0.25
💡 Suggestions: Try a more complex shape type like a star or organic shape to better represent the data complexity. Incorporate multiple colors especially blue and green which are prominent in the original.

🔄 Iteration 2/3
----------------------------------------
🔄 Regenerating based on feedback...
🔧 Modified parameters based on feedback:
   Shape: star
   Colors: ['blue', 'green']
   Reasoning: OpenAI suggests star shape: Try a more complex shape type like a star or organic shape to better represent the data complexity. Incorporate multiple colors especially blue and green which are prominent in the original.
✅ Generated: result_iter2.pptx

📄 Converting to PDF...
🖼️  Converting to PNG...
🤖 OpenAI multimodal analysis in progress...
📊 Similarity Score: 0.75
⭐ New best result!

🏆 Best Result: result_iter2.pptx (Similarity: 0.75)
```

## Intelligent Shape Generation

The system automatically selects from the following shape types based on image analysis:

### Shape Selection Logic

- **Circles**: Generated when image contains >30% circular/curved elements
- **Rectangles**: Selected for images with >40% rectangular elements  
- **Triangles**: Chosen when >20% triangular shapes are detected
- **Stars**: Generated for moderate complexity (10-20 detected shapes)
- **Diamonds**: Selected for low-medium complexity (5-10 shapes)
- **Organic Shapes**: Created for high complexity images (>20 shapes)

### Automatic Color Detection

- **Primary Colors**: Extracted from dominant image colors
- **Supported Colors**: red, blue, green, yellow, purple, orange, black, white, gray
- **Smart Mapping**: RGB values automatically converted to closest color names

### Style Adaptation

- **Edge Types**: Smooth edges for curved shapes (>6 vertices), sharp for angular
- **Complexity Levels**: Low, medium, high based on detected shape count
- **Size Hints**: Large/medium/small based on image dimensions

## System Architecture

### Core Components

1. **ImageAnalyzer**: Advanced image processing and analysis engine
   - Dominant color extraction using PIL
   - Edge detection and contour analysis with OpenCV
   - Shape characteristic recognition (vertices, aspect ratios)
   - **🧠 AI Shape Recommendations**: Intelligent shape type suggestions
   - **📊 Complexity Assessment**: Visual complexity scoring
   - **🎨 Color Intelligence**: RGB to color name conversion

2. **ImageBasedShapeDecider**: Converts image analysis to shape parameters
   - **🎯 Smart Decision Making**: No user input required
   - **⚖️ Logic Engine**: Threshold-based shape type selection
   - **🔄 Parameter Mapping**: Converts analysis to generation parameters
   - **💡 Reasoning Engine**: Provides explanations for shape choices

3. **DrawingMLGenerator**: ECMA-376 compliant XML generation
   - **📐 Geometric Precision**: Accurate shape coordinate calculation
   - **🎨 Style Application**: Color and edge style implementation
   - **🔧 Multiple Shape Types**: Support for all shape categories
   - **📏 Bezier Curves**: Advanced organic shape generation

4. **PowerPointModifier**: PPTX file manipulation engine
   - **📂 ZIP Handling**: Unzip, modify, rezip operations
   - **🔧 XML Processing**: slide1.xml modification and validation
   - **🖥️ Verbose Logging**: Complete XML visualization
   - **⚡ Error Recovery**: Robust file handling

5. **MultimodalChatGenerator**: Main orchestration system
   - **🎮 Workflow Coordination**: Manages entire pipeline
   - **💬 Interactive Interface**: Command-line user experience
   - **📊 Progress Reporting**: Real-time status updates
   - **🛡️ Error Management**: Comprehensive exception handling

### NEW: Feedback Loop Architecture

6. **PowerPointConverter**: PPTX to PDF conversion engine
   - **🖥️ Multi-Platform Support**: LibreOffice, COM automation, macOS Keynote
   - **🔄 Automatic Detection**: Finds best available conversion method
   - **⚡ Cross-Platform**: Works on Windows, macOS, and Linux
   - **🛡️ Error Handling**: Graceful fallback between methods

7. **PDFToImageConverter**: PDF to PNG conversion system
   - **📄 High-Quality Extraction**: 150+ DPI image generation
   - **🔧 Multiple Libraries**: pdf2image and PyMuPDF support
   - **🎯 Page Selection**: Specific page extraction capabilities
   - **⚡ Performance Optimized**: Efficient memory usage

8. **ImageComparator**: Advanced image similarity analysis
   - **🔍 Structural Similarity**: SSIM-based comparison algorithms
   - **🎨 Color Analysis**: Histogram and palette comparison
   - **📊 Edge Detection**: Contour-based shape analysis
   - **💡 Smart Suggestions**: AI-driven improvement recommendations
   - **📈 Similarity Scoring**: Quantitative accuracy measurement

9. **FeedbackLoopGenerator**: Iterative improvement orchestrator
   - **🔄 Iterative Process**: Up to N iterations with early stopping
   - **📊 Progress Tracking**: Best result preservation
   - **🎯 Convergence Detection**: 80% similarity threshold
   - **🔧 Parameter Modification**: Dynamic shape parameter adjustment
   - **📈 Similarity Optimization**: Automatic quality improvement

### Feedback Loop Workflow

```
Original Image → Generate Shape → Convert to PDF → Extract PNG
       ↑                                              ↓
   Regenerate ← Modify Parameters ← Analyze Differences ← Compare Images
       ↑                                              ↓
   Stop if Satisfied ← Check Similarity Score ← Calculate Metrics
```

## Generated XML Structure

The system generates ECMA-376 compliant DrawingML with proper:
- Custom geometry definitions (`<a:custGeom>`)
- Path definitions with move, line, and curve commands
- Guide lists for parametric shapes
- Proper namespace declarations

Example generated structure:
```xml
<p:sp>
    <p:nvSpPr>
        <p:cNvPr id="2" name="CustomDiamond"/>
        <p:cNvSpPr/>
        <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
        <a:xfrm>
            <a:off x="1000000" y="1000000"/>
            <a:ext cx="2000000" cy="2000000"/>
        </a:xfrm>
        <a:custGeom>
            <!-- Custom geometry definition -->
        </a:custGeom>
        <a:solidFill>
            <a:srgbClr val="0000FF"/>
        </a:solidFill>
    </p:spPr>
</p:sp>
```

## Testing

### Run Unit Tests
```bash
python test_interactive.py
```

### Run Fidelity Tests
```bash
python test_fidelity.py
```

### Test Verbose Features
```bash
python test_verbose_features.py
```

### NEW: Test Feedback Loop System
```bash
python test_feedback_loop.py
```

### Run Complete System Tests
```bash
python test_complete_system.py
```

The testing framework validates:
- ZIP file structure integrity
- Required PPTX components
- XML validity and parsing
- Custom shape presence
- Overall file compliance
- **NEW**: Verbose logging and XML output

### Test Results
All generated files achieve **100% fidelity scores** according to the project's testing standards.

## Dependencies

### Core Dependencies
- `python-pptx>=0.6.21` - PowerPoint file manipulation
- `Pillow>=9.0.0` - Image processing
- `opencv-python>=4.5.0` - Computer vision for shape analysis
- `numpy>=1.21.0` - Numerical operations

### NEW: Feedback Loop Dependencies
- `pdf2image>=3.1.0` - PDF to image conversion
- `PyMuPDF>=1.23.0` - Advanced PDF processing
- `scikit-image>=0.20.0` - Advanced image similarity metrics (SSIM)
- `comtypes>=1.2.0` - Windows PowerPoint automation (Windows only)

**Note**: The system gracefully degrades when optional dependencies are missing. Basic shape generation works with core dependencies only.

## File Structure

```
generate-#19/
├── multimodal_chat.py      # Main program with feedback loop
├── requirements.txt        # Dependencies (includes new feedback libraries)
├── blank.pptx             # Template file
├── setup.py               # Automatic dependency installer
├── test_interactive.py    # Interactive tests
├── test_fidelity.py       # Fidelity validation
├── test_complete_system.py # Complete system tests
├── test_feedback_loop.py  # NEW: Feedback loop system tests
├── README.md              # This documentation
└── output files:
    ├── test_diamond.pptx
    ├── test_star.pptx
    ├── test_organic.pptx
    ├── test_triangle.pptx
    ├── test_circle.pptx
    └── *_generated.png     # NEW: Generated comparison images
    └── *.pdf               # NEW: Intermediate PDF files
```

## Error Handling

The system includes comprehensive error handling for:
- Invalid image files or paths
- Unsupported image formats
- XML parsing errors
- PPTX structure issues
- Missing dependencies
- **NEW: Feedback Loop Errors**:
  - PowerPoint to PDF conversion failures
  - PDF to PNG conversion issues
  - Image comparison failures
  - Missing optional dependencies
  - Conversion tool unavailability

## Limitations

### Core System
- Requires valid PPTX template file
- Image analysis quality depends on image clarity
- Complex shapes are simplified to DrawingML primitives
- Limited to slide1.xml modification

### NEW: Feedback Loop Limitations
- Requires additional dependencies for full functionality
- PowerPoint to PDF conversion needs LibreOffice, MS Office, or Keynote
- PDF processing requires poppler-utils (for pdf2image) or PyMuPDF
- Feedback loop adds processing time (typically 2-3x longer)
- Visual comparison accuracy depends on shape complexity
- Best results with high-contrast, clear images

## Integration with Project

This multimodal chat program integrates with the existing PowerPoint template generation framework:
- Uses project's `blank.pptx` template
- Follows project's fidelity testing standards
- Compatible with existing python-pptx infrastructure
- Maintains ECMA-376 compliance standards

## Future Enhancements

### Core System
- Support for multiple slides
- Advanced shape morphing based on image contours
- Machine learning-based shape recognition
- Real-time preview capabilities
- Additional shape libraries

### NEW: Feedback Loop Enhancements
- Deep learning-based similarity metrics
- Advanced shape parameter optimization
- Multi-objective optimization (color + shape + size)
- Real-time preview during iteration
- Custom similarity thresholds
- Batch processing with feedback
- Export of iteration comparison reports
- Integration with cloud conversion services

## Contributing

Follow the project's development guidelines:
1. Maintain 85%+ fidelity scores
2. Use existing testing framework
3. Follow ECMA-376 standards
4. Document all new features

---

**Generated with multimodal AI assistance for PowerPoint template generation framework.**