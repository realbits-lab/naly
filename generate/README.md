# PowerPoint AI Generator

An AI-powered PowerPoint shape generator that uses OpenXML and the AI SDK to create presentations from natural language prompts.

## Features

- 🤖 AI-powered shape generation using OpenAI GPT-4 with custom geometry
- 📦 Extracts and modifies PowerPoint OpenXML structure
- 🎨 Generates shapes with custom paths instead of preset geometry
- 📄 Creates valid PPTX files that can be opened in PowerPoint
- ⭐ Supports custom geometry for diamonds, stars, arrows, flowcharts, 3D objects, and callouts
- 🎯 Intelligent shape selection based on user prompts
- 🌈 Automatic color coding by shape category
- 🔧 Custom geometry generation based on PowerPoint OpenXML specifications

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up OpenAI API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Ensure blank.pptx is in the directory** (should already be present)

## Usage

Run the program with a natural language prompt:

```bash
node index.js "Your prompt here" [output-filename.pptx]
```

### Examples

```bash
# Create a simple title slide
node index.js "Create a title slide with Hello World"

# Create a slide with multiple elements
node index.js "Create a slide with a title 'Welcome' and a text box saying 'Getting Started'"

# Create specific shape types
node index.js "Create a star shape with Welcome" star-slide.pptx
node index.js "Create a diamond shape" diamond-slide.pptx
node index.js "Create arrow pointing down" arrow-slide.pptx
node index.js "Create a 3D cube shape" cube-slide.pptx

# Create flowchart elements
node index.js "Create a flowchart with start, process, and decision shapes" flowchart.pptx

# Create callout bubbles
node index.js "Create a callout bubble saying Hello" callout-slide.pptx

# Run the demo to see all available shapes
node demo.js
```

## How It Works

1. **Unzip**: Extracts the blank.pptx file to examine its OpenXML structure
2. **Find**: Locates the slide1.xml file in the PowerPoint structure
3. **Generate**: Uses AI to create OpenXML shape elements based on your prompt
4. **Inject**: Inserts the generated shapes into the slide XML
5. **Zip**: Packages everything back into a valid PPTX file

## File Structure

```
generate/
├── index.js          # Main program entry point
├── ai-generator.js   # AI SDK integration for shape generation
├── utils.js          # Utility functions for PPTX manipulation
├── blank.pptx        # Template PowerPoint file
├── package.json      # Node.js dependencies
├── .env.example      # Environment variables template
└── output/           # Generated PowerPoint files
```

## Custom Geometry Shapes

The AI generator uses custom geometry generation instead of preset shapes, creating authentic OpenXML paths based on PowerPoint specifications:

### Available Custom Shapes:
- **Basic Shapes**: diamond, ellipse, hexagon
- **Stars**: star5 (5-pointed star with customizable inner radius)
- **Arrows**: downArrow, leftArrow, rightArrow
- **Flowchart**: flowChartProcess, flowChartDecision
- **3D Objects**: cube (with perspective effect)
- **Callouts**: callout1 (speech bubble with tail)

### Custom Geometry Features:
- **Authentic Paths**: Generated using mathematical formulas from PowerPoint OpenXML specification
- **Dynamic Sizing**: Shapes adapt to requested dimensions while maintaining proper proportions
- **Custom Path Generation**: Creates `<a:custGeom>` elements with proper path definitions
- **Formula Evaluation**: Supports OpenXML guide formulas for accurate shape construction
- **Bezier Curves**: Smooth curves for ellipses and complex shapes

## Technical Details

- Uses OpenXML format for PowerPoint manipulation
- Shapes are positioned using EMU (English Metric Units)
- Slide dimensions: ~9144000 EMU width x 6858000 EMU height
- Generates custom geometry using `<a:custGeom>` elements instead of `<a:prstGeom>`
- Mathematical path generation based on PowerPoint OpenXML coordinate system
- Supports moveTo, lnTo, cubicBezTo, and close path commands
- AI generates appropriate positioning, sizing, and coloring
- Automatic fallback to rectangle geometry if shape not available

## Requirements

- Node.js 18+
- OpenAI API key
- NPM packages: ai, @ai-sdk/openai, jszip, xml2js, dotenv

## Troubleshooting

- Make sure your OpenAI API key is set in the .env file
- Ensure blank.pptx is present in the directory
- Check that all dependencies are installed with `npm install`