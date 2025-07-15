#!/usr/bin/env python3
"""
ECMA-376 Markdown Parser - FIXED VERSION
Correctly extracts descriptions from element title to next element title
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

class EcmaParserFixed:
    """Fixed Parser for ECMA-376 markdown file"""
    
    def __init__(self, markdown_file: str):
        self.markdown_file = Path(markdown_file)
        self.sections: List[Section] = []
        self.section_hierarchy: Dict[str, str] = {}
        
        # Updated pattern to match section structure like "20.1.2.2.1"
        self.section_number_pattern = r'^(\d+(?:\.\d+){0,4})$'
        
        # Pattern to match element titles like "bldChart (Build Chart)"
        self.element_title_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]+)\)$'
        
        # Pattern to match general titles
        self.general_title_pattern = r'^([A-Z][^.]*?)(?:\s*\.{3,}.*)?$'
        
    def parse_file(self) -> List[Section]:
        """Parse the markdown file and extract all sections"""
        logger.info(f"Starting to parse {self.markdown_file}")
        
        if not self.markdown_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {self.markdown_file}")
        
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        self._parse_lines_fixed(lines)
        
        logger.info(f"Parsed {len(self.sections)} sections")
        return self.sections
    
    def _parse_lines_fixed(self, lines: List[str]) -> None:
        """Fixed parsing logic to correctly extract descriptions"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
                
            # Check if this line is a section number
            section_match = re.match(self.section_number_pattern, line)
            
            if section_match:
                section_number = section_match.group(1)
                
                # Look for the title in the next few lines
                title_line_idx = self._find_title_line(lines, i + 1)
                
                if title_line_idx != -1:
                    title = lines[title_line_idx].strip()
                    
                    # Skip table of contents entries (have dots and page numbers)
                    if '...' in title and re.search(r'\d+\s*$', title):
                        i += 1
                        continue
                    
                    # Extract description starting from after the title
                    description_start = title_line_idx + 1
                    description_end = self._find_next_section_start(lines, description_start)
                    
                    # Extract description text
                    description_lines = []
                    for desc_idx in range(description_start, description_end):
                        desc_line = lines[desc_idx].strip()
                        if desc_line and not self._is_noise_line(desc_line):
                            description_lines.append(desc_line)
                    
                    description = ' '.join(description_lines).strip()
                    
                    # Clean up title (remove page numbers and dots)
                    clean_title = re.sub(r'\s*\.{3,}.*$', '', title).strip()
                    
                    # Create section
                    section = self._create_section(section_number, clean_title, description)
                    self.sections.append(section)
                    
                    # Move to the next section
                    i = description_end
                else:
                    i += 1
            else:
                i += 1
    
    def _find_title_line(self, lines: List[str], start_idx: int) -> int:
        """Find the title line after a section number"""
        # Look in the next few lines for the title
        for i in range(start_idx, min(start_idx + 5, len(lines))):
            line = lines[i].strip()
            if line and not line.isdigit() and len(line) > 2:
                # Skip obvious noise lines
                if not self._is_noise_line(line):
                    return i
        return -1
    
    def _find_next_section_start(self, lines: List[str], start_idx: int) -> int:
        """Find where the next section starts"""
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            
            # Check if this is a section number
            if re.match(self.section_number_pattern, line):
                # Verify it's followed by a title
                title_idx = self._find_title_line(lines, i + 1)
                if title_idx != -1:
                    return i
        
        return len(lines)
    
    def _is_noise_line(self, line: str) -> bool:
        """Check if line is noise (page numbers, headers, etc.)"""
        line = line.strip()
        
        # Skip very short lines
        if len(line) < 3:
            return True
            
        # Skip lines that are just numbers
        if line.isdigit():
            return True
            
        # Skip lines that are just page references
        if re.match(r'^\d+\s*$', line):
            return True
            
        # Skip obvious headers
        if line in ['ECMA-376 Part 1', '20. DrawingML - Framework Reference Material']:
            return True
            
        # Skip lines with just dots
        if re.match(r'^\.+$', line):
            return True
            
        return False
    
    def _create_section(self, section_number: str, title: str, description: str) -> Section:
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
            description=description,
            level1=levels[0],
            level2=levels[1],
            level3=levels[2],
            level4=levels[3],
            level5=levels[4],
            depth=depth,
            page_reference=None,
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
    
    def print_statistics(self) -> None:
        """Print parsing statistics"""
        depth_counts = {}
        type_counts = {}
        
        for section in self.sections:
            depth_counts[section.depth] = depth_counts.get(section.depth, 0) + 1
            type_counts[section.section_type] = type_counts.get(section.section_type, 0) + 1
        
        print(f"\n=== ECMA-376 Fixed Parsing Statistics ===")
        print(f"Total sections parsed: {len(self.sections)}")
        print(f"\nSections by depth:")
        for depth in sorted(depth_counts.keys()):
            print(f"  Level {depth}: {depth_counts[depth]} sections")
        
        print(f"\nSections by type:")
        for section_type in sorted(type_counts.keys()):
            print(f"  {section_type}: {type_counts[section_type]} sections")

def main():
    """Main function for testing the fixed parser"""
    parser = EcmaParserFixed('ecma-376.md')
    
    try:
        sections = parser.parse_file()
        parser.print_statistics()
        
        # Save parsed data
        parser.save_to_json('parsed_sections_fixed.json')
        
        # Look for the specific bldChart section to verify it's correct
        bld_chart_section = None
        for section in sections:
            if section.full_section_number == '20.1.2.2.1':
                bld_chart_section = section
                break
        
        if bld_chart_section:
            print(f"\n=== Found bldChart Section ===")
            print(f"Number: {bld_chart_section.full_section_number}")
            print(f"Title: {bld_chart_section.title}")
            print(f"Type: {bld_chart_section.section_type}")
            print(f"Description: {bld_chart_section.description[:200]}...")
        else:
            print("\n❌ bldChart section not found!")
        
        # Show some example sections
        print(f"\n=== Sample Sections ===")
        for i, section in enumerate(sections[:5]):
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