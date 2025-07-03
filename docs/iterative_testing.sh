#!/bin/bash
# Iterative PowerPoint Fidelity Testing Script
# This script runs multiple test iterations to progressively improve fidelity

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLES_DIR="$(dirname "$SCRIPT_DIR")/examples"
TEST_FILE="sample1.pptx"
MAX_ITERATIONS=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
FIDELITY_TARGET=85
IMPROVEMENT_THRESHOLD=2

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}PowerPoint Fidelity Iterative Testing${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if test file exists
if [ ! -f "$EXAMPLES_DIR/$TEST_FILE" ]; then
    echo -e "${RED}Error: Test file $EXAMPLES_DIR/$TEST_FILE not found${NC}"
    echo "Please ensure the test file exists in the examples directory"
    exit 1
fi

# Create testing directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_DIR="$SCRIPT_DIR/iterative_test_$TIMESTAMP"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "Test directory: $TEST_DIR"
echo "Target fidelity: ${FIDELITY_TARGET}%"
echo "Test file: $TEST_FILE"
echo ""

run_iteration_test() {
    local iteration=$1
    local iteration_dir="iteration_$iteration"
    
    echo -e "${YELLOW}=== ITERATION $iteration ===${NC}"
    echo "Starting iteration $iteration at $(date)"
    
    mkdir -p "$iteration_dir"
    cd "$iteration_dir"
    
    # Step 1: Extract data with current extractor
    echo "Step 1: Extracting data from $TEST_FILE..."
    python "$EXAMPLES_DIR/ppt_extractor.py" "$EXAMPLES_DIR/$TEST_FILE" > extract.log 2>&1
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Extraction failed in iteration $iteration${NC}"
        cat extract.log
        cd ..
        return 1
    fi
    
    # Check if all expected files were generated
    local base_name=$(basename "$TEST_FILE" .pptx)
    local expected_files=(
        "${base_name}_shapes.json"
        "${base_name}_layouts.json"
        "${base_name}_theme.json"
        "${base_name}_media.json"
        "${base_name}_properties.json"
        "${base_name}_summary.json"
    )
    
    for file in "${expected_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${YELLOW}⚠️  Warning: Expected file $file not generated${NC}"
        fi
    done
    
    # Step 2: Generate enhanced PowerPoint
    echo "Step 2: Generating enhanced PowerPoint..."
    local output_file="${base_name}_iteration_${iteration}.pptx"
    
    python "$EXAMPLES_DIR/ppt_generator_enhanced.py" \
        "${base_name}_shapes.json" \
        "${base_name}_layouts.json" \
        "${base_name}_theme.json" \
        --media-file "${base_name}_media.json" \
        --properties-file "${base_name}_properties.json" \
        --output "$output_file" > generate.log 2>&1
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Generation failed in iteration $iteration${NC}"
        cat generate.log
        cd ..
        return 1
    fi
    
    if [ ! -f "$output_file" ]; then
        echo -e "${RED}❌ Output file $output_file not created${NC}"
        cd ..
        return 1
    fi
    
    # Step 3: Compare structures and calculate fidelity
    echo "Step 3: Analyzing fidelity..."
    bash "$SCRIPT_DIR/compare_pptx_structures.sh" "$EXAMPLES_DIR/$TEST_FILE" "$output_file" > comparison.log 2>&1
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Comparison failed in iteration $iteration${NC}"
        cat comparison.log
        cd ..
        return 1
    fi
    
    # Extract fidelity score from comparison
    local comparison_dir=$(ls -d comparison_* | head -1)
    if [ -d "$comparison_dir" ]; then
        cd "$comparison_dir"
        
        # Extract overall fidelity score
        local fidelity_score=0
        if [ -f "statistics.txt" ]; then
            fidelity_score=$(grep "OVERALL_FIDELITY_SCORE=" statistics.txt | cut -d'=' -f2)
        fi
        
        # Extract individual scores
        local dir_score=$(grep "DIRECTORY_MATCH_PERCENTAGE=" statistics.txt | cut -d'=' -f2 2>/dev/null || echo "0")
        local file_score=$(grep "FILE_MATCH_PERCENTAGE=" statistics.txt | cut -d'=' -f2 2>/dev/null || echo "0")
        local xml_score=$(grep "XML_MATCH_PERCENTAGE=" statistics.txt | cut -d'=' -f2 2>/dev/null || echo "0")
        local media_score=$(grep "MEDIA_MATCH_PERCENTAGE=" statistics.txt | cut -d'=' -f2 2>/dev/null || echo "0")
        
        cd ..
        cd ..
        
        # Save iteration results
        cat > "iteration_${iteration}_results.txt" <<EOF
ITERATION=$iteration
TIMESTAMP=$(date)
OVERALL_FIDELITY=$fidelity_score
DIRECTORY_FIDELITY=$dir_score
FILE_FIDELITY=$file_score
XML_FIDELITY=$xml_score
MEDIA_FIDELITY=$media_score
OUTPUT_FILE=$output_file
EOF
        
        echo -e "${GREEN}✅ Iteration $iteration completed${NC}"
        echo "   Overall Fidelity: ${fidelity_score}%"
        echo "   Directory: ${dir_score}% | Files: ${file_score}% | XML: ${xml_score}% | Media: ${media_score}%"
        
        # Check if target reached
        if [ "$fidelity_score" -ge "$FIDELITY_TARGET" ]; then
            echo -e "${GREEN}🎯 Target fidelity of ${FIDELITY_TARGET}% reached!${NC}"
            return 2  # Success code
        fi
        
        return 0
    else
        echo -e "${RED}❌ Comparison directory not found${NC}"
        cd ..
        return 1
    fi
}

analyze_progress() {
    echo ""
    echo -e "${BLUE}=== PROGRESS ANALYSIS ===${NC}"
    
    # Create progress summary
    cat > progress_summary.txt <<EOF
# Iterative Testing Progress Summary

Generated: $(date)
Test File: $TEST_FILE
Target Fidelity: ${FIDELITY_TARGET}%

## Iteration Results

| Iteration | Overall | Directory | Files | XML | Media | Status |
|-----------|---------|-----------|-------|-----|-------|--------|
EOF
    
    local iterations_completed=0
    local last_fidelity=0
    local best_fidelity=0
    local best_iteration=0
    
    # Process all iteration results
    for result_file in iteration_*_results.txt; do
        if [ -f "$result_file" ]; then
            source "$result_file"
            
            local status="🔄 In Progress"
            if [ "$OVERALL_FIDELITY" -ge "$FIDELITY_TARGET" ]; then
                status="🎯 Target Reached"
            elif [ "$OVERALL_FIDELITY" -gt "$best_fidelity" ]; then
                status="📈 Improvement"
            elif [ "$OVERALL_FIDELITY" -eq "$last_fidelity" ]; then
                status="📊 No Change"
            else
                status="📉 Regression"
            fi
            
            echo "| $ITERATION | ${OVERALL_FIDELITY}% | ${DIRECTORY_FIDELITY}% | ${FILE_FIDELITY}% | ${XML_FIDELITY}% | ${MEDIA_FIDELITY}% | $status |" >> progress_summary.txt
            
            iterations_completed=$((iterations_completed + 1))
            last_fidelity=$OVERALL_FIDELITY
            
            if [ "$OVERALL_FIDELITY" -gt "$best_fidelity" ]; then
                best_fidelity=$OVERALL_FIDELITY
                best_iteration=$ITERATION
            fi
        fi
    done
    
    # Add summary statistics
    cat >> progress_summary.txt <<EOF

## Summary Statistics

- **Iterations Completed**: $iterations_completed
- **Best Fidelity Achieved**: ${best_fidelity}% (Iteration $best_iteration)
- **Current Fidelity**: ${last_fidelity}%
- **Target Fidelity**: ${FIDELITY_TARGET}%
- **Progress to Target**: $((last_fidelity * 100 / FIDELITY_TARGET))%

## Recommendations

EOF
    
    # Generate recommendations based on progress
    if [ "$last_fidelity" -ge "$FIDELITY_TARGET" ]; then
        echo "🎯 **Target Achieved**: Fidelity target has been reached!" >> progress_summary.txt
    elif [ "$last_fidelity" -gt "$((FIDELITY_TARGET - 10))" ]; then
        echo "🔥 **Close to Target**: Focus on fine-tuning and edge cases" >> progress_summary.txt
    elif [ "$iterations_completed" -ge 3 ]; then
        # Check for stagnation
        local improvement=$((last_fidelity - $(head -1 iteration_1_results.txt | grep OVERALL_FIDELITY | cut -d'=' -f2)))
        if [ "$improvement" -lt "$IMPROVEMENT_THRESHOLD" ]; then
            echo "⚠️ **Stagnation Detected**: Consider major architectural changes" >> progress_summary.txt
        else
            echo "📈 **Good Progress**: Continue with current approach" >> progress_summary.txt
        fi
    else
        echo "🚀 **Early Stage**: More iterations needed to establish trends" >> progress_summary.txt
    fi
    
    echo ""
    echo "Progress summary saved to: progress_summary.txt"
    
    # Display current status
    echo ""
    echo "Current Status:"
    echo "  Iterations completed: $iterations_completed"
    echo "  Best fidelity: ${best_fidelity}%"
    echo "  Current fidelity: ${last_fidelity}%"
    
    # Return status for decision making
    if [ "$last_fidelity" -ge "$FIDELITY_TARGET" ]; then
        return 2  # Target reached
    elif [ "$iterations_completed" -ge "$MAX_ITERATIONS" ]; then
        return 1  # Max iterations reached
    else
        return 0  # Continue testing
    fi
}

identify_improvement_areas() {
    echo ""
    echo -e "${BLUE}=== IMPROVEMENT AREAS ===${NC}"
    
    # Find the latest iteration results
    local latest_iteration=$(ls iteration_*_results.txt | tail -1)
    if [ -f "$latest_iteration" ]; then
        source "$latest_iteration"
        
        echo "Based on latest iteration results:"
        echo ""
        
        # Analyze weak areas
        if [ "$XML_FIDELITY" -lt 70 ]; then
            echo -e "${RED}🔴 Critical: XML Fidelity (${XML_FIDELITY}%)${NC}"
            echo "   - Focus on XML structure generation"
            echo "   - Review namespace handling"
            echo "   - Check element creation logic"
            echo ""
        fi
        
        if [ "$MEDIA_FIDELITY" -lt 50 ]; then
            echo -e "${RED}🔴 Critical: Media Preservation (${MEDIA_FIDELITY}%)${NC}"
            echo "   - Review base64 encoding/decoding"
            echo "   - Check media file embedding"
            echo "   - Verify relationship creation"
            echo ""
        fi
        
        if [ "$FILE_FIDELITY" -lt 80 ]; then
            echo -e "${YELLOW}🟡 Important: File Structure (${FILE_FIDELITY}%)${NC}"
            echo "   - Check missing files generation"
            echo "   - Review directory structure creation"
            echo "   - Verify content types"
            echo ""
        fi
        
        if [ "$DIRECTORY_FIDELITY" -lt 90 ]; then
            echo -e "${YELLOW}🟡 Moderate: Directory Structure (${DIRECTORY_FIDELITY}%)${NC}"
            echo "   - Review directory creation logic"
            echo "   - Check for missing subdirectories"
            echo ""
        fi
        
        # Suggest next steps
        echo -e "${BLUE}Next Steps:${NC}"
        echo "1. Address critical issues first (XML and Media)"
        echo "2. Test individual components in isolation"
        echo "3. Compare with successful PowerPoint files"
        echo "4. Review extraction completeness"
    fi
}

# Main testing loop
echo "Starting iterative testing..."
echo ""

previous_fidelity=0
stagnation_count=0

for iteration in $(seq 1 $MAX_ITERATIONS); do
    # Run iteration test
    run_iteration_test $iteration
    local test_result=$?
    
    if [ $test_result -eq 2 ]; then
        # Target reached
        echo -e "${GREEN}🎯 SUCCESS: Target fidelity reached in iteration $iteration!${NC}"
        break
    elif [ $test_result -eq 1 ]; then
        # Test failed
        echo -e "${RED}❌ FAILED: Iteration $iteration failed${NC}"
        echo ""
        echo "Please review the errors above and fix issues before continuing."
        break
    fi
    
    # Analyze progress after each iteration
    analyze_progress
    local progress_result=$?
    
    if [ $progress_result -eq 2 ]; then
        # Target reached
        break
    elif [ $progress_result -eq 1 ]; then
        # Max iterations reached
        echo -e "${YELLOW}⚠️  Maximum iterations reached without reaching target${NC}"
        break
    fi
    
    # Check for stagnation
    local current_fidelity=$(grep "OVERALL_FIDELITY=" "iteration_${iteration}_results.txt" | cut -d'=' -f2)
    local improvement=$((current_fidelity - previous_fidelity))
    
    if [ "$improvement" -lt "$IMPROVEMENT_THRESHOLD" ]; then
        stagnation_count=$((stagnation_count + 1))
        echo -e "${YELLOW}⚠️  Low improvement detected (${improvement}%). Stagnation count: $stagnation_count${NC}"
        
        if [ $stagnation_count -ge 3 ]; then
            echo -e "${YELLOW}⚠️  Stagnation detected after 3 iterations with minimal improvement${NC}"
            echo "Consider making significant changes to the extraction or generation logic."
            
            identify_improvement_areas
            
            echo ""
            read -p "Continue testing? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                break
            fi
            stagnation_count=0
        fi
    else
        stagnation_count=0
        echo -e "${GREEN}✅ Good improvement: +${improvement}%${NC}"
    fi
    
    previous_fidelity=$current_fidelity
    
    # Pause between iterations for review
    if [ $iteration -lt $MAX_ITERATIONS ]; then
        echo ""
        echo "Review the results above and make any necessary improvements to the code."
        echo "Press Enter to continue to the next iteration, or Ctrl+C to stop."
        read -r
    fi
done

# Final analysis
echo ""
echo -e "${BLUE}=== FINAL ANALYSIS ===${NC}"
analyze_progress
identify_improvement_areas

echo ""
echo "Testing completed. Results available in: $TEST_DIR"
echo ""
echo "To review detailed results:"
echo "  cd $TEST_DIR"
echo "  cat progress_summary.txt"
echo "  # Review individual iteration directories for detailed analysis"