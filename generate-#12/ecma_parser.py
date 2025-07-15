#!/usr/bin/env python3
"""
ECMA-376 Markdown Parser
Extracts hierarchical content structure from ECMA-376.md file
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Section:
    """Represents a document section with hierarchical structure"""
    full_section_number: str
    title: str
    description: str
    level1: Optional[str] = None
    level2: Optional[str] = None
    level3: Optional[str] = None
    level4: Optional[str] = None
    level5: Optional[str] = None
    depth: int = 1
    page_reference: Optional[str] = None
    section_type: str = "heading"
    parent_section: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for database insertion"""
        return asdict(self)

class EcmaParser:
    """Parser for ECMA-376 markdown file"""
    
    def __init__(self, markdown_file: str):
        self.markdown_file = Path(markdown_file)
        self.sections: List[Section] = []
        self.section_hierarchy: Dict[str, str] = {}  # Maps section numbers to parent section numbers
        
        # Regular expressions for parsing - more restrictive patterns
        self.section_patterns = [
            # Pattern for main sections with dots like "1.  Scope .... 1"
            r'^(\d+)\.\s\s+([A-Z][A-Za-z\s\-]+?)(?:\s+\.{3,}\s*(\d+))?$',
            # Pattern for main sections without dots like "12." (title on next line)
            r'^(\d+)\.\s*$',
            # Pattern for subsections like "8.4  WordprocessingML .... 16"
            r'^(\d+\.\d+)\s\s+([A-Z][A-Za-z\s\-()]+?)(?:\s+\.{3,}\s*(\d+))?$',
            # Pattern for detailed sections like "11.3.10  Main Document Part .... 432"
            r'^(\d+\.\d+\.\d+)\s\s+([A-Z][A-Za-z\s\-()]+?)(?:\s+\.{3,}\s*(\d+))?$',
            # Pattern for deep sections like "17.3.1.1  mirrorIndents .... 232"
            r'^(\d+\.\d+\.\d+\.\d+)\s\s+([A-Za-z][A-Za-z\s\-()]+?)(?:\s+\.{3,}\s*(\d+))?$',
            # Pattern for deepest sections like "20.1.2.2.1  bldChart (Build Chart) .... 2728"
            r'^(\d+\.\d+\.\d+\.\d+\.\d+)\s\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]+)\)(?:\s+\.{3,}\s*(\d+))?$',
        ]
        
        # Known level 1 sections that should be captured
        self.level1_sections = {
            '1': 'Scope',
            '2': 'Conformance', 
            '3': 'Normative References',
            '4': 'Terms and Definitions',
            '5': 'Notational Conventions',
            '6': 'Acronyms and Abbreviations',
            '7': 'General Description',
            '8': 'Overview',
            '9': 'Packages',
            '10': 'Markup Compatibility and Extensibility',
            '11': 'WordprocessingML',
            '12': 'SpreadsheetML',
            '13': 'PresentationML',
            '14': 'DrawingML',
            '15': 'Shared',
            '16': 'Part Overview',
            '17': 'WordprocessingML Reference Material',
            '18': 'SpreadsheetML Reference Material',
            '19': 'PresentationML Reference Material',
            '20': 'DrawingML - Framework Reference Material',
            '21': 'DrawingML - Components Reference Material',
            '22': 'Shared MLs Reference Material',
            '23': 'Custom XML Schema References'
        }
        
        # Pattern to extract page numbers
        self.page_pattern = r'\.+\s*(\d+)\s*$'
        
    def parse_file(self) -> List[Section]:
        """Parse the markdown file and extract all sections"""
        logger.info(f"Starting to parse {self.markdown_file}")
        
        if not self.markdown_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {self.markdown_file}")
        
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        self._parse_lines(lines)
        
        logger.info(f"Parsed {len(self.sections)} sections")
        return self.sections
    
    def _parse_lines(self, lines: List[str]) -> None:
        """Parse individual lines to extract sections"""
        current_description = []
        last_section = None
        seen_sections = set()  # Track seen section numbers to avoid duplicates
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip lines that shouldn't be processed
            if self._should_skip_line(line):
                continue
            
            # Try to match section patterns
            section = self._parse_section_line(line, i, lines)
            
            if section:
                # Skip duplicate section numbers
                if section.full_section_number in seen_sections:
                    continue
                    
                # If we have a previous section, finalize its description
                if last_section and current_description:
                    last_section.description = ' '.join(current_description).strip()
                    current_description = []
                
                self.sections.append(section)
                seen_sections.add(section.full_section_number)
                last_section = section
                
                # Build hierarchy mapping
                self._update_hierarchy(section)
                
            else:
                # Collect description text
                if last_section and line and not self._is_table_of_contents_line(line):
                    # Skip page numbers and dots
                    cleaned_line = re.sub(r'\.{3,}.*?\d+\s*$', '', line).strip()
                    if cleaned_line and len(cleaned_line) > 3:
                        current_description.append(cleaned_line)
        
        # Finalize last section description
        if last_section and current_description:
            last_section.description = ' '.join(current_description).strip()
    
    def _parse_section_line(self, line: str, line_index: int, lines: List[str]) -> Optional[Section]:
        """Parse a single line to extract section information"""
        for i, pattern in enumerate(self.section_patterns):
            match = re.match(pattern, line)
            if match:
                section_number = match.group(1)
                
                # Handle different pattern formats
                if i == 1:  # Pattern for "12." (title on next line)
                    # Check if this is a valid level 1 section
                    if section_number in self.level1_sections:
                        title = self.level1_sections[section_number]
                        page_ref = None
                    else:
                        continue
                elif i == 5:  # Level 5 pattern with parentheses: "20.1.2.2.1  bldChart (Build Chart)"
                    element_name = match.group(2).strip()
                    description = match.group(3).strip()
                    title = f"{element_name} ({description})"
                    page_ref = match.group(4) if len(match.groups()) > 3 and match.group(4) else None
                else:
                    title = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else ""
                    page_ref = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
                
                # Skip if title is empty
                if not title:
                    continue
                
                # Skip if title is too short (likely not a real section)
                if len(title.strip()) < 3:
                    continue
                
                # Validate section number format
                if not self._is_valid_section_number(section_number):
                    continue
                
                # For level 1 sections, only accept if it's in our known list and has proper context
                if '.' not in section_number:
                    if section_number not in self.level1_sections:
                        continue
                    # Additional validation for level 1 sections
                    if not self._is_valid_level1_context(line, line_index, lines):
                        continue
                
                return self._create_section(section_number, title, page_ref)
        
        return None
    
    def _create_section(self, section_number: str, title: str, page_ref: Optional[str]) -> Section:
        """Create a Section object from parsed components"""
        # Parse the hierarchical levels
        parts = section_number.split('.')
        depth = len(parts)
        
        # Initialize level fields
        levels = [None] * 5
        for i, part in enumerate(parts[:5]):  # Max 5 levels
            if i == 0:
                levels[i] = part
            else:
                levels[i] = '.'.join(parts[:i+1])
        
        # Determine section type based on title patterns
        section_type = self._determine_section_type(title)
        
        # Find parent section number
        parent_section = None
        if depth > 1:
            parent_section = '.'.join(parts[:-1])
        
        section = Section(
            full_section_number=section_number,
            title=title,
            description="",  # Will be filled later
            level1=levels[0],
            level2=levels[1],
            level3=levels[2],
            level4=levels[3],
            level5=levels[4],
            depth=depth,
            page_reference=page_ref,
            section_type=section_type,
            parent_section=parent_section
        )
        
        return section
    
    def _determine_section_type(self, title: str) -> str:
        """Determine the type of section based on title patterns"""
        title_lower = title.lower()
        
        if '(' in title and ')' in title:
            # Elements like "bldChart (Build Chart)"
            return "element"
        elif any(keyword in title_lower for keyword in ['property', 'properties', 'attribute']):
            return "property"
        elif any(keyword in title_lower for keyword in ['reference', 'material']):
            return "reference"
        elif title.isupper():
            return "constant"
        else:
            return "heading"
    
    def _update_hierarchy(self, section: Section) -> None:
        """Update the hierarchy mapping"""
        if section.parent_section:
            self.section_hierarchy[section.full_section_number] = section.parent_section
    
    def _is_valid_section_number(self, section_number: str) -> bool:
        """Check if a section number is valid"""
        if not section_number:
            return False
            
        parts = section_number.split('.')
        try:
            # All parts should be numeric and positive
            if not all(part.isdigit() and int(part) > 0 for part in parts):
                return False
            
            # Should have 1-5 parts for depth 1-5
            if len(parts) < 1 or len(parts) > 5:
                return False
            
            # For level 1, check if it's in our known list
            if len(parts) == 1:
                return section_number in self.level1_sections
            
            # First part should be reasonable (not too large)
            if int(parts[0]) > 100:  # Arbitrary reasonable limit
                return False
                
            return True
        except:
            return False
    
    def _is_table_of_contents_line(self, line: str) -> bool:
        """Check if line is part of table of contents (has dots and page numbers)"""
        return bool(re.search(r'\.{3,}.*?\d+\s*$', line))
    
    def _should_skip_line(self, line: str) -> bool:
        """Check if line should be skipped during parsing"""
        line = line.strip()
        if not line:
            return True
            
        # Skip lines that are clearly not section headers
        skip_patterns = [
            r'^[a-z]',  # Lines starting with lowercase (likely content)
            r'^\[',     # Lines starting with brackets
            r'^\s*$',   # Empty lines
            r'^[A-Z]{2,}:',  # Lines like "NOTE:", "EXAMPLE:", etc.
            r'^\s*\d+\s*$',  # Lines with just numbers
            r'^[^0-9]',  # Lines not starting with numbers (except for specific patterns)
            r'^\d+\s*[a-z]',  # Lines like "1 some text" without proper formatting
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, line):
                return True
                
        return False
    
    def _is_valid_level1_context(self, line: str, line_index: int, lines: List[str]) -> bool:
        """Check if this is a valid level 1 section based on context"""
        # Check if we're in the table of contents area (first 1000 lines)
        # or in a main section area
        if line_index > 1000:
            # For sections after table of contents, be very strict
            # Only accept if the line has dots leading to page numbers
            if re.search(r'\.{3,}.*?\d+\s*$', line):
                return True
            # Or if it's the simple format that appears at known locations
            section_num = re.match(r'^(\d+)\.\s*$', line)
            if section_num:
                num = section_num.group(1)
                # Check if the next few lines contain the expected title
                for j in range(1, 5):  # Check next 4 lines
                    if line_index + j < len(lines):
                        next_line = lines[line_index + j].strip()
                        if next_line and num in self.level1_sections:
                            expected_title = self.level1_sections[num]
                            if expected_title.lower() in next_line.lower():
                                return True
                return False
        
        # In table of contents area, accept valid sections
        return True
    
    def save_to_json(self, output_file: str) -> None:
        """Save parsed sections to JSON file for debugging"""
        output_path = Path(output_file)
        data = {
            'sections': [section.to_dict() for section in self.sections],
            'hierarchy': self.section_hierarchy,
            'total_sections': len(self.sections)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved parsed data to {output_path}")
    
    def get_sections_by_depth(self, depth: int) -> List[Section]:
        """Get all sections at a specific depth level"""
        return [section for section in self.sections if section.depth == depth]
    
    def get_section_by_number(self, section_number: str) -> Optional[Section]:
        """Get a specific section by its number"""
        for section in self.sections:
            if section.full_section_number == section_number:
                return section
        return None
    
    def print_statistics(self) -> None:
        """Print parsing statistics"""
        depth_counts = {}
        type_counts = {}
        
        for section in self.sections:
            depth_counts[section.depth] = depth_counts.get(section.depth, 0) + 1
            type_counts[section.section_type] = type_counts.get(section.section_type, 0) + 1
        
        print(f"\n=== ECMA-376 Parsing Statistics ===")
        print(f"Total sections parsed: {len(self.sections)}")
        print(f"\nSections by depth:")
        for depth in sorted(depth_counts.keys()):
            print(f"  Level {depth}: {depth_counts[depth]} sections")
        
        print(f"\nSections by type:")
        for section_type in sorted(type_counts.keys()):
            print(f"  {section_type}: {type_counts[section_type]} sections")

def main():
    """Main function for testing the parser"""
    parser = EcmaParser('ecma-376.md')
    
    try:
        sections = parser.parse_file()
        parser.print_statistics()
        
        # Save parsed data
        parser.save_to_json('parsed_sections.json')
        
        # Show some example sections
        print(f"\n=== Sample Sections ===")
        for i, section in enumerate(sections[:10]):
            print(f"{i+1}. {section.full_section_number} - {section.title}")
            if section.description:
                desc = section.description[:100] + "..." if len(section.description) > 100 else section.description
                print(f"   Description: {desc}")
            print()
        
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        raise

if __name__ == "__main__":
    main()