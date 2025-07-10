#!/bin/bash

# PowerPoint extraction and generation test script
set -e

# Configuration
SAMPLE_DIR="./sample_parts"
OUTPUT_DIR="./outputs"
EXTRACTOR="./ppt_extractor.py"
GENERATOR="./ppt_generator.py"

# Function to clean outputs directory
clean_outputs() {
    if [ -d "$OUTPUT_DIR" ]; then
        echo "Cleaning outputs directory: $OUTPUT_DIR"
        rm -rf "$OUTPUT_DIR"/*
        echo "✓ All files and directories in $OUTPUT_DIR have been deleted"
    else
        echo "Output directory $OUTPUT_DIR does not exist"
    fi
}

# Function to show usage and available files
show_usage() {
    echo "Usage: $0 [OPTIONS] <file_index>"
    echo
    echo "Options:"
    echo "  --clean, -C    Clean all files and directories in outputs directory"
    echo
    echo "Available sample files:"
    if [ -d "$SAMPLE_DIR" ]; then
        for file in "$SAMPLE_DIR"/sample*.pptx; do
            if [ -f "$file" ]; then
                basename=$(basename "$file" .pptx)
                index=${basename#sample}
                echo "  $index (sample$index.pptx)"
            fi
        done
    else
        echo "  Sample directory not found: $SAMPLE_DIR"
    fi
    echo
    echo "Examples:"
    echo "  $0 1-2         # Use sample1-2.pptx"
    echo "  $0 1-3         # Use sample1-3.pptx"
    echo "  $0 1           # Use sample1.pptx"
    echo "  $0 --clean     # Clean outputs directory"
    echo "  $0 -C          # Clean outputs directory"
}

# Check if argument is provided
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Handle clean option
if [ "$1" = "--clean" ] || [ "$1" = "-C" ]; then
    clean_outputs
    exit 0
fi

FILE_INDEX="$1"
INPUT_FILE="sample${FILE_INDEX}.pptx"
INPUT_PATH="$SAMPLE_DIR/$INPUT_FILE"

# Check if input file exists
if [ ! -f "$INPUT_PATH" ]; then
    echo "Error: File '$INPUT_FILE' not found in $SAMPLE_DIR"
    echo
    show_usage
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "=== PowerPoint Extraction and Generation Test ==="
echo "Processing: $INPUT_FILE"
echo

# Step 1: Extract PowerPoint XML data from sample file
echo "Step 1: Extracting PowerPoint data from $INPUT_FILE..."
/opt/homebrew/anaconda3/envs/naly/bin/python "$EXTRACTOR" "$INPUT_PATH" --output-dir "$OUTPUT_DIR"
echo "✓ Extraction completed"
echo

# Step 2: Generate PowerPoint file from extracted data
echo "Step 2: Generating PowerPoint file from extracted data..."
/opt/homebrew/anaconda3/envs/naly/bin/python "$GENERATOR" \
    "$OUTPUT_DIR/sample${FILE_INDEX}_shapes.json" \
    "$OUTPUT_DIR/sample${FILE_INDEX}_layouts.json" \
    "$OUTPUT_DIR/sample${FILE_INDEX}_theme.json" \
    --media-file "$OUTPUT_DIR/sample${FILE_INDEX}_media.json" \
    --properties-file "$OUTPUT_DIR/sample${FILE_INDEX}_properties.json" \
    --output "$OUTPUT_DIR/sample${FILE_INDEX}_generated.pptx"
echo "✓ Generation completed"
echo

# Step 3: Unzip input PowerPoint file
echo "Step 3: Unzipping input PowerPoint file..."
INPUT_UNZIP_DIR="$OUTPUT_DIR/sample${FILE_INDEX}_input"
mkdir -p "$INPUT_UNZIP_DIR"
cd "$INPUT_UNZIP_DIR"
unzip -q "../../sample_parts/$INPUT_FILE"
cd - > /dev/null
echo "✓ Input file unzipped to: $INPUT_UNZIP_DIR"
echo

# Step 4: Unzip output PowerPoint file
echo "Step 4: Unzipping generated PowerPoint file..."
OUTPUT_UNZIP_DIR="$OUTPUT_DIR/sample${FILE_INDEX}_generated"
mkdir -p "$OUTPUT_UNZIP_DIR"
cd "$OUTPUT_UNZIP_DIR"
unzip -q "../sample${FILE_INDEX}_generated.pptx"
cd - > /dev/null
echo "✓ Generated file unzipped to: $OUTPUT_UNZIP_DIR"
echo

echo "=== Test Completed Successfully ==="
echo "Files created:"
echo "  - Extracted JSON data: $OUTPUT_DIR/sample${FILE_INDEX}_*.json"
echo "  - Generated PowerPoint: $OUTPUT_DIR/sample${FILE_INDEX}_generated.pptx"
echo "  - Input unzipped: $INPUT_UNZIP_DIR/"
echo "  - Generated unzipped: $OUTPUT_UNZIP_DIR/"
echo
echo "You can now compare the XML structures between input and generated files."