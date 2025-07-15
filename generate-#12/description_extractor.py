#!/usr/bin/env python3
"""
Description Extractor for ECMA-376 Level 5 Sections
Systematically extracts descriptions from the markdown file for missing level 5 elements
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import psycopg2
from database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DescriptionExtractor:
    """Extracts descriptions for ECMA-376 elements from markdown"""
    
    def __init__(self, markdown_file: str):
        self.markdown_file = Path(markdown_file)
        self.content = ""
        self.lines = []
        
    def load_content(self):
        """Load the markdown file content"""
        logger.info(f"Loading content from {self.markdown_file}")
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        self.lines = self.content.split('\n')
        logger.info(f"Loaded {len(self.lines)} lines")
    
    def find_section_content(self, section_number: str, title: str) -> Optional[str]:
        """Find and extract content for a specific section"""
        logger.info(f"Searching for section {section_number} - {title}")
        
        # Extract element name from title (e.g., "alpha" from "alpha (Alpha)")
        element_name = title.split('(')[0].strip()
        
        # First try to find the actual documentation section (not table of contents)
        content = self._find_actual_documentation(section_number, title, element_name)
        
        if content:
            return content
        
        # Fallback: look for section headers directly
        return self._find_section_header_content(section_number, title)
    
    def _find_actual_documentation(self, section_number: str, title: str, element_name: str) -> Optional[str]:
        """Find the actual documentation content (not table of contents)"""
        
        # Look for patterns that indicate actual documentation
        doc_patterns = [
            # Look for section headers followed by description content
            rf'^{re.escape(section_number)}\s+{re.escape(element_name)}\s*\(',
            # Look for element name at beginning of line with description
            rf'^{re.escape(element_name)}\s*\(',
            # Look for XML examples with the element
            rf'<[^>]*{re.escape(element_name)}[^>]*>',
        ]
        
        potential_sections = []
        
        # Search for documentation patterns
        for i, line in enumerate(self.lines):
            line_stripped = line.strip()
            
            # Skip table of contents lines (those with dots and page numbers)
            if re.search(r'\\.{3,}.*?\d+\s*$', line_stripped):
                continue
            
            for pattern in doc_patterns:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    # Check if this looks like actual documentation
                    if self._is_documentation_context(i, element_name):
                        potential_sections.append(i)
                        logger.info(f"Found potential documentation at line {i+1}: {line_stripped[:100]}")
                        break
        
        # If we found potential sections, extract from the best one
        if potential_sections:
            # Use the first one that seems to have substantial content
            for start_line in potential_sections:
                content = self._extract_documentation_content(start_line, element_name)
                if content and len(content.strip()) > 50:
                    return content
        
        return None
    
    def _is_documentation_context(self, line_index: int, element_name: str) -> bool:
        """Check if the context around a line looks like documentation"""
        # Look at surrounding lines for documentation indicators
        start = max(0, line_index - 5)
        end = min(len(self.lines), line_index + 20)
        
        context_lines = self.lines[start:end]
        context_text = ' '.join(context_lines).lower()
        
        # Indicators of documentation content
        doc_indicators = [
            'this element',
            'specifies',
            'attribute',
            'example',
            'schema',
            'complex type',
            'data type',
            'val=',
            '<a:',
            'percentage',
            'opacity',
        ]
        
        indicator_count = sum(1 for indicator in doc_indicators if indicator in context_text)
        return indicator_count >= 2
    
    def _extract_documentation_content(self, start_line: int, element_name: str) -> str:
        """Extract documentation content starting from a specific line"""
        content_lines = []
        i = start_line
        
        # Collect content for up to 50 lines or until we hit another section
        max_lines = 50
        lines_collected = 0
        
        while i < len(self.lines) and lines_collected < max_lines:
            line = self.lines[i].strip()
            
            # Stop if we hit a clear section boundary
            if self._is_section_boundary(line, start_line, i):
                break
            
            # Collect meaningful content
            if line:
                # Skip table of contents style lines
                if not re.search(r'\\.{3,}.*?\d+\s*$', line):
                    content_lines.append(line)
                    lines_collected += 1
            
            i += 1
        
        if not content_lines:
            return ""
        
        return self._process_documentation_content(content_lines, element_name)
    
    def _is_section_boundary(self, line: str, start_line: int, current_line: int) -> bool:
        """Check if we've hit a section boundary"""
        # If we're more than 30 lines from start, look for new sections
        if current_line - start_line > 30:
            # Look for patterns that indicate new sections
            if re.match(r'^\d+\.\d+\.\d+\.\d+\.\d+\s+\w+', line):
                return True
            if re.match(r'^\d+\.\d+\.\d+\.\d+\s+\w+', line):
                return True
        
        return False
    
    def _process_documentation_content(self, content_lines: List[str], element_name: str) -> str:
        """Process and structure the documentation content"""
        content = ' '.join(content_lines)
        
        # Clean up excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Structure the content
        structured_parts = []
        
        # Look for description
        if 'this element' in content.lower():
            desc_match = re.search(r'this element[^.]*\.', content, re.IGNORECASE)
            if desc_match:
                structured_parts.append(desc_match.group(0))
        
        # Look for attributes
        if 'attribute' in content.lower() or 'val' in content:
            structured_parts.append("This element has attributes that control its behavior.")
        
        # Look for examples
        if any(indicator in content for indicator in ['<a:', 'example', 'val=']):
            structured_parts.append("XML examples and usage patterns are provided in the specification.")
        
        # Look for data types
        if 'data type' in content.lower() or 'ST_' in content:
            structured_parts.append("Defined with specific data types in the schema.")
        
        # If we have structured content, use it; otherwise use raw content
        if structured_parts:
            description = '. '.join(structured_parts)
            # Add some raw content for context
            if len(content) > 100:
                description += f". {content[:300]}..."
            else:
                description += f". {content}"
        else:
            # Just use the content, trimmed
            description = content[:500] + '...' if len(content) > 500 else content
        
        return description.strip()
    
    def _find_section_header_content(self, section_number: str, title: str) -> Optional[str]:
        """Fallback method to find content using section headers"""
        # This is the original approach - look for table of contents entries
        patterns = [
            rf'^{re.escape(section_number)}\s\s+{re.escape(title)}.*?(\d+)\s*$',
            rf'^{re.escape(section_number)}\s+{re.escape(title)}',
        ]
        
        for i, line in enumerate(self.lines):
            line_stripped = line.strip()
            for pattern in patterns:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    return self._extract_content_after_header(i, section_number)
        
        return None
    
    def _extract_content_after_header(self, start_line: int, section_number: str) -> str:
        """Extract meaningful content after a section header"""
        content_lines = []
        i = start_line + 1
        
        # Skip empty lines after header
        while i < len(self.lines) and not self.lines[i].strip():
            i += 1
        
        # Determine the next section to stop at
        section_parts = section_number.split('.')
        next_section_patterns = self._get_next_section_patterns(section_parts)
        
        # Extract content until we hit another section or reach content limit
        lines_collected = 0
        max_lines = 100  # Reasonable limit to avoid collecting too much
        
        while i < len(self.lines) and lines_collected < max_lines:
            line = self.lines[i].strip()
            
            # Stop if we hit another section
            if self._is_next_section(line, next_section_patterns):
                break
            
            # Stop if we hit a page break or form feed
            if line.startswith('\f') or line == '---':
                break
            
            # Collect meaningful content
            if line:
                # Skip table of contents style lines
                if not re.search(r'\\.{3,}.*?\d+\s*$', line):
                    content_lines.append(line)
                    lines_collected += 1
            
            i += 1
        
        if not content_lines:
            return ""
        
        # Process the collected content
        return self._process_extracted_content(content_lines)
    
    def _get_next_section_patterns(self, current_section_parts: List[str]) -> List[str]:
        """Generate patterns for the next possible sections"""
        patterns = []
        
        # Next sibling section (e.g., 20.1.2.2.2 after 20.1.2.2.1)
        if len(current_section_parts) >= 1:
            last_num = int(current_section_parts[-1])
            next_sibling = current_section_parts[:-1] + [str(last_num + 1)]
            patterns.append(r'^' + re.escape('.'.join(next_sibling)) + r'\s')
        
        # Parent's next sibling (e.g., 20.1.2.3 after 20.1.2.2.x)
        if len(current_section_parts) >= 2:
            parent_parts = current_section_parts[:-1]
            parent_last_num = int(parent_parts[-1])
            parent_next = parent_parts[:-1] + [str(parent_last_num + 1)]
            patterns.append(r'^' + re.escape('.'.join(parent_next)) + r'\s')
        
        # Any other section at same or higher level
        level = len(current_section_parts)
        for i in range(1, level + 1):
            patterns.append(r'^\d+' + r'\.d+' * (i-1) + r'\s')
        
        return patterns
    
    def _is_next_section(self, line: str, patterns: List[str]) -> bool:
        """Check if line starts a new section"""
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        return False
    
    def _process_extracted_content(self, content_lines: List[str]) -> str:
        """Process and clean the extracted content"""
        # Join lines and clean up
        content = ' '.join(content_lines)
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Identify and structure different types of content
        structured_content = []
        
        # Look for attributes section
        if 'attribute' in content.lower():
            structured_content.append("This element has the following attributes:")
        
        # Look for examples
        if any(keyword in content.lower() for keyword in ['example', 'instance', '<']):
            if not any('example' in part.lower() for part in structured_content):
                structured_content.append("Example usage is provided in the specification.")
        
        # Look for schema information
        if any(keyword in content.lower() for keyword in ['schema', 'complex type', 'CT_']):
            if not any('schema' in part.lower() for part in structured_content):
                structured_content.append("Defined in the W3C XML Schema.")
        
        # If we have structured content, combine it
        if structured_content:
            description = '. '.join(structured_content) + f'. {content[:200]}...' if len(content) > 200 else f'. {content}'
        else:
            # Just use the raw content, trimmed
            description = content[:500] + '...' if len(content) > 500 else content
        
        return description.strip()

def extract_descriptions_for_missing_sections():
    """Main function to extract descriptions for all missing level 5 sections"""
    
    # Initialize components
    extractor = DescriptionExtractor('ecma-376.md')
    extractor.load_content()
    
    db = DatabaseManager()
    
    # Get sections without descriptions
    with psycopg2.connect(**db.db_config) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT full_section_number, title
                FROM ecma_sections 
                WHERE depth = 5 AND (description IS NULL OR description = '')
                ORDER BY full_section_number;
            ''')
            
            missing_sections = cur.fetchall()
    
    logger.info(f"Found {len(missing_sections)} sections without descriptions")
    
    # Extract descriptions for each section
    extracted_count = 0
    failed_count = 0
    
    for section_number, title in missing_sections:
        try:
            description = extractor.find_section_content(section_number, title)
            
            if description and len(description.strip()) > 10:  # Minimum meaningful length
                # Update database
                with psycopg2.connect(**db.db_config) as conn:
                    with conn.cursor() as cur:
                        cur.execute('''
                            UPDATE ecma_sections 
                            SET description = %s
                            WHERE full_section_number = %s
                        ''', (description, section_number))
                        conn.commit()
                
                logger.info(f"✅ Updated {section_number} - {title}")
                logger.info(f"   Description: {description[:100]}...")
                extracted_count += 1
            else:
                logger.warning(f"❌ No meaningful description found for {section_number} - {title}")
                failed_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error processing {section_number}: {e}")
            failed_count += 1
    
    logger.info(f"\n=== Extraction Complete ===")
    logger.info(f"Successfully extracted: {extracted_count}")
    logger.info(f"Failed extractions: {failed_count}")
    logger.info(f"Total processed: {len(missing_sections)}")

if __name__ == "__main__":
    extract_descriptions_for_missing_sections()