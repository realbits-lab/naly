#!/usr/bin/env python3
"""
RAG-based Slide Generator
Creates PowerPoint slides based on vector database queries and generates complete PPTX files.
"""

import os
import json
import shutil
import zipfile
import xml.dom.minidom
from pathlib import Path
from typing import Dict, List, Any
from vector_db_system import VectorDatabase, RAGChatBot
import xml.etree.ElementTree as ET

class RAGSlideGenerator:
    """Generates slide XML content based on RAG queries and reference slides."""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
    
    def generate_slide_xml(self, query: str, title: str = None, subtitle: str = None) -> str:
        """
        Generate slide1.xml content based on user query and reference slides.
        
        Args:
            query: User query describing desired slide content
            title: Optional custom title
            subtitle: Optional custom subtitle
            
        Returns:
            Complete slide XML string
        """
        # Search for relevant reference slides
        relevant_slides = self.vector_db.search_similar(query, top_k=3)
        
        if not relevant_slides:
            # Fallback to basic slide if no relevant content found
            return self._generate_basic_slide(title or "New Slide", subtitle or "Generated content")
        
        # Use the most relevant slide as base template
        base_slide = relevant_slides[0]
        base_xml = base_slide.get('xml_content', '')
        
        if not base_xml:
            return self._generate_basic_slide(title or "New Slide", subtitle or "Generated content")
        
        # Parse and modify the XML based on query
        try:
            # Parse the base XML
            root = ET.fromstring(base_xml)
            
            # Extract shapes and text content for analysis
            slide_info = self._extract_slide_info(relevant_slides, query)
            
            # Modify the slide content
            modified_xml = self._modify_slide_content(root, slide_info, title, subtitle, query)
            
            return modified_xml
            
        except Exception as e:
            print(f"Error generating slide XML: {e}")
            return self._generate_basic_slide(title or "Error", subtitle or "Could not generate content")
    
    def _extract_slide_info(self, relevant_slides: List[Dict], query: str) -> Dict:
        """Extract useful information from relevant slides."""
        slide_info = {
            "titles": [],
            "subtitles": [],
            "shapes": [],
            "purposes": [],
            "colors": [],
            "query_focus": query.lower()
        }
        
        for slide in relevant_slides:
            slide_info["titles"].append(slide.get('title', ''))
            slide_info["purposes"].append(slide.get('overall_purpose', ''))
            
            # Extract shape information
            shapes = slide.get('shapes_json', [])
            for shape in shapes:
                slide_info["shapes"].append({
                    "type": shape.get('type', ''),
                    "description": shape.get('description', ''),
                    "purpose": shape.get('purpose', ''),
                    "color": shape.get('color', '')
                })
        
        return slide_info
    
    def _modify_slide_content(self, root: ET.Element, slide_info: Dict, title: str, subtitle: str, query: str) -> str:
        """Modify slide XML content based on extracted information and query."""
        
        # Find and update title text
        if title:
            self._update_text_elements(root, title, "ctrTitle")
        elif slide_info["titles"]:
            # Generate title based on query and reference titles
            generated_title = self._generate_contextual_title(query, slide_info["titles"])
            self._update_text_elements(root, generated_title, "ctrTitle")
        
        # Find and update subtitle text  
        if subtitle:
            self._update_text_elements(root, subtitle, "subTitle")
        elif query:
            # Generate subtitle based on query
            generated_subtitle = self._generate_contextual_subtitle(query, slide_info)
            self._update_text_elements(root, generated_subtitle, "subTitle")
        
        # Pretty format the XML
        try:
            xml_str = ET.tostring(root, encoding='unicode')
            dom = xml.dom.minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="", newl="")
            # Remove the XML declaration for consistency with original format
            if pretty_xml.startswith('<?xml'):
                pretty_xml = pretty_xml.split('\n', 1)[1] if '\n' in pretty_xml else pretty_xml
            return pretty_xml.strip()
        except:
            # Fallback to simple string conversion
            return ET.tostring(root, encoding='unicode')
    
    def _update_text_elements(self, root: ET.Element, new_text: str, placeholder_type: str):
        """Update text elements in the slide XML."""
        # Define namespace
        namespaces = {
            'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
        }
        
        # Find text elements with the specified placeholder type
        for sp in root.findall('.//p:sp', namespaces):
            nvpr = sp.find('.//p:nvPr', namespaces)
            if nvpr is not None:
                ph = nvpr.find('p:ph', namespaces)
                if ph is not None and ph.get('type') == placeholder_type:
                    # Find the text element and update it
                    txt_body = sp.find('.//p:txBody', namespaces)
                    if txt_body is not None:
                        # Find the text run
                        for t_elem in txt_body.findall('.//a:t', namespaces):
                            t_elem.text = new_text
                            break
    
    def _generate_contextual_title(self, query: str, reference_titles: List[str]) -> str:
        """Generate a contextual title based on query and reference titles."""
        query_lower = query.lower()
        
        # Map common query terms to title patterns
        title_patterns = {
            "chart": "Data Visualization Charts",
            "graph": "Statistical Graphs", 
            "infographic": "Information Graphics",
            "design": "Design Elements",
            "template": "Presentation Template",
            "data": "Data Analysis",
            "business": "Business Insights",
            "analytics": "Analytics Dashboard",
            "comparison": "Comparative Analysis",
            "trend": "Trend Analysis"
        }
        
        # Find matching pattern
        for keyword, pattern in title_patterns.items():
            if keyword in query_lower:
                return pattern
        
        # Fallback: Use first reference title or generate generic
        if reference_titles and reference_titles[0]:
            return reference_titles[0]
        
        return "Generated Slide Content"
    
    def _generate_contextual_subtitle(self, query: str, slide_info: Dict) -> str:
        """Generate a contextual subtitle based on query and slide information."""
        query_lower = query.lower()
        
        # Generate subtitle based on query intent
        if any(word in query_lower for word in ["create", "generate", "make", "build"]):
            return "Custom generated content based on your requirements"
        elif any(word in query_lower for word in ["show", "display", "present"]):
            return "Visual presentation of key information"
        elif any(word in query_lower for word in ["analyze", "compare", "study"]):
            return "Detailed analysis and insights"
        else:
            return "Professional slide content"
    
    def _generate_basic_slide(self, title: str, subtitle: str) -> str:
        """Generate a basic slide XML when no reference is available."""
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:mv="urn:schemas-microsoft-com:mac:vml" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name="Content Placeholder 1"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr><p:sp><p:nvSpPr><p:cNvPr id="2" name="Title 2"/><p:cNvSpPr/><p:nvPr><p:ph type="ctrTitle"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="914400" y="457200"/><a:ext cx="7315200" cy="1542600"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-US" sz="4400" b="1"/><a:t>{title}</a:t></a:r></a:p></p:txBody></p:sp><p:sp><p:nvSpPr><p:cNvPr id="3" name="Subtitle 3"/><p:cNvSpPr/><p:nvPr><p:ph type="subTitle" idx="1"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="914400" y="2057400"/><a:ext cx="7315200" cy="1027200"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-US" sz="2000"/><a:t>{subtitle}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''


class PowerPointBuilder:
    """Builds complete PowerPoint files from generated slides and template structure."""
    
    def __init__(self, template_path: str = "sample1-pptx"):
        self.template_path = Path(template_path)
        
    def create_presentation(self, slide_xml: str, output_filename: str = "generated_presentation.pptx") -> str:
        """
        Create a complete PowerPoint presentation with the generated slide.
        
        Args:
            slide_xml: Generated slide XML content
            output_filename: Output PPTX filename
            
        Returns:
            Path to the generated PPTX file
        """
        # Create temporary working directory
        temp_dir = Path("temp_pptx_build")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        # Copy template structure
        shutil.copytree(self.template_path, temp_dir)
        
        # Replace slide1.xml with generated content
        slide1_path = temp_dir / "ppt" / "slides" / "slide1.xml"
        with open(slide1_path, 'w', encoding='utf-8') as f:
            f.write(slide_xml)
        
        # Remove all other slides to create single-slide presentation
        self._create_single_slide_presentation(temp_dir)
        
        # Create ZIP file (PPTX format)
        output_path = Path(output_filename)
        if output_path.exists():
            output_path.unlink()
            
        self._create_zip_file(temp_dir, output_path)
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        
        return str(output_path.absolute())
    
    def _create_single_slide_presentation(self, temp_dir: Path):
        """Modify the presentation to contain only slide1."""
        
        # Update presentation.xml to reference only slide1
        pres_xml_path = temp_dir / "ppt" / "presentation.xml"
        self._update_presentation_xml(pres_xml_path)
        
        # Remove other slide files
        slides_dir = temp_dir / "ppt" / "slides"
        rels_dir = slides_dir / "_rels"
        
        # Keep only slide1 files
        for slide_file in slides_dir.glob("slide*.xml"):
            if not slide_file.name.startswith("slide1."):
                slide_file.unlink()
        
        for rels_file in rels_dir.glob("slide*.rels"):
            if not rels_file.name.startswith("slide1."):
                rels_file.unlink()
        
        # Remove corresponding notes slides (optional)
        notes_dir = temp_dir / "ppt" / "notesSlides"
        if notes_dir.exists():
            for note_file in notes_dir.glob("notesSlide*.xml"):
                if not note_file.name.startswith("notesSlide1."):
                    note_file.unlink()
            
            notes_rels_dir = notes_dir / "_rels"
            if notes_rels_dir.exists():
                for note_rels_file in notes_rels_dir.glob("notesSlide*.rels"):
                    if not note_rels_file.name.startswith("notesSlide1."):
                        note_rels_file.unlink()
        
        # Update Content_Types.xml to remove references to deleted slides
        self._update_content_types(temp_dir)
    
    def _update_presentation_xml(self, pres_xml_path: Path):
        """Update presentation.xml to reference only slide1."""
        try:
            with open(pres_xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Find slide ID list and keep only first slide
            namespaces = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
            sld_id_lst = root.find('.//p:sldIdLst', namespaces)
            
            if sld_id_lst is not None:
                # Keep only the first slide ID
                slides = sld_id_lst.findall('p:sldId', namespaces)
                for slide in slides[1:]:  # Remove all except first
                    sld_id_lst.remove(slide)
            
            # Write back
            xml_str = ET.tostring(root, encoding='unicode')
            with open(pres_xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
                
        except Exception as e:
            print(f"Warning: Could not update presentation.xml: {e}")
    
    def _update_content_types(self, temp_dir: Path):
        """Update Content_Types.xml to remove references to deleted slides."""
        content_types_path = temp_dir / "[Content_Types].xml"
        
        try:
            with open(content_types_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove slide references except slide1
            lines = content.split('>')
            filtered_lines = []
            
            for line in lines:
                # Keep everything except slide/notesSlide references that aren't slide1/notesSlide1
                if (('slide' in line and 'PartName="/ppt/slides/slide' in line and 'slide1.xml' not in line) or
                    ('notesSlide' in line and 'PartName="/ppt/notesSlides/notesSlide' in line and 'notesSlide1.xml' not in line)):
                    continue
                filtered_lines.append(line)
            
            updated_content = '>'.join(filtered_lines)
            
            with open(content_types_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
        except Exception as e:
            print(f"Warning: Could not update Content_Types.xml: {e}")
    
    def _create_zip_file(self, source_dir: Path, output_path: Path):
        """Create ZIP file from directory structure."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    # Get relative path for ZIP entry
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)


class RAGSlideChat:
    """Enhanced chat interface for slide generation."""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        self.slide_generator = RAGSlideGenerator(vector_db)
        self.ppt_builder = PowerPointBuilder()
        self.chat_bot = RAGChatBot(vector_db)
    
    def chat_with_generation(self, query: str, generate_slide: bool = False, 
                           title: str = None, subtitle: str = None, 
                           output_file: str = None) -> Dict[str, Any]:
        """
        Enhanced chat that can optionally generate slides.
        
        Args:
            query: User query
            generate_slide: Whether to generate a slide
            title: Optional slide title
            subtitle: Optional slide subtitle
            output_file: Optional output filename
            
        Returns:
            Dictionary with chat response and generation results
        """
        result = {
            "chat_response": "",
            "slide_generated": False,
            "pptx_path": None,
            "error": None
        }
        
        try:
            # Get chat response (without XML content)
            result["chat_response"] = self.chat_bot.chat(query)
            
            if generate_slide:
                # Generate slide XML
                slide_xml = self.slide_generator.generate_slide_xml(query, title, subtitle)
                
                # Create PowerPoint file
                output_filename = output_file or f"generated_slide_{len(query.split()[:3])}_{''.join(query.split()[:3])}.pptx"
                pptx_path = self.ppt_builder.create_presentation(slide_xml, output_filename)
                
                result["slide_generated"] = True
                result["pptx_path"] = pptx_path
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def interactive_slide_chat(self):
        """Start interactive chat session with slide generation capabilities."""
        print("🎯 RAG Slide Generator Chat")
        print("=" * 50)
        print("I can help you find slides AND generate new PowerPoint presentations!")
        print("\nCommands:")
        print("  • [query] - Search existing slides")
        print("  • generate: [query] - Generate new slide based on query")
        print("  • custom: [title] | [subtitle] | [query] - Generate with custom title/subtitle")
        print("  • 'quit' - Exit")
        print()
        
        # Ensure database is loaded
        if hasattr(self.vector_db, '_load_existing_embeddings'):
            try:
                # Try to trigger loading if not already done
                test_search = self.vector_db.search_similar("test", top_k=1)
                if not test_search:
                    print("📂 Loading vector database...")
            except:
                print("📂 Loading vector database...")
        
        generation_count = 0
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye! 👋")
                    break
                
                if not user_input:
                    continue
                
                # Parse commands
                if user_input.startswith("generate:"):
                    query = user_input[9:].strip()
                    if query:
                        print("\n🔧 Generating slide...")
                        result = self.chat_with_generation(query, generate_slide=True)
                        self._print_generation_result(result, query)
                        generation_count += 1
                    else:
                        print("Please provide a query after 'generate:'")
                        
                elif user_input.startswith("custom:"):
                    parts = user_input[7:].strip().split('|')
                    if len(parts) >= 3:
                        title = parts[0].strip()
                        subtitle = parts[1].strip()
                        query = parts[2].strip()
                        
                        print(f"\n🎨 Generating custom slide...")
                        print(f"   Title: {title}")
                        print(f"   Subtitle: {subtitle}")
                        result = self.chat_with_generation(query, generate_slide=True, 
                                                         title=title, subtitle=subtitle)
                        self._print_generation_result(result, query)
                        generation_count += 1
                    else:
                        print("Format: custom: [title] | [subtitle] | [query]")
                        
                else:
                    # Regular chat
                    print("\n🤖 Bot:", end=" ")
                    response = self.chat_bot.chat(user_input)
                    print(response)
                    print("\n💡 Tip: Use 'generate: [your query]' to create a PowerPoint slide!")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        if generation_count > 0:
            print(f"\n📊 Generated {generation_count} PowerPoint presentations this session!")
    
    def _print_generation_result(self, result: Dict[str, Any], query: str):
        """Print the results of slide generation."""
        if result["error"]:
            print(f"❌ Error: {result['error']}")
            return
        
        print("✅ Slide generated successfully!")
        
        if result["pptx_path"]:
            print(f"📁 PowerPoint file: {result['pptx_path']}")
        
        print(f"\n🔍 Related content found:")
        print(result["chat_response"][:300] + ("..." if len(result["chat_response"]) > 300 else ""))


def main():
    """Main function for RAG slide generation system."""
    print("🚀 Initializing RAG Slide Generation System...")
    
    # Check if comprehensive database exists
    db_path = "comprehensive_slides_db.sqlite"
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("Please run enhanced_vector_db.py first to build the database.")
        return
    
    # Initialize system
    vector_db = VectorDatabase(db_path)
    slide_chat = RAGSlideChat(vector_db)
    
    print("✅ System ready!")
    print("\n" + "="*60)
    
    # Start interactive chat
    slide_chat.interactive_slide_chat()


if __name__ == "__main__":
    main()