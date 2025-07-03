#!/bin/bash
# PowerPoint Structure Comparison Script
# Usage: ./compare_pptx_structures.sh original.pptx generated.pptx

compare_pptx_files() {
    local original=$1
    local generated=$2
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_dir="comparison_$timestamp"
    
    echo "Starting PPTX structure comparison..."
    echo "Original: $original"
    echo "Generated: $generated"
    echo "Output directory: $output_dir"
    
    # Validation
    if [ ! -f "$original" ]; then
        echo "Error: Original file '$original' not found"
        exit 1
    fi
    
    if [ ! -f "$generated" ]; then
        echo "Error: Generated file '$generated' not found"
        exit 1
    fi
    
    mkdir -p "$output_dir"
    cd "$output_dir"
    
    # Convert and extract
    echo "Converting PPTX files to ZIP format..."
    cp "../$original" original.zip
    cp "../$generated" generated.zip
    
    mkdir original_structure generated_structure
    echo "Extracting original structure..."
    cd original_structure && unzip ../original.zip >/dev/null 2>&1 && cd ..
    echo "Extracting generated structure..."
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
    
    # Size comparison
    echo "Analyzing file sizes..."
    find original_structure -type f -exec ls -l {} \; | awk '{print $5, $9}' | sort -k2 > original_sizes.txt
    find generated_structure -type f -exec ls -l {} \; | awk '{print $5, $9}' | sort -k2 > generated_sizes.txt
    
    # XML analysis
    echo "Analyzing XML content..."
    analyze_xml_differences
    
    # Media analysis
    echo "Analyzing media content..."
    analyze_media_differences
    
    # Calculate statistics
    calculate_statistics
    
    # Generate report
    generate_comparison_report
    
    echo "Comparison complete. Results in $output_dir/"
    echo "Main report: $output_dir/comparison_report.md"
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
        "_rels/.rels"
        "ppt/_rels/presentation.xml.rels"
    )
    
    local xml_match_count=0
    local xml_total_count=0
    
    for file in "${key_files[@]}"; do
        xml_total_count=$((xml_total_count + 1))
        echo "--- Analyzing $file ---" >> xml_analysis.txt
        
        if [ -f "original_structure/$file" ] && [ -f "generated_structure/$file" ]; then
            # Use xmllint for pretty printing and comparison if available
            if command -v xmllint >/dev/null 2>&1; then
                xmllint --format "original_structure/$file" > "orig_${file//\//_}.formatted" 2>/dev/null
                xmllint --format "generated_structure/$file" > "gen_${file//\//_}.formatted" 2>/dev/null
                
                if diff "orig_${file//\//_}.formatted" "gen_${file//\//_}.formatted" >/dev/null 2>&1; then
                    echo "✅ Files match" >> xml_analysis.txt
                    xml_match_count=$((xml_match_count + 1))
                else
                    echo "❌ Files differ" >> xml_analysis.txt
                    diff "orig_${file//\//_}.formatted" "gen_${file//\//_}.formatted" | head -50 >> xml_analysis.txt
                fi
            else
                # Fallback to regular diff
                if diff "original_structure/$file" "generated_structure/$file" >/dev/null 2>&1; then
                    echo "✅ Files match" >> xml_analysis.txt
                    xml_match_count=$((xml_match_count + 1))
                else
                    echo "❌ Files differ" >> xml_analysis.txt
                    diff "original_structure/$file" "generated_structure/$file" | head -50 >> xml_analysis.txt
                fi
            fi
        elif [ -f "original_structure/$file" ]; then
            echo "❌ Missing in generated" >> xml_analysis.txt
        elif [ -f "generated_structure/$file" ]; then
            echo "⚠️  Extra in generated" >> xml_analysis.txt
        else
            echo "ℹ️  Not found in either" >> xml_analysis.txt
        fi
        echo "" >> xml_analysis.txt
    done
    
    # Calculate XML match percentage
    if [ $xml_total_count -gt 0 ]; then
        local xml_percentage=$((xml_match_count * 100 / xml_total_count))
        echo "XML_MATCH_PERCENTAGE=$xml_percentage" > xml_stats.txt
        echo "XML_MATCH_COUNT=$xml_match_count" >> xml_stats.txt
        echo "XML_TOTAL_COUNT=$xml_total_count" >> xml_stats.txt
    fi
}

analyze_media_differences() {
    echo "=== MEDIA CONTENT ANALYSIS ===" > media_analysis.txt
    
    local media_match=true
    
    # Compare media directories
    if [ -d "original_structure/ppt/media" ]; then
        echo "Original media files:" >> media_analysis.txt
        ls -la original_structure/ppt/media/ >> media_analysis.txt
        echo "" >> media_analysis.txt
        
        # Calculate file hashes for integrity check
        find original_structure/ppt/media -type f -exec md5sum {} \; 2>/dev/null > original_media_hashes.txt
        orig_media_count=$(find original_structure/ppt/media -type f | wc -l)
    else
        echo "No media files in original" >> media_analysis.txt
        orig_media_count=0
    fi
    
    if [ -d "generated_structure/ppt/media" ]; then
        echo "Generated media files:" >> media_analysis.txt
        ls -la generated_structure/ppt/media/ >> media_analysis.txt
        echo "" >> media_analysis.txt
        
        find generated_structure/ppt/media -type f -exec md5sum {} \; 2>/dev/null > generated_media_hashes.txt
        gen_media_count=$(find generated_structure/ppt/media -type f | wc -l)
    else
        echo "No media files in generated" >> media_analysis.txt
        gen_media_count=0
    fi
    
    # Compare hashes if both exist
    if [ -f "original_media_hashes.txt" ] && [ -f "generated_media_hashes.txt" ]; then
        echo "Media hash comparison:" >> media_analysis.txt
        if diff original_media_hashes.txt generated_media_hashes.txt >/dev/null 2>&1; then
            echo "✅ All media files match" >> media_analysis.txt
        else
            echo "❌ Media files differ:" >> media_analysis.txt
            diff original_media_hashes.txt generated_media_hashes.txt >> media_analysis.txt
            media_match=false
        fi
    fi
    
    # Calculate media preservation percentage
    if [ $orig_media_count -gt 0 ]; then
        if [ $gen_media_count -eq $orig_media_count ] && [ "$media_match" = true ]; then
            media_percentage=100
        elif [ $gen_media_count -eq $orig_media_count ]; then
            media_percentage=50  # Same count but different content
        else
            media_percentage=$((gen_media_count * 100 / orig_media_count))
        fi
    else
        media_percentage=100  # No media to preserve
    fi
    
    echo "MEDIA_MATCH_PERCENTAGE=$media_percentage" > media_stats.txt
    echo "ORIGINAL_MEDIA_COUNT=$orig_media_count" >> media_stats.txt
    echo "GENERATED_MEDIA_COUNT=$gen_media_count" >> media_stats.txt
}

calculate_statistics() {
    echo "=== CALCULATING STATISTICS ===" > statistics.txt
    
    # Directory statistics
    orig_dir_count=$(cat original_dirs.txt | wc -l)
    gen_dir_count=$(cat generated_dirs.txt | wc -l)
    common_dirs=$(comm -12 original_dirs.txt generated_dirs.txt | wc -l)
    if [ $orig_dir_count -gt 0 ]; then
        dir_percentage=$((common_dirs * 100 / orig_dir_count))
    else
        dir_percentage=100
    fi
    
    # File statistics
    orig_file_count=$(cat original_files.txt | wc -l)
    gen_file_count=$(cat generated_files.txt | wc -l)
    common_files=$(comm -12 original_files.txt generated_files.txt | wc -l)
    if [ $orig_file_count -gt 0 ]; then
        file_percentage=$((common_files * 100 / orig_file_count))
    else
        file_percentage=100
    fi
    
    # Load XML and media stats
    source xml_stats.txt 2>/dev/null || { XML_MATCH_PERCENTAGE=0; XML_MATCH_COUNT=0; XML_TOTAL_COUNT=0; }
    source media_stats.txt 2>/dev/null || { MEDIA_MATCH_PERCENTAGE=0; ORIGINAL_MEDIA_COUNT=0; GENERATED_MEDIA_COUNT=0; }
    
    # Calculate overall fidelity score (weighted average)
    # Weights: Directory 10%, Files 20%, XML 50%, Media 20%
    if [ "$XML_MATCH_PERCENTAGE" = "" ]; then XML_MATCH_PERCENTAGE=0; fi
    if [ "$MEDIA_MATCH_PERCENTAGE" = "" ]; then MEDIA_MATCH_PERCENTAGE=0; fi
    overall_fidelity=$(( (dir_percentage * 10 + file_percentage * 20 + XML_MATCH_PERCENTAGE * 50 + MEDIA_MATCH_PERCENTAGE * 20) / 100 ))
    
    # Save all statistics
    cat > statistics.txt <<EOF
DIRECTORY_ORIGINAL_COUNT=$orig_dir_count
DIRECTORY_GENERATED_COUNT=$gen_dir_count
DIRECTORY_COMMON_COUNT=$common_dirs
DIRECTORY_MATCH_PERCENTAGE=$dir_percentage

FILE_ORIGINAL_COUNT=$orig_file_count
FILE_GENERATED_COUNT=$gen_file_count
FILE_COMMON_COUNT=$common_files
FILE_MATCH_PERCENTAGE=$file_percentage

XML_MATCH_PERCENTAGE=$XML_MATCH_PERCENTAGE
XML_MATCH_COUNT=$XML_MATCH_COUNT
XML_TOTAL_COUNT=$XML_TOTAL_COUNT

MEDIA_MATCH_PERCENTAGE=$MEDIA_MATCH_PERCENTAGE
ORIGINAL_MEDIA_COUNT=$ORIGINAL_MEDIA_COUNT
GENERATED_MEDIA_COUNT=$GENERATED_MEDIA_COUNT

OVERALL_FIDELITY_SCORE=$overall_fidelity
EOF
}

generate_comparison_report() {
    source statistics.txt
    
    cat > comparison_report.md <<EOF
# PowerPoint Fidelity Analysis Report

**Generated:** $(date)  
**Original File:** $original  
**Generated File:** $generated  

## Executive Summary

**Overall Fidelity Score: ${OVERALL_FIDELITY_SCORE}%**

| Category | Score | Details |
|----------|-------|---------|
| Directory Structure | ${DIRECTORY_MATCH_PERCENTAGE}% | ${DIRECTORY_COMMON_COUNT}/${DIRECTORY_ORIGINAL_COUNT} directories match |
| File Structure | ${FILE_MATCH_PERCENTAGE}% | ${FILE_COMMON_COUNT}/${FILE_ORIGINAL_COUNT} files match |
| XML Content | ${XML_MATCH_PERCENTAGE}% | ${XML_MATCH_COUNT}/${XML_TOTAL_COUNT} key XML files match |
| Media Preservation | ${MEDIA_MATCH_PERCENTAGE}% | ${GENERATED_MEDIA_COUNT}/${ORIGINAL_MEDIA_COUNT} media files preserved |

## Detailed Analysis

### Directory Structure
$(if [ -s directory_diff.txt ]; then 
    echo "**Issues Found:**"
    echo "\`\`\`"
    cat directory_diff.txt
    echo "\`\`\`"
else 
    echo "✅ **No Issues:** Directory structures match perfectly"
fi)

### File Structure  
$(if [ -s file_diff.txt ]; then 
    echo "**Issues Found:**"
    echo "\`\`\`"
    cat file_diff.txt | head -20
    echo "\`\`\`"
    echo ""
    echo "*Note: Showing first 20 differences. See file_diff.txt for complete list.*"
else 
    echo "✅ **No Issues:** File structures match perfectly"
fi)

### XML Content Analysis
$(cat xml_analysis.txt)

### Media Content Analysis
$(cat media_analysis.txt)

## Improvement Recommendations

### Critical Issues (High Priority)
EOF

    # Add specific recommendations based on findings
    if [ $XML_MATCH_PERCENTAGE -lt 70 ]; then
        echo "- **XML Structure Gaps**: Only ${XML_MATCH_PERCENTAGE}% of key XML files match. Focus on improving XML generation in the enhanced generator." >> comparison_report.md
    fi
    
    if [ $MEDIA_MATCH_PERCENTAGE -lt 50 ]; then
        echo "- **Media Preservation Issues**: Only ${MEDIA_MATCH_PERCENTAGE}% of media files preserved. Improve base64 encoding/decoding and media embedding." >> comparison_report.md
    fi
    
    if [ $FILE_MATCH_PERCENTAGE -lt 80 ]; then
        echo "- **Missing Files**: Only ${FILE_MATCH_PERCENTAGE}% of files present. Check for missing relationship files and content types." >> comparison_report.md
    fi
    
    cat >> comparison_report.md <<EOF

### Extractor Improvements Needed
- [ ] Extract missing XML elements and attributes
- [ ] Improve media file extraction and encoding
- [ ] Extract complete relationship mappings
- [ ] Capture missing document properties

### Generator Improvements Needed  
- [ ] Generate missing XML structure elements
- [ ] Improve media embedding with proper relationships
- [ ] Create complete file structure
- [ ] Apply missing formatting and properties

### Next Steps
1. Focus on issues with highest impact on fidelity score
2. Test iteratively after each improvement
3. Target overall fidelity score of 85%+

---
*Generated by PowerPoint Fidelity Testing Framework*
EOF

    echo ""
    echo "📊 FIDELITY ANALYSIS COMPLETE"
    echo "=================================="
    echo "Overall Fidelity Score: ${OVERALL_FIDELITY_SCORE}%"
    echo "Directory Match: ${DIRECTORY_MATCH_PERCENTAGE}%"
    echo "File Match: ${FILE_MATCH_PERCENTAGE}%"
    echo "XML Match: ${XML_MATCH_PERCENTAGE}%"
    echo "Media Preservation: ${MEDIA_MATCH_PERCENTAGE}%"
    echo "=================================="
}

# Check arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <original.pptx> <generated.pptx>"
    exit 1
fi

# Run comparison
compare_pptx_files "$1" "$2"