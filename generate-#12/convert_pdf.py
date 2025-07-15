#!/usr/bin/env python3
"""
Convert PDF to Markdown using PyMuPDF4LLM with structure preservation
"""
import pymupdf4llm

def convert_pdf_to_markdown(pdf_path, output_path):
    """Convert PDF to markdown with structure preservation"""
    try:
        # Convert PDF to markdown
        md_text = pymupdf4llm.to_markdown(pdf_path)
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        
        print(f"Successfully converted {pdf_path} to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return False

if __name__ == "__main__":
    pdf_file = "ecma-376.pdf"
    output_file = "ecma-376-pymupdf.md"
    
    success = convert_pdf_to_markdown(pdf_file, output_file)
    if success:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed!")