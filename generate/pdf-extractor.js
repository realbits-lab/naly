import fs from 'fs';
import { createRequire } from 'module';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';

const require = createRequire(import.meta.url);
const pdf = require('pdf-parse');

class PDFExtractor {
  constructor() {
    this.textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200,
    });
  }

  async extractTextWithHierarchy(pdfPath) {
    try {
      const dataBuffer = fs.readFileSync(pdfPath);
      const data = await pdf(dataBuffer);
      
      console.log(`Extracted ${data.numpages} pages from PDF`);
      
      // Parse the text to identify hierarchy
      const structuredContent = this.parseTextStructure(data.text);
      
      // Create chunks with metadata
      const chunks = await this.createChunksWithMetadata(structuredContent);
      
      return {
        totalPages: data.numpages,
        chunks: chunks,
        metadata: {
          title: this.extractTitle(data.text),
          totalCharacters: data.text.length,
          extractedAt: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Error extracting PDF:', error);
      throw error;
    }
  }

  parseTextStructure(text) {
    const lines = text.split('\n');
    const structuredContent = [];
    let currentSection = null;
    let currentSubsection = null;
    let currentParagraph = [];
    
    // Regex patterns for different hierarchy levels
    const titlePattern = /^[A-Z][A-Z\s\d\.\-:]{10,}$/;
    const sectionPattern = /^\d+\.?\s+[A-Z][A-Za-z\s\d\.\-:]{5,}$/;
    const subsectionPattern = /^\d+\.\d+\.?\s+[A-Z][A-Za-z\s\d\.\-:]{5,}$/;
    const listItemPattern = /^[\s]*[•\-\*\d+\.]\s+/;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (!line) continue;
      
      // Check for different hierarchy levels
      if (titlePattern.test(line)) {
        this.flushCurrentParagraph(structuredContent, currentParagraph, currentSection, currentSubsection);
        currentSection = {
          type: 'title',
          level: 0,
          text: line,
          content: []
        };
        structuredContent.push(currentSection);
        currentSubsection = null;
        currentParagraph = [];
      } else if (sectionPattern.test(line)) {
        this.flushCurrentParagraph(structuredContent, currentParagraph, currentSection, currentSubsection);
        currentSection = {
          type: 'section',
          level: 1,
          text: line,
          content: []
        };
        structuredContent.push(currentSection);
        currentSubsection = null;
        currentParagraph = [];
      } else if (subsectionPattern.test(line)) {
        this.flushCurrentParagraph(structuredContent, currentParagraph, currentSection, currentSubsection);
        currentSubsection = {
          type: 'subsection',
          level: 2,
          text: line,
          content: []
        };
        if (currentSection) {
          currentSection.content.push(currentSubsection);
        } else {
          structuredContent.push(currentSubsection);
        }
        currentParagraph = [];
      } else if (listItemPattern.test(line)) {
        this.flushCurrentParagraph(structuredContent, currentParagraph, currentSection, currentSubsection);
        const listItem = {
          type: 'list-item',
          level: 3,
          text: line
        };
        this.addToCurrentContainer(listItem, currentSection, currentSubsection, structuredContent);
        currentParagraph = [];
      } else {
        // Regular paragraph text
        if (line.length > 5) { // Filter out very short lines
          currentParagraph.push(line);
        }
      }
    }
    
    // Flush any remaining paragraph
    this.flushCurrentParagraph(structuredContent, currentParagraph, currentSection, currentSubsection);
    
    return structuredContent;
  }

  flushCurrentParagraph(structuredContent, currentParagraph, currentSection, currentSubsection) {
    if (currentParagraph.length > 0) {
      const paragraph = {
        type: 'paragraph',
        level: 3,
        text: currentParagraph.join(' ')
      };
      this.addToCurrentContainer(paragraph, currentSection, currentSubsection, structuredContent);
      currentParagraph.length = 0;
    }
  }

  addToCurrentContainer(item, currentSection, currentSubsection, structuredContent) {
    if (currentSubsection) {
      currentSubsection.content.push(item);
    } else if (currentSection) {
      currentSection.content.push(item);
    } else {
      structuredContent.push(item);
    }
  }

  async createChunksWithMetadata(structuredContent) {
    const chunks = [];
    
    for (const section of structuredContent) {
      await this.processSection(section, chunks, []);
    }
    
    return chunks;
  }

  async processSection(section, chunks, parentPath) {
    const currentPath = [...parentPath, section.text || section.type];
    
    if (section.type === 'paragraph' || section.type === 'list-item') {
      // Create chunks for content
      const textChunks = await this.textSplitter.splitText(section.text);
      
      for (const chunk of textChunks) {
        chunks.push({
          id: `chunk_${chunks.length + 1}`,
          text: chunk,
          metadata: {
            type: section.type,
            level: section.level,
            hierarchy: currentPath.slice(0, -1), // Exclude the paragraph text itself
            section: parentPath.join(' > '),
            chunkIndex: chunks.length + 1
          }
        });
      }
    } else if (section.content && section.content.length > 0) {
      // Process nested content
      for (const subsection of section.content) {
        await this.processSection(subsection, chunks, currentPath);
      }
    } else {
      // Section header without content
      chunks.push({
        id: `chunk_${chunks.length + 1}`,
        text: section.text,
        metadata: {
          type: section.type,
          level: section.level,
          hierarchy: currentPath.slice(0, -1),
          section: parentPath.join(' > '),
          chunkIndex: chunks.length + 1
        }
      });
    }
  }

  extractTitle(text) {
    const lines = text.split('\n');
    for (const line of lines.slice(0, 20)) {
      if (line.trim().length > 20 && line.trim().length < 100) {
        return line.trim();
      }
    }
    return 'ECMA-376 Document';
  }
}

export default PDFExtractor;